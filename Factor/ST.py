import xlrd
import xlwt
import pandas as pd

data=xlrd.open_workbook("derive_stpt_list.xlsx")
sheet=data.sheet_by_name('derive_stpt_list')
data1=xlwt.Workbook()
sheet1=data1.add_sheet(u'sheet1')

datelist=sheet.col_values(1)
stocklist=sheet.col_values(4)
SNamelist=[]
Slist=[]
Flist=[]
SDate=["0430","0830","1031"]
def searfunc(datelist,i):
    try:
        return datelist.index(i)
    except(ValueError):
        return searfunc(datelist,i-1)
for i in SDate:
    SNamelist.append(int('2009'+i))
for i in range(22):
    SNamelist.append(int("201"+str(i//3)+SDate[i%3]))
for i in SNamelist:
    try:
        A=datelist.index(i)
        Slist.append(searfunc(datelist,i))
    except(ValueError):
        Slist.append(searfunc(datelist,i)+1)
for i in Slist:
    A=stocklist[i].split(";")
    Flist.append(A)
for i in range(0,len(Flist)):
    sheet1.write(i,0,datelist[Slist[i]])
    for j in range(0,len(Flist[i])):
        sheet1.write(i,j+1,Flist[i][j])

data1.save('PT.xls')
DF=pd.read_csv('F.csv')    
   
        
        
