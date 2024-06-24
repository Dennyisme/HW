import torch

def standardize_data(data):
    mean = data.mean(dim=0, keepdim=True)
    std = data.std(dim=0, keepdim=True)
    standardized_data = (data - mean) / (std + 1e-6)  # 加上一个小的值避免除以0
    return standardized_data, mean, std

def normalize_data(data):
    min_val = data.min(dim=0, keepdim=True)[0].min(dim=1, keepdim=True)[0]
    max_val = data.max(dim=0, keepdim=True)[0].max(dim=1, keepdim=True)[0]
    return (data - min_val) / (max_val - min_val), max_val, min_val

def inverse_normalize(data_normalized, min_val, max_val):
    return data_normalized * (max_val - min_val) + min_val
