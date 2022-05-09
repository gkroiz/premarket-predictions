# Premarket Predictions
As most people know, the stock market opens at 9:30 am and closes at 4:00 pm. In addition to this, people have the opportunity, based on their brokerage, to trade during premarket hours (4:00 am to 9:30 am) or during after hours (4:00 pm to 8:00 pm). Everyone's goal with the stock market is to make a profit, whether it is through daily trading and making short term profits, or buying and holding onto stocks for long term profits. To try gaining an advantage, traders refer to popular finance-based websites such as finance.yahoo.com, nasdaq.com, and marketwatch.com to analyze companies and their stock information. While these websites focus on showing lots of information for stocks, they provide little to no analysis regarding premarket movement of a stock's price. Premarket information is can be very helpful in gauging the market outlook ahead of the regular open. As such, this UI has a focus on the premarket information to see if any trends can be found.

The layout of the UI is shown below:
![Screenshot](readme_images/Screen%20Shot%202022-05-08%20at%209.31.45%20PM.png)
![Screenshot](readme_images/Screen%20Shot%202022-05-08%20at%209.32.08%20PM.png)
![Screenshot](readme_images/Screen%20Shot%202022-05-08%20at%209.32.21%20PM.png)

This project was implemented using Python via Django with data stored via MySQL. 
The data to populate the database for this project was scraped from the following sources:
- https://www.alphaquery.com/
- https://api.polygon.io/ (api key needed)
- https://finance.yahoo.com/
- https://stocknewsapi.com/ (api key needed)

## Database Structure
The code for this project is designed with the following ER diagram:


## Using this Repository
To use this repository, you first need to install Python and MySQL. For python, you will need the following dependencies:
- sqlalchemy
- pymysql
- numpy
- pandas
- django
- requests
- beautifulsoup4
- requests_html
- pychart.js
- scikit-learn


## Reset mirgations
1) python manage.py migrate --fake homepage zero
2) find . -path "*/migrations/*.py" -not -name "__init__.py" -delete
find . -path "*/migrations/*.pyc"  -delete
3) python manage.py makemigrations
4) python manage.py sqlmigrate homepage 0001
5) python manage.py migrate