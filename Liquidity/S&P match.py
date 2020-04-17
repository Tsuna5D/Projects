import pandas as pd
import datetime
import calendar
res=pd.read_csv('S&P_coef.csv',index_col=[0,1,2])
print(res.xs(('Communication Services', '10Y', 'HY')))
assets = pd.read_csv('E:\possible_asset.csv', encoding="ISO-8859-1")
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
assets=assets.dropna(subset=['sectorType'])
for name,data in assets.groupby('instrumentType'):
    if name=='Loan':
        print(data['id'])
print(assets.groupby('instrumentType').count())
tenyear_yield=pd.read_csv('E:\正式文件\BAM\Liquidity data\HistoricalPrices_10Y.csv',engine='python',header=None,skiprows=[0],names=['Date']+['10Y_'+i for i in ['Open','High','Low','Close']])
oneyear_yield=pd.read_csv('E:\正式文件\BAM\Liquidity data\HistoricalPrices_1Y.csv',engine='python',header=None,skiprows=[0],names=['Date']+['1Y_'+i for i in ['Open','High','Low','Close']])
whole_yield=tenyear_yield.merge(oneyear_yield,how='inner',left_on='Date',right_on='Date')
whole_yield['curve_spread']=whole_yield['10Y_Close']-whole_yield['1Y_Close']

def date_conversion(x):
    temp=x.split('/')
    temp[-1]='20'+temp[-1]
    temp_date='/'.join(temp)
    return datetime.datetime.strptime(temp_date,'%m/%d/%Y')
whole_yield['Date']=whole_yield['Date'].apply(lambda x:date_conversion(x))
whole_yield['Date']=whole_yield['Date'].apply(lambda x:x.date())
#assets['sectorType']=assets['sectorType'].apply(lambda x:sector_change[x])
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
        assets[item_name]=assets[item_name].apply(lambda x:datetime.datetime.strptime(str(x),'%Y/%m/%d'))
    else:
        assets[item_name] = assets[item_name].apply(lambda x: mat_judge(x))
    return list(assets[item_name].quantile(quantiles))
quantiles=get_quantiles('dateOfArrears',[0.25,0.5,0.75])
print(quantiles)
mat_quantiles=get_quantiles('maturity',[0.25,0.5,0.75])
print(mat_quantiles)
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
            return (x['sectorType'], '10Y', 'HY')
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

def simulation(x):
    cons,vol,curve=res.xs(key_match(x['Key']))
    sector=sector_change[x['sectorType']]
    SP_temp='E:\正式文件\BAM\Liquidity data\%s.csv'% sector
    #SP_temp=pd.read_excel(SP_temp, header=6).dropna()
    SP_temp=pd.read_csv(SP_temp,engine='python',index_col=[0])
    #SP_temp=SP_temp.rename(columns={'Effective date ': 'Date'})
    # print(SP_sector[i].columns[-1]=='S&P 500 %s (Sector)'%i)
    # print(SP_sector[i].columns)
    #SP_temp['Date'] = SP_temp['Date'].apply(lambda x: datetime.date(x.year, x.month, x.day))
    SP_temp['Date'] = SP_temp['Date'].apply(lambda x: x.split(' ')[0])
    SP_temp['Date'] = SP_temp['Date'].apply(lambda x: datetime.datetime.strptime(x, '%Y-%m-%d'))
    SP_temp['vol'] = SP_temp['S&P 500 %s (Sector)' % sector].rolling(30).std()
    DF_temp = SP_temp.merge(whole_yield, how='inner', left_on='Date', right_on='Date')
    DF_temp['forecast']=cons+vol*DF_temp['vol']+curve*DF_temp['curve_spread']
    DF_temp['forecast_pct']=-(DF_temp['forecast']-DF_temp['forecast'].shift(5))/DF_temp['forecast'].shift(5)
    return DF_temp['forecast_pct'][-5:]
assets['Map']=assets.apply(lambda x:map(x),axis=1)
assets['Key']=assets['Map'].apply(lambda x:key(x))

final=assets.apply(lambda x:{x['id']:simulation(x)},axis=1).values
add_data={}
#for i in final:
    #add_data.update(i)
'''
result=pd.read_csv('Liq_data.csv',header=None)
result=result.T.dropna()
result.columns=['id','LiquidityData_1','LiquidityData_2','LiquidityData_3','LiquidityData_4','LiquidityData_5']
result[['LiquidityData_%s'%str(i) for i in range(1,6)]]=result[['LiquidityData_%s'%str(i) for i in range(1,6)]].astype(float).applymap(lambda x:x*100)
print(result)
result.to_csv('Liq_data.csv')'''

