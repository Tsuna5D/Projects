import pymongo
import pandas as pd
from bson.objectid import ObjectId
'''
liq=pd.read_csv('Liq_data.csv',index_col=0)
asset_map=pd.read_csv('possible_asset_withmap.csv',index_col=0)
asset_color_map=asset_map[['id','Color']]
liq_values=[]
for i in liq.columns:
    liq_values.append(liq[i].values[-25:])

columns=['LiquidityData_'+str(i) for i in range(1,26)]
res=pd.DataFrame(liq_values,columns=columns)
res['id']=liq.columns
res=res.merge(asset_color_map,how='inner',left_on='id',right_on='id')
res.to_csv('Liq_data_part.csv')
print(res)
'''
liq=pd.read_csv('Liq_data_part.csv',index_col=0)

#myclient = pymongo.MongoClient(host='localhost', port=27017)
#mydb = myclient["bam"]
#mycol = mydb["assets"]
liq_dict={}
for i in range(len(liq)):
    for j in liq.columns:
        liq_dict[j]=liq.ix[i,j]
    id_temp=liq_dict['id']
    del liq_dict['id']
    print(liq_dict)
    #mycol.update_many({"_id": ObjectId(id_temp)}, {"$set": liq_dict})
