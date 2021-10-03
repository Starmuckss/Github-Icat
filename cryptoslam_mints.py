# -*- coding: utf-8 -*-
"""
Get historical information of a series from /mints. Eg: https://cryptoslam.io/cryptopunks/mints
@author: HP
"""
from selenium import webdriver
from selenium.webdriver.support.ui import Select
import pandas
import time
import requests
from bs4 import BeautifulSoup
from selenium.common.exceptions import ElementClickInterceptedException,StaleElementReferenceException,ElementNotInteractableException,NoSuchElementException
from datetime import datetime, timedelta
import os 

dir_path = os.path.dirname(os.path.realpath(__file__))
output_directory = dir_path+"\\cryptoslam_mints" # Data will be outputed here

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
    """
    obtain links of mint pages from series names.
    returns a list
    """
    links = []
    for product in series_names[0]:
        product = product.lower()
        splitted = product.split()
        product = "-".join(splitted)
        series_link = "https://cryptoslam.io/" + product + "/mints" 
        links.append((product,series_link))
    return links

series_names =  pandas.read_pickle("series_names.pkl") # Get series names (cryptopunks, art blocks etc.)
series_main_pages = obtain_series_links(series_names) # contains tuples [("art-blocks","https://cryptoslam.io/art-blocks/mints"),(,)...]
test = [('cryptopunks', 'https://cryptoslam.io/cryptopunks/mints')]

for page in test: 
    series_names = page[0]
    urlpage = page[1]
    
    # If we have it, skip
    if os.path.exists(str(output_directory+"\\cryptoslam_"+series_names+"_mints.xlsx")):
        continue
    
    options = webdriver.FirefoxOptions()
    # options.headless = True
    browser = webdriver.Firefox(options=options)
    
    browser.get(urlpage)
    # browser.find_element_by_xpath("//select[@name='element_name']/option[text()='option_text']").click()
    time.sleep(6)
    table_list = []
    start = time.time()
    
    # Get 1000 rows (only do it once per series)
    try:
        ddelement= Select(browser.find_element_by_xpath('/html/body/div[2]/div/div[4]/div/div/div/div[3]/div[1]/div[1]/div[1]/div/label/select'))
        ddelement.select_by_visible_text("1000")
    except ElementNotInteractableException as e:
        print(e)
        time.sleep(2)
        ddelement= Select(browser.find_element_by_xpath('/html/body/div[2]/div/div[4]/div/div/div/div[3]/div[1]/div[1]/div[1]/div/label/select'))
        ddelement.select_by_visible_text("1000")
    except NoSuchElementException as e:
        print(e)
        time.sleep(2)
        ddelement= Select(browser.find_element_by_xpath('/html/body/div[2]/div/div[4]/div/div/div/div[3]/div[1]/div[1]/div[1]/div/label/select'))
        ddelement.select_by_visible_text("1000")
    time.sleep(10) # wait for the page to load 1000 rows
    
    while True : # Keep until all the pages are scraped
        soup = BeautifulSoup(browser.page_source)
        
        
        soup_table = soup.find_all("table")[-1]
        soup_table = soup.find("table")
        
        
        tables = pandas.read_html(str(soup_table))
        table = tables[0]
        
        columns_len = len(table.columns) 
        
        results_original_owner = browser.find_elements_by_xpath("/html/body/div[2]/div/div[4]/div/div/div/div[3]/div[1]/div[3]/div/table/tbody/tr/td["+str(columns_len+1)+"]/a")
        results_nft = browser.find_elements_by_xpath("/html/body/div[2]/div/div[4]/div/div/div/div[3]/div[1]/div[3]/div/table/tbody/tr/td[3]/a")
        results_etherscan_link = browser.find_elements_by_xpath("/html/body/div[2]/div/div[4]/div/div/div/div[3]/div[1]/div[3]/div/table/tbody/tr/td[2]/a")

        
        original_owner_data = list()
        nft_data = list()
        etherscan_links = list()
        
        try:
        
            for result in results_etherscan_link:     
                link = result.get_attribute("href")
                etherscan_links.append(link)
                    
            for result in results_original_owner:
                product_link = result.get_attribute("data-original-title")
                original_owner_data.append(product_link)
            
            for result in results_nft:
                product_link = result.get_attribute("href")
                nft_data.append(product_link)        
            
        except StaleElementReferenceException as e:
            print(e)
            time.sleep(10)
            results_original_owner = browser.find_elements_by_xpath("/html/body/div[2]/div/div[4]/div/div/div/div[3]/div[1]/div[3]/div/table/tbody/tr/td["+str(columns_len+1)+"]/a")
            results_nft = browser.find_elements_by_xpath("/html/body/div[2]/div/div[4]/div/div/div/div[3]/div[1]/div[3]/div/table/tbody/tr/td[3]/a")
            results_etherscan_link = browser.find_elements_by_xpath("/html/body/div[2]/div/div[4]/div/div/div/div[3]/div[1]/div[3]/div/table/tbody/tr/td[2]/a")
            
            original_owner_data = list()
            nft_data = list()
            etherscan_links = list()
            
            for result in results_etherscan_link:     
                link = result.get_attribute("href")
                etherscan_links.append(link)
                    
            for result in results_original_owner:
                product_link = result.get_attribute("data-original-title")
                original_owner_data.append(product_link)
            
            for result in results_nft:
                product_link = result.get_attribute("href")
                nft_data.append(product_link)        
            

        table = pandas.read_html(browser.page_source)[0]
        table = table[1:]
        
        table["Original Owner"] = original_owner_data[1:]
        table["NFT_links"] = nft_data
        
        
        table["Minted_link"] = etherscan_links
        table["Minted"] = find_transaction_time(table["Minted"])
        
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
            t = table_list[-1].loc[0:1]["Minted_link"]
            y = table_list[-2].loc[0:1]["Minted_link"]
            if len(table) <= 1 or t.equals(y):
                break
        except IndexError:
            pass
        
        time.sleep(10)

        
    final_table = pandas.concat(table_list)
    cols = list(final_table)
    cols.remove('Minted')
    t = final_table.drop_duplicates(subset=cols,inplace=False)
    
    browser.quit()
    t.to_excel(output_directory+"\\cryptoslam_"+series_names+"_mints.xlsx")
    end = time.time()
    print(end - start)