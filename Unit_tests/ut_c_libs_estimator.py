# Created by Gubanov Alexander (aka Derzhiarbuz) at 18.02.2020
# Contacts: derzhiarbuz@gmail.com

from da_icascades_manager import CascadesManager
import Statistics.da_diffusion_estimation as est
from Statistics.da_diffusion_simulation import Simulator
from da_network_manager import NetworkManager
import Unit_tests.ut_statanalysis as st_test
import Unit_tests.ut_plot_renderer as pl_rend
import random
import numpy as np
import matplotlib.pyplot as plt
import math
import Unit_tests.ut_statanalysis as ut_stat
import scipy.stats as sp_stat


def test_network_manager(ntype=None):
    if ntype is None:
        net = st_test.make_test_network()
    elif ntype.lower() == 'connected':
        net = st_test.make_test_network_connected()
    elif ntype.lower() == 'star':
        net = st_test.make_test_network_star()
    elif ntype.lower() == 'chain':
        net = st_test.make_test_network_chain()
    else:
        net = st_test.make_test_network()
    net_man = NetworkManager(net, 'ut_c_libs_estimator_test', '../Output/')
    net_man.save_to_file()
    return net_man


def test_convergence(niter=10):
    nm = test_network_manager()
    result = Simulator.simulate_SI_relic(underlying=nm.network, theta=0.1, relic=0.005,
                                            infected={1}, tmax=300, dt=0.01)
    result['outcome'][1] = 0.0
    est.set_diffusion_data(nm.get_dos_filepath(), counters=None, outcome=result['outcome'])
    for i in range(niter):
        t0 = random.random() + 1e-12
        r0 = random.random() + 1e-12
        print('Max: ' + str(est.llmax_for_diffusion_SI_relic(t0, r0)))


def test_SI_relic(niter=10, show=False):
    nm = test_network_manager()
    result = Simulator.simulate_SI_relic(underlying=nm.network, theta=0.05, relic=0.01,
                                            infected={1}, tmax=300, dt=0.01)
    result['outcome'][1] = 0.0
    est.set_diffusion_data(nm.get_dos_filepath(), counters=None, outcome=result['outcome'])

    t0 = random.random() + 1e-12
    r0 = random.random() + 1e-12
    res = est.llmax_for_diffusion_SI_relic(t0, r0)
    print('Max: ' + str(res))
    print(result['outcome'])
    if show:
        thetas = np.arange(1e-12, 0.1, 0.001)
        relics = np.arange(1e-12, 0.1, 0.001)
        func = generate_ll_func_SI_relic(nm, result['outcome'], thetas, relics)
        pl_rend.show_likelyhood_heatmap2D(thetas, relics, func, [0.05, 0.01],
                                          [res['theta'], res['relic']],
                                          xlabel='theta', ylabel='relic', exp=True)



def generate_ll_func_SI_relic(nmanager, outcome, thetas, relics):
    est.set_diffusion_data(nmanager.get_dos_filepath(), counters=None, outcome=outcome)
    ps = np.zeros((len(thetas), len(relics)))
    for i in range(len(thetas)):
        for j in range(len(relics)):
            ps[i][j] = -est.loglikelyhood_SI_relic([thetas[i], relics[j]])
    return ps


def test_zashitim_taigu_confirm(post_id):
    casman = CascadesManager(name='Zashitim_taigu_-164443025_8726_8021_6846', base_dir='D:/BigData/Charity/Cascades/')
    casman.load_from_file()
    cascade = casman.get_cascade_by_id(post_id)
    min_delay = cascade.get_minimum_delay()
    outcome = cascade.get_outcome(normalization_factor=min_delay)
    counters = casman.underlying_net.counters_meta
    print(casman.get_underlying_path())
    est.set_diffusion_data(casman.get_underlying_path(), counters=counters, outcome=outcome)
    print('Max: ' + str(est.llmax_for_diffusion(1.00019217e-6, 3.61779381e-01, 4.07895457e-03, 1.24224204e-07)))


