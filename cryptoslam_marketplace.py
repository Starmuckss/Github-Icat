# -*- coding: utf-8 -*-
"""
Created on Thu Aug 26 09:47:22 2021

@author: HP
"""
from selenium import webdriver
from selenium.webdriver.support.ui import Select
import pandas
import time
import requests
from bs4 import BeautifulSoup
from selenium.common.exceptions import ElementClickInterceptedException
from datetime import datetime, timedelta
import os 
from selenium.webdriver.support import expected_conditions as EC

from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys

dir_path = os.path.dirname(os.path.realpath(__file__))
output_directory = dir_path+"\\cryptoslam_marketplace" # Data will be printed out here
if not os.path.exists(output_directory): # create the folder if not exists already
    os.mkdir(output_directory)


def get_transaction_time_from_etherscan(etherscan_links):
    transaction_time_list = list()
    for link in etherscan_links:
        start = time.time()
        
        browser = webdriver.Firefox()
        browser.get(link)
        time.sleep(1)

        transaction_time = browser.find_element_by_xpath("/html/body/div[1]/main/div[3]/div[1]/div[2]/div[1]/div/div[4]/div/div[2]/i")
        transaction_time_list.append(transaction_time)
        end = time.time()
        print("one request took "+ str(end - start) + " seconds")
    
    return transaction_time_list    

def find_transaction_time(table_time_column): # NOT ACCURATE
    now = datetime.today()
    dates = ["minute","hour","day","month","year"]
    timestamps = []
    for cell in table_time_column:
        splitted = cell.split(" ")
        integer_time_value = int(splitted[0]) 
        date = splitted[1]
        if "second" in cell:
            d = datetime.today() - timedelta(seconds=integer_time_value)
        if "minute" in cell:
            d =datetime.today() - timedelta(minutes=integer_time_value)
        elif "hour" in cell:
            d =datetime.today() - timedelta(hours=integer_time_value)
        elif "day" in cell:
            d =datetime.today() - timedelta(days=integer_time_value)
        elif "month" in cell:
            d =datetime.today() - timedelta(days=30*integer_time_value)
        elif "year" in cell:
            d =datetime.today() - timedelta(days=360*integer_time_value)
        timestamps.append(d)
    return timestamps    
def obtain_series_links(series_names):
    links = []
    for product in series_names[0]:
        product = product.lower()
        splitted = product.split()
        product = "-".join(splitted)
        series_link = "https://cryptoslam.io/" + product + "/marketplace" 
        links.append((product,series_link))
    return links

def get_links_from_table():
    results_nft = browser.find_elements_by_xpath("/html/body/div[2]/div/div[4]/div/div/div/div[3]/div[1]/div[3]/div/table/tbody/tr/td[4]/a")
    results_owner = browser.find_elements_by_xpath("/html/body/div[2]/div/div[4]/div/div/div/div[3]/div[1]/div[3]/div/table/tbody/tr/td["+str(owner_data_index+2)+"]/a")
    results_etherscan_link = browser.find_elements_by_xpath("/html/body/div[2]/div/div[4]/div/div/div/div[3]/div[1]/div[3]/div/table/tbody/tr/td[2]/a")
    
    owner_data = list()
    nft_data = list()
    etherscan_links = list()
    
    for result in results_etherscan_link:
        link = result.get_attribute("href")
        if link is None:
            link = ""
        etherscan_links.append(link)
    for result in results_owner:
        address = result.get_attribute("data-original-title")
        if address is None :
            address = ""
        owner_data.append(address)
    for result in results_nft:
        link = result.get_attribute("href")
        if link is None:
            link = ""
        nft_data.append(link)           
    
    return (etherscan_links,nft_data,owner_data)
        
series_names =  pandas.read_pickle("series_names.pkl") # Get series names (cryptopunks, art blocks etc.)
series_main_pages = obtain_series_links(series_names)

