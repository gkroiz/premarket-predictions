
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
    



# stocksToTrack = ','.join(jsondata['tickers'])

data = []
for ticker in jsondata['tickers']:

# import ast
# f = open('test.txt', 'r').read()

# jsonscrape = ast.literal_eval(f)


# https://seekingalpha.com/symbol/AAPL/earnings
    
    from bs4 import BeautifulSoup 
    response = requests.get(f"https://www.alphaquery.com/stock/{ticker}/earnings-history")


    soup = BeautifulSoup(response.content, "html.parser")


    parseinfo = soup.find_all("tr")

    for quarter in parseinfo:
        if quarter != parseinfo[0]:

            quarter = quarter.text.split('\n')
            quarter.pop(0)
            quarter.pop(-1)
            
            announce_date = quarter[0]
            fisc_end_date = quarter[1]
            est_eps = float(quarter[2][1:])
            act_eps = float(quarter[3][1:])
            print(announce_date, fisc_end_date, est_eps, act_eps)
            data.append([ticker, pd.to_datetime(fisc_end_date), est_eps, act_eps])

data = pd.DataFrame(data, columns=['ticker', 'date', 'exp_eps', 'actual_eps'])    
# print(data)
data.to_sql('eps', con = engine, if_exists = 'append', index = False)

