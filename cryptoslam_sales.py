# -*- coding: utf-8 -*-
"""
Created on Tue Aug 24 18:16:21 2021
Sales data is gathered in this script.
@author: HP
"""
from selenium import webdriver
from selenium.webdriver.support.ui import Select
import pandas
import time
from bs4 import BeautifulSoup
from selenium.common.exceptions import ElementClickInterceptedException, StaleElementReferenceException,ElementNotInteractableException
from datetime import datetime, timedelta
import os
import requests
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.expected_conditions import staleness_of

dir_path = os.path.dirname(os.path.realpath(__file__))
output_directory = dir_path+"\\cryptoslam_sales" # Data will be printed out here

if not os.path.exists(output_directory): # create the folder if not exists already
    os.mkdir(output_directory)


# https://cryptoslam.io/cryptopunks/marketplace buraya da bak
# product sayfasından top market buyers ı al
def obtain_series_links(series_names):
    links = []
    for product in series_names[0]:
        product = product.lower()
        splitted = product.split()
        product = "-".join(splitted)
        series_link = "https://cryptoslam.io/" + product + "/sales" 
        links.append((product,series_link))
    return links

def get_transaction_time_from_etherscan(etherscan_links):
    transaction_time_list = list()
    for link in etherscan_links:
        start = time.time()
        options = webdriver.FirefoxOptions()
        options.headless = True
        b = webdriver.Firefox(firefox_options=options)

        # b = webdriver.Firefox()
        b.get(link)
        
        time.sleep(3)
        if "etherscan" in link:
            transaction_time = b.find_element_by_xpath("/html/body/div[1]/main/div[3]/div[1]/div[2]/div[1]/div/div[4]/div/div[2]/i")
            transaction_time_list.append(transaction_time)
        elif "roninchain" in link:
            transaction_time = b.find_element_by_xpath("/html/body/div[1]/div/main/div[2]/div/div[1]/div[4]/div[2]/span[2]").text
            transaction_time_list.append(transaction_time)
        
        end = time.time()
        print("one request took "+ str(end - start) + " seconds")
    return transaction_time_list
    
def find_transaction_time(table_time_column): # NOT ACCURATE
    now = datetime.today()
    dates = ["second","minute","hour","day","month","year"]
    timestamps = []
    for cell in table_time_column:
        splitted = cell.split(" ")
        integer_time_value = int(splitted[0]) 
        date = splitted[1]
        if "second" in cell:
            d = datetime.today() - timedelta(seconds=integer_time_value)
        elif "minute" in cell:
            d = datetime.today() - timedelta(minutes=integer_time_value)
        elif "hour" in cell:
            d = datetime.today() - timedelta(hours=integer_time_value)
        elif "day" in cell:
            d =datetime.today() - timedelta(days=integer_time_value)
        elif "month" in cell:
            d =datetime.today() - timedelta(days=30*integer_time_value)
        elif "year" in cell:
            d =datetime.today() - timedelta(days=360*integer_time_value)
        timestamps.append(d)
    return timestamps    

series_names =  pandas.read_pickle("series_names.pkl") # Get series names (cryptopunks, art blocks etc.)
series_main_pages = obtain_series_links(series_names)

