from selenium import webdriver
from bs4 import BeautifulSoup
import requests
import re
import datetime
import calendar
import pandas as pd
import numpy as np

def spread():
    try:
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
        #print(float(yield_10.strip())-float(yield_1.strip()))
        return float(yield_10.strip())-float(yield_1.strip())
    except:
        raise ValueError('Spread not found!')
def industry():
    try:
        url=requests.get('https://www.tradingview.com/markets/indices/quotes-snp/').text
        soup=BeautifulSoup(url,'lxml')
        table=soup.find('table',attrs={'class':'tv-data-table tv-screener-table'})
        inf_dic={}
        for tr in table.find_all('tr'):
            inf = [td.get_text() for td in tr.find_all('td')]
            if len(inf):
                inf[0] = inf[0].strip()
                inf[0] = re.sub('(\t)+|\n', '', inf[0])
                inf[0] = inf[0].split(' ')
                inf[0] = inf[0][2:][:-1]
                inf[0] = [i.lower().capitalize() for i in inf[0]]
                inf[0] = ' '.join(inf[0])
                inf_dic[inf[0]]=float(inf[1])
        #print(inf_dic)
        return inf_dic
    except:
        raise ValueError('Industry Indices not found!')
class asset:
    def __init__(self,assetclass,maturity,sector,dateOfArrears):
        self.assetClass=assetclass
        self.maturity=maturity
        self.sectorType=sector
        self.dateOfArrears=dateOfArrears
sector_change={}
sectors=['Communication Services',
         'Consumer Discretionary',
         'Consumer Staples','Energy',
         'Financials','Health Care',
         'Industrials','Information Technology',
         'Materials','Real Estate','Utilities']
for i in sectors:
    sector_change[''.join(i.split(' '))]=i
    sector_change['Material']='Materials'
    sector_change['Technology']='Information Technology'
    sector_change['Telecommunication']='Communication Services'
    sector_change[i]=i
def mat_judge(i):
    temp=str(i).split(' ')
    if len(temp)>2:
        res=temp[1:]
        res[0]=str(list(calendar.month_abbr).index(res[0]))
        res='/'.join(res)
        return datetime.datetime.strptime(res,'%M/%d/%Y')
    else:
        try:
            return datetime.datetime.strptime(i,'%M/%d/%Y')
        except:
            return
def get_quantiles(item_name,quantiles):
    assets=pd.read_csv('E:\possible_asset.csv',encoding="ISO-8859-1")
    assets=assets.dropna(subset=[item_name])
    if item_name=='dateOfArrears':
        assets[item_name] = assets[item_name].apply(lambda x:datetime.datetime.strptime(str(x),'%Y/%m/%d'))
    else:
        assets[item_name] = assets[item_name].apply(lambda x: mat_judge(x))
    return list(assets[item_name].quantile(quantiles))
quantiles=get_quantiles('dateOfArrears',[0.25,0.5,0.75])
mat_quantiles=get_quantiles('maturity',[0.25,0.5,0.75])
def map(x):
    x['sectorType']=sector_change[x['sectorType']]
    if x['assetClass']=='Deep Distressed' or x['assetClass']=='Distressed':
        if pd.notnull(x['dateOfArrears']):
            ind=0
            temp_date=datetime.datetime.strptime(str(x['dateOfArrears']),'%Y/%m/%d')
            if temp_date <= quantiles[0]:
                ind = 0
            elif temp_date >= quantiles[2]:
                ind = 3
            else:
                for i in range(len(quantiles)):
                    if temp_date < quantiles[i] and temp_date > quantiles[i - 1]:
                        ind = i
            if x['assetClass']=='Deep Distressed':
                if ind==0 or ind==1:
                    return (x['sectorType'], '3Y', 'HY')
                else:
                    return (x['sectorType'], '5Y', 'HY')
            else:
                if ind == 0:
                    return (x['sectorType'], '3Y', 'HY')
                elif ind==1 or ind==2:
                    return (x['sectorType'], '5Y', 'HY')
                else:
                    return (x['sectorType'], '10Y', 'HY')
        else:
            return (x.sectorType, '10Y', 'HY')
    else:
        temp_date = mat_judge(str(x['maturity']))
        if pd.notnull(temp_date):
            ind = 0
            if temp_date <= mat_quantiles[0]:
                ind = 0
            elif temp_date >= mat_quantiles[2]:
                ind = 3
            else:
                for i in range(len(mat_quantiles)):
                    if temp_date < mat_quantiles[i] and temp_date > mat_quantiles[i - 1]:
                        ind = i
            if ind == 0:
                return (x['sectorType'], '5Y', 'IG')
            elif ind==1:
                return (x['sectorType'], '10Y', 'IG')
            else:
                return (x['sectorType'], '3Y', 'IG HVOL')
        else:
            return (x['sectorType'], '5Y', 'IG')
