# from tracemalloc import start
import yfinance as yf
from datetime import datetime
import pandas as pd

stocksToTrack = ['AAPL', 'MSFT', 'AMZN', 'TLSA', 'GOOGL', 'GOOG', 'NVDA', 'BRK-B', 'FB',  'UNH',]
# stocksToTrack = ' '.join([item for item in stocksToTrack])
# interval = '1m'
# # print(stocksToTrack)
# start = '2022-01-01'
# end = datetime.today().strftime('%Y-%m-%d')
# data = yf.download(stocksToTrack, start="2017-01-01", end="2017-01-08", period= 'interval = )
# print(data)

start = '2022-04-21'
end = datetime.today().strftime('%Y-%m-%d')
for stock in stocksToTrack:
    data = yf.Ticker(stock)
    history = data.history(interval='1m', start=start, end=end, prepost=True)
    pd.DataFrame.to_csv(history, stock + '.txt')