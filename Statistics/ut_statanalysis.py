# Created by Gubanov Alexander (aka Derzhiarbuz) at 07.11.2019
# Contacts: derzhiarbuz@gmail.com

import pandas as pd
from da_diffusion_simulation import Simulator
from da_network import Network
import da_diffusion_estimation as de
from matplotlib import pyplot
import da_stat as stat


# nonaz_df = pd.read_csv('D:/BigData/Galina_Kovarzh/Nenatsionalnye.csv',
#                        sep=';', decimal=',', encoding='windows-1251', index_col=0)
# nonaz_df.drop(nonaz_df.columns[24], axis=1, inplace=True)
# naz_df = pd.read_csv('D:/BigData/Galina_Kovarzh/Natsionalnye.csv',
#                      sep=';', decimal=',', encoding='windows-1251', index_col=0)
# naz_df.drop(naz_df.columns[24], axis=1, inplace=True)
# naz_total =
#
# # print(nonaz_df)
# # print(naz_df)
# nonaz_corr = nonaz_df.corr().iloc[0:19, 19:]
# naz_corr = nonaz_df.corr().iloc[0:19, 19:]
#
#
# nonaz_corr.to_csv('D:/BigData/Galina_Kovarzh/nonaz_corr.csv')
# naz_corr.to_csv('D:/BigData/Galina_Kovarzh/naz_corr.csv')

ntw = Network()
ntw.add_node(1)
ntw.add_node(2)
ntw.add_node(3)
ntw.add_node(4)
ntw.add_node(5)
ntw.add_node(6)
ntw.add_node(7)
ntw.add_node(8)
ntw.add_node(9)
ntw.add_node(10)
ntw.add_node(11)
ntw.add_node(12)
ntw.add_node(13)
ntw.add_node(14)
ntw.add_node(15)
ntw.add_node(16)
ntw.add_node(17)
ntw.add_node(18)
ntw.add_node(19)
ntw.add_node(20)
ntw.add_link(1, 2)
ntw.add_link(1, 3)
ntw.add_link(2, 3)
ntw.add_link(3, 4)
ntw.add_link(4, 5)
ntw.add_link(4, 6)
ntw.add_link(5, 6)
ntw.add_link(4, 7)
ntw.add_link(7, 8)
ntw.add_link(7, 9)
ntw.add_link(7, 10)
ntw.add_link(8, 10)
ntw.add_link(9, 10)
ntw.add_link(9, 11)
ntw.add_link(11, 12)
ntw.add_link(11, 13)
ntw.add_link(12, 13)
ntw.add_link(13, 14)
ntw.add_link(8, 15)
ntw.add_link(3, 16)
ntw.add_link(16, 17)
ntw.add_link(17, 18)
ntw.add_link(18, 19)
ntw.add_link(19, 20)
ntw.add_link(15, 20)
result = Simulator.simulate_SI(underlying=ntw, theta=0.85, infected={1}, tmax=300, dt=1)
print(result)
th = 0.0
est_th = th
best_pest = 0
ml_pval = 0
thetas = []
ps = []
total_pest = 0
while th <= 1.0:
    pest = Simulator.estimate_SI(underlying=ntw, outcome=result['outcome'], theta=th, initials={1}, tmax=300, dt=1)
    # print(str(th) + ' ' + str(pest))
    if pest > best_pest:
        best_pest = pest
        est_th = th
    thetas.append(th)
    ps.append(pest)
    total_pest += pest
    th += 0.01
pval = de.estimate_pvalue_SI(underlying=ntw, outcome=result['outcome'], theta=est_th, initials={1}, tmax=300, dt=1,
                             n_iterations=1000)
print('True theta: ' + str(0.85))
print('Max liklehood estimation: ' + str(est_th) + ' p-val ' + str(pval))
psnorm = stat.normalize_series(ps)
confide = stat.confidential_from_p_series(psnorm, 0.95)
print('0.95 confidential interval: (' + str(thetas[confide[0]]) + ', ' + str(thetas[confide[1]]) + ')')

pyplot.plot(thetas, psnorm)
pyplot.show()