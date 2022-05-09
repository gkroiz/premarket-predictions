#file name: scrapebackground.py
#description: This file takes in the scrapedata.json file, and adds background information for each ticker to the stock datatable

#imports
import yfinance as yf
from datetime import datetime
import pandas as pd
import json
import numpy as np
import requests
from sqlalchemy import create_engine
from bs4 import BeautifulSoup 

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
    
data = []

#iterate through each of the tickers
for ticker in jsondata['tickers']:

    #apikey
    apiKey = jsondata['polygon_io_api_token']

    #scrape information from api
    response = requests.get(f"https://api.polygon.io/v3/reference/tickers/{ticker}?apiKey={apiKey}")
    jsonscrape = response.json()

    name = jsonscrape['results']['name']
    age = jsonscrape['results']['list_date']
    age = pd.to_datetime(age)
    description = jsonscrape['results']['description']
    totalemployees = jsonscrape['results']['total_employees']
    website = jsonscrape['results']['homepage_url']
    
    #another scrape to get more information from yahoo finance
    response = requests.get(f"https://finance.yahoo.com/quote/{ticker}/")

    soup = BeautifulSoup(response.content, "html.parser")
    parseinfo = soup.find_all("div", class_="Mb(25px)")

    sector = parseinfo[1].find_all("span", class_="Fw(600)")[0].text
    industry = parseinfo[1].find_all("span", class_="Fw(600)")[1].text
    data.append([ticker, name, sector, industry, age, description, totalemployees, website])


#add data to stock datatable
data = pd.DataFrame(data, columns=['ticker', 'name', 'sector', 'industry', 'age', 'description', 'total_employees', 'website'])    
data.to_sql('stock', con = engine, if_exists = 'append', index = False)