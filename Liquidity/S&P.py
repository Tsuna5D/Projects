import pandas as pd
import statsmodels.api as sm
import datetime
import matplotlib.pyplot as plt
import calendar
import numpy as np
sectors=['Communication Services',
         'Consumer Discretionary',
         'Consumer Staples','Energy',
         'Financials','Health Care',
         'Industrials','Information Technology',
         'Materials','Real Estate','Utilities']
html_dict={}
for i in sectors:
    html_dict[i]='E:\正式文件\BAM\Liquidity data\%s.xls'% i
SP_sector={}
for i in sectors:
    SP_sector[i]=pd.read_excel(html_dict[i],header=6).dropna()
    SP_sector[i]=SP_sector[i].rename(columns={'Effective date ':'Date'})
    #print(SP_sector[i].columns[-1]=='S&P 500 %s (Sector)'%i)
    #print(SP_sector[i].columns)
    SP_sector[i]['Date']=SP_sector[i]['Date'].apply(lambda x:datetime.date(x.year,x.month,x.day))
    SP_sector[i]['vol']=SP_sector[i]['S&P 500 %s (Sector)'%i].rolling(30).std()
    SP_sector[i]=SP_sector[i].dropna()
#print(SP_sector)
middle=['IG','HY','IG HVOL']
years=['3Y','5Y','7Y','10Y']
namedict={}
for i in years:
    namedict[i]=['CDX'+' '+j+' '+i for j in middle]
DFdict={}
VIX=pd.read_excel('E:\正式文件\BAM\Liquidity data\VIX.xlsx',header=None,names=['Character','Date','VIX'])
VIX=VIX.dropna().drop(['Character'],axis=1)
VIX['Date']=VIX['Date'].apply(lambda x:x.date())
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
whole_yield['Date']=whole_yield['Date'].apply(lambda x:x.date())

for i in years:
    DFdict[i]=[pd.read_excel('E:\正式文件\BAM\Liquidity data\\'+j+'.xlsx' ,header=None,names=['Character','Date',j+'Bid',j+'Ask'],skiprows=[0])for j in namedict[i]]
    DFdict[i]=[df.dropna().drop(['Character'],axis=1).sort_values(by=['Date']) for df in DFdict[i]]
    for df,j in zip(DFdict[i],namedict[i]):
        df[j+'Spread']=(df[j+'Bid']-df[j+'Ask'])
        print(j,df[j+'Spread'].mean(),df[j+'Spread'].std())
        df[j+'Scale']=df[j+'Spread'].apply(lambda x:(x-df[j+'Spread'].min())/(df[j+'Spread'].max()-df[j+'Spread'].min()))
        df['Date']=df['Date'].apply(lambda x:x.date())
def linear_reg(i,sector,ind1):
    SP_temp=SP_sector[sector]
    DF_templist=DFdict[i]
    DF_temp=DF_templist[ind1].merge(SP_temp,how='inner',left_on='Date',right_on='Date')
    DF_temp = DF_temp.merge(VIX, how='inner', left_on='Date', right_on='Date')
    DF_temp = DF_temp.merge(whole_yield, how='inner', left_on='Date', right_on='Date')
    DF_temp['VIX']=DF_temp['VIX'].values.astype(float)
    #print(DF_temp)
    X=DF_temp[['vol','curve_spread']].values.astype(float)
    X=sm.add_constant(X)
    Y=DF_temp[namedict[i][ind1] + 'Spread'].values.astype(float)
    org=sm.OLS(Y,X)
    model=org.fit()
    #print(model.summary())
    return (model.params,model.rsquared)
def plot(i,ind1):
    DF_templist = DFdict[i]
    for sector in sectors:
        SP_temp = SP_sector[sector]
        DF_temp = DF_templist[ind1].merge(SP_temp, how='inner', left_on='Date', right_on='Date')
        DF_temp = DF_temp.merge(VIX, how='inner', left_on='Date', right_on='Date')
        DF_temp = DF_temp.merge(whole_yield, how='inner', left_on='Date', right_on='Date')
        const,vol,curve=res.xs((sector,i,middle[ind1]))
        DF_temp['forecast']=const+vol*DF_temp['vol']+curve*DF_temp['curve_spread']
        DF_temp['forecast_pct']=-(DF_temp['forecast']-DF_temp['forecast'].shift(5))/DF_temp['forecast'].shift(5)
        plt.plot(np.arange(10),DF_temp['forecast_pct'][-10:]*100)
    #plt.plot(np.arange(10),DF_temp['CDX %s %sSpread'%(middle[ind1],i)][-10:])
    plt.xticks(np.arange(10),['Day%s'%i for i in range(1,11)])
    plt.xlabel('Date')
    plt.ylabel('Percentage Change(%)')
    plt.legend(sectors)
    plt.show()
params={}
Rsquared=[]
for i in sectors:
    for j in ['5Y','7Y']:
        for k in range(0,len(middle)):
            print(i,j,k)
            params[(i,j,middle[k])],R2=linear_reg(j,i,k)
            Rsquared.append(R2)
print(np.mean(np.array(Rsquared)))
res=pd.DataFrame(params).T
res.columns=['constant','vol','curve_spread']
#res.to_csv('S&P_coef.csv')
assets = pd.read_csv('E:\possible_asset.csv', encoding="ISO-8859-1")
sector_change={}
for i in sectors:
    sector_change[''.join(i.split(' '))]=i
    sector_change['Material']='Materials'
    sector_change['Technology']='Information Technology'
    sector_change['Telecommunication']='Communication Services'
print(len(assets[assets['sectorType'].notnull()])/len(assets))
assets=assets.dropna(subset=['sectorType'])
assets['sectorType']=assets['sectorType'].apply(lambda x:sector_change[x])
#print(res.xs(('Communication Services','10Y','HY')))
#print(assets.groupby('sectorType').count())
#plot('5Y',1)