def key(x):
    return x[0]+'_'+x[1]+'_'+x[2]
def key_match(x):
    return tuple(x.split('_'))
res=pd.read_csv('S&P_coef.csv',index_col=[0,1,2])
tenyear_yield=pd.read_csv('E:\正式文件\BAM\Liquidity data\HistoricalPrices_10Y.csv',engine='python',\
                          header=None,skiprows=[0],names=['Date']+['10Y_'+i for i in ['Open','High','Low','Close']])
oneyear_yield=pd.read_csv('E:\正式文件\BAM\Liquidity data\HistoricalPrices_1Y.csv',engine='python',\
                          header=None,skiprows=[0],names=['Date']+['1Y_'+i for i in ['Open','High','Low','Close']])
whole_yield=tenyear_yield.merge(oneyear_yield,how='inner',left_on='Date',right_on='Date')
whole_yield['curve_spread']=whole_yield['10Y_Close']-whole_yield['1Y_Close']
def date_conversion(x):
    temp=x.split('/')
    temp[-1]='20'+temp[-1]
    temp_date='/'.join(temp)
    return datetime.datetime.strptime(temp_date,'%m/%d/%Y')
whole_yield['Date']=whole_yield['Date'].apply(lambda x:date_conversion(x))
whole_yield['Date']=whole_yield['Date'].apply(lambda x:x.date())
def refresh(sector):
    sector_ind = industry()
    SP_temp='E:\正式文件\BAM\Liquidity data\%s.csv'% sector
    SP_temp=pd.read_csv(SP_temp,engine='python',index_col=[0])
    # print(SP_sector[i].columns[-1]=='S&P 500 %s (Sector)'%i)
    # print(SP_sector[i].columns)
    SP_temp = SP_temp.drop(SP_temp.index[0])
    SP_temp['Date'] = SP_temp['Date'].apply(lambda x:x.split(' ')[0])
    SP_temp['Date'] = SP_temp['Date'].apply(lambda x: datetime.datetime.strptime(x,'%Y-%m-%d'))
    today = datetime.datetime.today()
    day, month, year = today.day, today.month, today.year
    #print(SP_temp['S&P 500 Energy (Sector) (TR)'].mean())
    SP_temp.ix[len(SP_temp), 'Date'] = datetime.date(year, month, day)
    SP_temp.ix[len(SP_temp), 'S&P 500 %s (Sector)' % sector] = sector_ind[sector]
    return SP_temp
def yield_refresh():
    yield_spread = spread()
    today_yield=whole_yield
    today_yield=today_yield.sort_values('Date')
    today_yield=today_yield.reset_index().drop(['index'],axis=1)
    today_yield = today_yield.drop(today_yield.index[0])
    today = datetime.datetime.today()
    day, month, year = today.day, today.month, today.year
    today_yield.ix[len(today_yield), 'Date'] = datetime.date(year, month, day)
    today_yield.ix[len(today_yield), 'curve_spread'] = yield_spread
    today_yield['Date'] = today_yield['Date'].apply(lambda x: x.strftime('%Y-%m-%d'))
    return today_yield
def simulation(x,SPs,today_yield):
    cons,vol,curve=res.xs(map(x))
    #print(x['sectorType'])
    sector=x['sectorType']
    SP_temp=SPs[sector]
    SP_temp['vol'] = SP_temp['S&P 500 %s (Sector)' % sector].rolling(30).std()
    #print(today_yield['Date'])
    DF_temp = SP_temp.merge(today_yield, how='inner', left_on='Date', right_on='Date')
    DF_temp['forecast']=cons+vol*DF_temp['vol']+curve*DF_temp['curve_spread']
    DF_temp['forecast_pct']=-(DF_temp['forecast']-DF_temp['forecast'].shift(10))/DF_temp['forecast'].shift(10)
    return DF_temp['forecast_pct'][-10:]
