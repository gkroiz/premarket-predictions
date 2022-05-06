   
from django.http import HttpResponse
from django.shortcuts import render, redirect


# Create your views here.
from django.urls import reverse

from .models import stock

def index(request):
    if request.method == "POST":
        # if 'search' in request.POST[0]:
            # print('t')
        # print(request.POST)
        search = request.POST.get('search')
        object = stock.objects.filter(ticker__exact=search)
        if len(object) == 1:
            print(object.values())
        # print(len(stock.objects.filter(ticker__exact=search)))
        # print(search)
    return render(request, 'index.html', context={})
