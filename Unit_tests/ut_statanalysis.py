# Created by Gubanov Alexander (aka Derzhiarbuz) at 07.11.2019
# Contacts: derzhiarbuz@gmail.com

import pandas as pd
from Statistics.da_diffusion_simulation import Simulator
from da_network import Network, NetworkOptimisation
import Statistics.da_diffusion_estimation as de
from matplotlib import pyplot
import Statistics.da_stat as stat
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import cm
from mpl_toolkits.mplot3d import Axes3D
import seaborn as sns
import math


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

def make_test_network():
    ntw = Network(optimisation=NetworkOptimisation.id_only)
    for i in range(31):
        ntw.add_node(i + 1)
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
    ntw.add_link(1, 21)
    ntw.add_link(1, 22)
    ntw.add_link(1, 23)
    ntw.add_link(1, 24)
    ntw.add_link(1, 25)
    ntw.add_link(1, 26)
    ntw.add_link(2, 21)
    ntw.add_link(2, 22)
    ntw.add_link(2, 23)
    ntw.add_link(2, 24)
    ntw.add_link(2, 25)
    ntw.add_link(2, 26)
    ntw.add_link(3, 21)
    ntw.add_link(3, 22)
    ntw.add_link(3, 23)
    ntw.add_link(3, 24)
    ntw.add_link(3, 25)
    ntw.add_link(3, 26)
    return ntw


def make_test_network_star():
    ntw = Network(optimisation=NetworkOptimisation.id_only)
    for i in range(31):
        ntw.add_node(i+1)
    for i in range(30):
        ntw.add_link(1, i+2)
    return ntw


def make_test_network_chain():
    ntw = Network(optimisation=NetworkOptimisation.id_only)
    for i in range(31):
        ntw.add_node(i+1)
    for i in range(30):
        ntw.add_link(i+1, i+2)
    return ntw


def make_test_network_connected():
    ntw = Network(optimisation=NetworkOptimisation.id_only)
    for i in range(31):
        ntw.add_node(i+1)
    for i in range(30):
        for j in range(i+1, 31):
            ntw.add_link(i+1, j+1)
    return ntw


def test_SI(ntw: Network, true_theta: float):
    result = Simulator.simulate_SI(underlying=ntw, theta=true_theta, infected={1}, tmax=300, dt=1)
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
    print('True theta: ' + str(true_theta))
    print('Max liklehood estimation: ' + str(est_th) + ' p-val ' + str(pval))
    psnorm = stat.normalize_series(ps)
    confide = stat.confidential_from_p_series(psnorm, 0.95)
    print('0.95 confidential interval: (' + str(thetas[confide[0]]) + ', ' + str(thetas[confide[1]]) + ')')

    pyplot.plot(thetas, psnorm)
    pyplot.show()


def test_SI_decay(ntw: Network, true_theta: float, true_decay: float, continuous = False):
    dt = 1
    if continuous:
        dt = 0.01
    result = Simulator.simulate_SI_decay(underlying=ntw, theta=true_theta, decay=true_decay,
                                         infected={1}, tmax=300, dt=dt)
    print(result)
    est_th = .0
    est_dc = .0
    best_pest = 0
    ml_pval = 0
    total_pest = 0
    th = 0.0
    thetas = np.arange(0.01, 1, 0.01)
    decays = np.arange(0.001, 0.1, 0.001)
    ps = np.zeros((len(thetas), len(decays)))
    i = 0
    for th in thetas:
        dc = 0.0
        j = 0
        for dc in decays:
            if continuous:
                pest = math.exp(Simulator.estimate_SI_relic_decay_confirm_continuous(underlying=ntw,
                                                                                     outcome=result['outcome'],
                                                                                     theta=th, decay=dc, relic=.0,
                                                                                     initials={1}, tmax=300))
            else:
                pest = Simulator.estimate_SI_decay(underlying=ntw, outcome=result['outcome'], theta=th, decay=dc,
                                                   initials={1}, tmax=300, dt=dt)
#            print(str(th) + ' ' + str(pest))
            if pest > best_pest:
                best_pest = pest
                est_th = th
                est_dc = dc
            ps[i][j] = pest
            total_pest += pest
            j += 1
        i += 1
