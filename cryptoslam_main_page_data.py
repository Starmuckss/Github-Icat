# -*- coding: utf-8 -*-
"""
Created on Mon Aug 30 17:48:44 2021

@author: HP
"""
from selenium import webdriver
from selenium.webdriver.support.ui import Select
import pandas
import time
from bs4 import BeautifulSoup
from selenium.common.exceptions import ElementClickInterceptedException, StaleElementReferenceException
from datetime import datetime, timedelta
import os
import requests

dir_path = os.path.dirname(os.path.realpath(__file__))
output_directory = dir_path+"\\cryptoslam_main_pages" # Data will be printed out here

if not os.path.exists(output_directory): # create the folder if not exists already
    os.mkdir(output_directory)

def contains(list_1,list_2):
    """
    Check if list_1 elements is in list_2
    """
    boolean = True
    for item in list_1:
        if item not in list_2:
            boolean = False
    return boolean    
# https://cryptoslam.io/cryptopunks/marketplace buraya da bak
# product sayfasından top market buyers ı al
def obtain_series_links(series_names):
    links = []
    for product in series_names[0]:
        product = product.lower()
        splitted = product.split()
        product = "-".join(splitted)
        series_link = "https://cryptoslam.io/" + product  
        links.append((product,series_link))
    return links

series_names =  pandas.read_pickle("series_names.pkl") # Get series names (cryptopunks, art blocks etc.)
series_main_pages = obtain_series_links(series_names)
options = webdriver.FirefoxOptions()
# options.headless = True
options.add_argument("--start-maximized")

browser = webdriver.Firefox(options=options)
for page in series_main_pages:
    series_name = page[0]
    if os.path.exists(output_directory+"\\cryptoslam_"+page[0]+".xlsx"):
        continue
    
    urlpage = page[1]

   
    browser.get(urlpage)
    browser.maximize_window() 
    time.sleep(10)

    try:
        browser.find_element_by_xpath("/html/body/div[3]/div[1]/div[1]").click()
    except :
        pass
    time.sleep(10)
    
    soup = BeautifulSoup(browser.page_source)
    soup_table = soup.find_all("table")
    tables = pandas.read_html(str(soup_table))
        
    for table in tables:
        if contains(["Buyer","Amount","USD"],table.columns) :
            top_buyers_table = table 
        elif contains(["Seller","Amount","USD"],table.columns):
            top_sellers_table = table 
    
    # Get the tables of top buyers and sellers
    result_buyers =browser.find_elements_by_xpath("/html/body/div[2]/div/div[4]/div/div[2]/div[2]/div[3]/div[1]/div/div[3]/div/div[2]/div/table/tbody/tr/td[1]/a")
    result_sellers =browser.find_elements_by_xpath("/html/body/div[2]/div/div[4]/div/div[2]/div[2]/div[3]/div[2]/div/div[3]/div/div[2]/div/table/tbody/tr/td[1]/a")
    
    # Sometimes the pages loads partially, and I cant gather top seller and buyer data,
    # If i cant gather data, I reload the page. try this until we gather the tables, or we tried atleast 5 times
    try_refreshing = 0
    while len(result_buyers) == 0:
       
        browser.refresh()
        time.sleep(5)
        result_buyers =browser.find_elements_by_xpath("/html/body/div[2]/div/div[4]/div/div[2]/div[2]/div[4]/div/div[3]/div/div[2]/div/table/tbody/tr/td[1]")
        result_sellers =browser.find_elements_by_xpath("/html/body/div[2]/div/div[4]/div/div[2]/div[2]/div[5]/div/div[3]/div/div[2]/div/table/tbody/tr/td[1]/a")
        try_refreshing +=1
        if try_refreshing == 5:
            break
        
    buyer_data= list()
    seller_data = list()
    
    # Gather buyer and seller addresses
    for result in result_buyers:
        address = result.get_attribute("data-original-title")
        buyer_data.append(address) 
        
    for result in result_sellers:
        address = result.get_attribute("data-original-title")
        seller_data.append(address) 
        
    try:
        top_buyers_table["Buyer"] = buyer_data
        top_sellers_table["Seller"] = seller_data    
        print(series_name,"gathered")
        
    except ValueError:
        print(series_name,"failed to gather")
        continue
    
    if len(top_buyers_table) == 0:
        print(series_name)

    top_buyers_table.to_excel(output_directory+"\\cryptoslam_"+page[0]+"_top_buyers.xlsx")
    top_sellers_table.to_excel(output_directory+"\\cryptoslam_"+page[0]+"_top_sellers.xlsx")
    browser.quit() # Kill the browser