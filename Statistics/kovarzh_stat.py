# Created by Gubanov Alexander (aka Derzhiarbuz) at 26.11.2019
# Contacts: derzhiarbuz@gmail.com

import pandas as pd
import numpy as np
import math
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.decomposition import PCA

# Первая задача
# nonaz_df = pd.read_csv('D:/BigData/Galina_Kovarzh/Nenatsionalnye.csv',
#                        sep=';', decimal=',', encoding='windows-1251', index_col=0)
# nonaz_df.drop(nonaz_df.columns[24], axis=1, inplace=True)
# naz_df = pd.read_csv('D:/BigData/Galina_Kovarzh/Natsionalnye.csv',
#                      sep=';', decimal=',', encoding='windows-1251', index_col=0)
# naz_df.drop(naz_df.columns[24], axis=1, inplace=True)

# print(nonaz_df)
# print(naz_df)
# nonaz_corr = nonaz_df.corr().iloc[0:19, 19:]
# naz_corr = nonaz_df.corr().iloc[0:19, 19:]
#
#
# nonaz_corr.to_csv('D:/BigData/Galina_Kovarzh/nonaz_corr.csv')
# naz_corr.to_csv('D:/BigData/Galina_Kovarzh/naz_corr.csv')

# Вторая задача
nonaz_df = pd.read_csv('D:/BigData/Galina_Kovarzh/Nenatsionalnye_2.csv',
                       sep=';', decimal=',', encoding='windows-1251', index_col=0)
naz_df = pd.read_csv('D:/BigData/Galina_Kovarzh/Natsionalnye_2.csv',
                     sep=';', decimal=',', encoding='windows-1251', index_col=0)

print(nonaz_df)
print(naz_df)
nonaz_corr = nonaz_df.corr().iloc[0:19, 20:29]
naz_corr = naz_df.corr().iloc[0:19, 20:29]

nonaz_corr.to_csv('D:/BigData/Galina_Kovarzh/nonaz_2_corr.csv')
naz_corr.to_csv('D:/BigData/Galina_Kovarzh/naz_2_corr.csv')

nonaz_df.drop(nonaz_df.columns[35], axis=1, inplace=True)
nonaz_df.drop(nonaz_df.columns[29], axis=1, inplace=True)
nonaz_df.drop(nonaz_df.columns[19], axis=1, inplace=True)
naz_df.drop(naz_df.columns[35], axis=1, inplace=True)
naz_df.drop(naz_df.columns[29], axis=1, inplace=True)
naz_df.drop(naz_df.columns[19], axis=1, inplace=True)
nonaz_corr = abs(nonaz_df.corr())
naz_corr = abs(naz_df.corr())
nonaz_corr.to_csv('D:/BigData/Galina_Kovarzh/Corr_graph_nonaz_2_summary.csv')
naz_corr.to_csv('D:/BigData/Galina_Kovarzh/Corr_graph_naz_2_summary.csv')

# print(nonaz_df.shape)
for j in range(2):
    plt.figure(figsize=(14, 14))
    x_nonaz = nonaz_df.iloc[:, j]
    x_naz = naz_df.iloc[:, j]
    x_name = x_naz.name[:20]
    print(x_naz.name + '   (синий - ненациональные, оранжевый - национальные)')
    max1 = x_nonaz.max()
    max2 = x_naz.max()
    min1 = x_nonaz.min()
    min2 = x_naz.min()
    if max2 > max1:
        max1 = max2
    if min2 < min1:
        min1 = min2
    marg = (max1 - min1) * 0.05
    for i in range(22):
        y_nonaz = nonaz_df.iloc[:, 19 + i]
        y_naz = naz_df.iloc[:, 19 + i]
        y_name = y_naz.name[:12] + '..' + y_naz.name[-12:]
        if i % 4 == 0:
            plt.subplot(6, 4, i + 1, xlabel=y_name, ylabel=x_name, xticklabels=[])
        else:
            plt.subplot(6, 4, i + 1, xlabel=y_name, xticklabels=[], yticklabels=[])
        plt.ylim([min1 - marg, max1 + marg])
        plt.scatter(y_nonaz, x_nonaz)
        plt.scatter(y_naz, x_naz)
    plt.show()

def centralize_frame(dframe: pd.DataFrame):
    result = pd.DataFrame(index=dframe.index, columns=dframe.columns)
    means = np.zeros(result.shape[1])
    for index, row in dframe.iterrows():
        for i in range(dframe.shape[1]):
            means[i] += row[i]
    means /= dframe.shape[0]
    for index, row in result.iterrows():
        for i in range(result.shape[1]):
            row[i] = dframe[dframe.columns[i]][index] - means[i]
    return result

def normalize_frame(dframe: pd.DataFrame):
    result = centralize_frame(dframe)
    stderrs = np.zeros(result.shape[1])
    for index, row in result.iterrows():
        for i in range(result.shape[1]):
            stderrs[i] += row[i] ** 2
    stderrs /= result.shape[0]
    for i in range(result.shape[1]):
        stderrs[i] = math.sqrt(stderrs[i])
    for index, row in result.iterrows():
        for i in range(result.shape[1]):
            row[i] /= stderrs[i]
    return result

def correlate_frames(df1: pd.DataFrame, df2: pd.DataFrame):
    mydf1 = normalize_frame(df1)
    mydf2 = normalize_frame(df2)
    result = pd.DataFrame(index=mydf1.columns, columns=mydf2.columns)
    for index, row in result.iterrows():
        for col in result.columns:
            result[col][index] = 0
            for i in mydf1.index:
                result[col][index] += mydf1[index][i] * mydf2[col][i]
            result[col][index] /= mydf1.shape[0]
    return result

# nonaz_internet = nonaz_df.iloc[:, :19]
# nonaz_rosstat = nonaz_df.iloc[:, 19:]
# naz_internet = naz_df.iloc[:, :19]
# naz_rosstat = naz_df.iloc[:, 19:]
#
# # print(correlate_frames(nonaz_rosstat, nonaz_rosstat))
# # print(nonaz_rosstat.corr())
#
# rosstat = normalize_frame(nonaz_rosstat)
# pca = PCA(n_components=5)
# pca.fit(rosstat)
# print(pca.explained_variance_ratio_)
# rosstat_trans = pd.DataFrame(data=pca.transform(rosstat), index=nonaz_rosstat.index,
#                              columns=range(5))
# plt.bar(range(len(pca.explained_variance_ratio_)), pca.explained_variance_ratio_)
# plt.show()
#
# internet = normalize_frame(nonaz_internet)
# pca = PCA(n_components=8)
# pca.fit(internet)
# print(pca.explained_variance_ratio_)
# internet_trans = pd.DataFrame(data=pca.transform(internet), index=nonaz_internet.index,
#                              columns=range(8))
# plt.bar(range(len(pca.explained_variance_ratio_)), pca.explained_variance_ratio_)
# plt.show()
#
# pca_corr = correlate_frames(internet_trans, rosstat_trans)
# print(pca_corr)
# pca_corr.to_csv('D:/BigData/Galina_Kovarzh/nonaz_pca_corr.csv')
