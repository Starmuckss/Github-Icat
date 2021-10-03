# -*- coding: utf-8 -*-
"""
Created on Thu Aug 26 17:32:46 2021
take series names from main page of cryptoslam 
@author: HP
"""
from selenium import webdriver
from selenium.webdriver.support.ui import Select
import pandas
import time
from bs4 import BeautifulSoup
from selenium.common.exceptions import ElementClickInterceptedException
options = webdriver.FirefoxOptions()
# options.headless = True
browser = webdriver.Firefox(firefox_options=options)
urlpage = "https://cryptoslam.io/"
browser.get(urlpage)
# browser.find_element_by_xpath("//select[@name='element_name']/option[text()='option_text']").click()
start = time.time()
# ddelement= Select(browser.find_element_by_xpath('/html/body/div[2]/div/div[4]/div/div/div/div[3]/div[1]/div[1]/div[1]/div/label/select'))
# ddelement.select_by_visible_text("1000")
time.sleep(20)
soup = BeautifulSoup(browser.page_source)
soup_table = soup.find_all("table")[-1]
soup_table = soup.find("table")


tables = pandas.read_html(str(soup_table))
table = tables[0]

series_names = [] 
results = browser.find_elements_by_xpath("/html/body/div[3]/div/div[4]/div/div/div/div[1]/div/div[1]/div[2]/table/tbody/tr/td[2]")
for result in results:
    name = result.text
    series_names.append(name)

series_names_df = pandas.DataFrame(series_names)
series_names_df.to_pickle("series_names.pkl") 
