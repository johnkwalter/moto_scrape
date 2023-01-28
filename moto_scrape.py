import requests
import urllib
from bs4 import BeautifulSoup
import time
import random
import re
import pandas as pd
from datetime import datetime


# selenium 4
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager

driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))
# above imports and driver from https://pypi.org/project/webdriver-manager/

from urllib.parse import urlparse

"""
TODO: DONE intelligently itterate the url for each loop
TODO: DONE functionize selenium code
TODO: DONE handle when driver gets redirected to an already visited page
TODO: DONE break the received URLS into parts and place the unique post IDs

TODO: DONE Incorporate list of cities to iterate through to create big url list
TODO: DONE Dedupe dataframe upon writing it to a csv
TODO: Variable and function names are messy and could be made clearer
"""

# Name of the dataframe
dataframe_loc = 'pacific_northwest_cl_moto'

# List of cities that craigslist motorcycle ads will be scraped from
cities = ["seattle", 
        "portland",
        "bellingham",
        "kpr",
        "moseslake",
        "olympic",
        "pullman",
        "skagit",
        "spokane",
        "wenatchee",
        "yakima"
        ]

# Create a blank dictionary to initialize a dataframe from
ad_details_dict = {
    # 'title' : [],
    # 'url' : [],
    # 'price' : [],
    # 'body' : [],
    # 'fuel' : [],
    # 'odometer' : [],
    # 'street legal' : [],
    # 'title status' : [],
    # 'transmission' : [],
}

# Flag to tell whether or not an existing dataframe is being used
new_dataframe = True

# Attempts to open existing dataframe as csv and saves a backup, else creates a new blank dataframe
try:
    main_df = pd.read_csv(dataframe_loc+'.csv')
    main_df.to_csv(dataframe_loc+'_old.csv', encoding='utf-8', index=False)
    new_dataframe = False
except:
    main_df = pd.DataFrame([ad_details_dict])

# Create a list of urls by list of cities to search craigslist with
def city_search_url_list(cities):
    base_city_url_search_list = []
    for city in cities:
        base_city_url_search_list.append('https://' + city + '.craigslist.org/search/mca#search=1~list~')
    return base_city_url_search_list

# Brings up a list of search results on Craiglist and scrapes all of the urls of each ad
def get_list_of_urls(url):
    driver.get(url)
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "titlestring")))
    results_list = driver.find_elements(By.CLASS_NAME, 'titlestring')
    url_ad_list = []
    for elem in results_list:
        url_ad_list.append(elem.get_attribute('href'))
    return url_ad_list

# Crawls through an individual ad and creates a dictionary of the ad details
def cl_ad_scrape(url):
    driver.get(url)
    details_dict = {}

    try:
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "postingbody")))
    except:
        return details_dict

    try:
        details_dict['title'] = driver.find_element(By.ID, 'titletextonly').text
    except:
        details_dict['title'] = 'blank'

    try:
        details_dict['url'] = driver.current_url
    except:
        details_dict['url'] = 'blank'
    
    try:
        post_id = re.search(r'\/(\d+)\.', driver.current_url)
        details_dict['id'] = post_id.group(1)
    except:
        details_dict['id'] = 'blank'

    now = datetime.now()
    details_dict['scrape date'] = now.strftime("%m/%d/%Y, %H:%M:%S")
        
    try:
        details_dict['price'] = driver.find_element(By.CLASS_NAME, 'price').text
    except:
        details_dict['price'] = 'blank'

    try:
        details_dict['body'] = driver.find_element(By.ID, 'postingbody').text
    except:
        details_dict['body'] = 'blank'

    try:
        side_info = driver.find_elements(By.CLASS_NAME, 'attrgroup')
        side_details = side_info[1].text.split('\n')
        for val in side_details:
            detail = re.split('[-:]', val)
            try:
                details_dict[detail[0]] = detail[1].lstrip()
            except:
                details_dict[detail[0]] = "yes"
    except:
        pass

    return details_dict

