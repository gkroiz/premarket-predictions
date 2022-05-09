   
#file name: views.py
#description: file that uses django interface to work with UI and update accordingly.

#imports
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from matplotlib import ticker
from matplotlib.pyplot import plot
from pyparsing import Opt
from .models import stock, eps, minute_stock_data, news, daily_data_trend
from pychartjs import BaseChart, ChartType, Color
import pandas as pd
import datetime


def index(request):
    if request.method == "POST":

        
        searched_stock = request.POST.get('search')
        searched_date = request.POST.get('compare_date')



        #get background information on the searched stock and the stock's movement from the date selected by the user
        search_results = daily_data_trend.objects.raw('SELECT daily_data_trend.id, daily_data_trend.ticker_id, \
            daily_data_trend.date_id, daily_data_trend.pre_percent_change, daily_data_trend.pre_MSE, \
                 daily_data_trend.pre_start, daily_data_trend.pre_end, stock.name, stock.sector, stock.industry, \
                     stock.age, stock.description, stock.total_employees, stock.website FROM daily_data_trend \
                         INNER JOIN dates ON (daily_data_trend.date_id = dates.date) INNER JOIN stock ON \
                             (daily_data_trend.ticker_id = stock.ticker) WHERE (dates.date = %s AND stock.ticker = %s)', [searched_date, searched_stock])

        #if the user did not pick a valid stock ticker or date, return them
        if len(search_results) == 0:
            return render(request, 'index.html')

        #populate background_info for html
        background_info = {}
        for data in search_results:
            background_info['ticker'] = data.ticker_id
            background_info['sector'] = data.sector
            background_info['indusctry'] = data.industry
            background_info['age'] = data.age
            background_info['description'] = data.description
            background_info['total_employees'] = data.total_employees
            background_info['website'] = data.website
        

        #variables from the search result
        #used to find day that is most similar        
        compared_daily_pre_percent_change = search_results[0].pre_percent_change
        compared_daily_MSE = search_results[0].pre_MSE
        compared_daily_date = search_results[0].date

        #get all of the daily data for the searched stock
        all_daily_data = daily_data_trend.objects.raw('SELECT * FROM daily_data_trend WHERE (daily_data_trend.ticker_id = %s)', [searched_stock])


        minDiff_day = None
        minDiff_percent_change = None

        #find day with the minimum difference in percent change
        for day_data in all_daily_data:
            if minDiff_day == None:
                minDiff_day = day_data.date_id
                minDiff_percent_change = abs(compared_daily_pre_percent_change - day_data.pre_percent_change)
            else:
                if minDiff_percent_change > abs(compared_daily_pre_percent_change - day_data.pre_percent_change):

                    #make sure you don't select the same day
                    if str(compared_daily_date) != str(day_data.date):

                        minDiff_percent_change = abs(compared_daily_pre_percent_change - day_data.pre_percent_change)
                        minDiff_day = day_data.date_id


        #get the minute data for the searched stock at the searched date
        searched_date_minute_data = minute_stock_data.objects.raw('SELECT minute_stock_data.id, minute_stock_data.ticker_id, minute_stock_data.date_id, \
            minute_stock_data.time, minute_stock_data.open_price, minute_stock_data.close_price, minute_stock_data.high_price, \
                minute_stock_data.low_price, minute_stock_data.volume, minute_stock_data.percent_change, \
                      daily_data_trend.pre_percent_change, daily_data_trend.pre_MSE, daily_data_trend.pre_start, daily_data_trend.pre_end \
                         FROM minute_stock_data INNER JOIN daily_data_trend ON (minute_stock_data.date_id = daily_data_trend.date_id) \
                             WHERE (daily_data_trend.date_id = %s)', [searched_date])

        #get the minute data for the date that best fits the searched date
        best_fit_minute_data = minute_stock_data.objects.raw('SELECT minute_stock_data.id, minute_stock_data.ticker_id, minute_stock_data.date_id, \
            minute_stock_data.time, minute_stock_data.open_price, minute_stock_data.close_price, minute_stock_data.high_price, \
                minute_stock_data.low_price, minute_stock_data.volume, minute_stock_data.percent_change, \
                      daily_data_trend.pre_percent_change, daily_data_trend.pre_MSE, daily_data_trend.pre_start, daily_data_trend.pre_end \
                         FROM minute_stock_data INNER JOIN daily_data_trend ON (minute_stock_data.date_id = daily_data_trend.date_id AND minute_stock_data.ticker_id = daily_data_trend.ticker_id) \
                             WHERE (daily_data_trend.date_id = %s AND minute_stock_data.ticker_id = %s)', [minDiff_day, searched_stock])
       
        time = datetime.datetime.now().replace(hour=4, minute=0, second=0, microsecond=0)

        #make array of all times from premarket open to aftermarket close (4:00 am to 8:00 pm)
        all_times = []
        #just times that consist of premarket (4:00 am to 9:30 am)
        pre_market_times = []
        while time != datetime.datetime.now().replace(hour=20, minute=0, second=0, microsecond=0):
            curr = time
            all_times.append(curr)
            if time < datetime.datetime.now().replace(hour=9, minute=30, second=0, microsecond=0):
                pre_market_times.append(curr.time().strftime('%I:%M'))
            time = time + datetime.timedelta(minutes=1)
        

        #get all of the open prices for the searched day and the day that best fits for plotting
        searched_date_open_prices = []
        best_fit_open_prices = []
        
        #starting prices for the searched date and the day that best fits
        searched_date_start = searched_date_minute_data[0].open_price
        best_fit_start = best_fit_minute_data[0].open_price

        
        best_fit_pre_percent_change = best_fit_minute_data[0].pre_percent_change
        best_fit_MSE = best_fit_minute_data[0].pre_MSE

        #index trackers for searched date and best fit date
        #this is needed because there may not be data for every minute
        searched_date_idx = 0
        best_fit_idx = 0

        #iterates through each minute from 4:00 am to 8:00 pm
        for i in range(len(all_times)):
            
            #go through and add either the open price if the data exists or null if it does not 
            if searched_date_idx < len(searched_date_minute_data):
                if (all_times[i].time() == searched_date_minute_data[searched_date_idx].time):
                    searched_date_open_prices.append((searched_date_minute_data[searched_date_idx].open_price-searched_date_start)/searched_date_start * 100)
                    searched_date_idx += 1
                else:
                    searched_date_open_prices.append('null')
            else:
                searched_date_open_prices.append('null')
            
            #go through and add either the open price if the data exists or null if it does not 
            if best_fit_idx < len(best_fit_minute_data):
                if (all_times[i].time() == best_fit_minute_data[best_fit_idx].time):
                    best_fit_open_prices.append((best_fit_minute_data[best_fit_idx].open_price-best_fit_start)/best_fit_start  * 100)
                    best_fit_idx += 1
                else:
                    best_fit_open_prices.append('null')

            else:
                best_fit_open_prices.append('null')
            #convert all_times[i] to a string format for html compatability
            all_times[i] = all_times[i].time().strftime('%H:%M')

        #get all of the eps data for the searched stock
        eps_data = eps.objects.raw("SELECT eps.id, eps.ticker_id, eps.announced_date, eps.exp_eps, eps.actual_eps FROM eps INNER JOIN stock ON (eps.ticker_id = stock.ticker) WHERE (eps.ticker_id = %s)",[searched_stock])
        
        #containers for html
        eps_date_data = []
        eps_exp_data = []
        eps_actual_data = []
        
        #save information for the last 4 eps announcements
        for i in range(0,4):
            eps_date_data.append(str(eps_data[i].announced_date))
            eps_exp_data.append(eps_data[i].exp_eps)
            eps_actual_data.append(eps_data[i].actual_eps)


        #pychart.js class for plotting eps information
        class EPSGraph(BaseChart):
            class labels:
                grouped = eps_date_data
            class data:
                class exp:
                    label = "Expected EPS"
                    data = eps_exp_data
                    # backgroundColor = Color.Green
                    type = ChartType.Line
                    backgroundColor = Color.RGBA(0,0,0,0)
                    borderColor = Color.Red
                    borderWidth = 2
                    pointRadius = 10
                    hoverRadius = 8
                    hoverBorderWidth = 2
                    pointBackgroundColor = Color.Red
                    lineBackgroundColor = Color.RGBA(0,0,0,0)
                    fill = False

                class actual:
                    label = "Actual EPS"
                    data = eps_actual_data
                    type = ChartType.Line
                    backgroundColor = Color.RGBA(0,0,0,0)
                    borderColor = Color.Purple
                    pointBackgroundColor = Color.Purple
                    borderWidth = 2
                    pointRadius = 10
                    hoverRadius = 8
                    hoverBorderWidth = 2
                    lineBackgroundColor = Color.RGBA(0,0,0,0)
                    fill = False

            class options:
                title = {
                    "text": "Previous Earnings", 
                    "display": True, 
                    "fontSize": 16,
                    'fontColor': Color.Black
                    }

                legend = {
                    'position': 'bottom', 
                    'labels': {
                        'fontColor': Color.Black, 
                        'fullWidth': True
                        }
                    }

        EPSChart = EPSGraph()
        EPSChartJSON = EPSChart.get()

        #search for all sources of media on both searched date and best fit date that have information on the searched stock
        queryString = f"SELECT news.article_id, news.title, news.date_id, news.time, news.news_url, news.tickers, news.image_url, news.text, news.source_name, news.sentiment, news.type FROM news WHERE ((news.date_id = '{searched_date}' OR news.date_id = '{minDiff_day}') AND news.tickers like '%%{searched_stock}%%')"
        news_articles = news.objects.raw(queryString)

        #containers for html
        compare_article_positive = {}
        compare_article_neutral = {}
        compare_article_negative = {}
        best_fit_article_positive = {}
        best_fit_article_neutral = {}
        best_fit_article_negative = {}

        #read through each of the articles from the query and select the first for each sentiment and date to display in the UI
        for article in news_articles:

            #positive sentiment for the searched date
            if article.sentiment == 'Positive' and len(compare_article_positive) == 0 and str(article.date_id) == str(searched_date):
                compare_article_positive['image_url'] = article.image_url
                compare_article_positive['news_url'] = article.news_url
                compare_article_positive['title'] = article.title
                compare_article_positive['source_name'] = article.source_name 
                compare_article_positive['time'] = article.time
                compare_article_positive['date'] = article.date_id
                compare_article_positive['sentiment'] = article.sentiment

            #neutral sentiment for the searched date
            if article.sentiment == 'Neutral'  and len(compare_article_neutral) == 0 and str(article.date_id) == str(searched_date):
                compare_article_neutral['image_url'] = article.image_url
                compare_article_neutral['news_url'] = article.news_url
                compare_article_neutral['title'] = article.title
                compare_article_neutral['source_name'] = article.source_name
                compare_article_neutral['time'] = article.time
                compare_article_neutral['date'] = article.date_id
                compare_article_neutral['sentiment'] = article.sentiment

            #negative sentiment for the searched date
            if article.sentiment == 'Negative'  and len(compare_article_negative) == 0 and str(article.date_id) == str(searched_date):
                compare_article_negative['image_url'] = article.image_url
                compare_article_negative['news_url'] = article.news_url
                compare_article_negative['title'] = article.title
                compare_article_negative['source_name'] = article.source_name
                compare_article_negative['time'] = article.time
                compare_article_negative['date'] = article.date_id
                compare_article_negative['sentiment'] = article.sentiment

            #positive sentiment for the best fit date
            if article.sentiment == 'Positive' and len(best_fit_article_positive) == 0 and str(article.date_id) == str(minDiff_day):
                best_fit_article_positive['image_url'] = article.image_url
                best_fit_article_positive['news_url'] = article.news_url
                best_fit_article_positive['title'] = article.title
                best_fit_article_positive['source_name'] = article.source_name 
                best_fit_article_positive['time'] = article.time
                best_fit_article_positive['date'] = article.date_id
                best_fit_article_positive['sentiment'] = article.sentiment

            #neutral sentiment for the best fit date
            if article.sentiment == 'Neutral'  and len(best_fit_article_neutral) == 0 and str(article.date_id) == str(minDiff_day):
                best_fit_article_neutral['image_url'] = article.image_url
                best_fit_article_neutral['news_url'] = article.news_url
                best_fit_article_neutral['title'] = article.title
                best_fit_article_neutral['source_name'] = article.source_name
                best_fit_article_neutral['time'] = article.time
                best_fit_article_neutral['date'] = article.date_id
                best_fit_article_neutral['sentiment'] = article.sentiment

            #negative sentiment for the best fit date
            if article.sentiment == 'Negative'  and len(best_fit_article_negative) == 0 and str(article.date_id) == str(minDiff_day):
                best_fit_article_negative['image_url'] = article.image_url
                best_fit_article_negative['news_url'] = article.news_url
                best_fit_article_negative['title'] = article.title
                best_fit_article_negative['source_name'] = article.source_name
                best_fit_article_negative['time'] = article.time
                best_fit_article_negative['date'] = article.date_id
                best_fit_article_negative['sentiment'] = article.sentiment

        #context needed for html file
        context = {
        'date_analyze': str(searched_date),
        'date_best_fit': str(minDiff_day),
        'best_fit_all_dataJSON': best_fit_open_prices,
        'analysis_all_dataJSON': searched_date_open_prices,
        'plot_labels': all_times,
        'EPSChartJSON': EPSChartJSON,
        'analysis_slope':compared_daily_pre_percent_change  * 100,
        'lbf_slope': best_fit_pre_percent_change  * 100,
        'analysis_MSE': compared_daily_MSE*pow(10,4),
        'lbf_MSE': best_fit_MSE*pow(10,4),
        'stock': background_info, 
        'hidden': "no",
        'analysis_positive': compare_article_positive,
        'analysis_neutral': compare_article_neutral,
        'analysis_negative': compare_article_negative,
        'best_fit_positive': best_fit_article_positive,
        'best_fit_neutral': best_fit_article_neutral,
        'best_fit_negative': best_fit_article_negative,
        }
        return render(request, 'index.html', context=context)
    else:
        return render(request, 'index.html')
