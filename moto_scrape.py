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
TODO: intelligently itterate the url for each loop
TODO: functionize selenium code
TODO: handle when driver gets redirected to an already visited page
TODO: break the received URLS into parts and place the unique post IDs

"""

url_test = "https://seattle.craigslist.org/search/mca?purveyor=owner#search=1~list~0~0"
url_ad_list_test = ["https://seattle.craigslist.org/see/mcd/d/seattle-2020-harley-davidson-fat-bob/7582174231.html",
            "https://seattle.craigslist.org/see/mcd/d/kent-2018-kawasaki-z650-stunt-bike/7582217722.html",
            "https://seattle.craigslist.org/see/mcd/d/kent-2021-bmw-m1000rr/7582086314.html",
            ]

citys = ["seattle", "portland", "sfbay"]

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
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "postingbody")))
    try:
        details_dict['title'] = driver.find_element(By.ID, 'titletextonly').text
    except:
        details_dict['title'] = 'blank'

    try:
        details_dict['url'] = driver.current_url
    except:
        details_dict['url'] = 'blank'
    
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

main_df = pd.DataFrame([ad_details_dict])

# Creates a list of urls from a search results page
url_ad_list = get_list_of_urls(url_test)

# Adds a new row to the dataframe for each individual ad
for url_ad in url_ad_list:
    time.sleep(random.randint(0,3))
    ad_details = cl_ad_scrape(url_ad)
    new_df = pd.DataFrame([ad_details])
    main_df = pd.concat([main_df, new_df], ignore_index=True)

# Creates a csv file with all of the dataframe information
main_df.to_csv('test_df_to_csv.csv', encoding='utf-8', index=False)


"""
scrape function:
itterate through cities list
perform a driver call on each city, until our route number we get back, matches a search we have already performed.
then move to the next city in the list.

"""