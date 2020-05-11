# Created by Gubanov Alexander (aka Derzhiarbuz) at 24.04.2020
# Contacts: derzhiarbuz@gmail.com

import pandas as pd
import numpy as np
from scipy import stats

df = pd.read_csv('D:/BigData/Galina_Kovarzh/Sots-ekonom_pokazateli_naselenie.csv',
                       sep=';', decimal=',', thousands=' ', encoding='windows-1251', index_col=0)

print(df)
for i in range(len(df.columns)):
    print(str(i) + '  ' + str(df.dtypes[i]) + '  ' + str(df.columns[i]))

print(df[df.columns[16]])

nasel = df[df.columns[24]]

df[df.columns[1]] = df[df.columns[1]]/nasel
df[df.columns[16]] = df[df.columns[16]]/nasel
df[df.columns[18]] = df[df.columns[18]]/nasel
df[df.columns[19]] = df[df.columns[19]]/nasel
df[df.columns[20]] = df[df.columns[20]]/nasel
df[df.columns[24]] = df[df.columns[24]]/nasel
df[df.columns[26]] = df[df.columns[26]]/nasel
df[df.columns[27]] = df[df.columns[27]]/nasel
df[df.columns[28]] = df[df.columns[28]]/nasel
df[df.columns[29]] = df[df.columns[29]]/nasel
df[df.columns[30]] = df[df.columns[30]]/nasel
df[df.columns[31]] = df[df.columns[31]]/nasel
df[df.columns[32]] = df[df.columns[32]]/nasel
df[df.columns[33]] = df[df.columns[33]]/nasel
df[df.columns[34]] = df[df.columns[34]]/nasel
df[df.columns[36]] = df[df.columns[36]]/nasel
df[df.columns[37]] = df[df.columns[37]]/nasel
df[df.columns[40]] = df[df.columns[40]]/nasel
df[df.columns[41]] = df[df.columns[41]]/nasel
df[df.columns[42]] = df[df.columns[42]]/nasel

# for i in range(len(df.index)):
#     print(str(df.index[i]) + ' ' + str(df[df.columns[24]][i]) + ' ' + str(df[df.columns[16]][i]))
# print(df[df.columns[24]])
# print(df[df.columns[16]])
# print(stats.spearmanr(df[df.columns[24]], df[df.columns[16]], nan_policy='omit').correlation)

corr = stats.spearmanr(df, nan_policy='omit')
# corrp = df.corr().values
# corrdiff = np.zeros(corr.correlation.shape)
#
for i in range(corr.correlation.shape[0]):
    for j in range(corr.correlation.shape[1]):
        #corrdiff[i][j] = abs(corr.correlation[i][j]-corrp[i][j])
        if abs(corr.pvalue[i][j]) >= 0.05:
            corr.correlation[i][j] = np.nan
        #print(str(corr.correlation[i][j]) + '  ' + str(corr.pvalue[i][j]))

#
df_corr = pd.DataFrame(corr.correlation, df.columns, df.columns)
# df_corrdiff = pd.DataFrame(corrdiff, df.columns, df.columns)
print(df_corr)
df_corr.to_csv('D:/BigData/Galina_Kovarzh/Sots-ekonom_pokazateli_naselen_corr.csv')


