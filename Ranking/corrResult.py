#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: ericyuan
"""
from regAnalyst.corr import Corr
import pandas as pd
import numpy as np
from datetime import datetime

def chgprice(s):
    return float(''.join(s.split(',')))

def chgtime(s, form):
    return datetime.strptime(s, form)


sector = pd.read_excel('sector.xlsx')
sp500 = pd.read_csv('S&P500.csv')
sp500 = sp500[['date', 'close']]
sp500['close'] = sp500['close'].map(chgprice)

# log return of sector
sectorReturn = sector.drop('dates', axis = 1).apply(np.log).diff()
sectorReturn = sectorReturn.join(sector[['dates']]).dropna()
sectorReturn = sectorReturn.rename(index=str, columns={'dates': 'date'})

sp500Return = sp500.drop('date', axis = 1).apply(np.log).diff()
sp500Return = sp500Return.join(sp500[['date']]).dropna()
sp500Return['date'] = sp500Return['date'].map(lambda x: chgtime(x, '%Y-%m-%d'))

# join togther
alldata = pd.merge(sp500Return, sectorReturn, on = 'date')
allsectors = alldata.columns.drop(['date', 'close'])

# reduce martket effect
for eachSector in allsectors:
    alldata[eachSector] = alldata[eachSector] - alldata['close']

# correlation of sectors
SecCorr = Corr(sectorReturn)
result_secCorr = SecCorr.analyze()
print(result_secCorr)
SecCorr.visual()
result_secCorr.to_excel('corr_result.xlsx')

# correlation of sectors - S&P500
SecReduceCorr = Corr(alldata.drop('close', axis = 1))
result_redCorr = SecReduceCorr.analyze()
print(result_redCorr)
SecReduceCorr.visual()
result_redCorr.to_excel('corr_sp500_result.xlsx')