#    pval = de.estimate_pvalue_SI_decay(underlying=ntw, outcome=result['outcome'], theta=est_th, initials={1}, tmax=300, dt=1,
#                                 n_iterations=1000)
    print('True theta: ' + str(true_theta))
    print('Max liklehood estimation: ' + str(est_th))
    print('True decay: ' + str(true_decay))
    print('Max liklehood estimation: ' + str(est_dc))
    print('Probability: ' + str(best_pest))
#    print('p-val: ' + str(pval))
    # psnorm = stat.normalize_series(ps)
    # confide = stat.confidential_from_p_series(psnorm, 0.95)
    # print('0.95 confidential interval: (' + str(thetas[confide[0]]) + ', ' + str(thetas[confide[1]]) + ')')

    decays, thetas = np.meshgrid(decays, thetas)

    # fig = plt.figure()
    # ax = Axes3D(fig)
    # ax.plot_surface(thetas, decays, ps, rstride=1, cstride=1, cmap='twilight_shifted')
    # plt.show()

    plt.figure(figsize=(5, 5))
    plt.xlabel('$\\theta$ (virulence)')
    plt.ylabel('$\\delta$ (decay)')
    plt.contourf(thetas, decays, ps, levels=15)
    plt.scatter([est_th], [est_dc], color='blue', marker='+')
    plt.scatter([true_theta], [true_decay], color='red', marker='o')
    plt.show()


def test_SI_recover(ntw: Network, true_theta: float, true_recover_time: float):
    result = Simulator.simulate_SI_recover(underlying=ntw, theta=true_theta, recover_time=true_recover_time,
                                           infected={1}, tmax=300, dt=1)
    print(result)
    est_th = .0
    est_dc = .0
    best_pest = 0
    ml_pval = 0
    total_pest = 0
    th = 0.0
    thetas = np.arange(0, 1, 0.01)
    recovers = np.arange(1, 50, 0.5)
    ps = np.zeros((len(thetas), len(recovers)))
    i = 0
    for th in thetas:
        dc = 0.0
        j = 0
        for dc in recovers:
            pest = Simulator.estimate_SI_recover(underlying=ntw, outcome=result['outcome'], theta=th, recover_time=dc,
                                               initials={1}, tmax=300, dt=1)
#            print(str(th) + ' ' + str(pest))
            if pest > best_pest:
                best_pest = pest
                est_th = th
                est_dc = dc
            ps[i][j] = pest
            total_pest += pest
            j += 1
        i += 1
#    pval = de.estimate_pvalue_SI_decay(underlying=ntw, outcome=result['outcome'], theta=est_th, initials={1}, tmax=300, dt=1,
#                                 n_iterations=1000)
    print('True theta: ' + str(true_theta))
    print('Max liklehood estimation: ' + str(est_th))
    print('True recover time: ' + str(true_recover_time))
    print('Max liklehood estimation: ' + str(est_dc))
    print('Probability: ' + str(best_pest))
#    print('p-val: ' + str(pval))
    # psnorm = stat.normalize_series(ps)
    # confide = stat.confidential_from_p_series(psnorm, 0.95)
    # print('0.95 confidential interval: (' + str(thetas[confide[0]]) + ', ' + str(thetas[confide[1]]) + ')')

    decays, thetas = np.meshgrid(recovers, thetas)

    # fig = plt.figure()
    # ax = Axes3D(fig)
    # ax.plot_surface(thetas, decays, ps, rstride=1, cstride=1, cmap=cm.viridis)
    # plt.show()

    plt.figure(figsize=(5, 5))
    plt.xlabel('$\\theta$ (virulence)')
    plt.ylabel('$\\delta$ (recover time)')
    plt.contourf(thetas, decays, ps, levels=15)
    plt.scatter([est_th], [est_dc], color='blue', marker='+')
    plt.scatter([true_theta], [true_recover_time], color='red', marker='o')
    plt.show()


