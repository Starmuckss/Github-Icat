# -*- coding: utf-8 -*-
"""
SVI (Search Value Index) values RELATIVE with each other for NFT name searches in Google Trends API.
@author: HP
"""
import pandas as pd
import pytrends
from pytrends.request import TrendReq
from pycoingecko import CoinGeckoAPI
import numpy as np
# pytrend = TrendReq(hl='en-US', tz=360, timeout=(10,25), proxies=['https://34.203.233.13:80',], retries=2, backoff_factor=0.1, requests_args={'verify':False})
pytrend = TrendReq()
from datetime import datetime
import time 
cg = CoinGeckoAPI()
from sklearn import preprocessing

coin_limit = 20

def build_keyword_list():
    """
    Build a list of lists for relative svi
   [['Mutant Ape Yacht Club', 'Loot (for Adventurers)', 'Bored Ape Chemistry Club']
   ['Bored Ape Chemistry Club', 'Meebits', 'Art Blocks Factory']] is an example
   
   if t is a list, t's last element is the first element of (t+1)  
    """
    keyword_limit = 3 # How many keywords to search in one go, I went with 3, max is 5
    
    keyword_list = list()
    keywords = []
    
    iterator = coin_limit-1
    
    data = list(pd.read_excel("opensea_series.xlsx")["Serie_name"])
    
    while True:    
        for i in range(keyword_limit): 
            if iterator != -1:
                keywords.append(data[iterator])
                iterator -=1            
        if iterator ==-1:
            
            keyword_list.append(keywords)
            break
        keyword_list.append(keywords.copy())
        keywords.clear()
        iterator +=1    
    return keyword_list
        
def get_relative_svi_data():
    """
    Tüm NFTler kendi aralarında nasıl bir ilişki içinde buna bakıyor.
    """
    #Build keyword list
    keyword_list = build_keyword_list()
    all_keywords_data = pd.DataFrame()
    
    for keywords in keyword_list:
        # Find last 7 days search values for the 3 keyword given in keywords
        pytrend.build_payload(
        kw_list=keywords,
        timeframe='now 7-d',
        cat = 0
        ) # Finance : 7 Financial Markets : 1163 Default : 0
        next_data = pytrend.interest_over_time()
        next_data.drop(labels= ["isPartial"],axis=1,inplace=True)
        
        
        if len(all_keywords_data) == 0:
            all_keywords_data = next_data.copy()
        
        else:
            # My first idea is to use a scaling list. Match data date by date, not as a whole.
            # Each date is matched one by one.
            scaling_list=[]
            zipped_values = list(zip(all_keywords_data[all_keywords_data.columns[-1]],next_data[next_data.columns[0]]))
            
            for values in zipped_values:
                
                previous_data_point = values[0]
                next_data_point = values[1]
                # scale = whole_data's last column / next_data's first column not the whole dates, I do it date by date.
                try:
                    scale = previous_data_point / next_data_point
                
                # If there is a 0 in the data, we get an error and I don't know what to do here. 
                # when there is not enough search about a keyword, Trends returns 0
                # We can drop the 0's but I don't know what results would be
                
                # I made an assumption: SVI is an index, there is a 100 value representing
                # the top search given in a timeframe, and 1 the mininum search value.
                # 100 means at that time keyword is 100 times more searched than a 1 value.
                # And I assumed that if a value is 0, it is searched 0.0099 amount of times.
                
                # Yani eğer 0 sa, bugün SVI indeksi üstünden 0.0099 kere aratılmış gibi düşünüyorum. (1'den 0.001 düşük)
                
                except ZeroDivisionError: # Assumption here!!!!
                    scale = 0.0099
                scaling_list.append(scale)
            # Find scaled and put it into the dataframe
            scaled_data = next_data.mul(scaling_list,axis='rows')
            all_keywords_data = pd.concat(objs=[all_keywords_data,scaled_data[scaled_data.columns[1:]]],axis=1)
    
    return all_keywords_data

final_result = get_relative_svi_data()
    