def test_zashitim_taigu_noconfirm(post_id):
    casman = CascadesManager(name='Zashitim_taigu_-164443025_8726_8021_6846', base_dir='D:/BigData/Charity/Cascades/')
    casman.load_from_file()
    cascade = casman.get_cascade_by_id(post_id)
    min_delay = cascade.get_minimum_delay()
    outcome = cascade.get_outcome(normalization_factor=min_delay)
    counters = casman.underlying_net.counters_meta
    print(casman.get_underlying_path())
    est.set_diffusion_data(casman.get_underlying_path(), counters=counters, outcome=outcome)
    print('Max: ' + str(est.llmax_for_diffusion_noconfirm(1.64303668e-07, 5.57331835e-04, 3.55493627e-09)))


def show_dlldthetas(dlldthetas):
    l = list(dlldthetas.items())
    l.sort(key=lambda i: i[1])
    for itm in l:
        print(str(itm[0]) + " : " + str(itm[1]))

    vals = []
    for val in dlldthetas.values():
        if val >= 0:
            vals.append(math.log10(1. + val))
        else:
            vals.append(-math.log10(1. - val))
    # plt.hist(vals, bins=50)
    # plt.show()
    plt.hist(dlldthetas.values(), bins=50)
    plt.show()


def test_zashitim_taigu_dlldthetas(post_id, theta, decay, relic):
    casman = CascadesManager(name='Zashitim_taigu_-164443025_8726_8021_6846', base_dir='D:/BigData/Charity/Cascades/')
    casman.load_from_file()
    cascade = casman.get_cascade_by_id(post_id)
    min_delay = cascade.get_minimum_delay()
    outcome = cascade.get_outcome(normalization_factor=min_delay)
    counters = casman.underlying_net.counters_meta
    print(casman.get_underlying_path())
    est.set_diffusion_data(casman.get_underlying_path(), counters=counters, outcome=outcome)
    dlldthetas = est.dlldthetas_noconfirm(theta, decay, relic, outcome.keys())
    cascade.network.add_node_attribute('dth', 'dLL_dTheta', 'float')
    for k, v in dlldthetas.items():
        cascade.network.add_meta_for_node(k, {'dth': v})
    cascade.network.export_gexf('D:/BigData/Charity/Cascades/Zashitim_taigu_-164443025_'+str(post_id)+'_dlldth.gexf')
    show_dlldthetas(dlldthetas)


def test_simulation_dlldthetas(netwrk, theta, decay, relic):
    netman = NetworkManager(net=netwrk, name='temp', base_dir='D:/BigData/Charity/Cascades/')
    netman.save_to_file()
    targ_id = 2
