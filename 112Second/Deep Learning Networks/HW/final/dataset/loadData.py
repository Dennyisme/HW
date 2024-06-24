from Random_Buy_Example import Get_Stock_Informations
import torch
from datetime import datetime, timedelta
import pandas as pd
from datetime import datetime

# code="2330"
# start_data="20100101"
# end_data="20231231"
def getData(code):
    stop_date = datetime.today().strftime('%Y%m%d')
    data = Get_Stock_Informations(code, "20210101", stop_date)
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

def get_train_close_price(stock_code, start_date):
    end_date = datetime.today().strftime('%Y%m%d')
    data = Get_Stock_Informations(stock_code, start_date, end_date)
    data = pd.DataFrame(data)
    data['date'] = pd.to_datetime(data['date'], unit='s')
    data = data[['date', 'close']]
    
    # print(data)
    data = data.sort_values(by='date', ascending=True)
    return data

def get_close_price(stock_code, num_day):
    end_date = datetime.today().strftime('%Y%m%d')
    start_date = "20100101"
    data = Get_Stock_Informations(stock_code, start_date, end_date)
    extracted_data=[]

    # 挑出date、high、low、open、close
    for item in data:
        extracted_data.append(item['close'])
    extracted_data = list(reversed(extracted_data))
    return [extracted_data[-num_day:]]
    