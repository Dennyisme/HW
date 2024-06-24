from Random_Buy_Example import Buy_Stock, Sell_Stock, Get_Stock_Informations, Get_User_Stocks
from datetime import datetime, timedelta
import os
import numpy as np
import torch
from torch import nn, optim
from model_predict import model_predict

stop_date = datetime.today().strftime('%Y%m%d')
start_date = (datetime.today() - timedelta(days=14)).strftime('%Y%m%d')

def getData(stock_code): # 抓當日到前14天的數據
    stop_date = datetime.today().strftime('%Y%m%d')
    start_date = (datetime.today() - timedelta(days=14)).strftime('%Y%m%d')
    data = Get_Stock_Informations(stock_code, start_date, stop_date)
    data = list(reversed(data))
    return data

def input_model_data(data): # 處理要輸入model內的資料
    extracted_data=[]
    # 挑出date、high、low、open、close
    for item in data:
        extracted_data.append([item['high'], item['low'], item['open'], item['close']])
    extracted_data = list(reversed(extracted_data))
    extracted_data = torch.tensor(extracted_data, dtype=torch.float)
    extracted_data = extracted_data.unsqueeze(0)
    
    return extracted_data

def calculate_rsi(data): # 計算rsi
    up_date_count = 0
    total_up = 0
    down_date_count = 0
    total_down = 0
    for item in data:
        if item['change'] < 0:
            down_date_count += 1
            total_down += item['change']
        else:
            up_date_count += 1
            total_up += item['change']
    averge_up = total_up / up_date_count
    # print("averge_up: ",averge_up)
    averge_down = abs(total_down / down_date_count)
    # print("averge_down: ",averge_down)
    rsi = round(averge_up / (averge_up + averge_down) * 100, 2)
    return rsi

def sell(stock_code, account, password): # 賣出
    user_stocks = Get_User_Stocks(account, password)

    for stock in user_stocks:
        if stock['stock_code_id'] == stock_code:
            sell_price = sell_or_buy_price(stock_code)
            Sell_Stock(account, password, stock_code, stock['shares'], sell_price)
            
def buy(stock_code, account, password): # 買入
    buy_price = sell_or_buy_price(stock_code)
    drift_price = buy_price * 0.02
    if buy_price > 100:
        for i in range(11):
            Buy_Stock(account, password, stock_code, 10, buy_price - drift_price + (i / 5) * drift_price)
    else:
        for i in range(11):
            Buy_Stock(account, password, stock_code, 20, buy_price - drift_price + (i / 5) * drift_price)
            
def sell_or_buy_price(stock_code): # 獲取交易價格
    today = datetime.today().strftime('%Y%m%d')
    start_date = (datetime.today() - timedelta(days=7)).strftime('%Y%m%d')
    # print(Get_Stock_Informations(stock_code, start_date, today))
    last_day_info = Get_Stock_Informations(stock_code, start_date, today)
    price = last_day_info[0]["close"]
    print("交易價格: ", price)
    return price


def predict(stock_code, account, password): # 預測交易動作
    data = getData(stock_code)
    rsi = calculate_rsi(data)
    print("RSI: ", rsi)
    if rsi > 70:
        sell(stock_code, account, password)
        # Sell_Stock(account, password, stock_code, quantity, price)
    elif rsi < 30:
        buy(stock_code, account, password)
    else: # DL 輔助
        lookback = 14
        operation = model_predict(stock_code, lookback)
        
        match operation:
            case "買入":
                buy(stock_code, account, password)
            case "賣出":
                sell(stock_code, account, password)
            case "觀望":
                print('觀望中')



account = "P76121314"
password = "1314"

# 欲預測之股票
stock_code_list = ["1614", "2467", "2476", "2615", "8462", "5906", "5388", "4739",
                   "1608", "4126", "3705", "2511", "6442", "1447", "4739", "3454",
                   "1615", "1442", "3622", "1323", "9940", "3229", "2438", "1414"]

for stock_code in stock_code_list:
    print("===============================================================")
    print(f"Predict stock code: {stock_code}")
    predict(stock_code, account, password)