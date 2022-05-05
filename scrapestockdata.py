# from tracemalloc import start
import yfinance as yf
# from datetime import datetime
import datetime
from datetime import timedelta, tzinfo
import pandas as pd
import json
import numpy as np

#for linear regression
import numpy as np
from sklearn import datasets, linear_model
from sklearn.metrics import mean_squared_error, r2_score

# import the module
from sqlalchemy import create_engine

import requests


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

start_date = pd.to_datetime(start_date)
end_date = pd.to_datetime(end_date)
for stock in stocksToTrack:
    date = pd.to_datetime(start_date)
    daily_trend_data = []
    while date <= end_date:
        monthStr = str(date.month)
        if date.month < 10:
            monthStr = '0' + monthStr
        dayStr = str(date.day)
        if date.day < 10:
            dayStr = '0' + dayStr

        datestr = str(date.year) + '-' + monthStr + '-' + dayStr
        # print(datestr)
        # exit()
        apikey = '2LAQUprTxW0lDVCXc05Ni8YFpJH2og3x'
        req = requests.get(f"https://api.polygon.io/v2/aggs/ticker/{stock}/range/1/minute/{datestr}/{datestr}?adjusted=true&sort=asc&limit=50000&apiKey={apikey}")
        if req.json()['resultsCount'] > 0:
            print(date)
            data = req.json()['results']
            # print(data[0])
            # print(data[1])
            allDayData = []
            startPrice = data[0]['o']
            for minData in data:
                o = minData['o']
                c = minData['c']
                h = minData['h']
                l = minData['l']
                v = minData['v']
                
                time = int(minData['t']) / 1000
                allDayData.append([stock, time, o, c, h, l, v, (c-startPrice)/startPrice])
            
            dataforsql = pd.DataFrame(allDayData, columns=['ticker', 'datetime', 'open_price', 'close_price', 'high_price', 'low_price', 'volume', 'percent_change'])
            dataforsql['datetime'] = pd.to_datetime(dataforsql['datetime'], unit='s', utc=True).dt.tz_convert('America/New_York')
            # print(dataforsql)
            # exit()
            dataforsql.to_sql('minute_stock_data', con = engine, if_exists = 'append', index=False)


            preMarket = pd.to_datetime(dataforsql['datetime'][0]).replace(hour=4, minute=00)
            startMarket = pd.to_datetime(dataforsql['datetime'][0]).replace(hour=9, minute=30)
            # endMarket = pd.to_datetime(dataforsql['datetime'][0]).replace(hour=16, minute=00)


    

            # print(preMarket, startMarket)
            # for i in range(len(dataforsql['datetime'])):
                # print(dataforsql['datetime'][i])
            # print(dataforsql['datetime'])
            # exit()
            # dataforsql[dataforsql['datetime']==startMarket].index.values
            # l = None
            # while l == None:
                # if preMarket in dataforsql['datetime']:
            # l = (dataforsql.loc[dataforsql['datetime'] == preMarket]).index.values[0]
            l = 0
                # else:
                    # preMarket = preMarket + datetime.timedelta(minutes=1)
            r = (dataforsql.loc[dataforsql['datetime'] == startMarket]).index.values[0]
            # print(l)
            # print(r)
            pre_market_data = dataforsql[l:r]
            # print(dataforsql[l])
            # exit()
            # print(pre_market_data)
            # exit()
            pre_market_delta = (pre_market_data['datetime'] - pre_market_data['datetime'].min())  / np.timedelta64(1,'D')
            # print(pre_market_delta)
            pre_market_delta = np.array(pre_market_delta).reshape(-1,1)
            # print(pre_market_delta.shape)
            # print(pre_market_data['open_price'].shape)
            regr = linear_model.LinearRegression()
            regr.fit(pre_market_delta, np.array(pre_market_data['open_price']).reshape(-1,1))
            pre_y = regr.predict(pre_market_delta)
            pre_MSE = mean_squared_error(pre_y, pre_market_data['open_price'])
            pre_m = regr.intercept_
            pre_b = regr.coef_
            pre_start = pre_market_data['open_price'][0]
            pre_end = pre_market_data['close_price'][len(pre_market_data)-1]
            
            daily_trend_data.append([stock, date.date(), pre_b[0][0], pre_m[0], pre_MSE, pre_start, pre_end])
            # print(daily_trend_data)
            # import matplotlib.pyplot as plt
            # plt.scatter(pre_market_delta,  np.array(pre_market_data['open_price']).reshape(-1,1), color="black")
            # plt.plot(pre_market_delta, pre_y, color="blue", linewidth=3)

            # plt.savefig('tmp.png')
            # exit()
        #end of loop
        date = date + datetime.timedelta(days=1)
        # break
    # print(daily_trend_data)

    transformed_data = pd.DataFrame(daily_trend_data,columns=['ticker','date','pre_b','pre_m','pre_MSE', 'pre_start', 'pre_end'])
    # print(transformed_data)

    transformed_data.to_sql('daily_data_trend', con = engine, if_exists = 'append', index=False)
    # exit()
    