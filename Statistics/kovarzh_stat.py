# Created by Gubanov Alexander (aka Derzhiarbuz) at 26.11.2019
# Contacts: derzhiarbuz@gmail.com

import pandas as pd
import numpy as np
import math
import re
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.decomposition import PCA
from sklearn.decomposition import FactorAnalysis

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
# nonaz_df = pd.read_csv('D:/BigData/Galina_Kovarzh/Nenatsionalnye_2.csv',
#                        sep=';', decimal=',', encoding='windows-1251', index_col=0)
# naz_df = pd.read_csv('D:/BigData/Galina_Kovarzh/Natsionalnye_2.csv',
#                      sep=';', decimal=',', encoding='windows-1251', index_col=0)
#
# print(nonaz_df)
# print(naz_df)
# nonaz_corr = nonaz_df.corr().iloc[0:19, 20:29]
# naz_corr = naz_df.corr().iloc[0:19, 20:29]
#
# nonaz_corr.to_csv('D:/BigData/Galina_Kovarzh/nonaz_2_corr.csv')
# naz_corr.to_csv('D:/BigData/Galina_Kovarzh/naz_2_corr.csv')
#
# nonaz_df.drop(nonaz_df.columns[35], axis=1, inplace=True)
# nonaz_df.drop(nonaz_df.columns[29], axis=1, inplace=True)
# nonaz_df.drop(nonaz_df.columns[19], axis=1, inplace=True)
# naz_df.drop(naz_df.columns[35], axis=1, inplace=True)
# naz_df.drop(naz_df.columns[29], axis=1, inplace=True)
# naz_df.drop(naz_df.columns[19], axis=1, inplace=True)
# nonaz_corr = abs(nonaz_df.corr())
# naz_corr = abs(naz_df.corr())
# nonaz_corr.to_csv('D:/BigData/Galina_Kovarzh/Corr_graph_nonaz_2_summary.csv')
# naz_corr.to_csv('D:/BigData/Galina_Kovarzh/Corr_graph_naz_2_summary.csv')
#
# # print(nonaz_df.shape)
# for j in range(2):
#     plt.figure(figsize=(14, 14))
#     x_nonaz = nonaz_df.iloc[:, j]
#     x_naz = naz_df.iloc[:, j]
#     x_name = x_naz.name[:20]
#     print(x_naz.name + '   (синий - ненациональные, оранжевый - национальные)')
#     max1 = x_nonaz.max()
#     max2 = x_naz.max()
#     min1 = x_nonaz.min()
#     min2 = x_naz.min()
#     if max2 > max1:
#         max1 = max2
#     if min2 < min1:
#         min1 = min2
#     marg = (max1 - min1) * 0.05
#     for i in range(22):
#         y_nonaz = nonaz_df.iloc[:, 19 + i]
#         y_naz = naz_df.iloc[:, 19 + i]
#         y_name = y_naz.name[:12] + '..' + y_naz.name[-12:]
#         if i % 4 == 0:
#             plt.subplot(6, 4, i + 1, xlabel=y_name, ylabel=x_name, xticklabels=[])
#         else:
#             plt.subplot(6, 4, i + 1, xlabel=y_name, xticklabels=[], yticklabels=[])
#         plt.ylim([min1 - marg, max1 + marg])
#         plt.scatter(y_nonaz, x_nonaz)
#         plt.scatter(y_naz, x_naz)
#     plt.show()

def centralize_frame(dframe: pd.DataFrame):
    result = pd.DataFrame(index=dframe.index, columns=dframe.columns)
    means = np.zeros(result.shape[1])
    for index, row in dframe.iterrows():
        for i in range(dframe.shape[1]):
            #print(str())
            means[i] += float(row[i])
    means /= dframe.shape[0]
    for index, row in result.iterrows():
        for i in range(result.shape[1]):
            row[i] = float(dframe[dframe.columns[i]][index]) - means[i]
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
            if stderrs[i] != 0:
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

