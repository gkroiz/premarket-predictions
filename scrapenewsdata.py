# from tracemalloc import start
import yfinance as yf
from datetime import datetime
import pandas as pd
import json
import numpy as np

import requests

# import the module
from sqlalchemy import create_engine


# response = pd.DataFrame(response.content)
# print(response.content)
# exit()

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



# stocksToTrack = ['AAPL', 'MSFT', 'AMZN', 'TLSA', 'GOOGL', 'GOOG', 'NVDA', 'BRK-B', 'FB',  'UNH',]
with open('scrapedata.json') as json_file:
    jsondata = json.load(json_file)
    print(jsondata)
    


start_date = datetime.strptime(jsondata['start_date'], "%Y-%m-%d").strftime("%m%d%Y")

end_date = None
if jsondata['end_date'] == 'today':
    end_date = datetime.today().strftime('%Y-%m-%d')
else:
    end_date = jsondata['end_date']

stocksToTrack = ','.join(jsondata['tickers'])
end_date = datetime.strptime(end_date, "%Y-%m-%d").strftime("%m%d%Y")


import ast
f = open('test.txt', 'r').read()

jsonscrape = ast.literal_eval(f)

api_token = 'o3b5ritrjxmkitqln5lbihcyufm11vkfnxwonb2r'
# print(f"https://stocknewsapi.com/api/v1?tickers={stocksToTrack}&date={start_date}-{end_date}&items=50&page=1&token={api_token}")
# response = requests.get(f"https://stocknewsapi.com/api/v1?tickers={stocksToTrack}&date={start_date}-{end_date}&items=50&page=1&token={api_token}")
# jsonscrape = response.json()

num_pages = jsonscrape['total_pages']

data = []
for page in range(1,num_pages+1):
    if page != 1:
        break
        response = requests.get(f"https://stocknewsapi.com/api/v1?tickers={stocksToTrack}&date={start_date}-{end_date}&items=50&page={page}&token={api_token}")
        jsonscrape = response.json()

    for article in jsonscrape['data']:
        date = pd.to_datetime(article['date'].split(',')[1], format=' %d %b %Y %H:%M:%S %z')
        
        data.append([article['title'], date, article['news_url'], json.dumps(article['tickers']), article['image_url'], article['text'], article['source_name'], article['sentiment'], article['type']])

data = pd.DataFrame(data, columns=['title', 'datetime', 'news_url', 'tickers', 'image_url', 'text', 'source_name', 'sentiment', 'type'])    
# print(data)
data.to_sql('news', con = engine, if_exists = 'append', index = False, chunksize = 1000)
exit()