for page in series_main_pages:
    count = 0
    # If we have it don't bother getting it again
    
    series_names = page[0]
    urlpage = page[1]
    
    options = webdriver.FirefoxOptions()
    
    #Headless is problematic
    # options.headless = True
    browser = webdriver.Firefox(options=options)
    browser.get(urlpage)    
    time.sleep(5)
    
    browser.maximize_window() 
    table_list = []
    start = time.time()
    ddelement= Select(browser.find_element_by_xpath('/html/body/div[2]/div/div[4]/div/div/div/div[3]/div[1]/div[1]/div[1]/div/label/select'))
    ddelement.select_by_visible_text("1000")
    
        
    #I'm sure this will be interchangeable with the Chrome driver too
    
    #Set the focus to the browser rather than the web content
    browser.set_context("chrome")
    #Create a var of the window
    win = browser.find_element_by_tag_name("body")
    
    #Send the key combination to the window itself rather than the web content to zoom out
    #(change the "-" to "+" if you want to zoom in)
    for i in range(5):
        win.send_keys(Keys.CONTROL + "-")
        
    #Set the focus back to content to re-engage with page elements
    browser.set_context("content")    
    
    time.sleep(15)
    while True: 
        start = time.time()

        soup = BeautifulSoup(browser.page_source)
        
        
        soup_table = soup.find_all("table")[-1]
        soup_table = soup.find("table")
        
        
        tables = pandas.read_html(str(soup_table))
        table = tables[0]
        
        #Cektigin anın zamanini değişken olarak tanimlayip kaç dakika önce olduğu bilgisini çıkararak daha kolay yapabilirsin
        columns_len = len(table.columns) 
        owner_data_index = list(table.columns).index("Owner")
        
        
        try:
            links_and_adresses = get_links_from_table()
            etherscan_links = links_and_adresses[0]
            nft_data = links_and_adresses[1]
            owner_data = links_and_adresses[2]
            
            
        except Exception as e: # StaleElementReferenceException 
            print(e)
            time.sleep(5)
            links_and_adresses = get_links_from_table()
            etherscan_links = links_and_adresses[0]
            nft_data = links_and_adresses[1]
            owner_data = links_and_adresses[2]
         
        table = pandas.read_html(browser.page_source)[0]
        table = table[1:]
        
        table["Owner"] = owner_data
        table["NFT_links"] = nft_data
        table["Listed"] = etherscan_links
        
        # table["Minted"] = time_as_timestamps
        if "Unnamed: 0" in table.columns:
            table.drop(labels = ["Unnamed: 0"],axis=1,inplace=True)
        
        table_list.append(table)
        browser.execute_script("window.scrollTo(0, document.body.scrollHeight);var lenOfPage=document.body.scrollHeight;return lenOfPage;")
    
        try:
            browser.find_element_by_xpath("/html/body/div[2]/div/div[4]/div/div/div/div[3]/div[1]/div[4]/div[2]/div/ul/li[3]/a").click()
        except ElementClickInterceptedException as e:
            #print(e)
            x_path = "/html/body/div[2]/div/div[4]/div/div/div/div[3]/div[1]/div[4]/div[2]/div/ul/li[3]/a"
            # browser.find_element_by_xpath(x_path).click()
            element = browser.find_element_by_xpath(x_path)
            browser.execute_script("arguments[0].click();", element)
        
         
        try:
            t = table_list[-1].loc[0:1]
            y = table_list[-2].loc[0:1]
            if len(table) == 0 or t.equals(y):
                break
        except IndexError:
            pass
        
        time.sleep(10)
        count +=1
        print("table count "+ str(count))
        end = time.time()
        print(end-start)
    final_table = pandas.concat(table_list)
    final_table.drop_duplicates(inplace=True)
    final_table.to_excel(output_directory+"\\cryptoslam_"+series_names+"marketplace.xlsx")
    end = time.time()
    # browser.quit() 
    print(end - start)