# Timewise correlation (Третья задача)
filename1 = 'D:/BigData/Galina_Kovarzh/Nenatsionalnye_timewise.csv'
n_subjects1 = 59
filename2 = 'D:/BigData/Galina_Kovarzh/Natsionalnye_timewise.csv'
n_subjects2 = 26

n_subjects = n_subjects1+n_subjects2

nonaz_df = pd.read_csv(filename1, sep=';', decimal=',', encoding='windows-1251', index_col=0)
nonaz_df = nonaz_df.iloc[:n_subjects1, :]
nonaz_df2 = pd.read_csv(filename2, sep=';', decimal=',', encoding='windows-1251', index_col=0)
nonaz_df2 = nonaz_df2.iloc[:n_subjects2, :]

nonaz_df2.columns = nonaz_df.columns

print(nonaz_df.columns)
print(nonaz_df2.columns)


nonaz_df = pd.concat([nonaz_df, nonaz_df2], axis=0, sort=False)
print(nonaz_df.columns)
print(nonaz_df)

nonaz_population = nonaz_df.iloc[:n_subjects, :1].copy()
nonaz_df.drop([nonaz_df.columns[0]], axis=1, inplace=True)

todrop_internet = []
todrop_stat = []
# for i in range(len(nonaz_df.columns)):
#     print(str(i) + '  ' + str(nonaz_df.columns[i]))

nonaz_internet = nonaz_df.iloc[:n_subjects, :247].copy()
nonaz_internet.drop(todrop_internet, axis=1, inplace=True)
nonaz_stat = nonaz_df.iloc[:1, 248:599].copy()

for i in range(len(nonaz_stat.columns)):
    print(str(i) + '  ' + str(nonaz_stat.columns[i]))

for i in range(len(nonaz_internet.columns)):
    if i%13 == 0:
        todrop_internet.append(nonaz_df.columns[i])

nonaz_internet.drop(todrop_internet, axis=1, inplace=True)

avg = .0
for i in range(0, 3):
    print(i)
    avg += nonaz_stat.iat[0, i]
avg /= 3.

nonaz_stat.insert(338, 'Индекс власти (ноябрь)', np.NaN)
nonaz_stat.insert(337, 'Индекс власти (сентябрь)', np.NaN)
nonaz_stat.insert(336, 'Индекс власти (июль)', np.NaN)
nonaz_stat.insert(335, 'Индекс власти (май)', np.NaN)
nonaz_stat.insert(334, 'Индекс власти (март)', np.NaN)
nonaz_stat.insert(333, 'Индекс власти (январь)', np.NaN)

nonaz_stat.insert(332, 'Индекс ожиданий (ноябрь)', np.NaN)
nonaz_stat.insert(331, 'Индекс ожиданий (сентябрь)', np.NaN)
nonaz_stat.insert(330, 'Индекс ожиданий (июль)', np.NaN)
nonaz_stat.insert(329, 'Индекс ожиданий (май)', np.NaN)
nonaz_stat.insert(328, 'Индекс ожиданий (март)', np.NaN)
nonaz_stat.insert(327, 'Индекс ожиданий (январь)', np.NaN)

nonaz_stat.insert(326, 'Индекс России (ноябрь)', np.NaN)
nonaz_stat.insert(325, 'Индекс России (сентябрь)', np.NaN)
nonaz_stat.insert(324, 'Индекс России (июль)', np.NaN)
nonaz_stat.insert(323, 'Индекс России (май)', np.NaN)
nonaz_stat.insert(322, 'Индекс России (март)', np.NaN)
nonaz_stat.insert(321, 'Индекс России (январь)', np.NaN)

nonaz_stat.insert(320, 'Индекс семьи (ноябрь)', np.NaN)
nonaz_stat.insert(319, 'Индекс семьи (сентябрь)', np.NaN)
nonaz_stat.insert(318, 'Индекс семьи (июль)', np.NaN)
nonaz_stat.insert(317, 'Индекс семьи (май)', np.NaN)
nonaz_stat.insert(316, 'Индекс семьи (март)', np.NaN)
nonaz_stat.insert(315, 'Индекс семьи (январь)', np.NaN)

