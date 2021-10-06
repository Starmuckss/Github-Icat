# -*- coding: utf-8 -*-
"""
Update historical data, can be run daily or every 12 hours, its your choice
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
input_output_directory = dir_path+"\\google_trends_historical_data" # Data will be printed out here

# For each historical data we have at hand
for file in os.listdir(input_output_directory):
    if file.endswith(".csv"):
        # Read historical data
        historical_data_path = os.path.join(input_output_directory, file)
        historical_data = pd.read_csv(historical_data_path)
        try:
            historical_data.drop("Unnamed: 0",axis =1 , inplace = True)
        except KeyError:
            pass
        
        historical_data.date =  pd.to_datetime(historical_data.date)
        # historical_data.date = historical_data.date.strftime("%Y-%m-%d-%H:%M:%S") error!
        
        NFT_name =  historical_data.columns[-1]
        
        # Last date and its SVI 
        last_date = historical_data.loc[len(historical_data)-1].date.strftime("%Y-%m-%d")
        last_SVI = historical_data.loc[len(historical_data)-1][NFT_name]

        # Today         
        
        now = datetime.now()
        
        current_time = now.strftime("%Y-%m-%d")
        
        # Find the latest SVI between the last date from historical data and now
        try:
            # Give timeframe as 2021-09-30 2021-10-6 YYYY-MM-DD YYYY-MM-DD    
            # T0's are added to get hourly data
            pytrend.build_payload(
            kw_list=[NFT_name],
            timeframe= last_date + 'T0 ' +  current_time + "T0",
            cat = 0
            ) # Finance : 7 Financial Markets : 1163 Default : 0
            fresh_data = pytrend.interest_over_time()
            fresh_data.drop("isPartial",axis=1,inplace=True)
        except:
            continue
        
        try:
            fresh_data.reset_index(inplace  = True)
        except ValueError:
            pass
        fresh_data.date =  pd.to_datetime(fresh_data.date)       
        # Get the latest SVI and match it with the latest historical data
        # Then Add the scaled version of new data to the historical data, update it.
        if last_SVI != 0:
            
            new_data = fresh_data.loc[last_date:]
            scale = last_SVI / new_data[NFT_name].iloc[0]
            scaled_new_data =  new_data[NFT_name] * scale 
            new_data[NFT_name] =  scaled_new_data  
            updated_historical_data = historical_data.append(scaled_new_data[1:])
            updated_historical_data.to_csv(historical_data_path)
        
        else:
            new_data = fresh_data.loc[last_date:]
            scale = 0.0099 # ASSUMPTION
            scaled_new_data =  new_data[NFT_name] * scale 
            new_data[NFT_name] =  scaled_new_data
            updated_historical_data = historical_data.append(new_data[1:])
            updated_historical_data.to_csv(historical_data_path)