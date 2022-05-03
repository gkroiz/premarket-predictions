# from tracemalloc import start
import yfinance as yf
# from datetime import datetime
import datetime
from datetime import timedelta
import pandas as pd
import json
import numpy as np

#for linear regression
import numpy as np
from sklearn import datasets, linear_model
from sklearn.metrics import mean_squared_error, r2_score

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
    end_date = datetime.datetime.today().strftime('%Y-%m-%d')
else:
    end_date = jsondata['end_date']
stocksToTrack = jsondata['tickers']

for stock in stocksToTrack:
    data = yf.Ticker(stock)
    history = data.history(interval='1m', start=start_date, end=end_date, prepost=True)
    tickers = [stock] * len(history)
    tickers = np.array(tickers)
    dayStartPrice = history['Open'][0]
    print(history.iloc[0])
    #for minute_stock_data
    transformed_data = pd.DataFrame(np.transpose(np.array([tickers, history.index, history['Open'], history['Close'], history['High'], history['Low'], history['Volume'], (history['Close'] - dayStartPrice) / dayStartPrice])),columns=['ticker','datetime','open_price','close_price','high_price', 'low_price', 'volume','percent_change'])
    # transformed_data.to_sql('minute_stock_data', con = engine, if_exists = 'append', index=False, chunksize = 1000)

    days = [history.index[0].date()]
    print(days)
    for i in range(len(history)):
        if history.index[i].date() != days[-1]:
            days.append(history.index[i].date())
    print(days)
    lastDay = pd.to_datetime(end_date) + timedelta(days=1)
    # print(lastDay)
    # print(type(lastDay))
    
    #for daily_movement_trend

    from datetime import timezone
    import pytz

    daily_trend_data = []
    est = pytz.timezone('US/Eastern')
    print(history.index[0])
    print(history.index[0].time())
    currDay = days[0]
    currDay = history.index[0].replace(year=currDay.year, month=currDay.month, day=currDay.day)
    print(currDay)
    while len(days) > 0:
        print('here')
        preMarket = currDay.replace(hour=4, minute=00)
        startMarket = currDay.replace(hour=9, minute=30)
        endMarket = currDay.replace(hour=16, minute=00)

        print(preMarket)
        # exit()
        pre_market_data = history.loc[preMarket:startMarket]

        pre_market_delta = (pre_market_data.index - pre_market_data.index.min())  / np.timedelta64(1,'D')
        # print(pre_market_delta)
        pre_market_delta = np.array(pre_market_delta).reshape(-1,1)

        regr = linear_model.LinearRegression()
        regr.fit(pre_market_delta, pre_market_data['Open'])
        pre_y = regr.predict(pre_market_delta)
        pre_MSE = mean_squared_error(pre_y, pre_market_data['Open'])
        pre_m = regr.intercept_
        pre_b = regr.coef_
        pre_start = pre_market_data['Open'][0]
        pre_end = pre_market_data['Close'][-1]
        
        daily_trend_data.append([stock, currDay.date(), pre_b[0], pre_m, pre_MSE, pre_start, pre_end])
        days.pop(0)
        if len(days) == 0:
            break
        currDay = days[0]
        currDay = history.index[0].replace(year=currDay.year, month=currDay.month, day=currDay.day)
        
    transformed_data = pd.DataFrame(daily_trend_data,columns=['ticker','date','pre_b','pre_m','pre_MSE', 'pre_start', 'pre_end'])
    # print(transformed_data)
    
    transformed_data.to_sql('daily_data_trend', con = engine, if_exists = 'append', index=False, chunksize = 1000)

        