nonaz_stat.insert(314, 'Индекс социальных настроений (ноябрь)', np.NaN)
nonaz_stat.insert(313, 'Индекс социальных настроений (сентябрь)', np.NaN)
nonaz_stat.insert(312, 'Индекс социальных настроений (июль)', np.NaN)
nonaz_stat.insert(311, 'Индекс социальных настроений (май)', np.NaN)
nonaz_stat.insert(310, 'Индекс социальных настроений (март)', np.NaN)
nonaz_stat.insert(309, 'Индекс социальных настроений (январь)', np.NaN)

nonaz_stat.insert(309, 'Индекс потребильских настроений (декабрь)', np.NaN)
nonaz_stat.insert(308, 'Индекс потребильских настроений (октябрь)', np.NaN)
nonaz_stat.insert(307, 'Индекс потребильских настроений (август)', np.NaN)
nonaz_stat.insert(306, 'Индекс потребильских настроений (июнь)', np.NaN)
nonaz_stat.insert(305, 'Индекс потребильских настроений (апрель)', np.NaN)
nonaz_stat.insert(304, 'Индекс потребильских настроений (февраль)', np.NaN)

nonaz_stat.insert(303, 'Протестный потенциал с политическими требованиями (декабрь) - Приняли бы участие', np.NaN)
nonaz_stat.insert(302, 'Протестный потенциал с политическими требованиями (октябрь) - Приняли бы участие', np.NaN)
nonaz_stat.insert(302, 'Протестный потенциал с политическими требованиями (сентябрь) - Приняли бы участие', np.NaN)
nonaz_stat.insert(302, 'Протестный потенциал с политическими требованиями (август) - Приняли бы участие', np.NaN)
nonaz_stat.insert(301, 'Протестный потенциал с политическими требованиями (июнь) - Приняли бы участие', np.NaN)
nonaz_stat.insert(301, 'Протестный потенциал с политическими требованиями (май) - Приняли бы участие', np.NaN)
nonaz_stat.insert(301, 'Протестный потенциал с политическими требованиями (апрель) - Приняли бы участие', np.NaN)
nonaz_stat.insert(300, 'Протестный потенциал с политическими требованиями (февраль) - Приняли бы участие', np.NaN)
nonaz_stat.insert(300, 'Протестный потенциал с политическими требованиями (январь) - Приняли бы участие', np.NaN)

nonaz_stat.insert(300, 'Протестный потенциал с политическими требованиями (декабрь) - Вполне возможны', np.NaN)
nonaz_stat.insert(299, 'Протестный потенциал с политическими требованиями (октябрь) - Вполне возможны', np.NaN)
nonaz_stat.insert(299, 'Протестный потенциал с политическими требованиями (сентябрь) - Вполне возможны', np.NaN)
nonaz_stat.insert(299, 'Протестный потенциал с политическими требованиями (август) - Вполне возможны', np.NaN)
nonaz_stat.insert(298, 'Протестный потенциал с политическими требованиями (июнь) - Вполне возможны', np.NaN)
nonaz_stat.insert(298, 'Протестный потенциал с политическими требованиями (май) - Вполне возможны', np.NaN)
nonaz_stat.insert(298, 'Протестный потенциал с политическими требованиями (апрель) - Вполне возможны', np.NaN)
nonaz_stat.insert(297, 'Протестный потенциал с политическими требованиями (февраль) - Вполне возможны', np.NaN)
nonaz_stat.insert(297, 'Протестный потенциал с политическими требованиями (январь) - Вполне возможны', np.NaN)

