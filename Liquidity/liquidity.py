import datetime
import pandas as pd
import re
import statsmodels.api as sm
from statsmodels.tsa.arima_model import ARMA
import matplotlib.pyplot as plt
import calendar
import numpy as np

middle=['IG','HY','IG HVOL']
years=['3Y','5Y','7Y','10Y']
namedict={}
for i in years:
    namedict[i]=['CDX'+' '+j+' '+i for j in middle]
DFdict={}

def date(i):
    return datetime.datetime.strptime(i,'%Y-%M-%D')
for i in years:
    DFdict[i]=[pd.read_excel('E:\正式文件\BAM\Liquidity data\\'+j+'.xlsx' ,header=None,names=['Character','Date',j+'Bid',j+'Ask'],skiprows=[0])for j in namedict[i]]
    DFdict[i]=[df.dropna().drop(['Character'],axis=1).sort_values(by=['Date']) for df in DFdict[i]]
    for df,j in zip(DFdict[i],namedict[i]):
        df[j+'Spread']=(df[j+'Bid']-df[j+'Ask'])
        df[j+'Scale']=df[j+'Spread'].apply(lambda x:(x-df[j+'Spread'].min())/(df[j+'Spread'].max()-df[j+'Spread'].min()))
def linear_reg(i,ind1,ind2):
    DF_templist=DFdict[i]
    DF_temp=DF_templist[ind1].merge(DF_templist[ind2],how='inner',left_on='Date',right_on='Date')
    print(DF_temp)
    X=DF_temp[namedict[i][ind1]+'Spread'].values
    X=sm.add_constant(X)
    Y=DF_temp[namedict[i][ind2]+'Spread'].values
    org=sm.OLS(Y,X)
    model=org.fit()
    print(model.summary())
liq_ind=pd.read_excel('E:\正式文件\BAM\Liquidity data\DB liquidity risk factor.xlsx').dropna().drop(['Character'],axis=1).sort_values(by=['Date'])
liq_ind['Index_scale']=liq_ind['Index'].apply(lambda x:(x-liq_ind['Index'].min())/(liq_ind['Index'].max()-liq_ind['Index'].min()))
def CDX_liq(i,ind):
    DF_templist = DFdict[i]
    DF_temp = DF_templist[ind].merge(liq_ind, how='inner', left_on='Date', right_on='Date')
    X = DF_temp['Index'].values
    X = sm.add_constant(X)
    Y = DF_temp[namedict[i][ind] + 'Spread'].values
    org = sm.OLS(Y, X)
    model = org.fit()
    print(model.summary())
    return model.params
def CDX_liq_scale(i,ind):
    DF_templist = DFdict[i]
    DF_temp = DF_templist[ind].merge(liq_ind, how='inner', left_on='Date', right_on='Date')
    X = DF_temp['Index_scale'].values
    X = sm.add_constant(X)
    Y = DF_temp[namedict[i][ind] + 'Scale'].values
    org = sm.OLS(Y, X)
    model = org.fit()
    print(model.summary())
    return model.params
def CDX_liq_scale_roll(i,ind,pos):
    DF_templist = DFdict[i]
    DF_temp = DF_templist[ind].merge(liq_ind, how='inner', left_on='Date', right_on='Date')
    X = DF_temp['Index_scale'].values[pos:]
    X = sm.add_constant(X)
    Y = DF_temp[namedict[i][ind] + 'Scale'].values[pos:]
    org = sm.OLS(Y, X)
    model = org.fit()
    print(model.summary())
    return model.params
def roll_CDX_liq(i,ind,start=None,end=None):
    DF_templist = DFdict[i]
    DF_temp = DF_templist[ind].merge(liq_ind, how='inner', left_on='Date', right_on='Date')
    if start==None and end==None:
        start=0
        end=len(DF_temp['Index'].values)
    X = DF_temp['Index'].values[start:end]
    X = sm.add_constant(X)
    Y = DF_temp[namedict[i][ind] + 'Spread'].values[start:end]
    org = sm.OLS(Y, X)
    model = org.fit()
    print(model.summary())
    return model.params
