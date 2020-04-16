import math
import talib

import numpy as np
import pandas as pd
from pandas import Series
import seaborn as sns
sns.set_style('white')

import scipy as sp
import scipy.optimize

import datetime
import calendar

import matplotlib.pyplot as plt
from matplotlib.finance import candlestick2_ochl

def plotKLine(open,close,high,low,tech):
    
    fig = plt.figure(figsize=(30, 15))
    y=len(close)
    date = np.linspace(0,y,y)
    candleAr = []
    ax1 = plt.subplot2grid((10,4),(0,0),rowspan=5,colspan=4)
    candlestick2_ochl(ax1,open,close,high,low,width=1,colorup='r',colordown='g', alpha=0.75)
    ax2 = plt.subplot2grid((10,4),(5,0),rowspan=4,colspan=4,sharex=ax1)
    if 'ATR' in tech.keys():
        ax2.plot(date, tech['ATR'],'-b')
    if 'ad_ATR' in tech.keys():
        ax2.plot(date, tech['ad_ATR'],'-r')
    if 'my_ATR' in tech.keys():
        ax2.plot(date, tech['my_ATR'],'-m')
    if 'short_ATR' in tech.keys():
        ax2.plot(date, tech_1['short_ATR'],'-b')
    if 'long_ATR' in tech.keys():
        ax2.plot(date, tech_1['long_ATR'],'-r')
    if 'close' in tech.keys():
        ax2.plot(date,tech_2['close'],'-b')
    if 'upper' in tech.keys():
        ax2.plot(date,tech_2['upper'],'-r')
    if 'lower' in tech.keys():
        ax2.plot(date,tech_2['lower'],'-r')

#按公式计算ATR        
def get_myATR(data):
    df = pd.DataFrame()
    df['HL'] = abs(data['high'] - data['low'])
    df['HCL'] = abs(data['high'] - data['preclose'])
    df['CLL'] = abs(data['preclose'] - data['low'])
    df['my_ATR'] = pd.rolling_mean(df.max(axis=1),window=10)
    return df['my_ATR'].values

data=pd.read_csv('APR.csv')
a = list(data['close'][:-1])
a.insert(0,0)
data['preclose']=a
data = data[data.preclose>0]
tech={}
open = data['open'].values
high = data['high'].values
low = data['low'].values
close = data['close'].values
preclose = data['preclose'].values
tech['ad_ATR']= talib.ATR(high,low,preclose,10)
tech['ATR'] = talib.ATR(high,low,close,10)
tech['my_ATR'] =  get_myATR(data)
plotKLine(open,close,high,low,tech)
