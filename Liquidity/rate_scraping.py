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

options=webdriver.ChromeOptions()
prefs={'profile.default_content_settings.popups': 0, 'download.default_directory': 'E:\\',"profile.default_content_setting_values.automatic_downloads":30}
options.add_experimental_option('prefs',prefs)
driver=webdriver.Chrome(executable_path='E:/chromedriver.exe',chrome_options=options)
driver.get('https://quotes.wsj.com/bond/BX/TMUBMUSD01Y/historical-prices')
driver.maximize_window()
driver.find_element_by_id('selectDateFrom').clear()
driver.find_element_by_id('selectDateFrom').send_keys('06/11/2018')
#driver.find_element_by_class_name('dl_button').click()
source=driver.page_source
soup=BeautifulSoup(source,'lxml')
table=soup.find('div',{'id':'historical_data_table'})
res=[]
for tr in table.find_all('tr'):
    temp = [td.get_text() for td in tr.find_all('td')]
    if len(temp):
        res.append(temp)
    else:
        continue
print(res)
button=driver.find_element_by_link_text('Next')
button.click()

middle=['IG','HY','IG HVOL']
years=['3Y','5Y','7Y','10Y']
namedict={}
for i in years:
    namedict[i]=['CDX'+' '+j+' '+i for j in middle]
DFdict={}
for i in years:
    DFdict[i]=[pd.read_excel('E:\正式文件\BAM\Liquidity data\\'+j+'.xlsx' ,header=None,names=['Character','Date',j+'Bid',j+'Ask'],skiprows=[0])for j in namedict[i]]
    DFdict[i]=[df.dropna().drop(['Character'],axis=1).sort_values(by=['Date']) for df in DFdict[i]]
    for df,j in zip(DFdict[i],namedict[i]):
        df[j+'Spread']=(df[j+'Bid']-df[j+'Ask'])
        print(j+':'+str(df[j+'Spread'].mean()))
        df[j+'Scale']=df[j+'Spread'].apply(lambda x:(x-df[j+'Spread'].min())/(df[j+'Spread'].max()-df[j+'Spread'].min()))
