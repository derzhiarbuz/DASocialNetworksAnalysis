# Created by Gubanov Alexander (aka Derzhiarbuz) at 21.02.2020
# Contacts: derzhiarbuz@gmail.com

import pandas as pd
import numpy as np
from sklearn.decomposition import PCA
from sklearn.decomposition import FactorAnalysis
import Statistics.kovarzh_stat as ks
from scipy import stats
from matplotlib import pyplot as plt
import math

df = pd.read_csv('D:/BigData/Galina_Kovarzh/Sots_pokazateli_aktivn.csv',
                       sep=';', decimal=',', thousands=' ', encoding='windows-1251', index_col=0)
df2 = pd.read_csv('D:/BigData/Galina_Kovarzh/Sots-ekonom_pokazateli_aktivn.csv',
                       sep=';', decimal=',', thousands=' ', encoding='windows-1251', index_col=0)

print(df)
for i in range(len(df.columns)):
    print(str(i) + '  ' + str(df.dtypes[i]) + '  ' + str(df.columns[i]))

print(df2)
for i in range(len(df2.columns)):
    print(str(i) + '  ' + str(df2.dtypes[i]) + '  ' + str(df2.columns[i]))

print(df[df.columns[16]])
print(df2[df2.columns[25]])

nasel = df[df.columns[24]]
nasel2 = df2[df2.columns[30]] #32 for naselen, 30 for active

df[df.columns[0]] = df[df.columns[0]]/nasel
df[df.columns[2]] = df[df.columns[2]]/nasel
df[df.columns[3]] = df[df.columns[3]]/nasel
df[df.columns[4]] = df[df.columns[4]]/nasel
df[df.columns[5]] = df[df.columns[5]]/nasel
df[df.columns[6]] = df[df.columns[6]]/nasel
df[df.columns[7]] = df[df.columns[7]]/nasel
df[df.columns[8]] = df[df.columns[8]]/nasel
df[df.columns[9]] = df[df.columns[9]]/nasel
df[df.columns[10]] = df[df.columns[10]]/nasel
df[df.columns[12]] = df[df.columns[12]]/nasel
df[df.columns[13]] = df[df.columns[13]]/nasel
df[df.columns[14]] = df[df.columns[14]]/nasel
df[df.columns[19]] = df[df.columns[19]]/nasel
df[df.columns[20]] = df[df.columns[20]]/nasel
df[df.columns[21]] = df[df.columns[21]]/nasel

df2[df2.columns[1]] = df2[df2.columns[1]]/nasel2
df2[df2.columns[16]] = df2[df2.columns[16]]/nasel2
df2[df2.columns[18]] = df2[df2.columns[18]]/nasel2
df2[df2.columns[19]] = df2[df2.columns[19]]/nasel2
df2[df2.columns[20]] = df2[df2.columns[20]]/nasel2
df2[df2.columns[23]] = df2[df2.columns[23]]/nasel2
df2[df2.columns[26]] = df2[df2.columns[26]]/nasel2
df2[df2.columns[27]] = df2[df2.columns[27]]/nasel2 #29 for naselen, 27 for active

for i in range(len(df.index)):
    print(str(df.index[i]) + ' ' + str(df[df.columns[24]][i]) + ' ' + str(df[df.columns[16]][i]) + '  -----  ' +
          str(df2.index[i]) + ' ' +  str(df2[df2.columns[30]][i]) + ' ' + str(df2[df2.columns[25]][i]))
print(df[df.columns[24]])
print(df[df.columns[16]])
print(stats.spearmanr(df[df.columns[24]], df[df.columns[16]], nan_policy='omit').correlation)
print(df2[df2.columns[30]])
print(df2[df2.columns[25]])
print(stats.spearmanr(df2[df2.columns[30]], df2[df2.columns[25]], nan_policy='omit').correlation)

# df[df.columns[18]][48] = np.nan
# for i in range(df.shape[0]):
#     df[df.columns[9]][i] = math.log(df[df.columns[9]][i])
#     df[df.columns[10]][i] = math.log(df[df.columns[10]][i])
#     df[df.columns[12]][i] = math.log(df[df.columns[12]][i])
#     df[df.columns[19]][i] = math.log(df[df.columns[19]][i])
#     df[df.columns[20]][i] = math.log(df[df.columns[20]][i])
#     df[df.columns[22]][i] = math.log(df[df.columns[22]][i])
#     df[df.columns[24]][i] = math.log(df[df.columns[24]][i])
#     df[df.columns[27]][i] = math.log(1+df[df.columns[27]][i])
#     df[df.columns[30]][i] = math.log(1+df[df.columns[30]][i])
#     df[df.columns[31]][i] = math.log(1+df[df.columns[31]][i])
#     df[df.columns[32]][i] = math.log(1+df[df.columns[32]][i])
#     df[df.columns[33]][i] = math.log(1+df[df.columns[33]][i])
#
greens = df.iloc[:, :14].copy()
greens = greens.fillna(greens.mean())
greens = ks.normalize_frame(greens)

