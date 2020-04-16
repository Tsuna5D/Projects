import xlrd
import csv

data=xlrd.open_workbook('ROEchoice.xls')
sheet=data.sheet_by_name('Sheet1')

list1=[]
list2=[]
for i in range(0,sheet.nrows):
    for j in range(1,sheet.ncols):
        A=str(int(sheet.row_values(i)[0]))+' '+sheet.row_values(i)[j]
        list2.append(A)
        list1.append(list2)
        list2=[]
with open('ROEFinal.csv','w') as csvfile:
    writer=csv.writer(csvfile)
    writer.writerows(list1)