for page in series_main_pages: #
    series_name = page[0]
    urlpage = page[1]
    if os.path.exists(output_directory+"\\cryptoslam_"+page[0]+".xlsx"):
        continue
    options = webdriver.FirefoxOptions()
    # options.headless = True
    options.add_argument("--start-maximized")

    browser = webdriver.Firefox(options=options)
    browser.get(urlpage)
    browser.maximize_window() 
    
    # browser.find_element_by_xpath("//select[@name='element_name']/option[text()='option_text']").click()
    table_list = []
    start = time.time()
    try:
        ddelement= Select(browser.find_element_by_xpath('/html/body/div[2]/div/div[4]/div/div/div/div[3]/div[1]/div[1]/div[1]/div/label/select'))
        ddelement.select_by_visible_text("1000")
    except ElementNotInteractableException as e:
        print(e)
        time.sleep(2)
        ddelement= Select(browser.find_element_by_xpath('/html/body/div[2]/div/div[4]/div/div/div/div[3]/div[1]/div[1]/div[1]/div/label/select'))
        ddelement.select_by_visible_text("1000")
    time.sleep(15)
    
    while True: 
        
        # WebDriverWait(browser, 10).until(lambda d: d.find_elements_by_xpath('//*[@id="table"]')[0].is_displayed())

        soup = BeautifulSoup(browser.page_source)
        soup_table = soup.find("table")
        
        tables = pandas.read_html(str(soup_table))
        table = tables[0]
        
        #Cektigin anın zamanini değişken olarak tanimlayip kaç dakika önce olduğu bilgisini çıkararak daha kolay yapabilirsin
                
        # column length helps us to find the seller and buyer column
        columns_len = len(table.columns) 
        
        table = pandas.read_html(browser.page_source)[0]
        table = table[1:]
        
        try:
            results_buyer = browser.find_elements_by_xpath("/html/body/div[2]/div/div[4]/div/div/div/div[3]/div[1]/div[3]/div/table/tbody/tr/td["+str(columns_len + 1)+"]/a")
            results_seller = browser.find_elements_by_xpath("/html/body/div[2]/div/div[4]/div/div/div/div[3]/div[1]/div[3]/div/table/tbody/tr/td["+str(columns_len)+"]/a")
            results_nft = browser.find_elements_by_xpath("/html/body/div[2]/div/div[4]/div/div/div/div[3]/div[1]/div[3]/div/table/tbody/tr/td[3]/a")
            results_etherscan_link = browser.find_elements_by_xpath("/html/body/div[2]/div/div[4]/div/div/div/div[3]/div[1]/div[3]/div/table/tbody/tr/td[2]/a")
        
            buyer_data = list()
            seller_data = list()
            nft_data = list()
            etherscan_links = list()
            
            for result in results_etherscan_link:
                product_link = result.get_attribute("href")
                etherscan_links.append(product_link)
                
            for result in results_seller:
                product_link = result.get_attribute("data-original-title")
                seller_data.append(product_link)
            
            for result in results_buyer:
                product_link = result.get_attribute("data-original-title")
                buyer_data.append(product_link)
            
            for result in results_nft:
                product_link = result.get_attribute("href")
                nft_data.append(product_link)        
                
            table["Sold"] = etherscan_links # etherscan data can be gathered later
            table["Seller"] = seller_data
            table["Buyer"] = buyer_data
            table["NFT_link"] = nft_data

        except StaleElementReferenceException as e:
            print(e)
            time.sleep(10)
            results_buyer = browser.find_elements_by_xpath("/html/body/div[2]/div/div[4]/div/div/div/div[3]/div[1]/div[3]/div/table/tbody/tr/td["+str(columns_len + 1)+"]/a")
            results_seller = browser.find_elements_by_xpath("/html/body/div[2]/div/div[4]/div/div/div/div[3]/div[1]/div[3]/div/table/tbody/tr/td["+str(columns_len)+"]/a")
            results_nft = browser.find_elements_by_xpath("/html/body/div[2]/div/div[4]/div/div/div/div[3]/div[1]/div[3]/div/table/tbody/tr/td[3]/a")
            results_etherscan_link = browser.find_elements_by_xpath("/html/body/div[2]/div/div[4]/div/div/div/div[3]/div[1]/div[3]/div/table/tbody/tr/td[2]/a")

            buyer_data = list()
            seller_data = list()
            nft_data = list()
            etherscan_links = list()
            
            for result in results_etherscan_link:
                product_link = result.get_attribute("href")
                etherscan_links.append(product_link)
                
            for result in results_seller:
                product_link = result.get_attribute("data-original-title")
                seller_data.append(product_link)
            
            for result in results_buyer:
                product_link = result.get_attribute("data-original-title")
                buyer_data.append(product_link)
            
            for result in results_nft:
                product_link = result.get_attribute("href")
                nft_data.append(product_link)        
                
            table["Sold"] = etherscan_links # etherscan data can be gathered later
            table["Seller"] = seller_data
            table["Buyer"] = buyer_data
            table["NFT_link"] = nft_data
        except ValueError as e:
            print(e)
            
            
        try:
            browser.find_element_by_xpath("/html/body/div[2]/div/div[4]/div/div/div/div[3]/div[1]/div[4]/div[2]/div/ul/li[3]/a").click()
        except ElementClickInterceptedException as e:
            browser.execute_script("window.scrollTo(0, document.body.scrollHeight);var lenOfPage=document.body.scrollHeight;return lenOfPage;")
    
            x_path = "/html/body/div[2]/div/div[4]/div/div/div/div[3]/div[1]/div[4]/div[2]/div/ul/li[3]/a"
            element = browser.find_element_by_xpath(x_path)
            browser.execute_script("arguments[0].click();", element)
        
        try:
            t = table_list[-1].loc[0:1]
            y = table_list[-2].loc[0:1]
            if len(table) == 0 or t.equals(y):
                break
        except IndexError:
            pass
        
            
        if "Unnamed: 0" in table.columns:
            table.drop(labels = ["Unnamed: 0"],axis=1,inplace=True)
        
        table_list.append(table)
        time.sleep(10)
        print(len(table))
        
    final_table = pandas.concat(table_list)
    final_table.drop_duplicates(inplace=True)
    final_table.to_excel(output_directory+"\\cryptoslam_"+page[0]+".xlsx")
    # browser.quit()
    end = time.time()
    print(end - start)