#!/usr/bin/python
# pip install lxml
# pip install geopy
# pip install xmltodict
# pip install googlemaps

from logging import error
import requests
import pandas as pd
from bs4 import BeautifulSoup
from urllib.parse import quote
from urllib.request import Request, urlopen
import ssl
import json
import googlemaps
import xmltodict
import time

googlemaps_key = ''
maxwidth = 400
maxheight = 400

print("Process initiating")
gmaps = googlemaps.Client(key=googlemaps_key)

decodingKey = ''
url = 'http://apis.data.go.kr/6270000/getTourKorAttract/getTourKorAttractList'
params = {'serviceKey': decodingKey, 'numOfRows': 255}
response = requests.get(url, params=params)
soup = BeautifulSoup(response.content, 'lxml-xml')
items = soup.find_all("item")


'''
data_dict = open('data.xml', 'r', encoding='utf-8-sig')
soup = BeautifulSoup(data_dict, 'lxml')
fullcnt = soup.find("totalCount")
'''

row = []
attractnames = []


def parse(item, i):
    ID = i
    NAME = item.find("attractname").get_text()
    CONTENT = item.find("attractcontents").get_text()
    if len(CONTENT) > 500:
        CONTENT = CONTENT[:500] + '...중략'
    ADDRESS = item.find("address").get_text()

    try:
        PAGE_URL = item.find("homepage").get_text()
    except:
        PAGE_URL = None
    try:
        TEL = item.find('tel').get_text()
    except:
        TEL = None
    try:
        HOUR = item.find('attr01').get_text()
    except:
        HOUR = None

    try:
        geo_location = gmaps.geocode(ADDRESS)[0].get('geometry')
        test = geo_location['location']
        LAT = geo_location['location']['lat']
        LON = geo_location['location']['lng']
        COORDINATE = [LAT, LON]
    except:
        COORDINATE = None

    try:
        temp = '대구 ' + NAME
        place_result = gmaps.geocode(temp)[0]
        # print(place_result)
        my_place_id = place_result['place_id']
        # print(my_place_id)
        place_details = gmaps.place(place_id=my_place_id, fields=['photo'])
        photo_id = place_details['result']['photos'][0]['photo_reference']
        raw_image_data = gmaps.places_photo(photo_reference=photo_id, max_height=maxheight,
                                            max_width=maxwidth)
        PHOTO_AVAIL = True
        # print(raw_image_data)
        filename = "images/%d.jpg" % i
        
        f = open(filename, 'wb')

        for chunk in raw_image_data:
            if chunk:
                f.write(chunk)

        f.close()
    except:
        PHOTO_AVAIL = False

    return {
        "id": ID,
        "name": NAME,
        "contents": CONTENT,
        "homepage": PAGE_URL,
        "address": ADDRESS,
        "tel": TEL,
        "hour": HOUR,
        "coordinate": COORDINATE
    }


for (i, item) in enumerate(items):
    row.append(parse(item, i))
    time.sleep(0.1)

df = pd.DataFrame(row)

df.to_csv("DataSet.csv", index=False, mode='w', encoding="utf-8-sig")
print(".csv file, images create")
print('Program shut down')
