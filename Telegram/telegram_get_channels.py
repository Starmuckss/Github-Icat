# -*- coding: utf-8 -*-
"""
Created on Sun Jul  4 11:25:00 2021
DOES NOT WORK IN ANACONDA, I opened a virtual environment for this.

@author: HP
"""
from telethon import TelegramClient
from telethon.sync import TelegramClient
from telethon.tl.functions.channels import GetFullChannelRequest
from telethon import functions, types
import pandas as pd
from collections import defaultdict
from datetime import datetime
from pycoingecko import CoinGeckoAPI
import time
import numpy as np

def get_coingecko_telegram_data():
    """
    Get the telegram username data from coingecko
    """
    gecko_telegram_data = list()
    for coin_id in top200_id:
        try:
            gecko_telegram_data.append((coin_id,cg.get_coin_by_id(coin_id)["links"]["telegram_channel_identifier"]))
        except:
            time.sleep(90)
            gecko_telegram_data.append((coin_id,cg.get_coin_by_id(coin_id)["links"]["telegram_channel_identifier"]))
    gecko_telegram_df = pd.DataFrame(gecko_telegram_data,columns = ["coin_id","telegram_channel_identifier"])

    gecko_telegram_df.to_csv("coingecko_telegram_data.csv")   

cg = CoinGeckoAPI()

# Get top 200 coins names and ids
top200_id = list(pd.DataFrame(cg.get_coins_markets('usd', per_page = 200)).id)
top200_coin_names =  list(pd.DataFrame(cg.get_coins_markets('usd', per_page = 200)).name)
top200_coins = list(zip(top200_id, top200_coin_names)) #top200_coins = [(coin_id,coin_name),(coin_id2,coin_name2)...]

 # Get coingecko data from memory, If you dont have it, pull it from coingecko with get_coingecko_telegram_data
try:
    gecko_telegram_data = pd.read_csv("coingecko_telegram_data.csv")
except FileNotFoundError:
    get_coingecko_telegram_data()
    gecko_telegram_data = pd.read_csv("coingecko_telegram_data.csv")

# Enter Api with these:
# You need to get your own cridentials for accesing Telegram Api
api_id = 6303180
api_hash = '92eea81aec875d961c115365ed89df99'
phone = "+905079158056"
username = "Sefa Yapıcı"

#Start Client
client = TelegramClient(username, api_id, api_hash)
client.start()
print("Client Created")

dict_of_coins = defaultdict(list)
data = defaultdict(list)

# Authorization for accessing api
if not client.is_user_authorized():
    #If not already authorized (for ex: entering first time), Telegram will send a code to the phone
    client.send_code_request(phone)
    try:
        client.sign_in(phone, input('Enter the code: '))
    except SessionPasswordNeededError:
        client.sign_in(password=input('Password: '))

async def main():    
    for coin in top200_coins:
        coin_id = coin[0]
        coin_name = coin[1]
        #Search in telegram for the coin_name
        result = await client(functions.contacts.SearchRequest(
            q=coin_name,
            limit=50
        ))
        for chat in result.chats:
            #print(chat.stringify())
            data["Coin_name"].append(coin_name) 
            data["Coin_id"].append(coin_id)
            data["Username"].append(chat.username)
            data["Channel_name"].append(chat.title)
            data["id"].append(chat.id)
            data["Participants_count"].append(chat.participants_count)
            data["Offical"] = np.nan

            data["Timestamp"].append(datetime.now())

    try:
        gecko_telegram_data = pd.read_csv("coingecko_telegram_data_updated_with_id.csv")   
    except FileNotFoundError:
        gecko_telegram_data = pd.read_csv("coingecko_telegram_data.csv")

    # Get the channel_id with channel username. We will do this for one time.
    if 'channel_id' not in gecko_telegram_data.columns: 
        id_list = list()
        for identifier in gecko_telegram_data["telegram_channel_identifier"]:
            try:
                if not pd.isna(identifier):
                    print(identifier)

                    channel_entity= await client.get_entity(identifier) # USE get_input_entity INSTEAD
                    id_list.append(channel_entity.id) 
                else:
                    id_list.append(np.nan)
            except ValueError:
                continue
            
            time.sleep(1)
        
        gecko_telegram_data["channel_id"] = id_list
        gecko_telegram_data.to_csv("coingecko_telegram_data_updated_with_id.csv")   

    gecko_telegram_data_updated = pd.read_csv("coingecko_telegram_data_updated_with_id.csv")   
    gecko_data = defaultdict(list)
    
    for row in gecko_telegram_data_updated.iterrows():
        channel_id = row[1]["channel_id"]         
        coin_id = row[1]["coin_id"]
        
        if not pd.isna(channel_id):
            channel_connect = await client.get_entity(int(channel_id))
            channel_full_info = await client(GetFullChannelRequest(channel=channel_connect))
            
            gecko_data["Coin_id"].append(coin_id)
            gecko_data["Username"].append(channel_connect.username)
            gecko_data["Channel_name"].append(channel_connect.title)
            gecko_data["id"].append(channel_id)
            gecko_data["Participants_count"].append(channel_full_info.full_chat.participants_count)
            gecko_data["Offical"] = True

            gecko_data["Timestamp"].append(datetime.now())
        else:
            continue      
    search_df = pd.DataFrame(data = data)
    gecko_df = pd.DataFrame(data = gecko_data)

    #merged = search_df.merge(gecko_df, how='outer', on='Username')    
    final_df = search_df.append(gecko_df)
    final_df.to_csv("final_df.csv")
with client:
    client.loop.run_until_complete(main())