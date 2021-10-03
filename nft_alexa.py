# -*- coding: utf-8 -*-
"""
Find Alexa Rank of series in cryptoslam with web scraping
@author: HP
"""
from selenium import webdriver
import time
import requests
from bs4 import BeautifulSoup
from selenium.common.exceptions import ElementClickInterceptedException,NoSuchElementException,TimeoutException

from datetime import datetime, timedelta
import os 
import requests
import sys
from bs4 import BeautifulSoup
import re
import validators
import pandas as pd
import numpy as np

# Problem gathering data
def get_nft_web_pages(opensea_series):
    """
    Find homepages of 600 opensea NFT series
    Homepage links are given at opensea product pages for eg:
    https://opensea.io/collection/boredapeyachtclub one of the buttons at the top right of the
    page redirects to the offical webpage of boredapeyacthclub, which is required for alexa rank
    """
    webpages_list = list()
    options = webdriver.FirefoxOptions()
    # options.headless = True
    options.add_argument("--start-maximized")
    browser = webdriver.Firefox(options=options)
    for url in opensea_series["Serie_link"]:
        try:
            browser.get(url)
        except TimeoutException as e:
            print(e)
            time.sleep(5)
            browser.get(url)
        browser.maximize_window()     
        time.sleep(2)
        try:                                       
            element = browser.find_element_by_xpath("/html/body/div[1]/div[1]/main/div/div/div[1]/div[2]/div[2]/div[1]/div/div/a[2]")
            web_page = element.get_attribute("href")
            webpages_list.append(web_page)
        except NoSuchElementException:
            webpages_list.append("")
    
    browser.close()
    opensea_series["Serie_link"] = webpages_list
    opensea_series.to_excel("webpages_for_alexa.xlsx")

opensea_series = pd.read_excel("opensea_series.xlsx") # Süleyman provided this file
# If we have it, read it and carry on. If not, obtain links for webpages
try:
    webpages_for_alexa = pd.read_excel("webpages_for_alexa.xlsx")
except FileNotFoundError:
    get_nft_web_pages(opensea_series)
    webpages_for_alexa = pd.read_excel("webpages_for_alexa.xlsx")
     
true_alexa_ranks = list()

# Get Alexa Rank from alexa.com
for homepage in webpages_for_alexa["webpages"]:
    if isinstance(homepage , float):
        true_alexa_ranks.append("")

        continue
    alexa_base_url = 'https://alexa.com/siteinfo/'
    site_name = homepage
    site_name.lower()
    
    url_for_rank = alexa_base_url + site_name
    
    # Request formatted url for rank(s)
    page = requests.get(url_for_rank)
    soup = BeautifulSoup(page.content, 'html.parser')
    
    # get ranks text in a list
    country_ranks = soup.find_all('div', id='CountryRank')
    
    # select the data with class='rank-global' and the class='data'
    global_rank = soup.select('.rank-global .data')
    
    # Display Global rank safely
    try:
        match = re.search(r'[\d,]+', global_rank[0].text.strip())
        true_alexa_ranks.append(match.group())
    except:
        print("No global rank found for ", site_name)
        true_alexa_ranks.append("")

webpages_for_alexa["Alexa Rank"] = true_alexa_ranks 
webpages_for_alexa.to_excel("alexa_ranks.xlsx")       
        # Display country rank(s) Not needed for now
        # try:
        #     ranks_list = country_ranks[0].text.strip().split("\n")
        #     print("Country Rank: ")
        #     for rank in ranks_list:
        #         if re.search(r'#\d+', rank):
        #             print("\t",rank)
        # except:
        #     print("No country rank was found for ", site_name)
        #time.sleep(5)    
