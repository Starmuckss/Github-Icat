from telethon import TelegramClient
from telethon.sync import TelegramClient
from telethon.tl.functions.channels import GetFullChannelRequest
from telethon import functions, types
import pandas as pd
from collections import defaultdict
from datetime import datetime, timedelta
from telethon import errors
import numpy as np
#Login to API
api_id = 6303180
api_hash = '92eea81aec875d961c115365ed89df99'
phone = "+905079158056"
username = "Sefa Yapıcı"

client = TelegramClient(username, api_id, api_hash)
client.start()
print("Client Created")

if not client.is_user_authorized():
    client.send_code_request(phone)
    try:
        client.sign_in(phone, input('Enter the code: '))
    except SessionPasswordNeededError:
        client.sign_in(password=input('Password: '))

async def main():    
    telegram_data = pd.read_excel("telegram_result.xlsx")
    chat_ids = telegram_data["id"]
    all_coins_message_count_in_6_hours = []
    all_coins_views_in_6_hours = []
    for id in chat_ids:
        messages_in_6_hours = [] 
        views_in_6_hours = [] # iterate
        channel_entity= await client.get_entity(id)
        messages = await client.get_messages(channel_entity, limit= 60,offset_date = datetime.now(),wait_time = 1) # think about the limit
        
        for msg in messages:
        	#print(msg)
        	timezone = msg.date.tzinfo

        	if msg.date > (datetime.now(timezone) -  timedelta(hours=6)):
        		messages_in_6_hours.append(msg)
        		views_in_6_hours.append(msg.views)
        		
        all_coins_message_count_in_6_hours.append(len(messages_in_6_hours))
        try:
        	all_coins_views_in_6_hours.append(sum(views_in_6_hours)/len(messages_in_6_hours))
        except ZeroDivisionError:
        	all_coins_views_in_6_hours.append(0)
        except TypeError:
        	all_coins_views_in_6_hours.append(np.nan)
        #print(messages_in_6_hours,views_in_6_hours)
    telegram_data["messages(6H)"] = all_coins_message_count_in_6_hours
    telegram_data["messages_viewed(6H)"] = all_coins_views_in_6_hours
    telegram_data.to_excel("telegram_data_with_messages.xlsx")
    print("done")

with client:
    client.loop.run_until_complete(main())