#    for i in range(100):
    thetas = {}
    for j in netman.network.nodes_ids:
        thetas[j] = theta * math.exp((0.5 - random.random()) * 4)
    thetas[targ_id] *= 10
    l = list(thetas.items())
    l.sort(key=lambda i: i[1])
    true_rank = 0
    i = 0
    for el in l:
        print(str(el[0])+' : '+str(el[1]))
        i += 1
        if el[0]==targ_id:
            true_rank = i

    N = 10
    avg_dll_rank = .0
    avg_ll_rank = .0
    avg_dll_corr = .0
    avg_ll_corr = .0
    dll_rank_diff = .0
    ll_rank_diff = .0
    for kk in range(N):
        result = Simulator.simulate_SI_decay_confirm_relicexp_hetero(underlying=netwrk, theta=theta, relic=relic,
                                                                 confirm=.0, decay=decay, infected={1}, tmax=300,
                                                                 dt=0.01, thetas=thetas)
        result['outcome'][1] = .0
        #print(result)
        est.set_diffusion_data(netman.get_dos_filepath(), counters={}, outcome=result['outcome'], echo=False)
        estimation = est.llmax_for_diffusion_noconfirm(theta, decay, relic, disp=False)
        #print('Max: ' + str(estimation))
        dlldthetas = est.dlldthetas_noconfirm(estimation['theta'], estimation['decay'],
                                              estimation['relic'], result['outcome'].keys(), 300)

        outcome_sorted = list(result['outcome'].items())
        outcome_sorted.sort(key=lambda i: i[1])
        out_thetas = []
        llthetas_sorted = []
        llthetas = {}
        dlldthetas_sorted = []
        for node_id in result['outcome'].keys():
            out_thetas.append(thetas[node_id])
            dlldthetas_sorted.append(dlldthetas[node_id])
            llthetas[node_id] = est.llmax_for_diffusion_noconfirm_by_node_theta(node_id, estimation['theta'], estimation['decay'],
                                                            estimation['relic'], (0.0001, 1.), disp=False)
            llthetas_sorted.append(llthetas[node_id])

        avg_dll_corr += sp_stat.spearmanr(out_thetas, dlldthetas_sorted)[0]
        avg_ll_corr += sp_stat.spearmanr(out_thetas, llthetas_sorted)[0]

        print('true_rank: ' + str(true_rank))

        l = list(dlldthetas.items())
        l.sort(key = lambda i: i[1])
        for pp in range(len(l)):
            if l[pp][0] == targ_id:
                print('dll_rank: ' + str(pp))
                avg_dll_rank += pp
                dll_rank_diff += abs(pp-true_rank)
                break

        l = list(llthetas.items())
        l.sort(key=lambda i: i[1])
        for pp in range(len(l)):
            if l[pp][0] == targ_id:
                print('ll_rank: ' + str(pp) + '   est_theta: ' + str(l[pp][1]) + '   theta: '
                      + str(estimation['theta']))
                avg_ll_rank += pp
                ll_rank_diff += abs(pp - true_rank)
                break

    print('avg_dll_rank: ' + str(avg_dll_rank/N))
    print('avg_dll_corr: ' + str(avg_dll_corr/N))
    print('avg_ll_rank: ' + str(avg_ll_rank/N))
    print('avg_ll_corr: ' + str(avg_ll_corr/N))
    print('true_rank: ' + str(true_rank))
    print('dll_rank_diff ' + str(dll_rank_diff/N))
    print('ll_rank_diff ' + str(ll_rank_diff / N))

    #print('True ths vs dll_dths: '+str(sp_stat.spearmanr(a=out_thetas, b=dlldthetas_sorted)))
    #print('True ths vs ll_ths: ' + str(sp_stat.spearmanr(a=out_thetas, b=llthetas_sorted)))
    #print('Ll_ths vs dll_dths: ' + str(sp_stat.spearmanr(a=llthetas_sorted, b=dlldthetas_sorted)))

    #show_dlldthetas(dlldthetas)
    #ntest = sp_stat.normaltest(list(dlldthetas.values()))
    #print('P-value: ' + str(ntest[1]))


