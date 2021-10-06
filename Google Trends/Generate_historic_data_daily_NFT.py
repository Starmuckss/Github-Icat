# -*- coding: utf-8 -*-
"""
Created on Mon Jul 26 09:06:26 2021

@author: HP
"""

import requests
import pandas as pd
import pytrends
from pytrends.request import TrendReq
from pycoingecko import CoinGeckoAPI
from pytrends import exceptions

from datetime import datetime, timedelta
import time 
cg = CoinGeckoAPI()
from sklearn import preprocessing
from pytrends import dailydata
import os
pytrend  = TrendReq()
# pytrend = TrendReq(hl='en-GB', tz=360)

dir_path = os.path.dirname(os.path.realpath(__file__))
output_directory = dir_path+"\\google_trends_historical_data" # Data will be printed out here

data = list(pd.read_excel("opensea_series.xlsx")["Serie_name"]) # Süleyman provided this file

if not os.path.exists(output_directory): # create the folder if not exists already
    os.mkdir(output_directory)
    

for coin in data:
    if not os.path.exists(output_directory+"\\"+coin+".csv"):    
        try:
            start=time.time()    
            result = pd.DataFrame()
            keywords = [coin]
            try:
                data = dailydata.get_daily_data(coin, 2020, 12, 2021, 10, geo = '') # Select Year and Month  Must be kept updated
                                                                                    # Write the month we are currently in
            except KeyError:
                print("error on method "+ coin)
                continue 
            # Clean the data
            data.drop(labels=["isPartial",coin+"_monthly","scale",coin+"_unscaled"],axis=1,inplace = True) 
            data.index =  pd.to_datetime(data.index)
            data.index = data.index.strftime("%Y-%m-%d-%H:%M:%S")
            
            #Save it to the output folder
            data.to_csv(output_directory+"\\"+coin+".csv")
            end = time.time()
            print(coin,"is done,took ",end-start)
            
        

        except requests.exceptions.Timeout:
            print("timeout occured")
            
    
    else:
        print(coin,"already done")
       