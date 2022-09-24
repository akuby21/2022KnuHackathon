from cmath import nan
from SQLPkg.CRUD import Landmark_CRUD
import pandas as pd
import numpy as np
from pprint import pprint
import time

SCHEMA = 'landmark'
TABLE = 'place'

crud = Landmark_CRUD('azureuser')

df = pd.read_csv('data.csv', sep=',', header = None)
datas = list(df.values)
print(type(datas[2][3]) is type(0.0))

for (i, component) in enumerate(datas):
    if type(component[0]) is type('') and i!=0:
        component[0] = component[0][:-2]
        for j, a in enumerate(component):
            if (type(a) is type(0.0)):
                component[j] = ''
        datas[i] = component



for i,data in enumerate(datas):
    if i is not 0 and type(data[0]) is not type(0.0):
        crud.insert(SCHEMA, TABLE, data[0], data[1], data[2], data[3], data[4], data[5], data[6], data[7])
        time.sleep(0.1)