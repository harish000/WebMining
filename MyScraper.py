# -*- coding: utf-8 -*-
"""
Created on Fri Jan 13 17:26:25 2017

@author: Sriharish
"""

import time
import string
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
 
 
from bs4 import BeautifulSoup
import pandas as pd

from Settings import Settings

from pymongo import MongoClient
 
import matplotlib.pylab as plt 
 
import numpy as np

from statsmodels.tsa.stattools import adfuller
from statsmodels.tsa.arima_model import ARIMA


def init_driver():
#    Give the path for Chrome web driver
#   Download it from here https://sites.google.com/a/chromium.org/chromedriver/downloads
    driver = webdriver.Chrome("D:\Software\chromedriver_win32\chromedriver.exe") 
    driver.wait = WebDriverWait(driver, 5)
    return driver
 
 
def lookup(driver):
#    Lookup the website and download the source to a local file or scrape it directly
    driver.get("https://finance.yahoo.com/quote/CSCO/history?p=CSCO")
    try:
        for i in range(1,5):
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        source = driver.page_source
        print(type(source))
        with open("source.html","wb") as f:
            f.write(source.encode('utf8'))
        driver.quit()               
        return source        
    except TimeoutException:
        print("Something is messed up. Check configuration...")
        return None
 

def parseSource(filename):
#    We use beautifulsoup to parse html file. It uses xpath or html.parser to lookup tags. 
    soup = BeautifulSoup((filename), 'html.parser')
    soup.prettify()
    head = soup.find_all('thead')
    head_th = head[0].find_all('th')
    header = []
    for th in head_th:
        header.append(th.string)
    punctuation = string.punctuation
    header = ["".join(c for c in s if c not in punctuation).lower().replace(' ','') for s in header]
   
    body = soup.find_all('tbody')
    tbody_tr = body[1]
    tbody_tr = tbody_tr.find_all('tr')
    data = []
    for tr in tbody_tr:
        values = []        
        tbody_td = tr.find_all('td')
        for td in tbody_td:
                values.append(td.span.contents)
        values = [val for sublist in values for val in sublist]
        if len(values) == 7:
            data.append(values)
    dataset = pd.DataFrame(data,columns=header)
    return dataset

def dataCleaning(df):
#   Basic data preprocessing such as data type conversion, handling missing values etc. 
#   Also converts the data into pandas dataframe.. 
    df.dropna()
    df['date'] = pd.to_datetime(df['date'])
    df = df.set_index('date', drop=False)
    df['open'] = df['open'].apply(lambda x: x.replace(',',''))
    df['high'] = df['high'].apply(lambda x: x.replace(',',''))
    df['low'] = df['low'].apply(lambda x: x.replace(',',''))
    df['close'] = df['close'].apply(lambda x: x.replace(',',''))
    df['adjclose'] = df['adjclose'].apply(lambda x: x.replace(',',''))
    df['volume'] = df['volume'].apply(lambda x: x.replace(',',''))
    df[['open','high','low','close','adjclose','volume']] =  df[['open','high','low','close','adjclose','volume']].astype(float)
    print(df.dtypes)
    return df
    

def pandasToMongo(df) :
#   Use this function to dump your data into mongodb. Dont forget to modify Settings.py..!!!
    collection = MongoClient(Settings.MONGO_CONNECTION_STRING)[Settings.DATABASE][
    Settings.COLLECTION]
    collection.insert_many(df.to_dict('records'))
    print(collection.find_one())
    
def plotting(ts):
    plt.plot(ts)
    rolmean = pd.rolling_mean(ts, window=12)
    rolstd = pd.rolling_std(ts, window=12)

    ts_log = np.log(ts)
    moving_avg = pd.rolling_mean(ts_log,12)
    #Plot rolling statistics:
    plt.figure(1)
    orig = plt.plot(ts, color='blue',label='Original')
    mean = plt.plot(rolmean, color='red', label='Rolling Mean')
    std = plt.plot(rolstd, color='black', label = 'Rolling Std')
    plt.legend(loc='best')
    plt.title('Rolling Mean & Standard Deviation')
      
    plt.figure(2)  
    red_trend = plt.plot(ts_log, color='green', label="Reduced Trend")
    red_mean = plt.plot(moving_avg, color='red')
    plt.legend(loc='best')

    
    plt.show(block=False)    
    
def checkForStationary(ts):
#   Perform Dickey-Fuller test:
#   This test allows you to check for null hypothesis.. basically to check if the series is stationary..!!!   
    print( 'Results of Dickey-Fuller Test:')
    dftest = adfuller(ts, autolag='AIC')
    dfoutput = pd.Series(dftest[0:4], index=['Test Statistic','p-value','#Lags Used','Number of Observations Used'])
    for key,value in dftest[4].items():
        dfoutput['Critical Value (%s)'%key] = value
    print(dfoutput)
    return dfoutput

def timeSeriesModel(ts):
#   I've used basic ARIMA Model.. 
#   To learn more check out https://en.wikipedia.org/wiki/Autoregressive_integrated_moving_average
    plt.figure(3)
    model = ARIMA(ts, order=(2, 1, 0))  
    results_AR = model.fit(disp=-1)  
    plt.plot(results_AR.fittedvalues, color='red',label="ARIMA Fit")
    plt.title('ARIMA')
    plt.legend(loc='best')

    predictions_ARIMA_diff = pd.Series(results_AR.fittedvalues, copy=True)
    print(predictions_ARIMA_diff.head())
    
    
def analysis(df):
#    I've started with volume column. I'm still figuring out what the other attributes are. .!!
    ts = df['volume']
    plotting(ts)
    dfoutput = checkForStationary(ts)
    ts_log = np.log(ts)
    dfoutput1 = checkForStationary(ts_log)
    if(dfoutput['p-value'] < dfoutput1['p-value']):
        timeSeriesModel(ts)
    else:
        timeSeriesModel(ts_log)
    
     
if __name__ == "__main__":
#    Initialize Google Chrome web driver to open a new window
    driver = init_driver()
    source = lookup(driver)
    if source is not None:
        dataset = parseSource(source)
    dataset = dataCleaning(dataset)
#    pandasToMongo(dataset)
    analysis(dataset) 