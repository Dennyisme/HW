import math
from dataclasses import dataclass
from typing import Union

import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
import math
from tqdm import tqdm
from dataset.loadData import getData, getValData
from torch.optim.lr_scheduler import StepLR
import torch.nn.functional as F
import time
from dataprocessor import standardize_data, normalize_data, inverse_normalize



@dataclass
class MambaConfig:
    d_model: int # D
    n_layers: int
    dt_rank: Union[int, str] = 'auto'
    d_state: int = 128
    expand_factor: int = 2 
    d_conv: int = 4

    dt_min: float = 0.001
    dt_max: float = 0.1
    dt_init: str = "random"
    dt_scale: float = 1.0
    dt_init_floor = 1e-4

    bias: bool = False
    conv_bias: bool = True

    pscan: bool = True 

    def __post_init__(self):
        self.d_inner = self.expand_factor * self.d_model

        if self.dt_rank == 'auto':
            self.dt_rank = math.ceil(self.d_model / 16)

class Mamba(nn.Module):
    def __init__(self, config: MambaConfig):
        super().__init__()

        self.config = config
        self.norm = nn.LayerNorm(config.d_model)
        self.layers = nn.ModuleList([ResidualBlock(config) for _ in range(config.n_layers)])
        #self.norm_f = RMSNorm(config.d_model)
        self.fc1 = nn.Linear(config.d_model, 128)
        self.batch_norm = nn.BatchNorm1d(1)
        self.relu = nn.ReLU()
        self.fc2 = nn.Linear(128, 128)
        self.fc3 = nn.Linear(128, config.d_model)


    def forward(self, x):
        x_shortcut = x.clone()
        # x = self.norm(x)
        for layer in self.layers:
            x = layer(x)
        x = x + x_shortcut
        out_put = x.sum(dim=1, keepdim=True)
        out_put = self.fc1(out_put)
        # out_put = self.batch_norm(out_put)
        out_put = self.relu(out_put)
        out_put = self.fc2(out_put)
        # out_put = self.relu(out_put)
        out_put = self.fc3(out_put)

        #x = self.norm_f(x)
        

        return out_put
    
    def step(self, x, caches):

        for i, layer in enumerate(self.layers):
            x, caches[i] = layer.step(x, caches[i])

        return x, caches

class ResidualBlock(nn.Module):
    def __init__(self, config: MambaConfig):
        super().__init__()

        self.mixer = MambaBlock(config)
        self.norm = RMSNorm(config.d_model)

    def forward(self, x):


        output = self.mixer(self.norm(x)) + x
        return output
    
    def step(self, x, cache):

        output, cache = self.mixer.step(self.norm(x), cache)
        output = output + x
        return output, cache

class MambaBlock(nn.Module):
    def __init__(self, config: MambaConfig):
        super().__init__()

        self.config = config

        # projects block input from D to 2*ED (two branches)
        self.in_proj = nn.Linear(config.d_model, 2 * config.d_inner, bias=config.bias)

        self.conv1d = nn.Conv1d(in_channels=config.d_inner, out_channels=config.d_inner, 
                              kernel_size=config.d_conv, bias=config.conv_bias, 
                              groups=config.d_inner,
                              padding=config.d_conv - 1)
        
        # projects x to -dependent Δ, B, C
        self.x_proj = nn.Linear(config.d_inner, config.dt_rank + 2 * config.d_state, bias=False)

        # projects Δ from dt_rank to d_inner
        self.dt_proj = nn.Linear(config.dt_rank, config.d_inner, bias=True)

        # dt initialization
        # dt weights
        dt_init_std = config.dt_rank**-0.5 * config.dt_scale
        if config.dt_init == "constant":
            nn.init.constant_(self.dt_proj.weight, dt_init_std)
        elif config.dt_init == "random":
            nn.init.uniform_(self.dt_proj.weight, -dt_init_std, dt_init_std)
        else:
            raise NotImplementedError
        
        # dt bias
        dt = torch.exp(
            torch.rand(config.d_inner) * (math.log(config.dt_max) - math.log(config.dt_min)) + math.log(config.dt_min)
        ).clamp(min=config.dt_init_floor)
        inv_dt = dt + torch.log(-torch.expm1(-dt))
        with torch.no_grad():
            self.dt_proj.bias.copy_(inv_dt)
      

        # S4D real initialization
        A = torch.arange(1, config.d_state + 1, dtype=torch.float32).repeat(config.d_inner, 1)
        self.A_log = nn.Parameter(torch.log(A))
        self.D = nn.Parameter(torch.ones(config.d_inner))

        self.out_proj = nn.Linear(config.d_inner, config.d_model, bias=config.bias)

    def forward(self, x):


        _, L, _ = x.shape

        xz = self.in_proj(x)
        x, z = xz.chunk(2, dim=-1)

        x = x.transpose(1, 2) 
        x = self.conv1d(x)[:, :, :L] 
        x = x.transpose(1, 2) 

        x = F.silu(x)
        y = self.ssm(x)

        z = F.silu(z)

        output = y * z
        output = self.out_proj(output)

        return output
    
    def ssm(self, x):
        A = -torch.exp(self.A_log.float())
        D = self.D.float()

        deltaBC = self.x_proj(x)

        delta, B, C = torch.split(deltaBC, 
                                  [self.config.dt_rank, self.config.d_state, self.config.d_state], dim=-1) # (B, L, dt_rank), (B, L, N), (B, L, N)
        delta = F.softplus(self.dt_proj(delta))

        y = self.selective_scan_seq(x, delta, A, B, C, D)

        return y
    
    def selective_scan_seq(self, x, delta, A, B, C, D):

        _, L, _ = x.shape

        deltaA = torch.exp(delta.unsqueeze(-1) * A)
        deltaB = delta.unsqueeze(-1) * B.unsqueeze(2)

        BX = deltaB * (x.unsqueeze(-1))

        h = torch.zeros(x.size(0), self.config.d_inner, self.config.d_state, device=deltaA.device) # (B, ED, N)
        hs = []

        for t in range(0, L):
            h = deltaA[:, t] * h + BX[:, t]
            hs.append(h)
            
        hs = torch.stack(hs, dim=1)

        y = (hs @ C.unsqueeze(-1)).squeeze(3)

        y = y + D * x

        return y
    

    
    def step(self, x, cache):
      
        h, inputs = cache
        
        xz = self.in_proj(x)
        x, z = xz.chunk(2, dim=1)

        x_cache = x.unsqueeze(2)
        x = self.conv1d(torch.cat([inputs, x_cache], dim=2))[:, :, self.config.d_conv-1] # (B, ED)

        x = F.silu(x)
        y, h = self.ssm_step(x, h)

        z = F.silu(z)

        output = y * z
        output = self.out_proj(output)

        inputs = torch.cat([inputs[:, :, 1:], x_cache], dim=2)
        cache = (h, inputs)
        
        return output, cache

    def ssm_step(self, x, h):
        
        A = -torch.exp(self.A_log.float())
        D = self.D.float()


        deltaBC = self.x_proj(x)

        delta, B, C = torch.split(deltaBC, [self.config.dt_rank, self.config.d_state, self.config.d_state], dim=-1) # (B, dt_rank), (B, N), (B, N)
        delta = F.softplus(self.dt_proj(delta))

        deltaA = torch.exp(delta.unsqueeze(-1) * A)
        deltaB = delta.unsqueeze(-1) * B.unsqueeze(1)

        BX = deltaB * (x.unsqueeze(-1))

        if h is None:
            h = torch.zeros(x.size(0), self.config.d_inner, self.config.d_state, device=deltaA.device) # (B, ED, N)

        h = deltaA * h + BX

        y = (h @ C.unsqueeze(-1)).squeeze(2)

        y = y + D * x

        return y, h.squeeze(1)

