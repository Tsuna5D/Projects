import pandas as pd
DF=pd.read_excel("CalculatorData.xlsx")
DF['PROFIT_OR_LOSS']=0
groups=DF.groupby('SYMBOL')
res={}
stock_stack=[]
opttype={'BUY':-1,'SELL':1,'SHORT':1}
exchange={'BUY':['SELL','SHORT'],'SELL':['BUY'],'SHORT':['BUY']}

def calculation(x):
    x=x.reset_index()
    side=x.ix[0,'SIDE']
    stock_stack = []
    stock_stack.append([x.ix[0,'QTY'], x.ix[0, 'PRICE']])
    for i in range(1,x.shape[0]):
        quan_new = x.ix[i, 'QTY']
        price_new = x.ix[i, 'PRICE']
        if x.ix[i,'SIDE'] in exchange[side]:
            profit=0
            while stock_stack and quan_new-stock_stack[-1][0]>=0:
                quan,price=stock_stack.pop()
                quan_new-=quan
                profit += quan * (price_new - price) * opttype[x.ix[i, 'SIDE']]
            if stock_stack:
                profit += quan_new * (price_new - stock_stack[-1][1]) * opttype[x.ix[i, 'SIDE']]
                stock_stack[-1][0]-=quan_new
            else:
                stock_stack.append([quan_new,price_new])
                side=x.ix[i,'SIDE']
            x.ix[i, 'PROFIT_OR_LOSS'] = profit
        else:
            stock_stack.append([quan_new, price_new])
    return x
res=[]

df1=groups.apply(calculation)
df1.index=df1['index']
df1=df1.sort_index().drop('index',axis=1)

#df1.to_csv('res.csv')
print(df1)