'''
liq_ind=pd.read_excel('E:\正式文件\BAM\Liquidity data\DB liquidity risk factor.xlsx').dropna().drop(['Character'],axis=1).sort_values(by=['Date'])
liq_ind['Index_scale']=liq_ind['Index'].apply(lambda x:(x-liq_ind['Index'].min())/(liq_ind['Index'].max()-liq_ind['Index'].min()))

VIX=pd.read_excel('E:\正式文件\BAM\Liquidity data\VIX.xlsx',header=None,names=['Character','Date','VIX'])
VIX=VIX.dropna().drop(['Character'],axis=1)
#print(VIX)
tenyear_yield=pd.read_csv('E:\HistoricalPrices_10Y.csv',header=None,skiprows=[0],names=['Date']+['10Y_'+i for i in ['Open','High','Low','Close']])
oneyear_yield=pd.read_csv('E:\HistoricalPrices_1Y.csv',header=None,skiprows=[0],names=['Date']+['1Y_'+i for i in ['Open','High','Low','Close']])
whole_yield=tenyear_yield.merge(oneyear_yield,how='inner',left_on='Date',right_on='Date')
whole_yield['curve_spread']=whole_yield['10Y_Close']-whole_yield['1Y_Close']
whole_yield['curve_spread_scale']=whole_yield['curve_spread'].apply(lambda x:(x-whole_yield['curve_spread'].min())/(whole_yield['curve_spread'].max()-whole_yield['curve_spread'].min()))
print(sm.tsa.stattools.adfuller(whole_yield['curve_spread']))
print(sm.tsa.stattools.adfuller(liq_ind['Index']))
def date_conversion(x):
    temp=x.split('/')
    temp[-1]='20'+temp[-1]
    temp_date='/'.join(temp)
    return datetime.datetime.strptime(temp_date,'%m/%d/%Y')
whole_yield['Date']=whole_yield['Date'].apply(lambda x:date_conversion(x))
#print(whole_yield['Date'])
def CDX_liq(i,ind):
    DF_templist = DFdict[i]
    DF_temp = DF_templist[ind].merge(liq_ind, how='inner', left_on='Date', right_on='Date')
    DF_temp = DF_temp.merge(whole_yield, how='inner', left_on='Date', right_on='Date')
    DF_temp = DF_temp.merge(VIX, how='inner', left_on='Date', right_on='Date')
    DF_temp['VIX']=DF_temp['VIX'].values.astype(float)
    print(DF_temp)
    X = DF_temp[['VIX','curve_spread']].values
    X = sm.add_constant(X)
    Y = DF_temp[namedict[i][ind] + 'Spread'].values
    print(sm.tsa.stattools.adfuller(DF_temp[namedict[i][ind] + 'Spread']))
    org = sm.OLS(Y, X)
    model = org.fit()
    print(model.summary())
    return model.params
def CDX_liq_scale(i,ind):
    DF_templist = DFdict[i]
    DF_temp = DF_templist[ind].merge(liq_ind, how='inner', left_on='Date', right_on='Date')
    DF_temp = DF_temp.merge(whole_yield, how='inner', left_on='Date', right_on='Date')
    X = DF_temp[['Index_scale','curve_spread_scale']].values
    X = sm.add_constant(X)
    Y = DF_temp[namedict[i][ind] + 'Scale'].values
    print(sm.tsa.stattools.adfuller(DF_temp[namedict[i][ind] + 'Scale']))
    org = sm.OLS(Y, X)
    model = org.fit()
    print(model.summary())
    return model.params
def CDX_liq_diff(i,ind):
    DF_templist = DFdict[i]
    DF_temp = DF_templist[ind].merge(liq_ind, how='inner', left_on='Date', right_on='Date')
    DF_temp = DF_temp.merge(whole_yield, how='inner', left_on='Date', right_on='Date')
    DF_temp['curve_diff']=DF_temp['curve_spread'].diff()
    DF_temp['Index_diff']=DF_temp['Index'].diff()
    DF_temp['spread_diff']=DF_temp[namedict[i][ind] + 'Spread'].diff()
    DF_temp=DF_temp.dropna(subset=['curve_diff'])
    X = DF_temp[['Index_diff','curve_diff']].values
    X = sm.add_constant(X)
    Y = DF_temp['spread_diff'].values
    print(sm.tsa.stattools.adfuller(DF_temp[namedict[i][ind] + 'Spread']))
    #print(sm.tsa.stattools.adfuller(DF_temp['curve_diff']))
    #print(sm.tsa.stattools.adfuller(DF_temp['Index_diff']))
    #print(sm.tsa.stattools.adfuller(DF_temp['spread_diff']))
    org = sm.OLS(Y, X)
    model = org.fit()
    print(model.summary())
    return model.params
print(CDX_liq('5Y',0))
params={}

for i in years:
    params[i]={}
    for j in range(3):
        params[i][middle[j]]=CDX_liq(i,j)
coef=pd.DataFrame(params)
def plot(i,ind):
    DF_templist = DFdict[i]
    DF_temp = DF_templist[ind].merge(liq_ind, how='inner', left_on='Date', right_on='Date')
    DF_temp = DF_temp.merge(whole_yield, how='inner', left_on='Date', right_on='Date')
    DF_temp = DF_temp.merge(VIX, how='inner', left_on='Date', right_on='Date')
    DF_temp['VIX']=DF_temp['VIX'].values.astype(float)
    fac1 = DF_temp['VIX'].values[-10:]
    fac2 = DF_temp['curve_spread'].values[-10:]
    forecast = {}
    fig, ax = plt.subplots(1, 3)
    for i in range(0, len(coef.index)):
        for j in range(0, len(coef.columns)):
            cons, beta1,beta2 = coef.ix[i, j]
            forecast[coef.index[i] + coef.columns[j]] = beta1 * fac1 + beta2 * fac2 + cons
            ax[i].plot(forecast[coef.index[i] + coef.columns[j]] )
        ax[i].set_ylabel(coef.index[i])
        ax[i].set_xlabel('Date')
        ax[i].legend(coef.columns, loc=0)
    plt.tight_layout()
    plt.show()
plot('10Y',1)
'''
def map(x):
    if x['instrumentType']=='Loan':
        return 'LCDX'
    elif x['instrumentType']=='Bond':
        return 'CDX'