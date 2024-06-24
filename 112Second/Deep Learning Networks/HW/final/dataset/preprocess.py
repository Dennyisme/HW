from copy import deepcopy as dc
import numpy as np
from torch.utils.data import Dataset


def prepare_dataframe_for_lstm(data, n_steps=7):
    # data = dc(data)
    
    data.set_index('date', inplace=True)
    
    for i in range(1, n_steps+1):
        data[f"close(t-{i})"] = data['close'].shift(i)
        
    data.dropna(inplace=True) # 刪除Nan的行
    # print(data)
    return data

class TimeSeriesDataset(Dataset):
    def __init__(self, X, y):
        self.X = X
        self.y = y
        
    def __len__(self):
        return len(self.X)
    
    def __getitem__(self, i):
        return self.X[i], self.y[i]