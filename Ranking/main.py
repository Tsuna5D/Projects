#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: ericyuan
"""
from regAnalyst.regression import Reg
from regAnalyst.preprocess import Outlier
from regAnalyst.evaluation import rollingReg

import pandas as pd
import numpy as np
from sklearn import preprocessing
import matplotlib.pyplot as plt
import seaborn as sns

import warnings
warnings.filterwarnings('ignore')

# from index name based on dict, get industry and rating
def getX(name, dicty):
    res = dicty[dicty['code'] == name]['name'].values[0].split(' ')
    ind = res[0]
    rating = res[1]
    return(ind, rating)
# parameters estimation
def est(data, indexName, dicty):
    ind, rating = getX(indexName, dicty)
    bondReg = Reg()
    try:
        resUtilitiesBBB = bondReg.ols(x = data[[ind, rating]], y = data[indexName])
        return(resUtilitiesBBB.coefs[0], ind + ' ' + rating, indexName, \
               resUtilitiesBBB.e1, resUtilitiesBBB.e2, resUtilitiesBBB.r2)
    except:
        return 0
def bondplot(industry, rating, index, data):
    reg = Reg()
    res = reg.ols(data[[industry, rating]], data[index])
    # plt.scatter(new_df['IGUUIA3M Index'], res.fitted.T.tolist()[0])
    sns.regplot(data[index], np.array(res.fitted.T.tolist()[0]))
    print(np.corrcoef(data[index], np.array(res.fitted.T.tolist()[0])))
    plt.show()
    plotdata = pd.DataFrame({'x': data[index], 'y': res.fitted.T.tolist()[0]})
    plotdata.index = data['date']
    return plotdata

# ------------------- 1. load data ------------------- #
# load data
rating = pd.read_excel('rating.xlsx')
sector = pd.read_excel('sector.xlsx')
alldata = pd.read_excel('alldata2.xlsx')
dicty = pd.read_excel('dict_bond_index.xlsx')
dicty = dicty[dicty['type'] != 0]
# merge & dropna
rating_sec = pd.merge(rating, sector, on = 'dates')
data = pd.merge(rating_sec, alldata, on = 'dates')
data = data.dropna()
# find intersection
bond_index = list(set(data.columns) & set(dicty['code'].values))
rating = list(rating.columns)
sector = list(sector)
inner = list(set(bond_index + rating + sector))
data = data[inner]
# diff
newdata = data.drop('dates', axis = 1)
newdata = newdata.shift(-1) / newdata - 1
newdata['date'] = data['dates']
newdata['dates'] = data['dates']
newdata = newdata.dropna()

# ----------------- 2. preprocess data ----------------- #
# standardize
scaler = preprocessing.StandardScaler().fit(newdata.drop(['date', 'dates'], axis = 1).values)
new_df1 = scaler.transform(newdata.drop(['date', 'dates'], axis = 1).values) 
new_df1 = pd.DataFrame(new_df1, columns = newdata.columns.drop(['dates', 'date']).tolist())
new_df1 = new_df1.join(newdata[['date']])
# remove outliers
bondOut = Outlier(data = new_df1)
new_df = bondOut.box(col = new_df1.columns.drop(['date']).tolist(), 
                        drawback = False, up_bound = 3.5, low_bound = -3.5)
new_df.head()
print('the precentage data we use {0}'.format(len(new_df)/len(new_df1)))

# ---------- 3. several examples for regression analysis ----------- #
case1 = bondplot('Industrials', 'BB', 'IGUUI53M Index', new_df)
case2 = bondplot('Industrials', 'A', 'IGUUIA3M Index', new_df)

# ----------------- 4. final result ----------------- #
estRes = dicty.iloc[0:28,]['code'].map(lambda x: est(new_df, x, dicty))
indRes = estRes.map(lambda x: x[0][0] if x != 0 else 0)
ratingRes = estRes.map(lambda x: x[0][1] if x != 0 else 0)
name = estRes.map(lambda x: x[1] if x != 0 else 0)
indexname = estRes.map(lambda x: x[2] if x != 0 else 0)
r2 = estRes.map(lambda x: x[5] if x != 0 else 0)
# corr = estRes.map(lambda x: x[6] if x != 0 else 0)
resDf = pd.DataFrame({'ratingCoef': ratingRes, 'indRes': indRes, 'name': name, \
                      'indexname': indexname, 'r2': r2})
print(resDf[resDf['indRes'] != 0].sort_values(by = 'r2', ascending = False))

# ----------------- 5. Kalman filter ----------------- #
#bondKalman = Kalman(case2)
#bondKalmanRes = bondKalman.analysis('x', 'y', visual = True)

# ----------------- 6. Rolling plot ----------------- #
new_df.index = range(len(new_df))
startpoint = 0
endpoint = 500
step = 10
rollingReg(end = endpoint, step = 10, data = new_df, \
           x = ['Industrials', 'BB'], y = 'IGUUI53M Index')
