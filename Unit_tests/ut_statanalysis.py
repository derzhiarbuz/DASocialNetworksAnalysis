# Created by Gubanov Alexander (aka Derzhiarbuz) at 07.11.2019
# Contacts: derzhiarbuz@gmail.com

from da_net.da_diffusion_simulation import Simulator
from da_network import Network, NetworkOptimisation
from da_network_manager import NetworkManager
import da_net.da_diffusion_estimation as de
from matplotlib import pyplot
import Statistics.da_stat as stat
import numpy as np
import matplotlib.pyplot as plt
import da_net.da_diffusion_estimation as est
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

def make_test_network_traingle():
    ntw = Network(optimisation=NetworkOptimisation.id_only)
    for i in range(3):
        ntw.add_node(i + 1)
    ntw.add_link(1, 2)
    ntw.add_link(1, 3)
    ntw.add_link(2, 3)
    return ntw


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


def make_test_network_chain(n=31):
    ntw = Network(optimisation=NetworkOptimisation.id_only)
    for i in range(n):
        ntw.add_node(i+1)
    for i in range(n-1):
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


def test_SI_relic_libtest(ntw: Network, true_theta: float, true_relic: float, newlib=False, single_point=False):
    #test_outcome = {5: 11.89999999999979, 6: 36.75000000000126, 20: 39.49000000000071, 1: 39.65000000000068, 3: 40.0600000000006, 26: 40.840000000000444, 11: 41.31000000000035, 2: 43.799999999999855, 13: 44.299999999999756, 22: 45.64999999999949, 25: 46.29999999999936, 12: 46.33999999999935, 16: 47.43999999999913, 9: 49.53999999999871, 7: 49.68999999999868, 23: 50.679999999998486, 27: 52.849999999998055, 30: 53.77999999999787, 29: 54.22999999999778, 24: 54.499999999997726, 21: 55.03999999999762, 15: 58.159999999997, 17: 58.56999999999692, 8: 62.05999999999622, 14: 66.41999999999707, 4: 79.06000000000354, 10: 87.63000000000793, 19: 110.38000000001956, 31: 146.84000000001143, 28: 159.5199999999999, 18: 0.0}
    netman = NetworkManager(net=netwrk, name='temp', base_dir='D:/BigData/Charity/Cascades/')
    netman.save_to_file()

    result = Simulator.simulate_SI_decay_confirm_relicexp_hetero(underlying=netwrk, theta=true_theta, relic=true_relic,
                                                                 confirm=.0, decay=.0, infected={1}, tmax=300,
                                                                 dt=0.01)
    result['outcome'][1] = .0
    #result['outcome'] = test_outcome #OVERWRITE TEST
    # result = Simulator.simulate_SI_relic(underlying=ntw, theta=true_theta, relic=true_relic,
    #                             infected={1}, tmax=300, dt=0.01)
    if(newlib):
        est.set_diffusion_data_newlib(netman.get_dos_filepath(), outcome=result['outcome'], observe_time=300, echo=False)
    else:
        est.set_diffusion_data(netman.get_dos_filepath(), counters={}, outcome=result['outcome'])
    est_th_py = .0
    est_dc_py = .0
    est_th_c = .0
    est_dc_c = .0
    best_pest_py = 0
    best_pest_c = 0
    ml_pval = 0
    total_pest = 0
    th = 0.0
    thetas = np.arange(0.0001, 0.05, 0.0005)
    relics = np.arange(0.0001, 0.01, 0.0001)
    ps_py = np.zeros((len(thetas), len(relics)))
    ps_c = np.zeros((len(thetas), len(relics)))
    i = 0
    if(single_point):
        print(math.exp(
            Simulator.estimate_SI_relic_continuous(underlying=ntw, outcome=result['outcome'], theta=true_theta,
                                                   relic=true_relic, initials={1}, tmax=300, echo=False)))
        if (newlib):
            print(math.exp(-est.loglikelyhood_SI_relic_newlib([true_theta, true_relic])))
        else:
            print(math.exp(-est.loglikelyhood_SI_relic([true_theta, true_relic])))
    else:
        for th in thetas:
            dc = 0.0
            j = 0
            for dc in relics:
                pest_py = math.exp(
                        Simulator.estimate_SI_relic_continuous(underlying=ntw, outcome=result['outcome'], theta=th,
                                                               relic=dc, initials={1}, tmax=300))
                if (newlib):
                    pest_c = math.exp(-est.loglikelyhood_SI_relic_newlib([th, dc]))
                else:
                    pest_c = math.exp(-est.loglikelyhood_SI_relic([th, dc]))
                #            print(str(th) + ' ' + str(pest))
                if pest_py > best_pest_py:
                    best_pest_py = pest_py
                    est_th_py = th
                    est_dc_py = dc
                if pest_c > best_pest_c:
                    best_pest_c = pest_c
                    est_th_c = th
                    est_dc_c = dc
                ps_py[i][j] = pest_py
                ps_c[i][j] = pest_c
                j += 1
            i += 1
        print('True theta: ' + str(true_theta))
        print('Max liklehood estimation Py: ' + str(est_th_py))
        print('Max liklehood estimation C: ' + str(est_th_c))
        print('True relic: ' + str(true_relic))
        print('Max liklehood estimation Py: ' + str(est_dc_py))
        print('Max liklehood estimation C: ' + str(est_dc_c))
        print('Likelyhood Py: ' + str(best_pest_py))
        print('Likelyhood C: ' + str(best_pest_c))

        relics, thetas = np.meshgrid(relics, thetas)

        plt.figure(figsize=(5, 5))
        plt.xlabel('$\\theta$ (virulence)')
        plt.ylabel('$\\rho$ (background)')
        plt.contourf(thetas, relics, ps_py, levels=15)
        plt.scatter([est_th_py], [est_dc_py], color='blue', marker='+')
        plt.scatter([true_theta], [true_relic], color='red', marker='o')
        plt.show()

        plt.figure(figsize=(5, 5))
        plt.xlabel('$\\theta$ (virulence)')
        plt.ylabel('$\\rho$ (background)')
        plt.contourf(thetas, relics, ps_c, levels=15)
        plt.scatter([est_th_c], [est_dc_c], color='blue', marker='+')
        plt.scatter([true_theta], [true_relic], color='red', marker='o')
        plt.show()


