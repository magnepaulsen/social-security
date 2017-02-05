#!/usr/bin/env python

from lxml import html
import requests
from scipy import stats 
import re
from datetime import datetime
from collections import Counter
from pylab import plot,show

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
    g_amounts = map(float, g_amounts)
    g_amounts.reverse()
    
    #Extract the dates from the raw data
    dates = rawdata[0:19:6]
    dates.append(rawdata[23])
    dates = dates + rawdata[28::5]
    dates.reverse()
    return dates, g_amounts

def avg_g_amounts(dates, g_amounts):
    #Calculate average social security base (G) amount per year. There could be one or multiple amounts per year
    avgGamounts = {}
    years=[]
    
    for x in dates:
        years.append(x.year)

    count_years = Counter(years) #count the number of social security base amounts per year
    
    for i in range(len(dates)):
        if count_years[dates[i].year] == 1:
            if i==len(dates)-1:
                avgGamounts[dates[i].year] = g_amounts[i]*(12-dates[i].month+1)/12.0 + g_amounts[i-1]*(1-(12-dates[i].month+1)/12.0)
            else:
                avgGamounts[dates[i].year] = g_amounts[i]*(12-dates[i].month+1)/12.0 + g_amounts[i-1]*(1-(12-dates[i].month+1)/12.0)
        else:
            if count_years[dates[i].year] == 2 and dates[i].year!=dates[i-1].year:
                #2 social security base amount changes in year
                if dates[i].month == 1:
                    avgGamounts[dates[i].year] = g_amounts[i]*(dates[i+1].month-1)/12.0 + g_amounts[i+1]*(12-dates[i+1].month+1)/12.0
                else:
                    avgGamounts[dates[i].year] = g_amounts[i-1]*(dates[i].month-1)/12.0 + g_amounts[i]*(dates[i+1].month-dates[i].month)/12.0 + g_amounts[i+1]*(12-dates[i+1].month+1)/12.0
            else:
                if dates[i].year!=dates[i-1].year:
                    #3 social security base amount changes in year. Assumes that the first change is on January 1
                    avgGamounts[dates[i].year] = g_amounts[i]*(dates[i+1].month-1)/12.0 + g_amounts[i+1]*(dates[i+2].month-dates[i+1].month)/12.0 + g_amounts[i+2]*(12-dates[i+2].month+1)/12.0
    
    return avgGamounts

def convert_dates(dates):
    #Convert dates from string to datetime objects
    converted_dates = [datetime.strptime(x, "%d.%m.%Y") for x in dates]
    return converted_dates

def g_increase(base_amounts):
    #Calculate the percentage increase of the social security base amount (G) per year
    years = base_amounts.keys()
    yrly_base_amounts = base_amounts.values()
    yrly_increases = [100*(yrly_base_amounts[i]/yrly_base_amounts[i-1]-1) for i in range(1,len(yrly_base_amounts))]
    return yrly_increases

def regression_fit(g_increases, years):
    #Fit linear regression line for the yearly social security base amount (G) increase    
    years = years[1:len(years)]
    slope, intercept, r_value, p_value, std_err = stats.linregress(years, g_increases)

    print 'r value', r_value
    print  'p_value', p_value
    print 'standard deviation', std_err

    line = slope*years+intercept
    plot(years,line,'r-',years,g_increases,'o')
    show()

def main():
    url = 'https://www.nav.no/no/NAV+og+samfunn/Kontakt+NAV/Utbetalinger/Grunnbelopet+i+folketrygden'
    data_website = read_website(url) #Read raw data from website
    dates, g_amounts = process_data(data_website) #Process data to readable format
    dates = convert_dates(dates)
    avg_base_amounts = avg_g_amounts(dates, g_amounts) #Calculate average G amounts per year
    g_increases = g_increase(avg_base_amounts)
    reg_model = regression_fit(g_increases, avg_base_amounts.keys())
    
if __name__ == '__main__':
    main()
