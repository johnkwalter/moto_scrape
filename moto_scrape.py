import requests
import urllib
from bs4 import BeautifulSoup
from urllib.parse import urlparse

# https://seattle.craigslist.org/see/mcy/d/seattle-2012-kawasaki-ninja-1000/7581479142.html > result of titlestring class grab. 
# https://seattle.craigslist.org/search/see/mca#search=1~gallery~1~38


url="https://seattle.craigslist.org/search/see/mca#search=1~gallery~1~38"

print(urlparse(url))

"""
class "titlestring" contains the needed href info. including the post ID

using urllib grab just the post ID and add it to a set this will handle duplicate posts (reposts which likely have a new ID will not be handled by this)
    if that number is not in the set, we scrape it and add the information to our DF or CSV file
    else: that number exists inside the set, we ignore it and move on. 

Itterates through all the titlestring classed elements then moves on to the next page and repeats. 

we can change the city in the URL for each scrape.
"""