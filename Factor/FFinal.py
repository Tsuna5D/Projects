import xlrd
import pandas as pd
import xlwt

data=xlrd.open_workbook('F.xlsx')
sheet=data.sheet_by_name(u'F')
data1=xlrd.open_workbook('ST.xls')
sheet2=data1.sheet_by_name(u'sheet1')
data2=xlrd.open_workbook('PT.xls')
sheet3=data2.sheet_by_name(u'sheet1')
data3=xlrd.open_workbook('上市日期.xlsx')
sheet4=data3.sheet_by_name(u'Sheet1')
Final=xlwt.Workbook()
sheet1=Final.add_sheet('Sheet1')
class Stock(str):
    def __init__(self,name):
        self.name=name
        self.F=[]
        self.date=0
    def construct(self,col,date):
        self.F=col
        self.date=date

Stocklist=[]
Finallist=[]
Stocklist1=[]
stocklist=sheet.col_values(0)

j=0
del stocklist[0]
datelist=sheet4.col_values(1)
choosedate=sheet4.col_values(2)
choosedate=choosedate[0:22]
for i in range(0,len(stocklist)):
    A=Stock(stocklist[i])
    F=sheet.row_values(i+1)
    del F[0]
    A.construct(F,datelist[i])
    Stocklist.append(A)
for i in range(1,sheet.ncols-1):
    if i%4!=0:
        for k in range(0,len(Stocklist)):
            if Stocklist[k].date<choosedate[i-1-(i//4)]:
                Stocklist1.append(Stocklist[k])
        Stocklist1.sort(key=lambda stock:stock.F[i-1],reverse=True)
        STlist=sheet2.row_values(j)
        del STlist[0]
        PTlist=sheet3.row_values(j)
        del PTlist[0]
        STlist.extend(PTlist)
        for name in STlist:
            try:
                Stocklist1.remove(name)
            except(ValueError):
                pass
        Namelist=Stocklist1[0:50]
        Finallist.append(Namelist)
        j+=1
        Stocklist1=[]
    else:
        pass
for i in range(0,len(Finallist)):
    for j in range(0,50):
        sheet1.write(j+1,i,Finallist[i][j])
Final.save('Fchoice.xls')
        