def CDX_liq_diff(i,ind,start=None,end=None):
    DF_templist = DFdict[i]
    DF_temp = DF_templist[ind].merge(liq_ind, how='inner', left_on='Date', right_on='Date')
    DF_temp['Index_diff']=DF_temp['Index'].diff()
    DF_temp['Spread_diff']=DF_temp[namedict[i][ind] + 'Spread'].diff()
    DF_temp=DF_temp.dropna()
    if start==None and end==None:
        start=0
        end=len(DF_temp['Index_diff'].values)
    X = DF_temp['Index_diff'].values[start:end]
    #X = sm.add_constant(X)
    Y = DF_temp['Spread_diff'].values[start:end]
    org = sm.OLS(Y, X)
    model = org.fit()
    print(model.summary())
    return model.params
def auto_corr(i,ind,k):
    DF_templist = DFdict[i]
    DF_temp = DF_templist[ind]
    DF_temp['lag']=DF_temp[namedict[i][ind] + 'Spread'].shift(k)
    print(DF_temp[[namedict[i][ind] + 'Spread','lag']].corr())
def tsa(i,ind,p,q):
    DF_templist = DFdict[i]
    DF_temp = DF_templist[ind]
    print(sm.tsa.stattools.adfuller(DF_temp[namedict[i][ind] + 'Spread']))
    model=ARMA(DF_temp[namedict[i][ind] + 'Spread'],order=(p,q))
    res=model.fit()
    print(res.summary())
def tsa_liq(p,q):
    print(sm.tsa.stattools.adfuller(liq_ind['Index']))
    model = ARMA(liq_ind['Index'], order=(p, q))
    res = model.fit()
    print(res.summary())
def vol(ind):
    temp=[]
    for i in years:
        DF_templist = DFdict[i]
        DF_temp = DF_templist[ind]
        temp.append(DF_temp[namedict[i][ind] + 'Spread'].pct_change().std())
    print(temp)
def plot(i,ind,pos):
    DF_templist = DFdict[i]
    DF_temp = DF_templist[ind]
    print(DF_temp)
    plt.plot(DF_temp['Date'][pos:],DF_temp[namedict[i][ind] + 'Scale'][pos:])
    plt.show()
linear_reg('10Y',0,1)
params={}
plot('10Y',1,-10)
for i in years:
    params[i]={}
    for j in range(3):
        params[i][middle[j]]=CDX_liq_scale(i,j)
params['10Y']['IG HVOL']=CDX_liq_scale_roll('10Y',2,-50)
params['5Y']['IG HVOL']=CDX_liq_scale_roll('5Y',2,-50)
coef=pd.DataFrame(params)
coef.to_csv('coef_con_scale.csv')
#vol(0)
#vol(1)
#vol(2)
#auto_corr('5Y',0,5)
#tsa('5Y',0,1,1)
#tsa_liq(1,1)
curr_date=datetime.date.today()
fac=liq_ind['Index_scale'].values[-100:]
date=liq_ind['Date'].values[-100:]
coef_HY=coef.ix['HY']
cons,beta=coef.ix['HY','10Y']

plt.plot(beta * fac+cons)
plt.show()
fig,ax=plt.subplots(1,3)

forecast={}
for i in range(0,len(coef.index)):
    for j in range(0,len(coef.columns)):
        cons,beta=coef.ix[i,j]
        forecast[coef.index[i]+coef.columns[j]]=beta * fac+cons
        ax[i].plot(beta * fac+cons)
    ax[i].set_ylabel(coef.index[i])
    ax[i].set_xlabel('Date')
    ax[i].legend(coef.columns,loc=0)
plt.tight_layout()
plt.show()
forecast_pct={}
for name,liquidity in forecast.items():
    pct=(np.array(liquidity[5:])-np.array(liquidity[:-5]))*100/np.array(liquidity[:-5])
    forecast_pct[name]=-pct

temp_name=[]
forecast_pct_temp={}
for name,liquidity in forecast_pct.items():
    forecast_pct_temp[name]=liquidity[len(liquidity)-21:len(liquidity):5]