def test_SI_relic_decay_libtest(ntw: Network, true_theta: float, true_relic: float, newlib=False, single_point=False):
    #test_outcome = {5: 11.89999999999979, 6: 36.75000000000126, 20: 39.49000000000071, 1: 39.65000000000068, 3: 40.0600000000006, 26: 40.840000000000444, 11: 41.31000000000035, 2: 43.799999999999855, 13: 44.299999999999756, 22: 45.64999999999949, 25: 46.29999999999936, 12: 46.33999999999935, 16: 47.43999999999913, 9: 49.53999999999871, 7: 49.68999999999868, 23: 50.679999999998486, 27: 52.849999999998055, 30: 53.77999999999787, 29: 54.22999999999778, 24: 54.499999999997726, 21: 55.03999999999762, 15: 58.159999999997, 17: 58.56999999999692, 8: 62.05999999999622, 14: 66.41999999999707, 4: 79.06000000000354, 10: 87.63000000000793, 19: 110.38000000001956, 31: 146.84000000001143, 28: 159.5199999999999, 18: 0.0}
    netman = NetworkManager(net=netwrk, name='temp', base_dir='D:/BigData/Charity/Cascades/')
    netman.save_to_file()

    result = Simulator.simulate_SI_decay_confirm_relicexp_hetero(underlying=netwrk, theta=true_theta, relic=true_relic,
                                                                 confirm=.0, decay=.0, infected={1}, tmax=300,
                                                                 dt=0.01)
    result['outcome'][1] = .0
    #result['outcome'] = test_outcome #OVERWRITE TEST
    # result = Simulator.simulate_SI_relic(underlying=ntw, theta=true_theta, relic=true_relic,
    #                             infected={1}, tmax=300, dt=0.01)
    if(newlib):
        est.set_diffusion_data_newlib(netman.get_dos_filepath(), outcome=result['outcome'], observe_time=300, echo=False)
    else:
        est.set_diffusion_data(netman.get_dos_filepath(), counters={}, outcome=result['outcome'])
    est_th_py = .0
    est_dc_py = .0
    est_th_c = .0
    est_dc_c = .0
    best_pest_py = 0
    best_pest_c = 0
    ml_pval = 0
    total_pest = 0
    th = 0.0
    thetas = np.arange(0.0001, 0.05, 0.0005)
    relics = np.arange(0.0001, 0.01, 0.0001)
    ps_py = np.zeros((len(thetas), len(relics)))
    ps_c = np.zeros((len(thetas), len(relics)))
    i = 0
    if(single_point):
        print(math.exp(
            Simulator.estimate_SI_relic_continuous(underlying=ntw, outcome=result['outcome'], theta=true_theta,
                                                   relic=true_relic, initials={1}, tmax=300, echo=False)))
        if (newlib):
            print(math.exp(-est.loglikelyhood_SI_relic_newlib([true_theta, true_relic])))
        else:
            print(math.exp(-est.loglikelyhood_SI_relic([true_theta, true_relic])))
    else:
        for th in thetas:
            dc = 0.0
            j = 0
            for dc in relics:
                pest_py = math.exp(
                        Simulator.estimate_SI_relic_continuous(underlying=ntw, outcome=result['outcome'], theta=th,
                                                               relic=dc, initials={1}, tmax=300))
                if (newlib):
                    pest_c = math.exp(-est.loglikelyhood_SI_relic_newlib([th, dc]))
                else:
                    pest_c = math.exp(-est.loglikelyhood_SI_relic([th, dc]))
                #            print(str(th) + ' ' + str(pest))
                if pest_py > best_pest_py:
                    best_pest_py = pest_py
                    est_th_py = th
                    est_dc_py = dc
                if pest_c > best_pest_c:
                    best_pest_c = pest_c
                    est_th_c = th
                    est_dc_c = dc
                ps_py[i][j] = pest_py
                ps_c[i][j] = pest_c
                j += 1
            i += 1
        print('True theta: ' + str(true_theta))
        print('Max liklehood estimation Py: ' + str(est_th_py))
        print('Max liklehood estimation C: ' + str(est_th_c))
        print('True relic: ' + str(true_relic))
        print('Max liklehood estimation Py: ' + str(est_dc_py))
        print('Max liklehood estimation C: ' + str(est_dc_c))
        print('Likelyhood Py: ' + str(best_pest_py))
        print('Likelyhood C: ' + str(best_pest_c))

        relics, thetas = np.meshgrid(relics, thetas)

        plt.figure(figsize=(5, 5))
        plt.xlabel('$\\theta$ (virulence)')
        plt.ylabel('$\\rho$ (background)')
        plt.contourf(thetas, relics, ps_py, levels=15)
        plt.scatter([est_th_py], [est_dc_py], color='blue', marker='+')
        plt.scatter([true_theta], [true_relic], color='red', marker='o')
        plt.show()

        plt.figure(figsize=(5, 5))
        plt.xlabel('$\\theta$ (virulence)')
        plt.ylabel('$\\rho$ (background)')
        plt.contourf(thetas, relics, ps_c, levels=15)
        plt.scatter([est_th_c], [est_dc_c], color='blue', marker='+')
        plt.scatter([true_theta], [true_relic], color='red', marker='o')
        plt.show()


