#file name: scrapestockdata.py
#description: This file takes in the scrapedata.json file, and adds minute and daily data to the minute_stock_data and daily_data_trend tables respectively.
#This is done for each of the trading days inbetween the start and end date specified in scrapedata.json for each ticker in scrapedata.json

#imports
import yfinance as yf
import datetime
from datetime import timedelta, tzinfo
import pandas as pd
import json
import numpy as np
import numpy as np
from sklearn.metrics import mean_squared_error
from sqlalchemy import create_engine
import requests

#open json file with script arguments
with open('scrapedata.json') as json_file:
    jsondata = json.load(json_file)

#credentials for engine
hostname = jsondata['hostname']
port = jsondata['port']
dbname = jsondata['dbname']
user = jsondata['user']
pwd = jsondata['pwd']

# create sqlalchemy engine
engine = create_engine("mysql+pymysql://{user}:{pwd}@localhost/{dbname}"
                       .format(user=user,
                               pwd=pwd,
                               dbname=dbname))

#define start and end date
start_date = jsondata['start_date']
end_date = None
if jsondata['end_date'] == 'today':
    end_date = datetime.datetime.today().strftime('%Y-%m-%d')
else:
    end_date = jsondata['end_date']
stocksToTrack = jsondata['tickers']
addDates = jsondata['add_dates']


start_date = pd.to_datetime(start_date)
end_date = pd.to_datetime(end_date)

#go through each ticker
for stock in stocksToTrack:
    date = pd.to_datetime(start_date)
    #iterate until you reach the last date
    while date <= end_date:

        #update date string
        monthStr = str(date.month)
        if date.month < 10:
            monthStr = '0' + monthStr
        dayStr = str(date.day)
        if date.day < 10:
            dayStr = '0' + dayStr

        datestr = str(date.year) + '-' + monthStr + '-' + dayStr

        #apikey
        apikey = jsondata['polygon_io_api_token']

        #scrape information from polygon.io api
        req = requests.get(f"https://api.polygon.io/v2/aggs/ticker/{stock}/range/1/minute/{datestr}/{datestr}?adjusted=true&sort=asc&limit=50000&apiKey={apikey}")
        
        #boolean if you need to add dates to dates table. This is a workaround to work with django foreginKey elements, is not necessarily logically
        if addDates and stock == stocksToTrack[0]:
            dates_data = pd.DataFrame([date.date()], columns=['date'])  
            dates_data.to_sql('dates', con = engine, if_exists = 'append', index = False)
        
        #if the day is a valid trading day
        if req.json()['resultsCount'] > 0:
            print(date)

            data = req.json()['results']
            startPrice = data[0]['o']

            #container for minute data
            allMinutesData = []

            #iterate through each minute
            for minData in data:
                o = minData['o']
                c = minData['c']
                h = minData['h']
                l = minData['l']
                v = minData['v']
                
                time = int(minData['t']) / 1000
                allMinutesData.append([stock, date.date(), time, o, c, h, l, v, (c-o)/o])
            
            minute_data_for_sql = pd.DataFrame(allMinutesData, columns=['ticker_id', 'date_id', 'time', 'open_price', 'close_price', 'high_price', 'low_price', 'volume', 'percent_change'])
            minute_data_for_sql['time'] = pd.to_datetime(minute_data_for_sql['time'], unit='s', utc=True).dt.tz_convert('America/New_York')

            startMarket = pd.to_datetime(minute_data_for_sql['time'][0]).replace(hour=9, minute=30)


            #only look at the premarket data to calculate values for daily data trend
            #l := left index
            #r := right index
            l = 0
            r = (minute_data_for_sql.loc[minute_data_for_sql['time'] == startMarket]).index.values[0]
            pre_market_data = minute_data_for_sql[l:r]
            pre_start_price = pre_market_data['open_price'][0]
            pre_close_price = pre_market_data['close_price'][len(pre_market_data)-1]
            pre_market_delta = (pre_market_data['time'] - pre_market_data['time'].min())  / np.timedelta64(1,'D')
            pre_market_delta = np.array(pre_market_delta).reshape(-1,1)

            #the days are compared based on their slope from open of premarket to open of trading day
            slope = (pre_close_price - pre_start_price) / pre_market_delta[len(pre_market_delta)-1]

            #linear equation
            def y(x):
                return (pre_start_price + slope * x) / pre_start_price

            #calculate MSE between the line and the fluctuating stock price
            pre_MSE = mean_squared_error(y(pre_market_delta), pre_market_data['open_price']/pre_start_price)

            #calculate overall percent change in premarket time
            pre_percent_change = (pre_close_price-pre_start_price)/pre_start_price
            daily_trend_data = [[stock, date.date(), pre_percent_change, pre_MSE, pre_start_price, pre_close_price]]
          
            daily_trend_data_for_sql = pd.DataFrame(daily_trend_data,columns=['ticker_id','date_id','pre_percent_change','pre_MSE', 'pre_start', 'pre_end'])

            #add daily trend data and minute data to their respective sql tables
            daily_trend_data_for_sql.to_sql('daily_data_trend', con = engine, if_exists = 'append', index = False)
            minute_data_for_sql.to_sql('minute_stock_data', con = engine, if_exists = 'append', index=False)

        #update the date
        date = date + datetime.timedelta(days=1)