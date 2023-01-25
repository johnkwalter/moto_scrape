import requests
import urllib
from bs4 import BeautifulSoup
import time
import re

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

JOHN: Turn the cl_ad_scrape into it's own Class maybe?
"""


# https://seattle.craigslist.org/see/mcy/d/seattle-2012-kawasaki-ninja-1000/7581479142.html > result of titlestring class grab. 
# https://seattle.craigslist.org/search/see/mca?purveyor=owner#search=1~list~0~0


url="https://seattle.craigslist.org/search/see/mca?purveyor=owner#search=1~list~0~0"
url_ad = "https://seattle.craigslist.org/see/mcd/d/seattle-2020-harley-davidson-fat-bob/7582174231.html"

citys = ["seattle", "portland", "sfbay"]

driver.get(url)

def get_list_of_urls():
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "titlestring")))
    results_list = driver.find_elements(By.CLASS_NAME, 'titlestring')
    # results_list = driver.find_elements(By.CLASS_NAME, "titlestring")
    for elem in results_list:
        print(elem.get_attribute('href'))
    print(f"The results list is {len(results_list)} elements long.")

def cl_ad_scrape(url):
    driver.get(url)
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "postingbody")))
    title = driver.find_element(By.ID, 'titletextonly').text
    price = driver.find_element(By.CLASS_NAME, 'price').text
    body_of_ad = driver.find_element(By.ID, 'postingbody').text
    side_info = driver.find_elements(By.CLASS_NAME, 'attrgroup')
    side_details = side_info[1].text.split('\n')
    details_dict = {}
    for val in side_details:
        detail = re.split('[-:]', val)
        try:
            details_dict[detail[0]] = detail[1].lstrip()
        except:
            details_dict[detail[0]] = "Blank or N/A"
    
    return [title, price, body_of_ad, details_dict]
    # print(title)
    # print(price)
    # print(body_of_ad)
    # print(details_dict)

ad_details_list = cl_ad_scrape(url_ad)
for var in ad_details_list:
    print(var)


print(driver.current_url)


"""
scrape function:
itterate through cities list
perform a driver call on each city, until our route number we get back, matches a search we have already performed.
then move to the next city in the list.

"""