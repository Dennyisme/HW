import torch
import torch.nn as nn
import torch.optim as optim
import torch.utils.data as data
import math
import copy
from tqdm import tqdm
from dataset.loadData import getData, getValData
from torch.optim.lr_scheduler import StepLR
import time
from dataprocessor import standardize_data, normalize_data, inverse_normalize
import numpy as np


class MultiHeadAttention(nn.Module):
    def __init__(self, d_model, num_heads):
        super(MultiHeadAttention, self).__init__()
        
        assert d_model % num_heads == 0, "d_model must be divisible by num_heads"
        
        self.d_model = d_model
        self.num_heads = num_heads
        self.d_k = d_model // num_heads
        self.W_q = nn.Linear(d_model, d_model) 
        self.W_k = nn.Linear(d_model, d_model) 
        self.W_v = nn.Linear(d_model, d_model)
        self.W_o = nn.Linear(d_model, d_model)
    
    def scaled_dot_product_attention(self, Q, K, V, mask=None):
        # Calculate attention scores
        attn_score = torch.matmul(Q, K.transpose(-2, -1)) / math.sqrt(self.d_k)
    
        # Apply mask if provided
        if mask is not None:
            attn_score = attn_score.masked_fill(mask == 0, -1e9)
        
        # Softmax is applied to obtain attention probability
        attn_probs = torch.softmax(attn_score, dim=-1)
        output = torch.matmul(attn_probs, V)
        return output

    def split_heads(self, x):
        batch_size, seq_length, d_model = x.size() # total_days == seq_length
        return x.view(batch_size, seq_length, self.num_heads, self.d_k).transpose(1, 2) # shape：(batch_size, self.num_heads, seq_length, self.d_k)

    def combine_heads(self, x):
        batch_size, num_heads, seq_length, d_k = x.shape
        return x.transpose(1, 2).contiguous().view(batch_size, seq_length, self.d_model) # shape：(batch_size, seq_length, self.d_model)
    
    def forward(self, Q, K, V, mask=None):
        Q = self.split_heads(self.W_q(Q))
        K = self.split_heads(self.W_k(K))
        V = self.split_heads(self.W_v(V))
        
        attn_output = self.scaled_dot_product_attention(Q, K, V, mask)
        
        output = self.W_o(self.combine_heads(attn_output))
        
        return output
    
class PositionWiseFeedForward(nn.Module):
    def __init__(self, d_model, d_ff):
        super(PositionWiseFeedForward, self).__init__()
        self.fc1 = nn.Linear(d_model, d_ff)
        self.fc2 = nn.Linear(d_ff, d_model)
        self.relu = nn.ReLU()
        
    def forward(self, x):
        return self.fc2(self.relu(self.fc1(x)))

class PositionalEncoding(nn.Module):
    def __init__(self):
        super(PositionalEncoding, self).__init__()
        
    def forward(self, x, device):
        position = torch.arange(0, x.shape[1]).unsqueeze(1).float().to(device=device)
        # position = position.expand(-1, x.shape[-1])
        # print("ww: ", position)
        position = position.unsqueeze(0).expand(x.shape[0], -1, -1)
        # print("kkk: ",position)
        # position, _, _ = normalize_data(position)
        # self.register_buffer("pe", position)
        # print("hhh: ",x)
        # return x + position[:, :x.size(1), :]
        # print("qqqq: ", torch.cat([position, x], dim=-1))
        return torch.cat([x, position], dim=-1)
        
# class PositionalEncoding(nn.Module):
#     def __init__(self, d_model, max_seq_len):
#         super(PositionalEncoding, self).__init__()
#         self.d_model = d_model
#         self.max_seq_len = max_seq_len
#         self.positional_encoding = self._generate_positional_encoding()

#     def _generate_positional_encoding(self):
#         pe = torch.zeros(self.max_seq_len, self.d_model)
#         position = torch.arange(0, self.max_seq_len).unsqueeze(1).float()
#         div_term = torch.exp(torch.arange(0, self.d_model, 2).float() * (-np.log(10000.0) / self.d_model))
#         pe[:, 0::2] = torch.sin(position * div_term)
#         pe[:, 1::2] = torch.cos(position * div_term)
#         return pe

#     def forward(self, x, device):
#         # Assuming x has shape (batch_size, seq_len, d_model)
#         seq_len = x.size(1)
#         pe = self.positional_encoding[:seq_len, :]
#         return torch.cat([x, pe.unsqueeze(0)], dim=1)
        


