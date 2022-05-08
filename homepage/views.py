   
from ctypes import pointer
from turtle import back
from django.http import HttpResponse
from django.shortcuts import render, redirect


# Create your views here.
from django.urls import reverse
from matplotlib import ticker
from pyparsing import Opt
# from requests import options

from .models import stock, eps, minute_stock_data, news, daily_data_trend

from pychartjs import BaseChart, ChartType, Color

import pandas as pd
import datetime


def index(request):
    if request.method == "POST":
        # if 'search' in request.POST[0]:
            # print('t')
        # print(request.POST)
        search = request.POST.get('search')
        # start_date = request.POST.get('start_date')
        # end_date = request.POST.get('end_date')
        compare_date = request.POST.get('compare_date')

        print(compare_date)


        # print(start_date)
        # print(type(start_date))
        background_info = stock.objects.filter(ticker__exact=search)
        # a = stock.objects.select_related('eps_to_stock').filter(eps_to_stock__ticker_id = search).values()
        # print(a.query)
        # print(a)
        
        # daily_trend = daily_data_trend.objects.select_related('date', 'ticker').filter(date__exact=compare_date).filter(ticker__exact=search).values()
        # print(daily_data_trend.objects.select_related('date', 'ticker').filter(date__exact=compare_date).filter(ticker__exact=search).query)
        # print(search)
        # print(type(search))

        search_results = daily_data_trend.objects.raw('SELECT daily_data_trend.id, daily_data_trend.ticker_id, \
            daily_data_trend.date_id, daily_data_trend.pre_percent_change, daily_data_trend.pre_MSE, \
                 daily_data_trend.pre_start, daily_data_trend.pre_end, stock.name, stock.sector, stock.industry, \
                     stock.age, stock.description, stock.total_employees, stock.website FROM daily_data_trend \
                         INNER JOIN dates ON (daily_data_trend.date_id = dates.date) INNER JOIN stock ON \
                             (daily_data_trend.ticker_id = stock.ticker) WHERE (dates.date = %s AND stock.ticker = %s)', [compare_date, search])
        # search_results = daily_data_trend.objects.raw('SELECT daily_data_trend FROM daily_data_trend INNER JOIN dates ON ' + 
                                # '(daily_data_trend.date_id = dates.date) INNER JOIN stock ON (daily_data_trend.ticker_id = stock.ticker) ' +
                                    # 'WHERE (date_id = %s AND daily_data_trend.ticker_id = %s) ', [compare_date,search])
        # daily_trend = daily_data_trend.objects.raw("SELECT * FROM daily_data_trend INNER JOIN dates ON (daily_data_trend.date_id = dates.date);")
        # daily_trend = daily_data_trend.objects.raw("SELECT * FROM daily_data_trend INNER JOIN dates ON (daily_data_trend.date_id = dates.date);")
        print(search_results)
        print('before this')
        print(len(search_results))
        for a in search_results:
            print(a.ticker)
            print(a.date)
            print(a.description)
        print('after this')
        # daily_trend = daily_trend.values()


        
        compared_daily_pre_percent_change = search_results[0].pre_percent_change
        compared_daily_MSE = search_results[0].pre_MSE
        compared_daily_date = search_results[0].date



        all_daily_data = daily_data_trend.objects.filter(ticker__exact=search).values()

        # minDiff_m = None
        minDiff_day = None
        minDiff_percent_change = None
        # best_fit_daily_m = None
        # best_fit_daily_b = None
        # best_fit_daily_MSE = None
        for day_data in all_daily_data:
            # if day_data['date_id'] != compared_daily_date:
            if minDiff_day == None:
                minDiff_day = day_data['date_id']
                minDiff_percent_change = abs(compared_daily_pre_percent_change - day_data['pre_percent_change'])
                # best_fit_daily_m = day_data['pre_m']
                # best_fit_daily_b = day_data['pre_b']
                # best_fit_daily_MSE = day_data['pre_MSE']
            else:
                if minDiff_percent_change > abs(compared_daily_pre_percent_change - day_data['pre_percent_change']):
                    if (abs(compared_daily_pre_percent_change - day_data['pre_percent_change']) != 0):

                        minDiff_percent_change = abs(compared_daily_pre_percent_change - day_data['pre_percent_change'])
                        minDiff_day = day_data['date_id']
                    # best_fit_daily_m = day_data['pre_m']
                    # best_fit_daily_b = day_data['pre_b']
                    # best_fit_daily_MSE = day_data['pre_MSE']



        # print(daily_trend.values())

        # compare_minute_data = minute_stock_data.objects.filter(ticker__exact=search).filter(date_id__exact=compare_date).values()
        compare_minute_data = minute_stock_data.objects.raw('SELECT minute_stock_data.id, minute_stock_data.ticker_id, minute_stock_data.date_id, \
            minute_stock_data.time, minute_stock_data.open_price, minute_stock_data.close_price, minute_stock_data.high_price, \
                minute_stock_data.low_price, minute_stock_data.volume, minute_stock_data.percent_change, \
                      daily_data_trend.pre_percent_change, daily_data_trend.pre_MSE, daily_data_trend.pre_start, daily_data_trend.pre_end \
                         FROM minute_stock_data INNER JOIN daily_data_trend ON (minute_stock_data.date_id = daily_data_trend.date_id) \
                             WHERE (daily_data_trend.date_id = %s)', [compare_date])

        # best_fit_minute_data = minute_stock_data.objects.filter(ticker__exact=search).filter(date_id__exact=minDiff_day).values()

        best_fit_minute_data = minute_stock_data.objects.raw('SELECT minute_stock_data.id, minute_stock_data.ticker_id, minute_stock_data.date_id, \
            minute_stock_data.time, minute_stock_data.open_price, minute_stock_data.close_price, minute_stock_data.high_price, \
                minute_stock_data.low_price, minute_stock_data.volume, minute_stock_data.percent_change, \
                      daily_data_trend.pre_percent_change, daily_data_trend.pre_MSE, daily_data_trend.pre_start, daily_data_trend.pre_end \
                         FROM minute_stock_data INNER JOIN daily_data_trend ON (minute_stock_data.date_id = daily_data_trend.date_id AND minute_stock_data.ticker_id = daily_data_trend.ticker_id) \
                             WHERE (daily_data_trend.date_id = %s AND minute_stock_data.ticker_id = %s)', [minDiff_day, search])
        print('before')
        print(len(best_fit_minute_data))
        # compare_minute_data = minute_stock_data.objects.filter(ticker__exact=search).filter(date_id__exact=compare_date).values()[:]['open_price']
        # print(compare_minute_data)
        compare_open_prices = []

        time = datetime.datetime.now().replace(hour=4, minute=0, second=0, microsecond=0)
        all_times = []
        pre_market_times = []
        while time != datetime.datetime.now().replace(hour=20, minute=0, second=0, microsecond=0):
            curr = time
            all_times.append(curr)
            if time < datetime.datetime.now().replace(hour=9, minute=30, second=0, microsecond=0):
                pre_market_times.append(curr.time().strftime('%I:%M'))
            time = time + datetime.timedelta(minutes=1)
        # print(times)
        

        # print(times)
        compare_open_prices = []
        best_fit_open_prices = []
        
        best_fit_start = best_fit_minute_data[0].open_price
        compare_start = compare_minute_data[0].open_price

        best_fit_pre_precent_change = best_fit_minute_data[0].pre_percent_change
        best_fit_MSE = best_fit_minute_data[0].pre_MSE
        print('compare info')
        print(compare_start)
        print(compared_daily_pre_percent_change)
        # print(compared_daily_m)
        print(compared_daily_date)

        print('bestfit info')
        print(best_fit_start)
        print(best_fit_pre_precent_change)
        # print(best_fit_daily_m)
        print(minDiff_day)
        comp_idx = 0
        best_fit_idx = 0
        # lbf1 = []
        # lbf2 = []

        best_fit_minute_data = minute_stock_data.objects.raw('SELECT minute_stock_data.id, minute_stock_data.ticker_id, minute_stock_data.date_id, \
            minute_stock_data.time, minute_stock_data.open_price, minute_stock_data.percent_change \
                         FROM minute_stock_data INNER JOIN daily_data_trend ON (minute_stock_data.date_id = daily_data_trend.date_id AND minute_stock_data.ticker_id = daily_data_trend.ticker_id) \
                             WHERE (daily_data_trend.date_id = %s AND minute_stock_data.ticker_id = %s)', [minDiff_day,search])
        
        # for i in range(len(best_fit_minute_data)):
            # print(best_fit_minute_data[i].ticker)
        print(len(best_fit_minute_data))
        print(type(best_fit_minute_data[best_fit_idx].time))
        print(best_fit_minute_data[1].time)
        for i in range(len(all_times)):
            # print(all_times[i].time())
            if comp_idx < len(compare_minute_data):
                if (all_times[i].time() == compare_minute_data[comp_idx].time):
                    # compare_open_prices.append(compare_minute_data[comp_idx]['open_price'])
                    compare_open_prices.append((compare_minute_data[comp_idx].open_price-compare_start)/compare_start)
                    comp_idx += 1
                else:
                    compare_open_prices.append(None)
            else:
                compare_open_prices.append(None)
            # print(all_times[i].time(), best_fit_minute_data[best_fit_idx].time, best_fit_idx)
            if best_fit_idx < len(best_fit_minute_data):
                if (all_times[i].time() == best_fit_minute_data[best_fit_idx].time):
                    # best_fit_open_prices.append(best_fit_minute_data[best_fit_idx]['open_price'])
                    best_fit_open_prices.append((best_fit_minute_data[best_fit_idx].open_price-best_fit_start)/best_fit_start)
                    best_fit_idx += 1
                else:
                    best_fit_open_prices.append(None)

            else:
                best_fit_open_prices.append(None)
            # if all_times[i] < datetime.datetime.now().replace(hour=9, minute=30, second=0, microsecond=0):
                # lbf1.append((compared_daily_m + (compared_daily_b/330)*0.22847222 * i))
                # lbf1.append(((compared_daily_m/330)*0.22847222 * i)/compared_daily_b)
                # lbf2.append(((best_fit_minute_data[best_fit_idx].pre_m/330)*0.22847222 * i)/best_fit_minute_data[best_fit_idx].pre_b)
            all_times[i] = all_times[i].time().strftime('%I:%M')

        print(best_fit_open_prices)

            # lbf2.append(best_fit)
        # print(lbf1)
        # print(lbf2)
        # compare_open_prices = (compare_open_prices - compare_open_prices[0]) / compare_open_prices[0]
        # best_fit_open_prices = (best_fit_open_prices - best_fit_open_prices[0]) / best_fit_open_prices[0]

        # print('after')
        # a = eps.objects.filter(stocks_isnull=True).values()
        # print(eps.objects.select_related('eps_to_stock').filter(ticker=search).values())
        # for i in a.values():
            # print('here')
            # print(i)
            # print('next')
        if len(background_info) == 1:
            print(background_info.values())
        # print(len(stock.objects.filter(ticker__exact=search)))
        # print(search)

        # data = daily_data_trend.objects.filter(date__exact=compare_date)
        # print(data)

        class MainGraph(BaseChart):
            class labels:
                grouped = all_times
            class data:
                class compare_data:
                    label = "Price for Evaluation Date"
                    data = compare_open_prices
                    # backgroundColor = Color.Green
                    type = ChartType.Line
                    backgroundColor = Color.RGBA(0,0,0,0)
                    borderColor = Color.Blue
                    borderWidth = 1.5
                    radius = 0.5
                class best_fit_data:
                    label = "Price for Day that Best Fits"
                    data = best_fit_open_prices
                    # backgroundColor = Color.Green
                    type = ChartType.Line
                    backgroundColor = Color.RGBA(0,0,0,0)
                    borderColor = Color.Green
                    borderWidth = 1.5
                    radius = 0.5
            class options:
                title = {
                    "text": "Comparision of Stock Price", 
                    "display": True, 
                    "fontSize": 18,
                    'fontColor': Color.Black
                    }

                legend = {
                    'position': 'bottom', 
                    'labels': {
                        'fontColor': Color.Black, 
                        'fullWidth': True
                        }
                    }

                # scales = {
                #     "yAxes": [{
                #         'ticks': {
                #             'beginAtZero': True, 
                #             'padding': 15,
                #             'max': 200
                #             }
                #         }]
                #     }
        eps_data = eps.objects.raw("SELECT eps.id, eps.ticker_id, eps.announced_date, eps.exp_eps, eps.actual_eps FROM eps INNER JOIN stock ON (eps.ticker_id = stock.ticker) WHERE (eps.ticker_id = %s)",[search])
        eps_date_data = []
        eps_exp_data = []
        eps_actual_data = []
        print(len(eps_data))
        for i in range(0,4):
            eps_date_data.append(str(eps_data[i].announced_date))
            eps_exp_data.append(eps_data[i].exp_eps)
            eps_actual_data.append(eps_data[i].actual_eps)
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
                 
                    # backgroundColor = Color.Green
                    
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
        MainChart = MainGraph()
        MainChartJSON = MainChart.get()

        EPSChart = EPSGraph()
        EPSChartJSON = EPSChart.get()

        #code to get news
        # news_articles = news.objects.raw('SELECT news.title, news.date_id, news_time, news.news_url, news.tickers, news.image_url, news.text, news.source_name, news.sentiment, news.type FROM news INNER JOIN dates ON (news.date_id = dates.date) WHERE (dates.date = %s AND stock.ticker = %s)', [compare_date, search])

        # for i in news_articles:
            # print(i.tickers)
        context = {
        'date_analyze': str(compare_date),
        'date_best_fit': str(minDiff_day),
        'mainChartJSON': MainChartJSON,
        'EPSChartJSON': EPSChartJSON,
        'analysis_slope':compared_daily_pre_percent_change,
        'lbf_slope': best_fit_pre_precent_change,
        # 'analysis_MSE': round(compared_daily_MSE,4),
        'analysis_MSE': compared_daily_MSE*4,
        # 'lbf_MSE': round(best_fit_MSE,4),
        'lbf_MSE': best_fit_MSE*4,
        'stock': background_info, 
        'hidden': "no"
        }
        return render(request, 'index.html', context=context)
    else:
        return render(request, 'index.html')