# Creates a list of urls from a search results page
def get_url_ad_list(base_url):
    full_url_ad_list = []
    last_page = 1000
    try: # In case a url isn't working this won't crash the program
        driver.get(base_url + str(last_page) + '~0')
    except:
        print(f"{base_url} does not exist - moving onto next page")
        return full_url_ad_list
    time.sleep(2)
    last_page = re.search(r'~(\d+)~', driver.current_url)
    last_page = int(last_page.group(1))
    i = 0
    while i <= last_page:
        url = base_url + str(i) + '~0'
        url_ad_list = get_list_of_urls(url)
        for url in url_ad_list:
            full_url_ad_list.append(url)
        i+=1
    return full_url_ad_list

# Adds a new row to the dataframe for each individual ad
def add_ads_to_dataframe(full_url_ad_list, main_df):
    i = 0
    total = len(full_url_ad_list)
    for url_ad in full_url_ad_list:
        time.sleep(random.randint(0,3))
        ad_details = cl_ad_scrape(url_ad)
        new_df = pd.DataFrame([ad_details])
        main_df = pd.concat([main_df, new_df], ignore_index=True)
        i+=1
        print(f" {str(i)} of {str(total)} scraped {str(int((i/total)*100))}% complete ~{str(int(2.15*(total - i)))} seconds left    ", end='\r')
    print('') # <-- clear the line where cursor is located
    print(' done')
    return main_df

# Combines all of the city ad lists into one large url list
def combine_city_url_lists(url_search_list):
    full_url_ad_list = []
    for search_url in url_search_list:
        url_ad_list = get_url_ad_list(search_url)
        for ad_url in url_ad_list:
            full_url_ad_list.append(ad_url)
    return full_url_ad_list

# Deduplicates the list of ad urls
def dedupe_full_url_ad_list(full_url_ad_list):
    deduped_list = []
    for url in full_url_ad_list:
        if url not in deduped_list:
            deduped_list.append(url)
    return deduped_list

# Compares new list of urls to already scraped urls to only scrape new urls
def dedupe_url_ad_list_from_df(ad_list, main_df):
    deduped_url_ad_list = []
    established_url_list = main_df['url'].values.tolist()
    for url in ad_list:
        if url not in established_url_list:
            deduped_url_ad_list.append(url)
    print(f'{str(len(deduped_url_ad_list))} new ads have been found')
    return deduped_url_ad_list

# Deduplicates the rows in the dataframe based on the URL
def dedupe_dataframe(dataframe, column):
    established_url_list = dataframe[column].values.tolist()
    deduped_url_list = []
    duplicates = []

    for url in established_url_list:
        if url not in deduped_url_list:
            deduped_url_list.append(url)
        else:
            duplicates.append(url)

    print(f'{len(duplicates)} duplicate rows will be removed from DataFrame')
    dataframe.drop_duplicates(subset=[column], inplace=True)
    return dataframe

# Creates a list of the base search url for each city in the cities list
base_city_url_search_list = city_search_url_list(cities)

# Creates a list of all of the urls of each ad from each city search
full_url_ad_list = combine_city_url_lists(base_city_url_search_list)

# Deduplicates the list made above because sometimes nearby cities show the same nearby ads
deduped_full_url_ad_list = dedupe_full_url_ad_list(full_url_ad_list)

# Check to see if we're working with a new dataframe, and if so, skips the deduping from dataframe
if new_dataframe:
    new_main_df = add_ads_to_dataframe(deduped_full_url_ad_list, main_df)
else:    
    deduped_url_ad_list_from_df = dedupe_url_ad_list_from_df(deduped_full_url_ad_list, main_df)
    new_main_df = add_ads_to_dataframe(deduped_url_ad_list_from_df, main_df)

# Deduplicates the DataFrame and requires a column argument to dedupe by
deduped_new_main_df = dedupe_dataframe(new_main_df, column='url')

# Creates a csv file with all of the dataframe information
deduped_new_main_df.to_csv(f'{dataframe_loc}.csv', encoding='utf-8', index=False)