def simulation_alt(x,SPs,today_yield):
    cons,vol,curve=res.xs(map(x))
    #print(x['sectorType'])
    sector=x['sectorType']
    SP_temp=SPs[sector]
    SP_temp['vol'] = SP_temp['S&P 500 %s (Sector)' % sector].rolling(30).std()
    #print(today_yield['Date'])
    DF_temp = SP_temp.merge(today_yield, how='inner', left_on='Date', right_on='Date')
    DF_temp['forecast']=cons+vol*DF_temp['vol']+curve*DF_temp['curve_spread']
    DF_temp['forecast_change']=DF_temp['forecast']-DF_temp['forecast'].shift(30)/DF_temp['forecast'].shift(30)
    return DF_temp['forecast_change'][-30:]

SPs={}
for sector in sectors:
    SP_temp=refresh(sector)
    SP_temp['Date']=SP_temp['Date'].apply(lambda x:x.strftime('%Y-%m-%d'))
    SPs[sector]=SP_temp
today_yield=yield_refresh()
def portfolio(IDs,notionals,df):
    df = df.reset_index().drop(['index'],axis=1)
    df.index = df['id']
    ratio=np.array([notional/sum(notionals) for notional in notionals])
    liquidity=[]
    durations=[]
    notionals=np.array(notionals)
    for ID in IDs:
        liquidity.append(simulation_alt(df.ix[ID],SPs,today_yield))
        kind,year=map(df.ix[ID])[2], int(map(df.ix[ID])[1].strip('Y'))
        durations.append(duration(kind,year))
    liquidity=np.array(liquidity)
    durations=np.array(durations)
    product=np.multiply(liquidity,durations[:,np.newaxis])
    product=np.multiply(product,notionals[:,np.newaxis])
    #print(np.sum(product,axis=0))
    #max_liquidity=max(np.dot(ratio,liquidity))
    #average_duration=np.dot(ratio,durations)
    return max(np.sum(product,axis=0))*0.0001
def duration(kind,year):
    if kind=='IG' or kind=='IG HVOL':
        coupon=1
    else:
        coupon=5
    value=0
    time=0
    for i in range(1,int(year//0.5)+1):
        value+=(coupon*0.5)/(1+0.025/2)**i
        time+=(coupon*i*0.25)/(1+0.025/2)**i
    value += 100 / (1 + 0.025/2) ** (year*2)
    time+=(100*year) / (1 + 0.025/2) ** (year*2)
    return time/value
def individual_liq_loss(x):
    liquidity=simulation_alt(x,SPs,today_yield)
    kind,year=map(x)[2], int(map(x)[1].strip('Y'))
    ind_duration=duration(kind,year)
    max_liquidity=max(liquidity)
    notional=x['notional']
    if not notional:
        return 1000000*max_liquidity*ind_duration*0.0001
    notional=notional.strip()
    if ',' in notional:
        notional=''.join(notional.split(','))
    notional=re.search('([0-9]+)|\w*([0-9]+)',notional).group(1)
    return int(notional)*max_liquidity*ind_duration*0.0001
assets=pd.read_csv('E:\possible_asset.csv', encoding="ISO-8859-1")
assets=assets.dropna(subset=['sectorType'])
#print(assets.ix[9:13,'notional'])
assets['keys']=assets.apply(lambda x:map(x),axis=1)
print(portfolio(assets.head(5)['id'],np.array([1,2,3,4,5])*1000000,assets))
assets['liq_loss']=assets.apply(lambda x:individual_liq_loss(x),axis=1)
#print(assets.groupby('keys').count().sort_values(by='isActiveByBAM')/assets['isActiveByBAM'].count())
#for Id in assets.head(5)['id']:
    #print(simulation(assets[assets['id']==Id],SPs,today_yield))

'''
import pymongo
from bson.objectid import ObjectId
client = pymongo.MongoClient('localhost', 27017)
mydb = client["bam"]
mycol = mydb["assets"]
df = pd.DataFrame(list(mycol.find()))
mongostore=df.apply(lambda x:{x['id']:simulation(x,SPs,today_yield)},axis=1).values
for data in mongostore:
    for key,value in data.items():
        renew={}
        for i in range(len(value)):
            renew['Liquidity_%d'%(i+1)]=value[i]
        mycol.update({"_id":ObjectId(key)},{"$set":renew},multi=True)'''
'''
import pymongo
from bson.objectid import ObjectId
client = pymongo.MongoClient('localhost', 27017)
mydb = client["bam"]
mycol = mydb["assets"]
df = pd.DataFrame(list(mycol.find()))
mongostore=df.apply(individual_liq_loss(x),axis=1).values
mongostore=zip(df['id'],mongostore)
for data in mongostore:
    for key,value in data:
        renew={}
        renew['LL']=value
        mycol.update({"_id":ObjectId(key)},{"$set":renew},multi=True)
'''