def test_simulation_infections_ensemble_by_n_infections(netwrk, theta, decay, relic, n_infections):
    netman = NetworkManager(net=netwrk, name='temp', base_dir='D:/BigData/Charity/Cascades/')
    netman.save_to_file()

    ths = []
    rels = []
    decs = []
    thnorms = []
    th = []
    rl = []
    dc = []
    for i in range(n_infections):
        outcomes = []
        for kk in range(i):
            start_id = random.randint(1, 29)
            result = Simulator.simulate_SI_decay_confirm_relicexp_hetero(underlying=netwrk, theta=theta, relic=relic,
                                                                         confirm=.0, decay=decay, infected={start_id},
                                                                         tmax=300, dt=0.01)
            result['outcome'][start_id] = .0
            outcomes.append(result['outcome'])
        est.set_diffusion_data_ensemble(netman.get_dos_filepath(), counters={}, outcomes=outcomes, echo=True)
        estimation = est.llmax_for_diffusion_noconfirm_ensemble(theta * math.exp((0.5 - random.random()) * 4),
                                                                decay,
                                                                relic * math.exp((0.5 - random.random()) * 4),
                                                                disp=True, observe_time=600)
        print('Max: ' + str(estimation))
        print('Norm: ' + str(estimation['theta']/estimation['relic']))
        ths.append(estimation['theta'])
        rels.append(estimation['relic'])
        decs.append(estimation['decay'])
        thnorms.append(estimation['theta']/estimation['relic'])
        th.append(theta)
        rl.append(relic)
        dc.append(decay)
    # plt.plot(ths)
    # plt.plot(rels)
    # plt.plot(decs)
    plt.plot(ths, 'r')
    plt.plot(th, 'r--')
    plt.plot(rels, 'g')
    plt.plot(rl, 'g--')
    plt.plot(decs, 'b')
    plt.plot(dc, 'b--')
    plt.show()
    #est.loglikelyhood_noconfirm_ensemble([theta, 0.02, relic])
    #return


def test_simulation_infections_ensemble_by_observe_time(netwrk, theta, decay, relic, n_infections, tmax, dt):
    netman = NetworkManager(net=netwrk, name='temp', base_dir='D:/BigData/Charity/Cascades/')
    netman.save_to_file()

    ths = []
    rels = []
    decs = []
    thnorms = []
    th = []
    rl = []
    dc = []
    outcomes = []
    for kk in range(n_infections):
        start_id = random.randint(1, 29)
        result = Simulator.simulate_SI_decay_confirm_relicexp_hetero(underlying=netwrk, theta=theta, relic=relic,
                                                                     confirm=.0, decay=decay, infected={start_id},
                                                                     tmax=tmax, dt=0.01)
        result['outcome'][start_id] = .0
        outcomes.append(result['outcome'])

    for i in range(40, tmax, dt):
        outcomes_trimmed = []
        for outcome in outcomes:
            new_outcome = {}
            for node_id, time in outcome.items():
                if time <= i:
                    new_outcome[node_id] = time
            outcomes_trimmed.append(new_outcome)
        print(outcomes_trimmed)

        est.set_diffusion_data_ensemble(netman.get_dos_filepath(), counters={}, outcomes=outcomes_trimmed, echo=True)
        estimation = est.llmax_for_diffusion_noconfirm_ensemble(theta * math.exp((0.5 - random.random()) * 4),
                                                                decay,
                                                                relic * math.exp((0.5 - random.random()) * 4),
                                                                disp=True, observe_time=i)
        print('Max: ' + str(estimation))
        print('Norm: ' + str(estimation['theta']/estimation['relic']))
        ths.append(estimation['theta'])
        rels.append(estimation['relic'])
        decs.append(estimation['decay'])
        thnorms.append(estimation['theta']/estimation['relic'])
        th.append(theta)
        rl.append(relic)
        dc.append(decay)
    # plt.plot(ths)
    # plt.plot(rels)
    # plt.plot(decs)
    plt.plot(ths, 'r')
    plt.plot(th, 'r--')
    plt.plot(rels, 'g')
    plt.plot(rl, 'g--')
    plt.plot(decs, 'b')
    plt.plot(dc, 'b--')
    plt.show()
    #est.loglikelyhood_noconfirm_ensemble([theta, 0.02, relic])
    #return


