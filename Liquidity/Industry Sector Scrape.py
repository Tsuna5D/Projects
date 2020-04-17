from selenium import webdriver
from bs4 import BeautifulSoup
import requests
import re
import time
def industry():
    url=requests.get('https://www.tradingview.com/markets/indices/quotes-snp/').text
    soup=BeautifulSoup(url,'lxml')
    table=soup.find('table',attrs={'class':'tv-data-table tv-screener-table'})
    inf_dic={}
    for tr in table.find_all('tr'):
        inf = [td.get_text() for td in tr.find_all('td')]
        if len(inf):
            print(inf)
            inf[0] = inf[0].strip()
            inf[0] = re.sub('(\t)+|\n', '', inf[0])
            inf[0] = inf[0].split(' ')
            inf[0] = inf[0][2:]
            inf[0] = [i.lower().capitalize() for i in inf[0]]
            inf[0] = ' '.join(inf[0])
            inf_dic[inf[0]]=float(inf[1])
    print(inf_dic)
    return inf_dic
industry()