def test_SI_halflife(ntw: Network, true_theta: float, true_halflife: float, continuous = False):
    dt = 1
    if continuous:
        dt = 0.01
    result = Simulator.simulate_SI_halflife(underlying=ntw, theta=true_theta, halflife=true_halflife,
                                           infected={1}, tmax=300, dt=dt)
    #result = Simulator.simulate_SI(underlying=ntw, theta=true_theta, infected={1}, tmax=300, dt=1)
    print(result)
    est_th = .0
    est_dc = .0
    best_pest = 0
    ml_pval = 0
    total_pest = 0
    th = 0.0
    thetas = np.arange(0.001, 1.001, 0.01)
    #thetas = np.array([true_theta])
    recovers = np.arange(1, 50, 0.5)
    #recovers = np.array([true_halflife])
    ps = np.zeros((len(thetas), len(recovers)))
    i = 0
    for th in thetas:
        dc = 0.0
        j = 0
        for dc in recovers:
            if continuous:
                pest = math.exp(Simulator.estimate_SI_relic_halflife_continuous(underlying=ntw, outcome=result['outcome'],
                                                                       theta=th, halflife=dc, relic=.0,
                                                                       initials={1}, tmax=300))
            else:
                pest = Simulator.estimate_SI_halflife(underlying=ntw, outcome=result['outcome'], theta=th, halflife=dc,
                                                      initials={1}, tmax=300, dt=dt)
#            print(str(th) + ' ' + str(pest))
            if pest > best_pest:
                best_pest = pest
                est_th = th
                est_dc = dc
            ps[i][j] = pest
            total_pest += pest
            j += 1
        i += 1
#    pval = de.estimate_pvalue_SI_decay(underlying=ntw, outcome=result['outcome'], theta=est_th, initials={1}, tmax=300, dt=1,
#                                 n_iterations=1000)
    print('True theta: ' + str(true_theta))
    print('Max liklehood estimation: ' + str(est_th))
    print('True halflife: ' + str(true_halflife))
    print('Max liklehood estimation: ' + str(est_dc))
    print('Probability: ' + str(best_pest))
#    print('p-val: ' + str(pval))
    # psnorm = stat.normalize_series(ps)
    # confide = stat.confidential_from_p_series(psnorm, 0.95)
    # print('0.95 confidential interval: (' + str(thetas[confide[0]]) + ', ' + str(thetas[confide[1]]) + ')')

    decays, thetas = np.meshgrid(recovers, thetas)

    # fig = plt.figure()
    # ax = Axes3D(fig)
    # ax.plot_surface(thetas, decays, ps, rstride=1, cstride=1, cmap=cm.viridis)
    # plt.show()

    plt.figure(figsize=(5, 5))
    plt.xlabel('$\\theta$ (virulence)')
    plt.ylabel('$\\delta$ (halflife)')
    plt.contourf(thetas, decays, ps, levels=15)
    plt.scatter([est_th], [est_dc], color='blue', marker='+')
    plt.scatter([true_theta], [true_halflife], color='red', marker='o')
    plt.show()


def test_SI_confirm(ntw: Network, true_theta: float, true_confirm: float, continuous = False):
    dt = 1
    if continuous:
        dt = 0.01
    result = Simulator.simulate_SI_confirm(underlying=ntw, theta=true_theta, confirm=true_confirm,
                                         infected={1}, tmax=300, dt=dt)
    print(result)
    est_th = .0
    est_dc = .0
    best_pest = 0
    ml_pval = 0
    total_pest = 0
    th = 0.0
    thetas = np.arange(0.01, 1.01, 0.01)
    #confirms = np.arange(-2, 2.01, 0.1)
    confirms = np.arange(-1, 1, 0.01)
    ps = np.zeros((len(thetas), len(confirms)))
    i = 0
    for th in thetas:
        dc = 0.0
        j = 0
        for dc in confirms:
            if continuous:
                pest = math.exp(Simulator.estimate_SI_relic_decay_confirm_continuous(underlying=ntw,
                                                                                     outcome=result['outcome'],
                                                                                     theta=th, decay=.000001, relic=.0,
                                                                                     confirm=dc, confirm_drop=0.1,
                                                                                     initials={1}, tmax=300))
            else:
                pest = Simulator.estimate_SI_confirm(underlying=ntw, outcome=result['outcome'], theta=th, confirm=dc,
                                                     initials={1}, tmax=300, dt=dt)