class RMSNorm(nn.Module):
    def __init__(self, d_model: int, eps: float = 1e-5):
        super().__init__()

        self.eps = eps
        self.weight = nn.Parameter(torch.ones(d_model))

    def forward(self, x):
        output = x * torch.rsqrt(x.pow(2).mean(-1, keepdim=True) + self.eps) * self.weight

        return output
    

if torch.cuda.is_available():
    device = torch.device("cuda")
    print("Mamba running on the GPU")
else:
    device = torch.device("cpu")
    print("Mamba running on the CPU")

code="2330"
start_data="20100101"
end_data="20231231"
train_data, train_label = getData(code, start_data, end_data)
train_data, max_data, min_data = normalize_data(train_data)
min_data = min_data.to(device)
max_data = max_data.to(device)
print(train_data.shape)
print(train_label.shape)
train_data = train_data.contiguous().to(device)
train_label = train_label.contiguous().to(device)

epoch_num = 5
batch_size = 10
config = MambaConfig(d_model=4, n_layers=3)

mamba = Mamba(config).to(device)
criterion = nn.MSELoss(reduction='mean')
optimizer = optim.Adam(mamba.parameters(), lr=0.01, betas=(0.9, 0.98), eps=1e-9)
scheduler = StepLR(optimizer, step_size=5, gamma=0.1)
mamba.train()

for epoch in tqdm(range(epoch_num)):
    for batch in range(0, train_data.shape[0], batch_size):
        optimizer.zero_grad()
        
        input_batch = train_data[batch:batch+batch_size, :, :] # shape: [batch_size, seq_length, feature_num]
        target_batch = train_label[batch:batch+batch_size, -1, :] # shape: [batch_size, feature_num]


        output = mamba(input_batch) # shape: [batch_size, seq_length, feature_num]

        output = output.squeeze(1) # shape: [batch_size, feature_num]
        # loss = criterion(output, target_batch)
        RMSLoss = torch.sqrt(criterion(output, target_batch))

        # loss.backward()
        RMSLoss.backward()
        optimizer.step()
        scheduler.step()

        # print(f"Epoch: {epoch+1}, Batch: {batch // batch_size + 1}, Loss: {loss.item()}")
        print(f"Epoch: {epoch+1}, Batch: {batch // batch_size + 1}, Loss: {RMSLoss.item()}")

mamba.eval()

start_time = time.time()
code="2330"
start_data="20231201"
end_data="20240316"

val_data ,val_label = getValData(code, start_data, end_data)
val_data = val_data.to(device)
val_label = val_label.to(device)
val_data = (val_data - min_data) / (max_data - min_data)
print("val_data: ",val_data)

result = mamba(val_data)
result = result.squeeze(1)

# result = inverse_normalize(result, min_data, max_data)
val_RMSLoss = torch.sqrt(criterion(result, val_label))
print("[最高, 最低, 開盤, 收盤]")
print("result: ", result)
print("target: ",val_label)
print(f"val loss: {val_RMSLoss}")

print(f'推論時間: {time.time() - start_time} seconds')
total_params = sum(p.numel() for p in mamba.parameters())
trainable_params = sum(p.numel() for p in mamba.parameters() if p.requires_grad)

print(f"Total Parameters: {total_params}")
print(f"Trainable Parameters: {trainable_params}")