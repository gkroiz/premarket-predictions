# project-premarket-predictions
https://stackoverflow.com/questions/63392426/how-to-use-tailwindcss-with-django

## Dependencies:
- sqlalchemy=1.4.36
- pymysql=1.0.2
- yfinance=0.1.63
- numpy=1.21.5
- pandas=1.3.5
- django=3.2
- requests
- beautifulsoup4
- requests_html


## Reset mirgations
1) python manage.py migrate --fake homepage zero
2) find . -path "*/migrations/*.py" -not -name "__init__.py" -delete
find . -path "*/migrations/*.pyc"  -delete
3) python manage.py makemigrations
4) python manage.py sqlmigrate homepage 0001
5) python manage.py migrate