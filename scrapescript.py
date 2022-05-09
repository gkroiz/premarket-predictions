#name: scrapescript.py
#description: this script will run all of the other scripts

import os

print('going to scrapebackground.py')
os.system('python3 scripts/scrapebackground.py')

print('going to scrapestockdata.py')
os.system('python3 scripts/scrapestockdata.py')

print('going to scrapenewsdata.py')
os.system('python3 scripts/scrapenewsdata.py')

print('going to scrapeeps.py')
os.system('python3 scripts/scrapeeps.py')


