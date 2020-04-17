import pandas as pd
import statsmodels.api as sm
VIX=pd.read_excel('E:\正式文件\BAM\Liquidity data\VIX.xlsx',header=None,names=['Character','Date','VIX'])
VIX=VIX.dropna().drop(['Character'],axis=1)
liq=pd.read_excel('E:\正式文件\BAM\Liquidity data\DB liquidity risk factor.xlsx',header=None,names=['Character','Date','DB'])
liq=liq.dropna().drop(['Character'],axis=1)
VIX['DB']=liq['DB']
VIX=VIX.dropna(subset=['DB'])
X=VIX['VIX'].values.astype(float)[-100:]
print(sm.tsa.stattools.adfuller(X))
X=sm.add_constant(X)
Y=VIX['DB'].values.astype(float)[-100:]
print(sm.tsa.stattools.adfuller(Y))
model=sm.OLS(Y,X)
model_fit=model.fit()
#print(model_fit.summary())
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
        df[j+'Scale']=df[j+'Spread'].apply(lambda x:(x-df[j+'Spread'].min())/(df[j+'Spread'].max()-df[j+'Spread'].min()))
def CDX_liq(i,ind):
    DF_templist = DFdict[i]
    DF_temp = DF_templist[ind].merge(VIX, how='inner', left_on='Date', right_on='Date')
    X = DF_temp['VIX'].values.astype(float)
    print(sm.tsa.stattools.adfuller(X))
    X = sm.add_constant(X)
    Y = DF_temp[namedict[i][ind] + 'Spread'].values
    print(sm.tsa.stattools.adfuller(Y))
    org = sm.OLS(Y, X)
    model = org.fit()
    print(model.summary())
    return model.params
CDX_liq('5Y',1)