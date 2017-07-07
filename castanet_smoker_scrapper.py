import requests
from bs4 import BeautifulSoup

import pandas as pd
import time

# Search for smoker on Castanet.net
URL = "https://classifieds.castanet.net/cat/house-home/garden_yard_patio/bbqs_smokers_heaters/"

# requesting the page above
page = requests.get(URL)

soup = BeautifulSoup(page.text, 'html.parser')


# input(soup.prettify())


def extract_listing_title_from_result(soup):
    """pulls the ad title for each listing on the current page"""
    ads = []
    for prod_container in soup.find_all(name='a', class_='prod_container'):
        for div in prod_container.find(name='h2'):
            print(div)
            ads.append(div)

    return ads


def extract_listing_price_from_result(soup):
    """pulls the listing price for each listing on the current page"""
    prices = []
    for description in soup.find_all(name='div', class_='descr'):
        for price in description.find_all(name='div', class_='price'):
            print(price.get_text())
            prices.append(price.get_text())

    return prices


def extract_listing_location_from_result(soup):
    """pulls the listing location for each listing on the current page"""
    location = []
    for div in soup.find_all(name='div', class_='pdate'):
        for city in div.find(name='span'):
            print(city)
            location.append(city)

    return location


# TODO - capture URL and Post ID, log contents to file, check on next iteration whether the listing exists
# already, or not. Parse through pages to the end of the listings.


ads = extract_listing_title_from_result(soup)

prices = extract_listing_price_from_result(soup)

locations = extract_listing_location_from_result(soup)

print(ads)
print(prices)
print(locations)
