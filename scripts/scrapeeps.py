#file name: scrapeeps.py
#description: this file for each ticker scrapes all of the recent year's eps data and adds it to eps datatable

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

#container to store eps data
data = []
for ticker in jsondata['tickers']:
    
    #scrape alphaquery.com (does not need apikey)
    response = requests.get(f"https://www.alphaquery.com/stock/{ticker}/earnings-history")
    soup = BeautifulSoup(response.content, "html.parser")

    #parse html file
    parseinfo = soup.find_all("tr")

    #for each available earnings annoucnement, add eps values to data container
    for quarter in parseinfo:
        if quarter != parseinfo[0]:

            quarter = quarter.text.split('\n')
            quarter.pop(0)
            quarter.pop(-1)
            
            announce_date = quarter[0]
            fisc_end_date = quarter[1]
            est_eps = float(quarter[2][1:])
            act_eps = float(quarter[3][1:])
            data.append([ticker, pd.to_datetime(fisc_end_date), pd.to_datetime(announce_date), est_eps, act_eps])


#send eps data to the eps datatable
data = pd.DataFrame(data, columns=['ticker_id', 'quarter_date', 'announced_date','exp_eps', 'actual_eps'])    
data.to_sql('eps', con = engine, if_exists = 'append', index = False)