nonaz_stat.insert(297, 'Протестный потенциал с экономическими требованиями (декабрь) - Приняли бы участие', np.NaN)
nonaz_stat.insert(296, 'Протестный потенциал с экономическими требованиями (октябрь) - Приняли бы участие', np.NaN)
nonaz_stat.insert(296, 'Протестный потенциал с экономическими требованиями (сентябрь) - Приняли бы участие', np.NaN)
nonaz_stat.insert(296, 'Протестный потенциал с экономическими требованиями (август) - Приняли бы участие', np.NaN)
nonaz_stat.insert(295, 'Протестный потенциал с экономическими требованиями (июнь) - Приняли бы участие', np.NaN)
nonaz_stat.insert(295, 'Протестный потенциал с экономическими требованиями (май) - Приняли бы участие', np.NaN)
nonaz_stat.insert(295, 'Протестный потенциал с экономическими требованиями (апрель) - Приняли бы участие', np.NaN)
nonaz_stat.insert(294, 'Протестный потенциал с экономическими требованиями (февраль) - Приняли бы участие', np.NaN)
nonaz_stat.insert(294, 'Протестный потенциал с экономическими требованиями (январь) - Приняли бы участие', np.NaN)

nonaz_stat.insert(294, 'Протестный потенциал с экономическими требованиями (декабрь) - Вполне возможны', np.NaN)
nonaz_stat.insert(293, 'Протестный потенциал с экономическими требованиями (октябрь) - Вполне возможны', np.NaN)
nonaz_stat.insert(293, 'Протестный потенциал с экономическими требованиями (сентябрь) - Вполне возможны', np.NaN)
nonaz_stat.insert(293, 'Протестный потенциал с экономическими требованиями (август) - Вполне возможны', np.NaN)
nonaz_stat.insert(292, 'Протестный потенциал с экономическими требованиями (июнь) - Вполне возможны', np.NaN)
nonaz_stat.insert(292, 'Протестный потенциал с экономическими требованиями (май) - Вполне возможны', np.NaN)
nonaz_stat.insert(292, 'Протестный потенциал с экономическими требованиями (апрель) - Вполне возможны', np.NaN)
nonaz_stat.insert(291, 'Протестный потенциал с экономическими требованиями (февраль) - Вполне возможны', np.NaN)
nonaz_stat.insert(291, 'Протестный потенциал с экономическими требованиями (январь) - Вполне возможны', np.NaN)

nonaz_stat.insert(3, 'Индекс Счастья (декабрь)', np.NaN)
nonaz_stat.insert(2, 'Индекс Счастья (октябрь)', np.NaN)
nonaz_stat.insert(2, 'Индекс Счастья (сентябрь)', np.NaN)
nonaz_stat.insert(2, 'Индекс Счастья (август)', np.NaN)
nonaz_stat.insert(1, 'Индекс Счастья (июнь)', np.NaN)
nonaz_stat.insert(1, 'Индекс Счастья (май)', np.NaN)
nonaz_stat.insert(1, 'Индекс Счастья (апрель)', np.NaN)
nonaz_stat.insert(0, 'Индекс Счастья (февраль)', np.NaN)
nonaz_stat.insert(0, 'Индекс Счастья (январь)', np.NaN)

for i in range(len(nonaz_stat.columns)):
    if i%12 == 0:
        print("<-->")
    print(str(i) + '  ' + str(nonaz_stat.columns[i]))

def make_monthly(df, n_vars, col_idx=0):
    months_index = ['январь', 'февраль', 'март', 'апрель', 'май', 'июнь', 'июль', 'август',
                    'сентябрь', 'октябрь', 'ноябрь', 'декабрь']
    janreg = re.compile(r"\(\D+нварь\)")

    ret_curr = df.iloc[:, col_idx:(col_idx + 1)].copy()
    ret_squared = ret_curr.iloc[:12, :].copy()
    ret_squared.columns = [janreg.sub("", ret_squared.index[0])]
    ret_squared.index = months_index
    for j in range(1, n_vars):
        tmp = ret_curr.iloc[j*12:(j+1)*12, :].copy()
        tmp.columns = [janreg.sub("", tmp.index[0])]
        tmp.index = months_index
        ret_squared = pd.concat([ret_squared, tmp], axis=1)
    return ret_squared