def test_ICM_libtest(netwrk: Network, true_theta: float, true_relic: float = .0, single_point=False):
    netman = NetworkManager(net=netwrk, name='temp', base_dir='D:/BigData/Charity/Cascades/')
    netman.save_to_file()

    #result = Simulator.simulate_ICM(underlying=netwrk, theta=true_theta, relic=true_relic, infected={1})
    outcomes = []
    otimes = []
    for i in range(50):
        result = Simulator.simulate_SI_decay_confirm_relicexp_hetero(underlying=netwrk, theta=.1, relic=.0,
                                                                     confirm=.0, decay=.1, infected={1}, tmax=300,
                                                                     dt=0.05)
        result['outcome'][1] = .0
        print(result)
        outcomes.append(result['outcome'])
        otimes.append(300)

    est.set_diffusion_data_ensemble_newlib(netman.get_dos_filepath(), outcomes=outcomes, observe_times=otimes, echo=False)
    est_th = .0
    best_pest = -99999999999
    total_pest = 0
    thetas = np.arange(0.01, 1.0, 0.001)
    ps = np.zeros(len(thetas))

    for i in range(len(thetas)):
        th = thetas[i]
        pest = math.exp(-est.loglikelyhood_ICM([th, .0]))
        print(pest)
        if pest > best_pest:
            best_pest = pest
            est_th = th
        ps[i] = pest
        total_pest += pest

    print('True theta: ' + str(true_theta))
    print('Max liklehood estimation: ' + str(est_th) + ' ' + str(-0.1*math.log(1-est_th)))
    psnorm = stat.normalize_series(list(ps))
    confide = stat.confidential_from_p_series(psnorm, 0.95)
    print('0.95 confidential interval: (' + str(thetas[confide[0]]) + ', ' + str(thetas[confide[1]]) + ')')

    pyplot.plot(thetas, psnorm)
    pyplot.show()



if __name__ == '__main__':
    netwrk = make_test_network()
    # mngr = NetworkManager(netwrk, 'test', 'D:/Projects/Study/DASocialNetworksAnalysis/da_net/c_libs/')
    # mngr.save_to_file()
    #
    # result = Simulator.simulate_SI_decay_confirm_relicexp_hetero(underlying=netwrk, theta=0.02,
    #                                                              decay=0.02, relic=0.001, infected={1},
    #                                                              confirm=0,
    #                                                              tmax=300)
    # print(result)
    # result = {'outcome': {24: 1.0, 2: 5.0, 9: 20.0, 29: 23.0, 30: 24.0, 3: 30.0, 7: 33.0, 16: 34.0, 20: 36.0, 25: 36.0, 22: 43.0, 21: 44.0, 23: 45.0, 26: 46.0, 19: 47.0, 4: 51.0, 31: 53.0, 15: 54.0, 12: 58.0, 6: 66.0, 10: 67.0, 13: 78.0, 8: 83.0, 5: 85.0, 11: 85.0, 17: 97.0, 18: 98.0, 14: 120.0}, 'p': 1.1345161734664304e-59}

    # netwrk.export_gexf('D:/Projects/Study/Papers please/Networks_MLE_Gubanov/ntwrk_connected.gexf')
    # result = Simulator.simulate_SI_recover(underlying=netwrk, theta=0.05, recover_time=30,
    #                                         infected={1}, tmax=300, dt=1)
    # print(result['p'])
    # print(Simulator.estimate_SI_recover(underlying=netwrk, outcome=result['outcome'], theta=0.05, recover_time=30,
    #                                      initials={1}, tmax=300, dt=1))
    # test_SI_relic(netwrk, 0.05, 0.05)
    # test_SI_relic_libtest(netwrk, 0.02, 0.001, newlib=True, single_point=False)
    test_ICM_libtest(netwrk, 0.8, single_point=True)