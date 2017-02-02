#!/usr/bin/env python

from lxml import html
import requests
import numpy as np 
import re
import datetime

def main():
    url = 'https://www.nav.no/no/NAV+og+samfunn/Kontakt+NAV/Utbetalinger/Grunnbelopet+i+folketrygden'
    data_website = read_website(url) #Read raw data from website
    processed_data = process_data(data_website) #Process data to readable format
    g_amounts_year = avg_g_amounts(processed_data) #Calculate average G amounts per year
    
def read_website(url):
    #Read Norwegian social security base amount data from NAV website
    page = requests.get(url)
    tree = html.fromstring(page.content)
    raw_data = tree.xpath('//td/text()') #
    return raw_data

def process_data(rawdata):
    #Extract the social security base amounts (G) from the raw data

    g_amounts = rawdata[1:20:6]
    g_amounts.append(rawdata[24])

    for i in rawdata[29::5]:
        g_amounts.append(i)

    g_amounts = [x.strip('kr') for x in g_amounts] #Remove currency
    g_amounts = [re.sub("[^0-9]", "", x) for x in g_amounts] #Remove all non-number characters
    g_amounts = map(int, g_amounts)
        
    #Extract the dates from the raw data
    dates = rawdata[0:19:6]
    dates.append(rawdata[23])
    dates.append(rawdata[28::5])

    return [dates, g_amounts]

def avg_g_amounts(dates_gamounts):
    print dates_gamounts
    return 0

if __name__ == '__main__':
    main()