#            print(str(th) + ' ' + str(pest))
            if pest > best_pest:
                best_pest = pest
                est_th = th
                est_dc = dc
            ps[i][j] = pest
            total_pest += pest
            j += 1
        i += 1
    print('True theta: ' + str(true_theta))
    print('Max liklehood estimation: ' + str(est_th))
    print('True confirm: ' + str(true_confirm))
    print('Max liklehood estimation: ' + str(est_dc))
    print('Probability: ' + str(best_pest))

    confirms, thetas = np.meshgrid(confirms, thetas)

    # fig = plt.figure()
    # ax = Axes3D(fig)
    # ax.plot_surface(thetas, confirms, ps, rstride=1, cstride=1, cmap=cm.viridis)
    # plt.show()

    plt.figure(figsize=(5, 5))
    plt.xlabel('$\\theta$ (virulence)')
    plt.ylabel('$\\kappa$ (confirmation)')
    plt.contourf(thetas, confirms, ps, levels=15)
    plt.scatter([est_th], [est_dc], color='blue', marker='+')
    plt.scatter([true_theta], [true_confirm], color='red', marker='o')
    plt.show()

def test_SI_relic(ntw: Network, true_theta: float, true_relic: float, continuous = False):
    dt = 1
    if continuous:
        dt = 0.01
    result = Simulator.simulate_SI_relic(underlying=ntw, theta=true_theta, relic=true_relic,
                                           infected={1}, tmax=300, dt=dt)
    print(result)
    est_th = .0
    est_dc = .0
    best_pest = 0
    ml_pval = 0
    total_pest = 0
    th = 0.0
    thetas = np.arange(0.001, 0.11, 0.001)
    relics = np.arange(0.001, 0.11, 0.001)
    ps = np.zeros((len(thetas), len(relics)))
    i = 0
    for th in thetas:
        dc = 0.0
        j = 0
        for dc in relics:
            if continuous:
                pest = math.exp(Simulator.estimate_SI_relic_continuous(underlying=ntw, outcome=result['outcome'], theta=th,
                                                              relic=dc, initials={1}, tmax=300))
            else:
                pest = Simulator.estimate_SI_relic(underlying=ntw, outcome=result['outcome'], theta=th, relic=dc,
                                                   initials={1}, tmax=300, dt=dt)
#            print(str(th) + ' ' + str(pest))
            if pest > best_pest:
                best_pest = pest
                est_th = th
                est_dc = dc
            ps[i][j] = pest
            total_pest += pest
            j += 1
        i += 1
    print('True theta: ' + str(true_theta))
    print('Max liklehood estimation: ' + str(est_th))
    print('True relic: ' + str(true_relic))
    print('Max liklehood estimation: ' + str(est_dc))
    print('Probability: ' + str(best_pest))

    relics, thetas = np.meshgrid(relics, thetas)

    # fig = plt.figure()
    # ax = Axes3D(fig)
    # ax.plot_surface(thetas, relics, ps, rstride=1, cstride=1, cmap=cm.viridis)
    # plt.show()

    plt.figure(figsize=(5, 5))
    plt.xlabel('$\\theta$ (virulence)')
    plt.ylabel('$\\rho$ (background)')
    plt.contourf(thetas, relics, ps, levels=15)
    plt.scatter([est_th], [est_dc], color='blue', marker='+')
    plt.scatter([true_theta], [true_relic], color='red', marker='o')
    plt.show()


if __name__ == '__main__':
    netwrk = make_test_network()
    # netwrk.export_gexf('D:/Projects/Study/Papers please/Networks_MLE_Gubanov/ntwrk_connected.gexf')
    # result = Simulator.simulate_SI_recover(underlying=netwrk, theta=0.05, recover_time=30,
    #                                         infected={1}, tmax=300, dt=1)
    # print(result['p'])
    # print(Simulator.estimate_SI_recover(underlying=netwrk, outcome=result['outcome'], theta=0.05, recover_time=30,
    #                                      initials={1}, tmax=300, dt=1))
    # test_SI_relic(netwrk, 0.05, 0.05)
    test_SI_relic(netwrk, 0.05, 0.01, continuous=True)