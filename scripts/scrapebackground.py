
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


    apiKey = '2LAQUprTxW0lDVCXc05Ni8YFpJH2og3x'



    # print(f"https://api.polygon.io/v3/reference/tickers/{ticker}?apiKey={apiKey}")
    response = requests.get(f"https://api.polygon.io/v3/reference/tickers/{ticker}?apiKey={apiKey}")
    jsonscrape = response.json()

    name = jsonscrape['results']['name']
    age = jsonscrape['results']['list_date']
    age = pd.to_datetime(age)
    description = jsonscrape['results']['description']
    totalemployees = jsonscrape['results']['total_employees']
    website = jsonscrape['results']['homepage_url']
    
    from bs4 import BeautifulSoup 
    response = requests.get(f"https://finance.yahoo.com/quote/{ticker}/")

    soup = BeautifulSoup(response.content, "html.parser")


    parseinfo = soup.find_all("div", class_="Mb(25px)")

    # print(parseinfo[1].find_all("span", class_="Fw(600)")[0].text)
    # print(parseinfo[1].find_all("span", class_="Fw(600)")[1].text)
    sector = parseinfo[1].find_all("span", class_="Fw(600)")[0].text
    industry = parseinfo[1].find_all("span", class_="Fw(600)")[1].text
    data.append([ticker, name, sector, industry, age, description, totalemployees, website])

data = pd.DataFrame(data, columns=['ticker', 'name', 'sector', 'industry', 'age', 'description', 'total_employees', 'website'])    
# print(data)
data.to_sql('stock', con = engine, if_exists = 'append', index = False)

