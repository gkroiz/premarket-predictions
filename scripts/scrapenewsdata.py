#file name: scrapenewsdata.py
#description: This file takes in the scrapedata.json file, and adds data to the sql tables minute_stock_data and daily_data_trend.
#This is done for each of the trading days inbetween the start and end date specified in scrapedata.json for each ticker in scrapedata.json


#imports
import yfinance as yf
from datetime import datetime
import pandas as pd
import json
import numpy as np
import requests
from sqlalchemy import create_engine


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
start_date = datetime.strptime(jsondata['start_date'], "%Y-%m-%d").strftime("%m%d%Y")
end_date = None
if jsondata['end_date'] == 'today':
    end_date = datetime.today().strftime('%Y-%m-%d')
else:
    end_date = jsondata['end_date']
end_date = datetime.strptime(end_date, "%Y-%m-%d").strftime("%m%d%Y")

#string of all tickers that will be added to the tables
stocksToTrack = ','.join(jsondata['tickers'])


#api_token
api_token = jsondata['stock_news_api_token']

#get data from stocknewsapi and convert to json structure
response = requests.get(f"https://stocknewsapi.com/api/v1?tickers={stocksToTrack}&date={start_date}-{end_date}&items=50&page=1&token={api_token}")
jsonscrape = response.json()


#number of pages of information to go through on api
num_pages = jsonscrape['total_pages']

#storage for all articles
data = []

#go throuhg each page, for each page, scrape all of the data
for page in range(1,num_pages+1):
    if page != 1:
        response = requests.get(f"https://stocknewsapi.com/api/v1?tickers={stocksToTrack}&date={start_date}-{end_date}&items=50&page={page}&token={api_token}")
        jsonscrape = response.json()

    for article in jsonscrape['data']:
        date = pd.to_datetime(article['date'].split(',')[1], format=' %d %b %Y %H:%M:%S %z')
        data.append([article['title'], date.date(), date.time(), article['news_url'], str(article['tickers']), article['image_url'], article['text'], article['source_name'], article['sentiment'], article['type']])

#append the article to the news datatable
data = pd.DataFrame(data, columns=['title', 'date_id', 'time', 'news_url', 'tickers', 'image_url', 'text', 'source_name', 'sentiment', 'type'])    
data.to_sql('news', con = engine, if_exists = 'append', index = False)