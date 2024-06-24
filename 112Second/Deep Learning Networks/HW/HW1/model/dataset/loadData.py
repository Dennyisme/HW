import requests, json
import sys
from dataset.reference.sell_and_buy import Get_Stock_Informations
# from reference.sell_and_buy import Get_Stock_Informations
from datetime import datetime
import torch


code="2330"
start_data="20100101"
end_data="20231231"
def getData(code, start_data, end_data):
    data = Get_Stock_Informations(code, start_data, end_data)
    # print(data)
    extracted_data=[]

    # 挑出date、high、low、open、close
    for item in data:
        extracted_data.append([item['high'], item['low'], item['open'], item['close']])

    extracted_data = list(reversed(extracted_data))


    train_data = extracted_data.copy()
    train_label = extracted_data.copy()

    del train_data[-1] # 預測數據刪除最後一個數據
    del train_label[0]
    
   
    print('len: ',len(train_data))
    print('len: ',len(train_label))

    train_data_group_num = len(train_data) - 30 + 1
    train_label_group_num = len(train_label) -30 + 1

    train_data = [train_data[i:i+30] for i in range(train_data_group_num)]
    train_label = [train_label[i:i+30] for i in range(train_label_group_num)]
   
    # # 張量化
    train_data = torch.tensor(train_data, dtype=torch.float)
    train_label = torch.tensor(train_label, dtype=torch.float)
    print("train_data: ",train_data.shape)
    print("train_label: ",train_label.shape)
    return train_data, train_label

def getValData(code, start_data, end_data):
    data = Get_Stock_Informations(code, start_data, end_data)
    extracted_data = []
    for item in data:
        extracted_data.append([item['high'], item['low'], item['open'], item['close']])
    extracted_data = list(reversed(extracted_data))
    val_data = extracted_data[-31:-1]
    val_label = extracted_data[-1]
    val_data = torch.tensor(val_data, dtype=torch.float)
    val_label = torch.tensor(val_label, dtype=torch.float)
    val_data = val_data.unsqueeze(0)
    val_label = val_label.unsqueeze(0)
    print("val_data",val_data.shape)
    print("val_label",val_label.shape)
    
    return val_data, val_label


    


#轉換成可讀日期
# for item in extracted_data:
#     item['date'] = datetime.fromtimestamp(item['date']).strftime('%Y-%m-%d')
# print(extracted_data)