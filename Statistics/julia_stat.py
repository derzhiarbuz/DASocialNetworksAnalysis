# Created by Gubanov Alexander (aka Derzhiarbuz) at 21.02.2020
# Contacts: derzhiarbuz@gmail.com

import pandas as pd
import numpy as np

df = pd.read_csv('D:/BigData/Galina_Kovarzh/Raschety_vliania.csv',
                       sep=';', decimal=',', encoding='windows-1251', index_col=0)
print(df)
for i in range(len(df.columns)):
    print(str(i) + '  ' + str(df.columns[i]))
print(df.dtypes)