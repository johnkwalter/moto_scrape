import requests
import urllib
from bs4 import BeautifulSoup
import time
import random
import re
import pandas as pd


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
TODO: handle when driver gets redirected to an already visited page
TODO: DONE break the received URLS into parts and place the unique post IDs

TODO: DONE Incorporate list of cities to iterate through to create big url list
"""

# Url variables to test from
url_test = "https://seattle.craigslist.org/search/mca#search=1~list~0~0"
url_ad_list_test = ["https://seattle.craigslist.org/see/mcd/d/seattle-2020-harley-davidson-fat-bob/7582174231.html",
            "https://seattle.craigslist.org/see/mcd/d/kent-2018-kawasaki-z650-stunt-bike/7582217722.html",
            "https://seattle.craigslist.org/see/mcd/d/kent-2021-bmw-m1000rr/7582086314.html",
            ]

dataframe_loc = 'test_df_to_csv.csv'

# List of cities that craigslist motorcycle ads will be scraped from
cities = ["wenatchee", "bellingham", "yakima"]

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

# Create a blank dataframe from that blank dictionary -OR- import existing dataframe
# main_df = pd.DataFrame([ad_details_dict])
main_df = pd.read_csv(dataframe_loc)

# Create a list of urls by list of cities to search craigslist with
def city_search_url_list(cities):
    url_search_list = []
    for city in cities:
        url_search_list.append('https://' + city + '.craigslist.org/search/mca#search=1~list~')
    return url_search_list

# Brings up a list of search results on Craiglist and scrapes all of the urls of each ad
def get_list_of_urls(url):
    driver.get(url)
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "titlestring"))) 
    results_list = driver.find_elements(By.CLASS_NAME, 'titlestring')
    url_list = []
    for elem in results_list:
        url_list.append(elem.get_attribute('href'))
    return url_list

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
    driver.get(base_url + str(last_page) + '~0')
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
def add_ad_to_dataframe(full_url_ad_list, main_df):
    i = 0
    total = len(full_url_ad_list)
    for url_ad in full_url_ad_list:
        time.sleep(random.randint(0,3))
        ad_details = cl_ad_scrape(url_ad)
        new_df = pd.DataFrame([ad_details])
        main_df = pd.concat([main_df, new_df], ignore_index=True)
        i+=1
        if i%10 == 0:
            print(f"{str(i)} of {str(total)} scraped ~{str(2*(total - i))} seconds left")
    return main_df

# Combines all of the city ad lists into one large url list
def combine_city_url_lists(url_search_list):
    full_url_ad_list = []
    for url in url_search_list:
        url_ad_list = get_url_ad_list(url)
        for url in url_ad_list:
            full_url_ad_list.append(url)
    return full_url_ad_list

def dedupe_url_ad_list(full_url_ad_list, main_df):
    deduped_url_ad_list = []
    established_url_list = main_df["url"].values.tolist()
    for url in full_url_ad_list:
        if url not in established_url_list:
            deduped_url_ad_list.append(url)
    return deduped_url_ad_list

url_search_list = city_search_url_list(cities)
full_url_ad_list = combine_city_url_lists(url_search_list)
deduped_url_ad_list = dedupe_url_ad_list(full_url_ad_list, main_df)

new_main_df = add_ad_to_dataframe(deduped_url_ad_list, main_df)

# Creates a csv file with all of the dataframe information
new_main_df.to_csv('test_df_to_csv.csv', encoding='utf-8', index=False)