whites = df.iloc[:, 15:].copy()
whites = whites.fillna(whites.mean())
whites = ks.normalize_frame(whites)
#
# def makefac(df, ncomp, csv_path, comp_name=""):
#     pca_df = PCA(n_components=ncomp)
#     pca_df.fit(df)
#     print(pca_df.explained_variance_ratio_.sum())
#     fac_df = FactorAnalysis(n_components=ncomp, svd_method='lapack')
#     fac_df.fit(df)
#     fac_df_df = pd.DataFrame(fac_df.components_, columns=df.columns)
#     fac_df_df.to_csv(csv_path)
#     new_cols = []
#     for i in range(ncomp):
#         new_cols.append(comp_name + '_' + str(i))
#     trans_df = pd.DataFrame(fac_df.transform(df), index=df.index, columns=new_cols)
#     return trans_df
#
#
# greens_trans = makefac(greens, 4, 'D:/BigData/Galina_Kovarzh/Greens_factors.csv', 'Green')
# grays_trans = makefac(grays, 5, 'D:/BigData/Galina_Kovarzh/Grays_factors.csv', 'Gray')
# whites_trans = makefac(whites, 4, 'D:/BigData/Galina_Kovarzh/Whites_factors.csv', 'White')
# transformed = pd.concat([greens_trans, grays_trans, whites_trans], axis=1)
#
# print(greens_trans)
# print(grays_trans)
# print(whites_trans)
# print(transformed)
#
# corr_trans = stats.spearmanr(transformed, nan_policy='omit')
# for i in range(corr_trans.correlation.shape[0]):
#     for j in range(corr_trans.correlation.shape[1]):
#         if abs(corr_trans.pvalue[i][j]) >= 0.05:
#             corr_trans.correlation[i][j] = np.nan
# df_corr_trans = pd.DataFrame(corr_trans.correlation, transformed.columns, transformed.columns)
# df_corr_trans.to_csv('D:/BigData/Galina_Kovarzh/Fact_Julia_corr.csv')
#
# # for colname in transformed.columns:
# #     res = stats.normaltest(transformed[colname], nan_policy='omit')
# #     if res.pvalue >= 0.05:
# #         print(str(colname) + ' is normal')
# #     plt.hist(transformed[colname])
# #     plt.xlabel(colname)
# #     plt.show()
#
#
corr = stats.spearmanr(df, nan_policy='omit')
corr2 = stats.spearmanr(df2, nan_policy='omit')
# corrp = df.corr().values
# corrdiff = np.zeros(corr.correlation.shape)
#
for i in range(corr.correlation.shape[0]):
    for j in range(corr.correlation.shape[1]):
        #corrdiff[i][j] = abs(corr.correlation[i][j]-corrp[i][j])
        if abs(corr.pvalue[i][j]) >= 0.05:
            corr.correlation[i][j] = np.nan
        #print(str(corr.correlation[i][j]) + '  ' + str(corr.pvalue[i][j]))

for i in range(corr2.correlation.shape[0]):
    for j in range(corr2.correlation.shape[1]):
        #corrdiff[i][j] = abs(corr.correlation[i][j]-corrp[i][j])
        if abs(corr2.pvalue[i][j]) >= 0.05:
            corr2.correlation[i][j] = np.nan
#
df_corr = pd.DataFrame(corr.correlation, df.columns, df.columns)
df_corr2 = pd.DataFrame(corr2.correlation, df2.columns, df2.columns)
# df_corrdiff = pd.DataFrame(corrdiff, df.columns, df.columns)
print(df_corr)
print(df_corr2)
df_corr.to_csv('D:/BigData/Galina_Kovarzh/Sots_pokazateli_aktivn_corr.csv')
df_corr2.to_csv('D:/BigData/Galina_Kovarzh/Sots-ekonom_pokazateli_aktivn_corr.csv')
# df_corrdiff.to_csv('D:/BigData/Galina_Kovarzh/All_Julia_corrdiff.csv')
# abs(df_corr).to_csv('D:/BigData/Galina_Kovarzh/All_Julia_corr_abs.csv')
#
#
#
# # for colname in df.columns:
# #     for col2name in df.columns:
# #         corr = stats.spearmanr(df[colname], df[col2name], nan_policy='omit')
# #         if corr.pvalue < 0.01:
# #             print(str(corr.correlation) + ' ' + colname + ' ' + col2name)
# #         else:
# #             print(str(corr.correlation) + ' no corr')