def test_display_simulation_infections_ensemble(netwrk, theta, decay, relic, n_infections):
    netman = NetworkManager(net=netwrk, name='temp', base_dir='D:/BigData/Charity/Cascades/')
    netman.save_to_file()
    dt = 0.01
    tmax = 80

    outcomes = []
    initials = []
    for kk in range(n_infections):
        start_id = random.randint(1, 29)
        start_id = 1
        initials.append(start_id)
        result = Simulator.simulate_SI_decay_confirm_relicexp_hetero(underlying=netwrk, theta=theta, relic=relic,
                                                                     confirm=.0, decay=decay, infected={start_id},
                                                                     tmax=tmax, dt=dt, echo=False)
        result['outcome'][start_id] = .0
        outcomes.append(result['outcome'])
    est.set_diffusion_data_ensemble(netman.get_dos_filepath(), counters={}, outcomes=outcomes, echo=True)

    # p1 = .0
    # for kk in range(n_infections):
    #     p = math.log(Simulator.estimate_SI_decay_confirm_relicexp_hetero(underlying=netwrk, theta=theta,
    #                                                                           relic=relic,
    #                                                                           confirm=.0, decay=decay,
    #                                                                           initials={initials[kk]},
    #                                                                           tmax=tmax, dt=dt, echo=True,
    #                                                                           outcome=outcomes[kk])
    #               /(dt**(len(outcomes[kk])-1)))
    #     p1 += p
    #     print(str(p) + '\n')
    #
    # p2 = -est.loglikelyhood_noconfirm_ensemble([theta, decay, relic], observe_time=tmax)
    # print(p1)
    # print(p2)
    #
    # return

    thetas = np.arange(0.0001, 0.05, 0.0005)
    relics = np.arange(0.0001, 0.05, 0.0005)
    ps = np.zeros((len(thetas), len(relics)))
    ps2 = np.zeros((len(thetas), len(relics)))
    best_pest = 1.0
    best_pest2 = 1.0
    # for kk in range(n_infections):
    #     best_pest += math.log(Simulator.estimate_SI_decay_confirm_relicexp_hetero(underlying=netwrk, theta=thetas[0],
    #                                                                 relic=relic,
    #                                                                 confirm=.0, decay=relics[0], initials={initials[kk]},
    #                                                                 tmax=tmax, dt=dt, echo=False,
    #                                                                 outcome=outcomes[kk])/(dt**(len(outcomes[kk])-1)))
    best_pest2 = -est.loglikelyhood_noconfirm_ensemble([thetas[0], relics[0], relic], observe_time=tmax)
    est_th = 0
    est_dc = 0
    est_th2 = 0
    est_dc2 = 0
    i = 0
    for th in thetas:
        dc = 0.0
        j = 0
        for dc in relics:
            pest = .0
            # for kk in range(n_infections):
            #     pest += math.log(Simulator.estimate_SI_decay_confirm_relicexp_hetero(underlying=netwrk, theta=th,
            #                                                                 relic=relic,
            #                                                     confirm=.0, decay=dc, initials={initials[kk]},
            #                                                     tmax=tmax, dt=dt, echo=False,
            #                                                                 outcome=outcomes[kk])/(dt**(len(outcomes[kk])-1)))
            pest2 = -est.loglikelyhood_noconfirm_ensemble([th, dc, relic], observe_time=tmax)
            print(str(th) + ' ' + str(dc) + ' ' + str(pest) + ' ' + str(pest2) + ' ' + str(abs(pest-pest2)))
            if pest > best_pest:
                best_pest = pest
                est_th = th
                est_dc = dc
            ps[i][j] = pest
            if pest2 > best_pest2:
                best_pest2 = pest2
                est_th2 = th
                est_dc2 = dc
            ps2[i][j] = pest2
            j += 1
        i += 1

    relics, thetas = np.meshgrid(relics, thetas)

    border_pest = best_pest-300
    for i in range(len(thetas)):
        for j in range(len(relics)):
            if ps[i][j] >= border_pest:
                ps[i][j] = math.exp(ps[i][j]-border_pest)
            else:
                ps[i][j] = .0

    plt.subplot(1,2,1)
    #plt.figure(figsize=(5, 5))
    plt.xlabel('$\\theta$ (virulence)')
    plt.ylabel('$\\delta$ (decay)')
    plt.contourf(thetas, relics, ps, levels=15)
    plt.scatter([est_th], [est_dc], color='blue', marker='+')
    plt.scatter([theta], [decay], color='red', marker='o')
    #plt.show()

    border_pest2 = best_pest2 - 300
    for i in range(len(thetas)):
        for j in range(len(relics)):
            if ps2[i][j] >= border_pest2:
                ps2[i][j] = math.exp(ps2[i][j] - border_pest2)
            else:
                ps2[i][j] = .0

    plt.subplot(1, 2, 2)
    #plt.figure(figsize=(5, 5))
    plt.xlabel('$\\theta$ (virulence)')
    plt.ylabel('$\\delta$ (decay)')
    plt.contourf(thetas, relics, ps2, levels=15)
    plt.scatter([est_th2], [est_dc2], color='blue', marker='+')
    plt.scatter([theta], [decay], color='red', marker='o')
    plt.show()


