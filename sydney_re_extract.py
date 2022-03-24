from email.mime import application
from tkinter import W
import requests
import json
import os.path
import os
import time
import random

import pandas as pd
from pandasql import sqldf
import csv

df = pd.read_csv ('australian_suburbs_1.csv')
df = sqldf('''

WITH betweened AS(

    SELECT suburb
         , state
         , postcode
         , lat
         , lng
      FROM df
     WHERE state = 'NSW'
       AND lat BETWEEN (-33.8708-0.9) AND (-33.8708+0.9)
       AND lng BETWEEN (151.2073-0.9) AND (151.2073+0.9)
)
    SELECT SQRT((lat+33.8708)*(lat+33.8708) + (lng-151.2073)*(lng-151.2073))*110 AS cbd_distance
         , *
      FROM betweened
     WHERE cbd_distance between 34.1 and 50
     ORDER BY cbd_distance
''')

suburbs = df.to_dict('records')

headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.82 Safari/537.36",'ACCEPT': 'application/json'}



def get_subinfo(record):
    suburb = record['suburb'].replace(' ', '-')
    state = 'nsw'
    postcode = record['postcode']
    return f'{suburb}-{state}-{postcode}'

def get_dist(record):
    return record['cbd_distance']

# return domain url for a given suburb
def get_url(suburb):
    return f'https://www.domain.com.au/sold-listings/{suburb}/?excludepricewithheld=1&ssubs=0'


# return domain url for a given suburb with page
def get_page_url(suburb, page):
    return f'https://www.domain.com.au/sold-listings/{suburb}/?excludepricewithheld=1&ssubs=0&page={page}'


#return content
def get_content(url):
    return requests.get(url = url, headers=headers).text

#load content into json
def get_json(url):
    return json.loads(requests.get(url = url, headers=headers).text)

def write_file(file_name, content):
    os.makedirs(os.path.dirname(file_name), exist_ok = True)
    with open(file_name, "w") as f:
        f.write(json.dumps(content)) 

def download_or_not(file_name: str, url: str) -> str:
    if os.path.isfile(file_name):
        print(f"Already has file: {file_name}")
    else: 
        content = get_json(url)
        print(f"Downloaded {url}")
        write_file(file_name, content)
        time.sleep(random.randrange(20)*random.random())
def json_file_name(suburb: str, page: int) -> str:
    page_str = str(page).zfill(3)
    return f"download/www.domain.com/{suburb}/page_{page}.json"

def download_suburbs(suburbs):
    for record in suburbs:
        suburb = get_subinfo(record)
        path = f"download/www.domain.com/{suburb}"
        isexist = os.path.exists(path)
        file_name = f"download/www.domain.com/{suburb}/page_50.json"
        filexist = os.path.isfile(file_name)
        if isexist == False or filexist == False:
            url = get_url(suburb)
            total_page = get_json(url)['props']['totalPages']
            print(get_dist(record))
            print(total_page)
            for page in range(1, total_page + 1):
                download_or_not(json_file_name(suburb, page), get_page_url(suburb, page))
        else:
            print(f"Already download suburb: {suburb}")
        time.sleep(random.randrange(10))
            
            
download_suburbs(suburbs)

