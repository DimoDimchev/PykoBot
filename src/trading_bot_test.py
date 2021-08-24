import os
import pandas as pd
from binance import Client

api_key = os.environ['API_KEY']
secret_key = os.environ['SECRET_KEY']

client = Client(api_key, secret_key)


def get_min_data(symbol, interval, lookback):
    frame = pd.DataFrame(client.get_historical_klines(symbol, interval, f'{lookback} min ago UTC'))
    frame = frame.iloc[:, :6]
    frame.columns = ['Time', 'Open', 'High', 'Low', 'Close', 'Volume']
    frame = frame.set_index('Time')
    frame.index = pd.to_datetime(frame.index, unit='ms')
    frame = frame.astype(float)
    return frame


def strategy_test(symbol, qty, entered=False):
    data_frame = get_min_data(symbol, '1m', '30')
    cumulative_returns = (data_frame.Open.pct_change() + 1).cumprod() - 1
    if not entered:
        if cumulative_returns[-1] < -0.002:
            order = client.create_order(symbol=symbol, side='BUY', type='MARKET', quantity=qty)
            print('Buy')
            print(order)
            entered = True
        else:
            print('Not buying')
    if entered:
        while True:
            data_frame = get_min_data(symbol, '1m', '30')
            since_buy = data_frame.loc[data_frame.index > pd.to_datetime(order['transactTime'], unit='ms')]
            if len(since_buy > 0):
                since_buy_returns = (since_buy.Open.pct_change() + 1).cumprod() - 1
                if since_buy_returns > 0.0015 or since_buy_returns[-1] < -0.0015:
                    order = client.create_order(symbol=symbol, side='SELL', type='MARKET', quantity=qty)
                    print('Sell')
                    print(order)
                    break


strategy_test('ADAUSDT', 5)
# info = client.get_symbol_info('ADAUSDT')
# print(info['filters'][2]['minQty'])