def test_likelyhood_decay():
    N = 1000
    dt = 0.001
    M = 1000
    theta = 0.03
    decay = 0.002
    outcomes = []
    for i in range(M):
        outcomes.append(-1.)
        for j in range(N):
            t = j*dt
            if t>0:
                prob = theta*dt*(math.exp(-decay*t))
            else:
                prob = .0
            if random.random() <= prob:
                outcomes[len(outcomes)-1] = t
                break
    print(outcomes)

    thetas = np.arange(0.0001, 0.1, 0.0005)
    decays = np.arange(0.01, 1, 0.005)
    #decays = np.zeros(1000)
    ps = np.zeros((len(thetas), len(decays)))
    best_pest = -math.inf
    est_th = 0
    est_dc = 0
    i = 0
    ths = []
    for th in thetas:
        dc = 0.0
        j = 0
        for dc in decays:
            pest = 0
            for outcome in outcomes:
                if outcome < .0:
                    pest -= th*(1/(1-dc)*(N*dt)**(1-dc))
                else:
                    pest += math.log(th * outcome**-dc) - th*(1/(1-dc)*outcome**(1-dc))
            #print(str(th) + ' ' + str(pest))
            if pest > best_pest:
                best_pest = pest
                est_th = th
                est_dc = dc
            ps[i][j] = pest
            j += 1
        ths.append(math.exp(ps[i][0]))
        i += 1

    #plt.plot(thetas, ths)
    #plt.show()
    border_pest = best_pest - 300
    for i in range(len(thetas)):
        for j in range(len(decays)):
            if ps[i][j] >= border_pest:
                ps[i][j] = math.exp(ps[i][j] - border_pest)
            else:
                ps[i][j] = .0

    decays, thetas = np.meshgrid(decays, thetas)
    plt.figure(figsize=(5, 5))
    plt.xlabel('$\\theta$ (theta)')
    plt.ylabel('$\\delta$ (decay)')
    plt.contourf(thetas, decays, ps, levels=15)
    plt.scatter([est_th], [est_dc], color='blue', marker='+')
    plt.scatter([theta], [decay], color='red', marker='o')
    plt.show()


def test_convergence_atomic():
    fun1 = []
    fun2 = []
    dts = [1, 0.1, 0.01, 0.001, 0.0001]
    decay = 0.02
    T = 10
    thetas = np.arange(0.0001, 0.1, 0.0005)
    fun1 = np.zeros((len(dts), len(thetas)))
    fun2 = np.zeros(len(thetas))
    for i in range(len(thetas)):
        fun2[i] = thetas[i] * (-1/decay) * (1. - math.exp(-decay * T))
        for j in range(len(dts)):
            dt = dts[j]
            N = int(T / dt)
            fun1[j][i] = .0
            for k in range(N):
                fun1[j][i] += math.log(1. - thetas[i] * math.exp(-decay * k * dt) * dt)
            #fun1[j][i] = math.log(fun1[j][i])
    for j in range(len(dts)):
        plt.plot(fun1[j])
    plt.plot(fun2, 'r--')
    plt.show()


