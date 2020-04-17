from selenium import webdriver
from bs4 import BeautifulSoup
import requests
import re
import time
def spread():
    url1=requests.get('https://quotes.wsj.com/bond/BX/TMUBMUSD10Y?mod=md_home_overview_quote').text
    soup1=BeautifulSoup(url1,'lxml')
    yield_rate_10=soup1.find('li',attrs={'class':'crinfo_quote'})
    url2=requests.get('https://quotes.wsj.com/bond/BX/TMUBMUSD01Y?mod=md_home_overview_quote').text
    soup2=BeautifulSoup(url2,'lxml')
    yield_rate_10=soup1.find('li',attrs={'class':'crinfo_quote'})
    yield_rate_1=soup2.find('li',attrs={'class':'crinfo_quote'})
    inf_dic1={}
    yield_10=yield_rate_10.find('span').get_text().replace('%','')
    yield_1=yield_rate_1.find('span').get_text().replace('%','')
    print(float(yield_10.strip())-float(yield_1.strip()))
    return float(yield_10.strip())-float(yield_1.strip())
#spread()