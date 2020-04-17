import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import datetime
import statsmodels.api as sm
import matplotlib.pyplot as plt
from bs4 import BeautifulSoup
from scipy.optimize import fsolve
'''
options=webdriver.ChromeOptions()
prefs={'profile.default_content_settings.popups': 0, 'download.default_directory': 'E:\\',"profile.default_content_setting_values.automatic_downloads":30}
options.add_experimental_option('prefs',prefs)
driver=webdriver.Chrome(executable_path='E:/chromedriver.exe',chrome_options=options)
driver.get('https://finance.yahoo.com/quote/%5EVIX/history?p=%5EVIX')
source=driver.page_source
soup=BeautifulSoup(source,'lxml')
res=[]
table = soup.find('table',attrs={'data-test':'historical-prices'})
for tr in table.find_all('tr'):
    temp = [td.get_text() for td in tr.find_all('td')]
    if len(temp):
        res.append(temp)
    else:
        continue
print(res)'''
def price_spread(aim_coup,aim_price,years):
    price=0
    for i in range(1,2*years+1):
        price+=2.5/(1+aim_coup/2)**i
    price+=100/(1+aim_coup/2)**(2*years)
    return price-aim_price
print(fsolve(price_spread,0.05,args=(104.791,5)))
'''
HY_5Y=pd.read_excel('E:\正式文件\BAM\Liquidity data\CDX HY 5Y.xlsx',header=None,names=['Character','Date','5Y_Bid','5Y_Ask'],skiprows=[0])
HY_5Y=HY_5Y.dropna().drop(['Character'],axis=1)
HY_5Y['5Y_Bid_Spread']=HY_5Y['5Y_Bid'].apply(lambda x: fsolve(price_spread,0.05,args=(x,5))[0])*10000
HY_5Y['5Y_Ask_Spread']=HY_5Y['5Y_Ask'].apply(lambda x: fsolve(price_spread,0.05,args=(x,5))[0])*10000
HY_5Y['Spread_Spread']=HY_5Y['5Y_Ask_Spread']-HY_5Y['5Y_Bid_Spread']
print(HY_5Y['5Y_Bid_Spread']/HY_5Y['5Y_Bid'])
print(sm.tsa.stattools.adfuller(HY_5Y['Spread_Spread']))
#HY_5Y.to_csv('CDX HY 5Y.csv')
VIX=pd.read_excel('E:\正式文件\BAM\Liquidity data\VIX.xlsx',header=None,names=['Character','Date','VIX'])
VIX=VIX.dropna().drop(['Character'],axis=1)
tenyear_yield=pd.read_csv('E:\HistoricalPrices_10Y.csv',header=None,skiprows=[0],names=['Date']+['10Y_'+i for i in ['Open','High','Low','Close']])
oneyear_yield=pd.read_csv('E:\HistoricalPrices_1Y.csv',header=None,skiprows=[0],names=['Date']+['1Y_'+i for i in ['Open','High','Low','Close']])
whole_yield=tenyear_yield.merge(oneyear_yield,how='inner',left_on='Date',right_on='Date')
whole_yield['curve_spread']=whole_yield['10Y_Close']-whole_yield['1Y_Close']
def date_conversion(x):
    temp=x.split('/')
    temp[-1]='20'+temp[-1]
    temp_date='/'.join(temp)
    return datetime.datetime.strptime(temp_date,'%m/%d/%Y')
whole_yield['Date']=whole_yield['Date'].apply(lambda x:date_conversion(x))
HY=HY_5Y.merge(VIX,how='inner',left_on='Date',right_on='Date')
HY=HY.merge(whole_yield,how='inner',left_on='Date',right_on='Date')
print(HY)
HY['VIX']=HY['VIX'].values.astype(float)
X = HY[['VIX','curve_spread']].values
X = sm.add_constant(X)
Y = HY['Spread_Spread'].values
model=sm.OLS(Y,X)
model=model.fit()
print(model.summary())'''
asset=pd.read_csv('E:\possible_asset.csv',encoding="ISO-8859-1")
print(asset.groupby('instrumentType').count())