def fill_empty_values_as_avg(df):
    df.fillna(df.mean())


def weighted_monthly_average(df, weights): #first fill na with averege in row, then calculate weighted avg for each col
    nedf = df.copy()
    nedf = nedf.transpose()
    nedf = nedf.fillna(nedf.mean(axis=0, skipna=True))
    nedf = nedf.transpose()
    #print(nedf)
    neweights = weights.copy()
    neweights[neweights.columns[0]] = neweights[neweights.columns[0]] * ((1. - nedf.isnull())[nedf.columns[0]])
    total_weight = neweights.sum().iat[0]
    #print(neweights)
    #print(total_weight)
    for j in nedf.columns:
        nedf[j] = nedf[j]*weights[weights.columns[0]]
    newrow = nedf.sum(axis=0) / total_weight
    return (pd.DataFrame(data=newrow, columns=['Среднее'])).transpose()


def make_weighted_avg_for_all_by_month(df, n_vars):
    newdf = weighted_monthly_average(nonaz_internet.iloc[:, :12], nonaz_population)
    for i in range(1, n_vars):
        temp_df = weighted_monthly_average(nonaz_internet.iloc[:, i*12:(i+1)*12], nonaz_population)
        newdf = pd.concat([newdf, temp_df], axis=1)
    return newdf



avg_squared = make_weighted_avg_for_all_by_month(nonaz_internet, 19)
avg_squared = avg_squared.transpose()
avg_squared = make_monthly(avg_squared, 19)
print(avg_squared)

# nonaz_internet = nonaz_internet.transpose()
nonaz_stat = nonaz_stat.transpose()
# for i in range(len(nonaz_stat.index)):
#     print(str(i) + '  ' + str(nonaz_stat.index[i]))
#
# for i in range(len(nonaz_stat.columns)):
#     print(str(i) + '  ' + str(nonaz_stat.columns[i]))

stat_squared = make_monthly(nonaz_stat, 36)
stat_squared = stat_squared.fillna(stat_squared.mean())
print(stat_squared)

corr = correlate_frames(stat_squared, avg_squared)
print(corr)
corr.to_csv('D:/BigData/Galina_Kovarzh/Timewise_avg.csv')

avg_squared_norm = normalize_frame(avg_squared)
stat_squared_norm = normalize_frame(stat_squared)
print(stat_squared_norm)

fac_avg = FactorAnalysis(n_components=4)
fac_avg.fit(avg_squared_norm)
fac_avg_df = pd.DataFrame(fac_avg.components_, columns=avg_squared_norm.columns)
fac_avg_df.to_csv('D:/BigData/Galina_Kovarzh/Timewise_avg_factors.csv')

fac_stat = FactorAnalysis(n_components=2)
fac_stat.fit(stat_squared_norm)
fac_stat_df = pd.DataFrame(fac_stat.components_, columns=stat_squared_norm.columns)
fac_stat_df.to_csv('D:/BigData/Galina_Kovarzh/Timewise_stat_factors.csv')

pca_avg = PCA(n_components=4)
pca_avg.fit(avg_squared_norm)
print(pca_avg.explained_variance_ratio_.sum())

pca_stat = PCA(n_components=2)
pca_stat.fit(stat_squared_norm)
print(pca_stat.explained_variance_ratio_.sum())


# print(nonaz_internet.columns)

# for i in range(len(nonaz_internet.columns)):
#     internet_squared = make_monthly(nonaz_internet, 19, i)
#     internet_squared = internet_squared.fillna(internet_squared.mean())
#     # print(nonaz_internet.columns[i])
#     # print(internet_squared.iloc[:, 6])
#     # print(internet_squared.dtypes)
#     corr = correlate_frames(stat_squared, internet_squared)
#     print(str(i+1) + ' of ' + str(len(nonaz_internet.columns)))
#     corr.to_csv('D:/BigData/Galina_Kovarzh/Naz/'+nonaz_internet.columns[i]+'.csv')
