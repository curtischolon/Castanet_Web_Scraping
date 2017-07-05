import requests
import bs4
from bs4 import BeautifulSoup

import pandas as pd
import time

# Search for smoker on Castanet.net
URL = "https://classifieds.castanet.net/search/?search=smoker&\
    id_cat=254&pfrom=&pto=&datetype=days&user=&datenr=&submit="

# requesting the page above
page = requests.get(URL)

soup = BeautifulSoup(page.text, 'html.parser')


# print(soup.prettify())

def extract_listing_title_from_result(soup):

    ads = []
    for prod_container in soup.find_all(name='a', class_='prod_container'):
        for div in prod_container.find_all(name='h2'):
            print(div.get_text())
            ads.append(div.get_text())

    return ads


ads = extract_listing_title_from_result(soup)

print(ads)
