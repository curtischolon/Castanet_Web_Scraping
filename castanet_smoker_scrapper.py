import requests
import re
from bs4 import BeautifulSoup
import os

import pandas as pd
import time

# Search for smoker on Castanet.net
URL = "https://classifieds.castanet.net/cat/house-home/garden_yard_patio/bbqs_smokers_heaters/"


# requesting the page above
page = requests.get(URL)

soup = BeautifulSoup(page.text, 'html.parser')


# input(soup.prettify())

def find_number_of_ads():
    """returns the number of ads to parse"""
    home_url = "https://classifieds.castanet.net/cat/house-home/garden_yard_patio"
    home_page = requests.get(home_url)
    number_of_soup_ads = BeautifulSoup(home_page.text, 'html.parser')

    # extract the category, which includes the number of ads
    header = number_of_soup_ads.find(name='a', href='bbqs_smokers_heaters/')
    number_of_ads = header.find('span')
    number_of_ads = number_of_ads.get_text()
    number_regex = re.compile(r'(\d)*')
    number_of_ads = number_regex.search(number_of_ads).group()

    return int(number_of_ads)


def download_image(urls):
    """downloads listing images and saves locally"""
    base_url = "https://classifieds.castanet.net"
    image_directory = os.path.join('C:\\', 'users', 'ccholon', 'my documents', 'castanet images')

    image_paths = []

    for url in urls:
        listing_url = base_url + url
        image_page = requests.get(listing_url)
        image_soup = BeautifulSoup(image_page.text, 'html.parser')

        # find the URL for the listing image
        image_element = image_soup.find(name='div', class_='image_container')
        image_element = image_element.find(name='img')
        image_url = image_element.get('src')

        # download the image
        image = requests.get(image_url, stream=True)
        # input(image)

        # save to local directory
        image_file = open(os.path.join(image_directory, os.path.basename(image_url)), 'wb')
        for bytes in image.iter_content(100000):
            image_file.write(bytes)
        image_file.close()

        image_paths.append(os.path.join(image_directory, os.path.basename(image_url)))

    return image_paths


def extract_listing_title_from_result(soup):
    """pulls the ad title for each listing on the current page"""
    ads = []
    add_count = 0
    for prod_container in soup.find_all(name='a', class_='prod_container'):
        for div in prod_container.find(name='h2'):
            ads.append(div)
            add_count += 1

    return ads, add_count


def extract_listing_price_from_result(soup):
    """pulls the listing price for each listing on the current page"""
    prices = []
    for description in soup.find_all(name='div', class_='descr'):
        for price in description.find_all(name='div', class_='price'):
            prices.append(price.get_text())

    return prices


def extract_listing_location_from_result(soup):
    """pulls the listing location for each listing on the current page"""
    location = []
    for div in soup.find_all(name='div', class_='pdate'):
        for city in div.find(name='span'):
            location.append(city)

    return location


def extract_url_from_result(soup):
    """pulls the url for each listing on the current page"""
    url = []
    listing_id = []
    for link in soup.find_all(name='a', class_='prod_container'):
        url.append(link.get('href'))
        link_text = link.get('href')

        # From URL - extract listing ID
        id_regex = re.compile(r'\d{7}')
        id_ = id_regex.search(link_text).group()
        listing_id.append(id_)

    return url, listing_id



# --MAIN--

ads, add_count = extract_listing_title_from_result(soup)

prices = extract_listing_price_from_result(soup)

locations = extract_listing_location_from_result(soup)

urls, ids = extract_url_from_result(soup)

number_of_ads = find_number_of_ads()

images = download_image(urls)

print(ads)
print(prices)
print(locations)
print(urls)
print(ids)
print(number_of_ads)
print(add_count)
print(images)