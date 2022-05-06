from datetime import datetime
from operator import mod
from pydoc import describe
import secrets
from django.db import models

# Create your models here.

class minute_stock_data(models.Model):
    id = models.AutoField(primary_key=True, unique=True)
    ticker = models.CharField(max_length=10, name='ticker')
    datetime = models.DateTimeField(name='datetime')
    open_price = models.FloatField()
    close_price = models.FloatField()
    high_price = models.FloatField()
    low_price = models.FloatField()
    volume = models.IntegerField()
    percent_change = models.FloatField()
    class Meta:
        db_table = 'minute_stock_data'

class daily_data_trend(models.Model):
    id = models.AutoField(primary_key=True, unique=True)
    ticker = models.CharField(max_length=10, name='ticker')
    date = models.DateField(name='date')
    pre_b = models.FloatField()
    pre_m = models.FloatField()
    pre_MSE = models.FloatField()
    pre_start = models.FloatField()
    pre_end = models.FloatField()
    class Meta:
        db_table = 'daily_data_trend'

class eps(models.Model):
    id = models.AutoField(primary_key=True, unique=True)
    ticker = models.CharField(max_length=10, name='ticker')
    date = models.DateField(name='date')
    exp_eps = models.FloatField()
    actual_eps = models.FloatField()
    class Meta:
        db_table = 'eps'

class news(models.Model):
    article_id = models.AutoField(primary_key=True, unique=True)
    title = models.TextField()
    datetime = models.DateTimeField()
    news_url = models.TextField()
    tickers = models.JSONField()
    image_url = models.TextField()
    text = models.TextField()
    source_name = models.TextField()
    sentiment = models.CharField(max_length=100)
    type = models.CharField(max_length= 100)
    class Meta:
        db_table = 'news'


class stock(models.Model):
    ticker = models.CharField(max_length=100, primary_key=True)
    name = models.CharField(max_length=100)
    sector = models.CharField(max_length=45)
    industry = models.CharField(max_length=45)
    age = models.DateField()
    description = models.TextField()
    total_employees = models.IntegerField()
    website = models.TextField()
    class Meta:
        db_table = 'stock'