pct_last_5=pd.DataFrame(forecast_pct_temp)
print(pct_last_5)
pct_last_5.to_csv('liq_dict.csv')
fig,ax=plt.subplots(1,2)
color_dict={'HY3Y':'white','HY5Y':'yellow','IG HVOL3Y':'gray','IG10Y':'blue','IG5Y':'orange','HY10Y':'purple'}
for name,liq_pct in forecast_pct.items():
    '''
    for i in range(4):
        if temp_pct[i]>0:
            plt.plot([i,i+1],[temp_pct[i], temp_pct[i + 1]], color='green')
        else:
            plt.plot([i,i+1],[temp_pct[i], temp_pct[i + 1]], color='red')'''
    if name in['HY3Y','HY5Y','HY10Y','IG5Y','IG10Y','IG HVOL3Y']:
        temp_name.append(name)
        temp_pct = liq_pct[len(liq_pct)-21:len(liq_pct):5]
        ax[0].plot(temp_pct)
ax[0].legend(temp_name)
temp_name=[]
for name,liq in forecast.items():
    if name in['HY3Y','HY5Y','HY10Y','IG5Y','IG10Y','IG HVOL3Y']:
        temp_name.append(name)
        temp_price = liq[len(liq)-25:len(liq)]
        ax[1].plot(temp_price)
ax[1].legend(temp_name)
plt.show()
fig,ax=plt.subplots(3,2,figsize=(14,8))
i=0
ind=[[0,0],[0,1],[1,0],[1,1],[2,0],[2,1]]
for name,liq in forecast.items():
    if name in['HY3Y','HY5Y','HY10Y','IG5Y','IG10Y','IG HVOL3Y']:
        ind0,ind1=ind[i]
        temp_price = liq[len(liq)-25:len(liq)]
        ax[ind0][ind1].plot(temp_price,color='red')
        ax[ind0][ind1].legend(name)
        ax[ind0][ind1].set_facecolor(color_dict[name])
        i += 1
plt.show()

DF=pd.read_csv('fake.csv')
DF=DF.dropna()
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
def rating(i):
    if i[0]=='A' or i[0]=='a':
        return True
    elif i[0]=='B':
        if 'Baa2' in i or 'Baa1' in i or 'BBB' in i:
            return True
    return False
def get_quantiles(item_name,quantiles):
    assets=pd.read_csv('E:\possible_asset.csv',encoding="ISO-8859-1")
    assets=assets.dropna(subset=[item_name])
    if item_name=='dateOfArrears':
        assets[item_name]=assets[item_name].apply(lambda x:datetime.datetime.strptime(str(x),'%Y/%m/%d'))
    else:
        assets[item_name] = assets[item_name].apply(lambda x: mat_judge(x))
    return list(assets[item_name].quantile(quantiles))
quantiles=get_quantiles('dateOfArrears',[0.25,0.5,0.75])
mat_quantiles=get_quantiles('maturity',[0.25,0.5,0.75])
now = datetime.datetime.now()
def map(x):
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
                    return 'HY3Y'
                else:
                    return 'HY5Y'
            else:
                if ind == 0:
                    return 'HY3Y'
                elif ind==1 or ind==2:
                    return 'HY5Y'
                else:
                    return 'HY10Y'
        else:
            return 'HY10Y'
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
                return 'IG5Y'
            elif ind==1:
                return 'IG10Y'
            else:
                return'IG HVOL3Y'
        else:
            return 'IG5Y'

assets = pd.read_csv('E:\possible_asset.csv', encoding="ISO-8859-1")

assets['Map']=assets.apply(lambda x:map(x),axis=1)
assets['Color']=assets.apply(lambda x:color_dict[x['Map']],axis=1)
assets=assets.drop(['similarDeals'],axis=1)
print(assets.groupby('Map').count())
print(len(assets[pd.notnull(assets['Map'])])/len(assets))
assets.to_csv('possible_asset_withmap.csv')
mat={}
def cons_dic(x):
    #return {x['id']:forecast_pct[x['Map']]}
    return {x['id']:forecast[x['Map']]}
add_data=assets.apply(lambda x:cons_dic(x),axis=1).values
#print(add_data)
add_data1={}
for i in add_data:
    add_data1.update(i)
result=pd.DataFrame(add_data1)
result.to_csv('Liq_data.csv')
print(quantiles,mat_quantiles)
def price_judge(i):
    temp=re.sub('\+','',i)
    temp=temp.strip('+').strip(' ').split(' ')
    main=temp[0].split('-')
    mainp=int(main[0])+float(int(main[1])/32)
    if len(temp)==1:
        return mainp
    else:
        frac=temp[1].split('/')
        fracp=float(frac[0])/float(frac[1])
        return mainp+fracp/32


