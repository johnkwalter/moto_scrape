import requests
import urllib
from bs4 import BeautifulSoup
import time

# selenium 4
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager

driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))
# above imports and driver from https://pypi.org/project/webdriver-manager/

from urllib.parse import urlparse

# https://seattle.craigslist.org/see/mcy/d/seattle-2012-kawasaki-ninja-1000/7581479142.html > result of titlestring class grab. 
# https://seattle.craigslist.org/search/see/mca?purveyor=owner#search=1~list~0~0


url="https://seattle.craigslist.org/search/see/mca?purveyor=owner#search=1~list~3~0"

citys = ["seattle", "portland", "sfbay"]

driver.get(url)
print(driver)
time.sleep(3)
results_list = driver.find_elements(By.CLASS_NAME, "titlestring")
print(f"The results list is {len(results_list)} elements long.")
for elem in results_list:
    print(elem.get_attribute('href'))

print(driver.current_url)
# print(urlparse(url))

# r = requests.get(url)
# soup = BeautifulSoup(r.content, 'html.parser')
# print(soup)
# posts = soup.find_all('li', class_="cl-search-result")
# print(posts)

"""
scrape function:
itterate through cities list
perform a driver call on each city, until our route number we get back, matches a search we have already performed.
then move to the next city in the list.

"""