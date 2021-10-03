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
from selenium.common.exceptions import ElementClickInterceptedException, StaleElementReferenceException,ElementNotInteractableException,NoSuchElementException
from datetime import datetime, timedelta
import os
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support.expected_conditions import staleness_of

dir_path = os.path.dirname(os.path.realpath(__file__))
output_directory = dir_path+"\\cryptoslam_sales" # Data will be printed out here

if not os.path.exists(output_directory): # create the folder if not exists already
    os.mkdir(output_directory)

def obtain_series_links(series_names):
    """
    Return crytoslam sales page of every serie
    """
    links = []
    for product in series_names[0]:
        product = product.lower()
        splitted = product.split()
        product = "-".join(splitted)
        series_link = "https://cryptoslam.io/" + product + "/sales" 
        links.append((product,series_link))
    return links

def get_transaction_time_from_etherscan(etherscan_links): # TAKES TOO MUCH TIME
    """
    Go to the transaction page for each transaction in the cryptoslam table,
    then get timestamp of the transaction there, very accurate, but slow
    """
    transaction_time_list = list()
    start = time.time()
    options = webdriver.FirefoxOptions()
    options.headless = True
    b = webdriver.Firefox(firefox_options=options)
    for link in etherscan_links:
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
    """
    Find the time from Sales column. If "25 days ago", subtract 25 days from now,
    and save it as a timestamp value. Accuracy declines if you go further back in time.
    """
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

def get_links_from_table():
    """
    Collect the data where we cant reach directly from table. 
    For ex: Seller address is written as 0x25f51d...081b5c as a string in table
    get_links_from_table takes the embedded data (real adress of the seller 0x25f51d434915902a895380fa5d6bf0ccef081b5c) and saves it in the table.
    """
    results_buyer = browser.find_elements_by_xpath("/html/body/div[2]/div/div[4]/div/div/div/div[3]/div[1]/div[3]/div/table/tbody/tr/td["+str(columns_len + 1)+"]/a")
    results_seller = browser.find_elements_by_xpath("/html/body/div[2]/div/div[4]/div/div/div/div[3]/div[1]/div[3]/div/table/tbody/tr/td["+str(columns_len)+"]/a")
    results_nft = browser.find_elements_by_xpath("/html/body/div[2]/div/div[4]/div/div/div/div[3]/div[1]/div[3]/div/table/tbody/tr/td[3]/a")
    results_etherscan_link = browser.find_elements_by_xpath("/html/body/div[2]/div/div[4]/div/div/div/div[3]/div[1]/div[3]/div/table/tbody/tr/td[2]/a")
    
    #results are FirefoxWebElement objects. We can get what we need from them.
    
    # Collect data from those columns.          
    buyer_data = list()
    seller_data = list()
    nft_data = list()
    etherscan_links = list()
    
    for result in results_etherscan_link:
        # The links for etherscan transaction sites are stored in href  
        link = result.get_attribute("href")
        etherscan_links.append(link)
        
    for result in results_seller:
        link = result.get_attribute("data-original-title")
        seller_data.append(link)
    
    for result in results_buyer:
        link = result.get_attribute("data-original-title")
        buyer_data.append(link)
    
    for result in results_nft:
        link = result.get_attribute("href")
        nft_data.append(link)        
    
    # Save the data collected to the table. 
    table["Sold"] = find_transaction_time(table["Sold"])
    table["Transaction_link"] = etherscan_links # etherscan data can be gathered later
    table["Seller"] = seller_data
    table["Buyer"] = buyer_data
    table["NFT_link"] = nft_data
    
    
series_names =  pandas.read_pickle("series_names.pkl") # Get series names (cryptopunks, art blocks etc.)
series_main_pages = obtain_series_links(series_names)

# Go to each series/sales page in the list.
for page in series_main_pages:  
    series_name = page[0]
    urlpage = page[1]
    if os.path.exists(output_directory+"\\cryptoslam_"+page[0]+".xlsx"): # If we have it dont collect it
        continue
    options = webdriver.FirefoxOptions() 
    # options.headless = True # Headless means no browser created visiually in your computer, I commented it to see how it works

    browser = webdriver.Firefox(options=options)
    browser.get(urlpage)
    browser.maximize_window() # Maximize to see  the whole table on the page
    
    table_list = [] # Whole data for pages will be contained in a list of tables
    start = time.time()
    
    # "//html/body/div[2]/div/div[4]/div/div/div/div[3]/div[1]/div[1]/div[1]/div/label/select" These type of references to
    # the web elements are Xpaths and can be obtained by ctrl+shift+I in the webpage. go on a object you wanna take,
    # right click, from "copy" select copy xpath
    
    # Click show 1000 elements on the table
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
    time.sleep(15) # Wait for the page to load
    
    # WebDriverWait(browser, 10).until(lambda d: d.find_elements_by_xpath('//*[@id="table"]')[0].is_displayed())
    # Webdriverwait can be used, it workes like wait until the page is loaded, it will speed up the code but i couldnt make it work
    while True: 
        # Get the whole table
        soup = BeautifulSoup(browser.page_source)
        soup_table = soup.find("table")
        tables = pandas.read_html(str(soup_table))
        table = tables[0]
        
        table = pandas.read_html(browser.page_source)[0]
        table = table[1:]

        # Some series have csv column at the end, i dropped it         
        if table.columns[-1] != "Buyer":
            table.drop(table.columns[-1],axis=1,inplace=True)
        
        columns_len = len(table.columns) 
        
        try:
            # Get some columns because they have data that we need to collect one by one 
            get_links_from_table()

        except StaleElementReferenceException as e: # Sometimes web page gives an error, so try the steps above again after waiting
            print(e)
            time.sleep(10)
            get_links_from_table()
        except ValueError as e:
            print(e)
            
        # Click to the next button to go to the next page    
        try:
            browser.find_element_by_xpath("/html/body/div[2]/div/div[4]/div/div/div/div[3]/div[1]/div[4]/div[2]/div/ul/li[3]/a").click()
        except ElementClickInterceptedException as e:
            browser.execute_script("window.scrollTo(0, document.body.scrollHeight);var lenOfPage=document.body.scrollHeight;return lenOfPage;")
    
            x_path = "/html/body/div[2]/div/div[4]/div/div/div/div[3]/div[1]/div[4]/div[2]/div/ul/li[3]/a"
            element = browser.find_element_by_xpath(x_path)
            browser.execute_script("arguments[0].click();", element)
        
        # Break condition for while loop: If the first transaction link of the last two tables 
        # have the same , break the table (Assuming different transactions have different transaction links)
        # Or the last table we collected has 0 length, break
        try: 
            t = table_list[-1].loc[0:1]["Transaction_link"]
            y = table_list[-2].loc[0:1]["Transaction_link"]
            if len(table) <= 1 or t.equals(y):
                break
        except IndexError:
            pass
        
            
        if "Unnamed: 0" in table.columns:
            table.drop(labels = ["Unnamed: 0"],axis=1,inplace=True)
        
        table_list.append(table)
        time.sleep(10)
        print(len(table))
        
    final_table = pandas.concat(table_list) # concat all the tables
    #Drop duplicates found in every column except timestamps
    cols = list(final_table)
    cols.remove('Sold')
    t = final_table.drop_duplicates(subset=cols,inplace=False)

    t.to_excel(output_directory+"\\cryptoslam_"+page[0]+".xlsx")
    browser.quit() # Kill browser
    
    end = time.time()
    print("historical data for " + series_name + " took " + str(end - start)+ " seconds")