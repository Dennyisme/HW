from dataset.loadData import get_train_close_price, get_close_price
from dataset.preprocess import prepare_dataframe_for_lstm, TimeSeriesDataset
from sklearn.preprocessing import MinMaxScaler
from copy import deepcopy as dc
import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import DataLoader
from model.lstm import LSTM
import matplotlib.pyplot as plt
import os

def train_one_epoch(model, train_loader, device, loss_function, optimizer):
    model.train(True)
    running_loss = 0.0
    for batch_index, batch in enumerate(train_loader):
        # print(batch.shape)
        x_batch, y_batch = batch[0].to(device), batch[1].to(device)
        
        output = model(x_batch)
        loss = loss_function(output, y_batch)
        running_loss += loss.item()
        loss.backward()
        optimizer.step()
        
        if batch_index % 100 == 99:
            avg_loss_across_batches = running_loss / 100
            print('Batch {0}, Loss: {1:3f}'.format(batch_index+1, avg_loss_across_batches))  
            
            running_loss = 0.0 
            
def validate_one_epoch(model, test_loader, device, loss_function):
    model.train(False)
    running_loss = 0.0
    
    for batch_index, batch in enumerate(test_loader):
        x_batch, y_batch = batch[0].to(device), batch[1].to(device)
        
        with torch.no_grad():
            output = model(x_batch)
            loss = loss_function(output, y_batch)
            running_loss += loss.item()
    
    avg_loss_across_batches = running_loss / len(test_loader)
    print('Val Loss: {0:.3f}'.format(avg_loss_across_batches))
    print('**************************************************')
    
# 創建保存圖像之資料夾
def ensure_dir(file_path):
    directory = os.path.dirname(file_path)
    if not os.path.exists(directory):
        os.makedirs(directory)

# stock_code = "2330"
# lookback = 14
def model_predict(stock_code, lookback):
    start = "20100101"
    data = get_train_close_price(stock_code, start)

    shifted_data = prepare_dataframe_for_lstm(data, lookback)

    shifted_data_as_np = shifted_data.to_numpy()

    scaler = MinMaxScaler(feature_range=(-1,1))
    shifted_data_as_np = scaler.fit_transform(shifted_data_as_np)

    X = shifted_data_as_np[:, 1:]
    X = dc(np.flip(X, axis=1)) # 將train data由t-1,t-2,...,t-7改成t-7, t-6,...,t-1
    y = shifted_data_as_np[:, 0]

    split_index = int(len(X) * 0.95)

    train_data = shifted_data.iloc[:split_index]
    test_data = shifted_data.iloc[split_index:]  
    
    X_train = X[:split_index]
    X_test = X[split_index:]
    y_train = y[:split_index]
    y_test = y[split_index:]

    X_train = X_train.reshape((-1, lookback, 1))
    X_test = X_test.reshape((-1, lookback, 1))
    y_train = y_train.reshape((-1, 1))
    y_test = y_test.reshape((-1, 1))

    X_train = torch.tensor(X_train).float()
    X_test = torch.tensor(X_test).float()
    y_train = torch.tensor(y_train).float()
    y_test = torch.tensor(y_test).float()

    train_dataset = TimeSeriesDataset(X_train, y_train)
    test_dataset = TimeSeriesDataset(X_test, y_test)
    
    batch_size = 16
    
    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
    test_loader = DataLoader(test_dataset, batch_size=batch_size, shuffle=False)

    input_size = 1
    hidden_size = 8
    num_layers = 1
    learning_rate = 0.001
    num_epochs = 30
    device = 'cuda:0' if torch.cuda.is_available() else 'cpu'

    model = LSTM(input_size, hidden_size, num_layers, device).to(device)
    loss_function = nn.MSELoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=learning_rate)

    for epoch in range(num_epochs):
        print(f"Epoch: {epoch + 1}")
        train_one_epoch(model, train_loader, device, loss_function, optimizer)
        validate_one_epoch(model, test_loader, device, loss_function)
        
    with torch.no_grad():
        train_predictions = model(X_train.to(device)).to('cpu').numpy() # numpy無法用gpu
        
    train_predictions = train_predictions.flatten()
    dummies = np.zeros((X_train.shape[0], lookback+1))
    dummies[:, 0] = train_predictions
    dummies = scaler.inverse_transform(dummies)
    train_predictions = dc(dummies[:, 0])

    dummies = np.zeros((X_train.shape[0], lookback + 1))
    dummies[:, 0] = y_train.flatten()
    dummies = scaler.inverse_transform(dummies)
    new_y_train = dc(dummies[:, 0])

    plt.figure(figsize=(12, 6))
    plt.plot(train_data.index, new_y_train, label='Actual Close')
    plt.plot(train_data.index, train_predictions, label = 'Predicted Close')
    plt.xlabel('Day')
    plt.ylabel('Close')
    plt.title(f'Stock Price Prediction for {stock_code}')
    plt.legend()
    
    train_file_path = f"predict_result/{stock_code}/train_predictions.jpg"
    ensure_dir(train_file_path)
    plt.savefig(train_file_path)
    plt.close()
    
    test_predictions = model(X_test.to(device)).detach().cpu().numpy().flatten()
    # print("X_test.shape[0]: ",X_test.shape[0])
    dummies = np.zeros((X_test.shape[0], lookback+1))
    dummies[:, 0] = test_predictions
    # print("fffff:", dummies)
    dummies = scaler.inverse_transform(dummies)
    test_predictions = dc(dummies[:, 0])

    dummies = np.zeros((X_test.shape[0], lookback+1))
    dummies[:, 0] = y_test.flatten()
    dummies = scaler.inverse_transform(dummies)
    new_y_test = dc(dummies[:, 0])

    plt.figure(figsize=(12, 6))
    plt.plot(test_data.index, new_y_test, label='Actual Close')
    plt.plot(test_data.index, test_predictions, label = 'Predicted Close')
    plt.xlabel('Day')
    plt.ylabel('Close')
    plt.title(f'Stock Price Prediction for {stock_code} : Last 14 days')
    plt.legend()
    
    vaildation_file_path = f'predict_result/{stock_code}/validation_predictions.jpg'
    ensure_dir(vaildation_file_path)
    plt.savefig(vaildation_file_path)
    plt.close()

    require_data = get_close_price(stock_code, lookback)
    # require_data = require_data.reshape(1, -1)
    require_data = np.insert(require_data, 0, 0, axis=1)
    require_data = scaler.transform(require_data)
    require_data = require_data[:, 1:]
    require_data = require_data.reshape(1, -1, 1)
    require_data = torch.tensor(require_data).float()

    predict = model(require_data.to(device)).detach().cpu().numpy().flatten()
    # print(predict)
    dummies = np.zeros((1, lookback+1))
    dummies[:, 0] = predict
    # print(dummies)

    predict = scaler.inverse_transform(dummies)
    predict = predict.flatten()[0]
    print("predict: ",predict)
    print("last_day_price: ",test_predictions[-1])
    last_day_price = test_predictions[-1]
    
    stock_range = round((predict - last_day_price) / last_day_price * 100, 2)
    print(f"漲幅: {stock_range}%")
    
    operation = "觀望"
    if stock_range > 5:
        print("操作: 買入")
        operation = "買入"
    elif stock_range < -5:
        print("操作: 賣出")
        operation = "賣出"
    else:
        print("操作: 觀望")
    return operation