class EncoderLayer(nn.Module):
    def __init__(self, d_model, num_heads, d_ff, dropout):
        super(EncoderLayer, self).__init__()
        self.self_attn = MultiHeadAttention(d_model, num_heads)
        self.feed_forward = PositionWiseFeedForward(d_model, d_ff)
        self.norm1 = nn.LayerNorm(d_model)
        self.norm2 = nn.LayerNorm(d_model)

        self.fc1 = nn.Linear(d_model, d_model // 2)
        self.fc2 = nn.Linear(d_model // 2, d_model // 2)
        self.fc3 = nn.Linear(d_model // 2, d_model)

        self.dropout = nn.Dropout(dropout)
        
    def forward(self, x, mask):
        attn_output = self.self_attn(x, x, x, mask)
        x = self.norm1(x + self.dropout(attn_output))
        ffn_output = self.feed_forward(x)
        x = self.norm2(x + self.dropout(ffn_output))

        return x

class Transformer(nn.Module):
    def __init__(self, d_model, num_heads, num_layer, d_ff, dropout):
        super(Transformer, self).__init__()
        self.positionEncodeing = PositionalEncoding()
        self.encoder_layers = nn.ModuleList([EncoderLayer(d_model, num_heads, d_ff, dropout) for _ in range(num_layer)])

        self.projection = nn.Linear(5, d_model)
        self.projection2 = nn.Linear(4, d_model)
        self.fc1 = nn.Linear(d_model, d_model // 4)
        self.fc2 = nn.Linear(d_model // 4, d_model // 16)
        self.fc3 = nn.Linear(d_model // 16, 4)
        self.norm = nn.LayerNorm(1024)
        self.relu = nn.ReLU()
        self.dropout = nn.Dropout(dropout)
        
    def forward(self, src, device):
        src_mask = None
        src_shortcut = src.clone()
        src = self.positionEncodeing(src, device)
        src = self.projection(src)
        for enc_layer in self.encoder_layers:
            src = enc_layer(src, src_mask)
        src_shortcut = self.projection2(src_shortcut)
        src = src_shortcut + src
        out_put = src.sum(dim=1, keepdim=True)
        out_put = self.fc1(out_put)
        out_put = self.relu(out_put)
        out_put = self.fc2(out_put)
        # out_put = self.relu(out_put)
        out_put = self.fc3(out_put)       
        return out_put

if torch.cuda.is_available():
    device = torch.device("cuda")
    print("Transformer running on the GPU")
else:
    device = torch.device("cpu")
    print("Transformer running on the CPU")

code="2330"
start_data="20100101"
end_data="20231231"

d_model = 128
num_heads = 8
num_layers = 6
d_ff = 256
dropout = 0.1
epoch_num = 10
batch_size = 10

transformer = Transformer(d_model, num_heads, num_layers, d_ff, dropout).to(device)

train_data, train_label = getData(code, start_data, end_data)
# train_data, max_data, min_data = normalize_data(train_data)
# min_data = min_data.to(device)
# max_data = max_data.to(device)
print(train_data.shape)
print(train_label.shape)
train_data = train_data.contiguous().to(device)
train_label = train_label.contiguous().to(device)

criterion = nn.MSELoss(reduction='mean')
optimizer = optim.Adam(transformer.parameters(), lr=0.01, betas=(0.9, 0.98), eps=1e-9)
scheduler = StepLR(optimizer, step_size=5, gamma=0.1)

transformer.train()
for epoch in tqdm(range(epoch_num)):
    for batch in range(0, train_data.shape[0], batch_size):
        optimizer.zero_grad()
        
        input_batch = train_data[batch:batch+batch_size, :, :] # shape: [batch_size, seq_length, feature_num]
        target_batch = train_label[batch:batch+batch_size, -1, :] # shape: [batch_size, feature_num]
        
        output = transformer(input_batch, device) # shape: [batch_size, seq_length, feature_num]
        output = output.squeeze(1) # shape: [batch_size, feature_num]
        output = output + input_batch[:, -1, :]
        # output = inverse_normalize(output, min_data, max_data)
        
        RMSLoss = torch.sqrt(criterion(output, target_batch))
        # high_low_penalty = (output[:, 1] - output[:, 0]).clamp(min=0).mean()
        # open_low_penalty = (output[:, 1] - output[:, 2]).clamp(min=0).mean()
        # close_low_penalty = (output[:, 1] - output[:, 3]).clamp(min=0).mean()
        # open_high_penalty = (output[:, 2] - output[:, 0]).clamp(min=0).mean()
        # close_high_penalty = (output[:, 3] - output[:, 0]).clamp(min=0).mean()
        # negative_penalty = output.clamp(max=0).abs().mean()
        # low_price_constraint = (output[:, 2] * 0.9 - output[:, 1]).clamp(min=0).mean()
        # high_price_constraint = (output[:, 0] - output[:, 2] * 1.1).clamp(min=0).mean()
        
        # loss = (RMSLoss + high_low_penalty + open_low_penalty + close_low_penalty + open_high_penalty
        #          + close_high_penalty + negative_penalty + low_price_constraint + high_price_constraint)
        
        # loss.backward()
        RMSLoss.backward()
        optimizer.step()
        scheduler.step()

        print(f"Epoch: {epoch+1}, Batch: {batch // batch_size + 1}, Loss: {RMSLoss.item()}")

transformer.eval()

start_time = time.time()
code="2330"
start_data="20231201"
end_data="20240101"

val_data ,val_label = getValData(code, start_data, end_data)
val_data = val_data.contiguous().to(device)
val_label = val_label.contiguous().to(device)
# val_data = (val_data - min_data) / (max_data - min_data)
print("val_data: ",val_data)

result = transformer(val_data, device)
result = result.squeeze(1)
result = result + val_data[:, -1, :]
val_loss = torch.sqrt(criterion(result, val_label))
print("[最高, 最低, 開盤, 收盤]")
print("result: ", result)
print("target: ",val_label)
print(f"val loss: {val_loss}")

print(f'推論時間: {time.time() - start_time} seconds')
total_params = sum(p.numel() for p in transformer.parameters())
trainable_params = sum(p.numel() for p in transformer.parameters() if p.requires_grad)

print(f"Total Parameters: {total_params}")
print(f"Trainable Parameters: {trainable_params}")
torch.save(transformer.state_dict(), './models/ownModel.pt')