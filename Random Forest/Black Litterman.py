import pandas as pd
import numpy as np
import statsmodels.api as sm

def covariance(stocks,timepoint,min=2520,flag=0):
    all_returns=[]
    for i in stocks:
        DF = pd.read_csv('D:\Formal\PythonCode\\temp' + i, index_col=0)
        idx_list = DF[DF['date'] == timepoint.strftime('%Y-%m-%d')].index.tolist()
        idx=idx_list[0]
        if idx>=min:
            returns=DF.loc[idx-min:idx,['RET']].values.flatten()
        else:
            returns=DF.loc[0:idx,['RET']].values.flatten()
            min=idx
        for i in range(len(returns)):
            try:
                returns[i]=float(returns[i])
            except:
                returns[i]=0
        all_returns.append(returns.astype(float))
    if flag:
        print(all_returns)
    for i in range(len(all_returns)):
        if len(all_returns[i])>min:
            all_returns[i]=all_returns[i][len(all_returns[i])-min:len(all_returns[i])]
    return np.cov(np.nan_to_num(np.array(all_returns)))*21

def prior_rate(risk_coeffcient,covariance,weights=None):
    if not weights:
        temp_weights=[1/len(covariance) for i in range(len(covariance))]
        temp_weights=np.array(temp_weights)
    else:
        temp_weights=np.array(weights)
    return risk_coeffcient*np.dot(covariance,temp_weights.T)
def reg(stock):
    DF_stock=pd.read_csv('D:\Formal\PythonCode\\temp' + stock, index_col=0)
    DF = pd.read_csv('GSPC.csv')
    DF['Date']=DF['Date'].apply(lambda x:conv_date(x))
    DF_total=DF.merge(DF_stock,left_on='Date',right_on='date')
    DF_total=DF_total.dropna(subset=['RET'])
    X = DF_total.loc[:2000, ['RET']].values.flatten()
    for i in range(len(X)):
        try:
            X[i] = float(X[i])
        except:
            X[i] = 0
    X = X.astype(float)
    Y = DF_total.loc[:2000, ['S&P_ret']].values.flatten().astype(float)
    temp_X = []
    temp_Y = []
    for i in range(len(X) // 21):
        temp_X.append(np.prod(X[i * 21:(i + 1) * 21] + 1)-1)
        temp_Y.append(np.prod(Y[i * 21:(i + 1) * 21] + 1)-1)
    Y = np.array(temp_Y).astype(float)
    X = np.array(temp_X).astype(float)
    X = sm.add_constant(X)
    model = sm.OLS(Y, X)
    res = model.fit()
    return DF_total,res
def SP_forecast():
    SP=pd.read_csv('GSPC.csv')
    Y = SP.loc[:2000, ['S&P_ret']].values.flatten().astype(float)
    temp_Y = []
    for i in range(len(Y) // 21):
        temp_Y.append(np.prod(Y[i * 21:(i + 1) * 21] + 1)-1)
    Y = np.array(temp_Y).astype(float)
    return np.var(Y),np.mean(Y)
def conv_date(x):
    temp=x.split('/')
    if int(temp[0])<10:
        temp[0]='0'+temp[0]
    if int(temp[1])<10:
        temp[1]='0'+temp[1]
    return '-'.join([temp[2],temp[0],temp[1]])

def produce_weights(stocks,timepoint,period,shrinkage,risk_averse,models_mem):
    cov=covariance(stocks,timepoint,period)
    prior_cov=np.identity(len(stocks))
    ind=0
    views=np.zeros(len(stocks))
    SP_var,SP_pred=SP_forecast()
    for i in stocks:
        if i not in models_mem.keys():
            model = reg(i)[1]
            models_mem[i]=model
        else:
            model=models_mem[i]
        views[ind]=model.predict([1,SP_pred])
        prior_cov[ind,ind]=np.var(model.resid)+(model.params[1]**2)*SP_var
        ind+=1
    prior_expect_rate=prior_rate(risk_averse, cov)
    shrink_cov=np.linalg.inv(shrinkage*cov)
    posterior_rate=np.dot(np.linalg.inv(shrink_cov+np.linalg.inv(prior_cov)),np.dot(shrink_cov,prior_expect_rate.T)+np.dot(np.linalg.inv(prior_cov),views.T))
    weights=np.dot(np.linalg.inv(risk_averse*cov),posterior_rate.T)
    for i in range(len(weights)):
        if weights[i]<=0:
            weights[i]=0
    return weights/np.sum(weights)

def produce_cap_weights(stocks,timepoint,period,shrinkage,risk_averse,models_mem):
    weights=produce_weights(stocks,timepoint,period,shrinkage,risk_averse,models_mem)
    weights=np.where(weights<0.1,weights,0.1)
    extra=1-np.sum(weights)
    return weights+extra/20