def test_generated():
    print('ttt')



if __name__ == '__main__':
    #test_zashitim_taigu_confirm(8726) #8726: 1615.7052609591547   [1.13705951e-06 1.74581006e-03 3.25539755e-03 5.87984155e-09] //садим
    #test_zashitim_taigu_confirm(8021) #8021: 1183.585359582195   [1.00457047e-06 3.01659167e-03 2.99908438e-03 5.07020291e-09] //уничтожают
    #test_zashitim_taigu_confirm(6846) #6846: 4495.705121637081   [1.00019217e-12 3.61779381e-01 4.07895457e-06 1.24224204e-07]

    #test_zashitim_taigu_noconfirm(8726) #8726: 1518.9405169617114   [3.36521979e-06 1.89269316e-03 1.19893198e-09] //садим
                                        #8726: 1465.5907051121358   [3.92357521e-06 2.40365989e-03 5.62792166e-07] (diff relic)
                                        #8726: 1305.008499198023 [2.09315858e-05 2.85589026e-02 2.61732097e-08] (prop relic)
                                        #8726: 1576.8013299857494   [4.72178036e-07 2.46718618e-04 2.80091069e-11] (decay relic)
                                        #8726: 1521.7875692581404   [4.24780551e-07 2.32506101e-04 6.90792330e-10] (decay relic no leafs)

    #test_zashitim_taigu_noconfirm(8021) #8021: 1141.2707004903534   [1.20088960e-06 1.76751640e-03 8.75065643e-10] //уничтожают
                                        #8021: 1092.0391011884008   [1.04792882e-06 1.68113820e-03 6.24631241e-07](diff relic)
                                        #8021: 938.7724928672329   [8.65774570e-06 4.89937777e-02 4.42351514e-08] (prop relic)
                                        #8021: 1188.4756416665496   [1.65643126e-07 2.34279104e-04 4.20309287e-11] (decay relic)
                                        #8021: 1143.5294896908626   [1.39992642e-07 2.17456783e-04 6.68459337e-10] (decay relic no leafs)

    #test_zashitim_taigu_noconfirm(6846) #6846: 4554.498599446362   [5.74562984e-06 7.95669549e-03 1.55133128e-08]
                                        #6846: 3990.998906822731   [6.25928617e-06 1.18988232e-02 1.33504284e-06](diff relic)
                                        #6846: 3791.5200987819803   [8.88895355e-06 2.33991702e-02 1.10156181e-08] (prop relic)
                                        #6846: 4547.146407866936   [4.19012993e-07 6.01627566e-04 5.09054380e-10] (decay relic)
                                        #6846: 4225.534759233273   [1.64294767e-07 5.57329221e-04 3.55493544e-09] (decay relic no leafs)

    #test_SI_relic(1, show=True)
    #test_convergence()

    #test_zashitim_taigu_dlldthetas(8726, 4.72178036e-07, 2.46718618e-04, 2.80091069e-11)
    #test_zashitim_taigu_dlldthetas(8021, 1.65643126e-07, 2.34279104e-04, 4.20309287e-11)
    #test_zashitim_taigu_dlldthetas(6846, 4.19012993e-07, 6.01627566e-04, 5.09054380e-10)

    test_simulation_dlldthetas(ut_stat.make_test_network_connected(), 0.005, 0.02, 0.0008)
    #test_simulation_infections_ensemble_by_n_infections(ut_stat.make_test_network(), 0.02, 0.02, 0.001, 50)
    #test_simulation_infections_ensemble_by_observe_time(ut_stat.make_test_network(), 0.02, 0.02, 0.001, 25, 500, 1)
    #test_display_simulation_infections_ensemble(ut_stat.make_test_network(), 0.02, 0.02, 0.001, 100)
    #test_likelyhood_decay()
    #test_convergence_atomic()