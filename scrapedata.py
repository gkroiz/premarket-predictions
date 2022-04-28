# from tracemalloc import start
import yfinance as yf
from datetime import datetime
import pandas as pd
import json
import numpy as np
import pymysql

# from sqlalchemy import create_engine


# import the module
from sqlalchemy import create_engine


# #connect to database
# # Credentials to database connection
hostname="localhost"
port="3306"
dbname="premarket_predictions_db"
user="root"
pwd="rootpassword"
# create sqlalchemy engine
engine = create_engine("mysql+pymysql://{user}:{pwd}@localhost/{dbname}"
                       .format(user=user,
                               pwd=pwd,
                               dbname=dbname))


# Connect to the database
# connection = pymysql.connect(host='localhost',
#                              user='root',
#                              password='rootpassword',
#                              db='premarket_predictions_db')

# cursor=connection.cursor()


# stocksToTrack = ['AAPL', 'MSFT', 'AMZN', 'TLSA', 'GOOGL', 'GOOG', 'NVDA', 'BRK-B', 'FB',  'UNH',]
with open('scrapedata.json') as json_file:
    jsondata = json.load(json_file)
    print(jsondata)
    

start_date = jsondata['start_date']
end_date = None
if jsondata['end_date'] == 'today':
    end_date = datetime.today().strftime('%Y-%m-%d')
else:
    enend_dated = jsondata['end_date']
stocksToTrack = jsondata['tickers']

for stock in stocksToTrack:
    data = yf.Ticker(stock)
    history = data.history(interval='1m', start=start_date, end=end_date, prepost=True)
    tickers = [stock] * len(history)
    tickers = np.array(tickers)
    dayStartPrice = history['Open'][0]
    transformed_data = pd.DataFrame(np.transpose(np.array([tickers, history.index, history['Open'], history['Close'], history['High'], history['Low'], history['Volume'], (history['Close'] - dayStartPrice) / dayStartPrice])),columns=['ticker','datetime','open_price','close_price','high_price', 'low_price', 'volume','percent_change'])
    transformed_data.to_sql('minute_stock_data', con = engine, if_exists = 'append', index=False, chunksize = 1000)
