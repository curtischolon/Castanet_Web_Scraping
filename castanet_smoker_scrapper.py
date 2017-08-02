#! python3

import requests
import re
from bs4 import BeautifulSoup
import os
import pandas as pd
import time
import xlsxwriter
import shelve
import csv


def find_listing_date(soup, dates):
    """pulls the ad date from the search results"""
    pdate = soup.find_all(name = 'div', class_='pdate')
    for i in pdate:
        # input(i)
        text = i.get_text()
        date = text.split(':')
        date = date[2:3]

        dates.append(date)

    return dates


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

    print("Number of ads: ", number_of_ads)

    return int(number_of_ads)


def download_image(urls):
    """downloads listing images and saves locally"""
    image_paths = []

    base_url = "https://classifieds.castanet.net"
    image_directory = os.path.join('C:\\', 'users', 'ccholon', 'my documents', 'castanet images')

    for url in urls:
        listing_url = base_url + url
        image_page = requests.get(listing_url)
        image_soup = BeautifulSoup(image_page.text, 'html.parser')

        # find the URL for the listing image
        image_element = image_soup.find(name='div', class_='image_container')
        image_element = image_element.find(name='img')
        image_url = image_element.get('src')

        # download the image
        #image = requests.get(image_url, stream=True)

        # save to local directory
        #image_file = open(os.path.join(image_directory, os.path.basename(image_url)), 'wb')
        #for bytes in image.iter_content(100000):
            #image_file.write(bytes)
        #image_file.close()

        image_paths.append(os.path.join(image_directory, os.path.basename(image_url)))

    return image_paths


def extract_listing_title_from_result(soup, ads, ad_count):
    """pulls the ad title for each listing on the current page"""
    for prod_container in soup.find_all(name='a', class_='prod_container'):
        for div in prod_container.find(name='h2'):
            ads.append(div)
            ad_count += 1

    # print(ads)
    print(ad_count)
    return ads, ad_count


def extract_listing_price_from_result(soup, prices):
    """pulls the listing price for each listing on the current page"""
    for description in soup.find_all(name='div', class_='descr'):
        price = description.find(name='div', class_='price')
        if price == None:
            prices.append('No Price')
        else:
            prices.append(price.get_text())
    # print(prices)
    return prices


def extract_listing_location_from_result(soup, location):
    """pulls the listing location for each listing on the current page"""
    for div in soup.find_all(name='div', class_='pdate'):
        for city in div.find(name='span'):
            location.append(city)
    # print(locations)
    return location


def extract_url_from_result(soup, url, listing_id):
    """pulls the url for each listing on the current page"""
    for link in soup.find_all(name='a', class_='prod_container'):
        url.append(link.get('href'))
        link_text = link.get('href')

        # From URL - extract listing ID
        try:
            id_regex = re.compile(r'\d{7}')
            id_ = id_regex.search(link_text).group()
            listing_id.append(id_)
        except:
            listing_id.append('Not found')
    # print(url)
    # print(listing_id)
    return url, listing_id


# --MAIN--

# Retrieve listing history to identify new ads
# shelf_file = shelve.open('bbq_listings')
# past_listings = shelf_file['past_listings']
# shelf_file.close()
try:
    input_list = open('listing_history.csv')
    past_listings = list(input_list)
    input_list.close()
except:
    past_listings = []
    print("Previous listings unavailable")


# base URL - Castanet BBQ, Smokers, Heaters
base_url = "https://classifieds.castanet.net/cat/house-home/garden_yard_patio/bbqs_smokers_heaters/?p="

# first step - determine the total number of ads
number_of_ads = find_number_of_ads()

# based on the total number of add, cycle through each page
ad_count = 0
page = 1
ads = []
prices = []
locations = []
urls = []
ids = []
dates = []
while ad_count < number_of_ads:
    # create custom search url based on number of ads
    url = base_url + str(page)

    # requesting the page above
    web_page = requests.get(url)
    time.sleep(1)

    soup = BeautifulSoup(web_page.text, 'html.parser')

    # extract ad details
    ads, ad_count = extract_listing_title_from_result(soup, ads, ad_count)

    prices = extract_listing_price_from_result(soup, prices)

    locations = extract_listing_location_from_result(soup, locations)

    urls, ids = extract_url_from_result(soup, urls, ids)

    dates = find_listing_date(soup, dates)

    page += 1

# Download images based on ad ID
image_list = download_image(urls)

# create empty dataframes to store all Castanet listings, as well as new listings
columns = ['Ad_Name', 'ID', 'AD Date', 'Price', 'Location', 'URL', 'Image_Path']
all_listings_df = pd.DataFrame(columns=columns)
new_listings_df = pd.DataFrame(columns=columns)

# compile listings to dataframe
row = 0
for i in range(number_of_ads):
    # increment row for dataframe
    row = (i+1)

    # create variable to store current row
    try:
        all_listings = [ads[i], ids[i], dates[i], prices[i], locations[i], "https://classifieds.castanet.net" + urls[i],\
                        image_list[i]]
    except:
        print("list index out of range")

    # append to dataframe
    all_listings_df.loc[row] = all_listings

    if all_listings not in past_listings:
        # print("check values")
        # print(all_listings)
        # input(past_listings)
        new_listings = all_listings
        new_listings_df.loc[row] = new_listings
        past_listings.append(new_listings)

# export files to excel
listing_path = os.path.join('C:\\', 'users', 'ccholon', 'my documents', 'castanet images', 'all_bbq_listings.xlsx')
xlwriter = pd.ExcelWriter(listing_path, engine='xlsxwriter')
all_listings_df.to_excel(xlwriter, sheet_name='Sheet 1')
xlwriter.save()

listing_path = os.path.join('C:\\', 'users', 'ccholon', 'my documents', 'castanet images', 'new_bbq_listings.xlsx')
xlwriter = pd.ExcelWriter(listing_path, engine='xlsxwriter')
new_listings_df.to_excel(xlwriter, sheet_name='Sheet 1')
xlwriter.save()

# save contents to CSV for future reference
output = open('listing_history.csv', 'w', newline='')
output_writer = csv.writer(output)
for i in past_listings:
    output_writer.writerow(i)

output.close()

# shelve listings for next run
# shelf_file = shelve.open('bbq_listings')
# shelf_file['past_listings'] = past_listings
# shelf_file.close()

# TODO - process excel file and insert hyperlinks where necessary
# TODO - log ID's to file for future lookup, avoid pulling duplicate listings
# TODO - develop schedule / recurrence theme for the automation

print('ads: ', len(ads))
print('prices: ', len(prices))
print('locations: ', len(locations))
print('urls: ', len(urls))
print('ids: ', len(ids))
print('dates: ', len(dates))
