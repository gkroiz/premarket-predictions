   
from django.http import HttpResponse
from django.shortcuts import render, redirect


# Create your views here.
from django.urls import reverse


def index(request):
    return render(request, 'index.html', context={})


def search(request):
    return redirect(reverse('lookup:index'))