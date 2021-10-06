# -*- coding: utf-8 -*-
"""
Created on Mon Jul 19 01:20:43 2021

@author: HP
"""
import pandas as pd
import numpy as np

df = pd.read_csv("final_df.csv")
result = pd.DataFrame()

for coin_id in  df["Coin_id"].unique(): 
    df_slice =df[ df["Coin_id"] == coin_id]
    #max_2 = df_slice['Participants_count'].nlargest(2) # Gives the highest 2 values
    df_slice_sorted = df_slice.sort_values(by='Participants_count', ascending=False)
    if df_slice_sorted['Offical'].isnull().values.all():    
        max2 = df_slice_sorted.iloc[0:2, :] # First place
    
    else:
        idx = df_slice_sorted['Offical'].argmax()
        official_channel = df_slice_sorted.iloc[idx]
        max2 = df_slice_sorted.iloc[0:2, :] # First place
        max2 = max2.append(official_channel)
        max2.drop_duplicates(subset=["Username"],keep='first', inplace=True)
    
    
    if len(result) == 0:
        result = max2    
    else:
    
        result = result.append(max2)
result.to_excel("telegram_result.xlsx")        
