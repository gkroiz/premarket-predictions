   
from turtle import back
from django.http import HttpResponse
from django.shortcuts import render, redirect


# Create your views here.
from django.urls import reverse

from .models import stock, eps, minute_stock_data, news, daily_data_trend

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
        a = eps.objects.select_related('ticker')
        # print(a.query)
        # print(a)

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

        data = daily_data_trend.objects.filter(date__exact=compare_date)
        print(data)

        context = {
        'stock': background_info
        }
        return render(request, 'index.html', context=context)
    else:
        return render(request, 'index.html')
