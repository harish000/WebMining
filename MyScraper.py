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
 
def init_driver():
    driver = webdriver.Chrome("D:\Software\chromedriver_win32\chromedriver.exe") 
    driver.wait = WebDriverWait(driver, 5)
    return driver
 
 
def lookup(driver):
    driver.get("https://finance.yahoo.com/quote/CSCO/history?p=CSCO")
    try:
        for i in range(1,5):
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        source = driver.page_source
        print(type(source))
#        with open("source.html","wb") as f:
#            f.write(source.encode('utf8'))
        driver.quit()               
        return source        
    except TimeoutException:
        print("Box or Button not found in google.com")
        return None
 

def parseSource(filename):
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
#    print(len(df.index.values))
    return df
    
def pandasToMongo(df) :
    collection = MongoClient(Settings.MONGO_CONNECTION_STRING)[Settings.DATABASE][
    Settings.COLLECTION]
    collection.insert_many(df.to_dict('records'))
    print(collection.find_one())

def analysis(df):
    ts = df['volume']
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
    
    plt.show(block=False)

        
    #Perform Dickey-Fuller test:
    print( 'Results of Dickey-Fuller Test:')
    dftest = adfuller(ts, autolag='AIC')
    dfoutput = pd.Series(dftest[0:4], index=['Test Statistic','p-value','#Lags Used','Number of Observations Used'])
    for key,value in dftest[4].items():
        dfoutput['Critical Value (%s)'%key] = value
    print(dfoutput)
     
if __name__ == "__main__":
    driver = init_driver()
    source = lookup(driver)
    if source is not None:
        dataset = parseSource(source)
    dataset = dataCleaning(dataset)
#    pandasToMongo(dataset)
    analysis(dataset) 
#    time.sleep(5)
#    driver.quit()