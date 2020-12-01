# Created by Gubanov Alexander (aka Derzhiarbuz) at 18.02.2020
# Contacts: derzhiarbuz@gmail.com

from da_icascades_manager import CascadesManager
import da_net.da_diffusion_estimation as est
from da_net.da_diffusion_simulation import Simulator
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


def test_zashitim_taigu_noconfirm(post_id, new_lib=False):
    casman = CascadesManager(name='Zashitim_taigu_-164443025_8726_8021_6846', base_dir='D:/BigData/Charity/Cascades/')
    casman.load_from_file()
    cascade = casman.get_cascade_by_id(post_id)
    min_delay = cascade.get_minimum_delay()
    #outcome = cascade.get_outcome(normalization_factor=min_delay)
    outcome = cascade.get_outcome(normalization_factor=3600)
    counters = casman.underlying_net.counters_meta
    print(casman.get_underlying_path())
    tmax = max(outcome.values())
    tmax *= 1.5
    if new_lib:
        est.set_diffusion_data_newlib(casman.get_underlying_path(), outcome=outcome, observe_time=tmax)
        print('Max: ' + str(est.llmax_for_diffusion_noconfirm(8.65381982e-04, 3.07426738e-08, 1.53208126e-07, new_lib=True)))
    else:
        est.set_diffusion_data(casman.get_underlying_path(), counters=counters, outcome=outcome)
        print('Max: ' + str(est.llmax_for_diffusion_noconfirm(1.41127581e-03, 1.07595601e-10, 2.65026813e-07, observe_time=tmax)))


def test_zashitim_taigu_noconfirm_multiple(post_ids=None):
    casman = CascadesManager(name='Zashitim_taigu_-164443025_8726_8021_6846', base_dir='D:/BigData/Charity/Cascades/')
    casman.load_from_file()
    cascades = []
    outcomes = []
    tmaxs = []
    if post_ids is None:
        cascades = casman.cascades
    else:
        for post_id in post_ids:
            cascades.append(casman.get_cascade_by_id(post_id))
    for cascade in cascades:
        outcome = cascade.get_outcome(normalization_factor=3600)
        outcomes.append(outcome)
        tmaxs.append(1.5 * max(outcome.values()))
    print(casman.get_underlying_path())
    est.set_diffusion_data_ensemble_newlib(casman.get_underlying_path(), outcomes=outcomes, observe_times=tmaxs)
    thetas0 = [0.03807278732354531 for i in range(len(outcomes))]
    relics0 = [1.6563014252743482e-06 for i in range(len(outcomes))]
    #thetas0 = [6.640777840198647e-05, 2.0334495598850714e-05, 2.4494338855225353e-05]
    #relics0 = [1.1620706275554255e-08, 1.8733700717464615e-08, 3.811750042715803e-08]
    print('Max: ' + str(est.llmax_for_diffusion_noconfirm_multiple_cases(thetas0=thetas0, decay0=0.03688237209138165,
                                                                         relics0=relics0)))


def test_zashitim_taigu_noconfirm_converge(post_id, delta, steps = 10):
    casman = CascadesManager(name='Zashitim_taigu_-164443025_8726_8021_6846', base_dir='D:/BigData/Charity/Cascades/')
    casman.load_from_file()
    cascade = casman.get_cascade_by_id(post_id)
    outcome = cascade.get_outcome(normalization_factor=3600)
    print(casman.get_underlying_path())
    tmax = max(outcome.values())
    tmax *= 1.5
    delta_t = tmax/(20*steps+1)
    thetas = []
    rhos = []
    lengths = []
    thetasICM = []
    rhosICM = []
    print(outcome)
    for i in range(steps):
        t = delta_t*(i+1)
        new_outcome = {}
        for k, v in outcome.items():
            if v <= t:
                new_outcome[k] = v
        print("T: ", t)
        print("Outcome length: ", len(new_outcome))
        est.set_diffusion_data_newlib(casman.get_underlying_path(), outcome=new_outcome, observe_time=t)
        #est.set_alpha_for_node(-164443025, 15)
        result = est.llmax_for_diffusion_SI_relic(6.102733267373096e-05, 1.2196174044195352e-08, delta=delta
                                                  , new_lib=True)
        thetas.append(result['theta'])
        rhos.append(result['relic'])
        result2 = est.llmax_for_diffusion_ICM(0.0011, 0.0000011)
        thetasICM.append(result2['theta'])
        rhosICM.append(result2['relic'])
        lengths.append(len(new_outcome))
        print(thetas)
        print(rhos)
        print(lengths)
        print(thetasICM)
        print(rhosICM)


def test_zashitim_taigu_confirm_multiple(post_ids=None):
    casman = CascadesManager(name='Zashitim_taigu_-164443025_8726_8021_6846', base_dir='D:/BigData/Charity/Cascades/')
    casman.load_from_file()
    cascades = []
    outcomes = []
    tmaxs = []
    if post_ids is None:
        cascades = casman.cascades
    else:
        for post_id in post_ids:
            cascades.append(casman.get_cascade_by_id(post_id))
    for cascade in cascades:
        outcome = cascade.get_outcome(normalization_factor=3600)
        print(len(outcome))
        outcomes.append(outcome)
        tmaxs.append(1.5 * max(outcome.values()))
    return
    print(casman.get_underlying_path())
    est.set_diffusion_data_ensemble_newlib(casman.get_underlying_path(), outcomes=outcomes, observe_times=tmaxs)
    thetas0 = [2.0334495598850714e-05 for i in range(len(outcomes))]
    relics0 = [1.1620706275554255e-08 for i in range(len(outcomes))]
    confirms0 = [0. for i in range(len(outcomes))]
    #thetas0 = [6.640777840198647e-05, 2.0334495598850714e-05, 2.4494338855225353e-05]
    #relics0 = [1.1620706275554255e-08, 1.8733700717464615e-08, 3.811750042715803e-08]
    print('Max: ' + str(est.llmax_for_diffusion_confirm_multiple_cases(thetas0=thetas0, decay0=0.03688237209138165,
                                                                     relics0=relics0, confirms0=confirms0)))



def test_zashitim_taigu_ICM_compare(post_id):
    casman = CascadesManager(name='Zashitim_taigu_-164443025_8726_8021_6846', base_dir='D:/BigData/Charity/Cascades/')
    casman.load_from_file()
    cascades = []
    tmaxs = []
    cascade = casman.get_cascade_by_id(post_id)
    outcome_old = cascade.get_outcome(normalization_factor=3600)
    outcome = cascade.get_outcome_connected_only(casman.underlying_net.network.nodes, normalization_factor=3600)
    print("Outcome total size: " + str(len(outcome_old)))
    print("Outcome giant size: " + str(len(outcome)))
    print(outcome)
    print(casman.get_underlying_path())

    tmax = max(outcome.values())
    tmax *= 1.5

    est.set_diffusion_data_newlib(casman.get_underlying_path(), outcome=outcome, observe_time=tmax)
    #est.set_alpha_for_node(-164443025, 30)
    result1 = est.llmax_for_diffusion_SI_decay(1.49969075e-05, 1.34657003e-02)
    #result1 = est.llmax_for_diffusion_SI_decay(1.49969075e-05, 0.03545553788287585, fixed_delta=True)
    print(result1)
    result2 = est.llmax_for_diffusion_ICM(0.001)
    print(result2)
    print("1-exp(theta/delta): " + str(1. - math.exp(-result1['theta'] / result1['decay'])))
    #print("1-exp(theta/delta): " + str(1. - math.exp(-result1['theta'] / 0.03545553788287585)))
    print("ICM p: " + str(result2['theta']))


def test_zashitim_taigu_noconfirm_theta_graph(post_id, decay, relic):
    casman = CascadesManager(name='Zashitim_taigu_-164443025_8726_8021_6846', base_dir='D:/BigData/Charity/Cascades/')
    casman.load_from_file()
    cascade = casman.get_cascade_by_id(post_id)
    min_delay = cascade.get_minimum_delay()
    outcome = cascade.get_outcome(normalization_factor=min_delay)
    counters = casman.underlying_net.counters_meta
    print(casman.get_underlying_path())
    est.set_diffusion_data(casman.get_underlying_path(), counters=counters, outcome=outcome)

    print(outcome)
    tmax = max(outcome.values())
    tmax *= 1.5

    thetas = np.arange(1e-9, 1e-6, 1e-8)
    lls = np.zeros(len(thetas))
    maxll = -999999999999999999.
    for i in range(len(thetas)):
        lls[i] = -est.loglikelyhood_noconfirm([thetas[i], decay, relic], observe_time=tmax)
        print(str(i) + ' - ' + str(lls[i]))
        if(maxll < lls[i]):
            maxll = lls[i]
    maxll -= 300
    for i in range(len(thetas)):
        lls[i] = lls[i] - maxll
        print(lls[i])
        if lls[i] < 0:
            lls[i] = 0
        else:
            lls[i] = math.exp(lls[i])
    plt.plot(thetas, lls)
    plt.show()


def simulate_diffusion_cascades_zashitim_taigu(n_cascades, theta, rho, delta):
    casman = CascadesManager(name='Zashitim_taigu_-164443025_8726_8021_6846', base_dir='D:/BigData/Charity/Cascades/')
    casman.load_from_file()
    cascade = casman.get_cascade_by_id(6846)
    print(cascade.get_minimum_delay())
    print(max(cascade.get_outcome(normalization_factor=3600).values()))
    est.set_alpha_for_node(-164443025, 25)
    outcome = Simulator.simulate_SI_decay_confirm_relicexp_hetero(casman.underlying_net.network, theta,
                                                         delta, .0, rho, infected={-164443025}, tmax=2500., dt=30,
                                                                  echo=True)
    print(outcome)


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


def test_simulation_infections_ensemble_by_n_infections(netwrk, theta, decay, relic, n_infections, newlib=False):
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
        if newlib==True:
            observe_times = [600 for j in range(len(outcomes))]
            est.set_diffusion_data_ensemble_newlib(netman.get_dos_filepath(), outcomes=outcomes,
                                                   observe_times=observe_times, echo=True)
            estimation = est.llmax_for_diffusion_noconfirm(theta * math.exp((0.5 - random.random()) * 4),
                                                                    decay,
                                                                    relic * math.exp((0.5 - random.random()) * 4),
                                                                    disp=True, new_lib=True)
        else:
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

#822.0651840508349   [9.74602368e-04 9.33282684e-11 7.53877958e-08]
#[4.52900402e-06 7.22579458e-03 2.93421738e-10]
#[7.94957995e-06 1.34126881e-02 1.24927401e-09]

if __name__ == '__main__':
    #test_zashitim_taigu_confirm(8726) #8726: 1615.7052609591547   [1.13705951e-06 1.74581006e-03 3.25539755e-03 5.87984155e-09] //садим
    #test_zashitim_taigu_confirm(8021) #8021: 1183.585359582195   [1.00457047e-06 3.01659167e-03 2.99908438e-03 5.07020291e-09] //уничтожают
    #test_zashitim_taigu_confirm(6846) #6846: 4495.705121637081   [1.00019217e-12 3.61779381e-01 4.07895457e-06 1.24224204e-07]

    #test_zashitim_taigu_noconfirm(8726, new_lib=True) #8726: 1518.9405169617114   [3.36521979e-06 1.89269316e-03 1.19893198e-09] //садим
                                        #8726: 1465.5907051121358   [3.92357521e-06 2.40365989e-03 5.62792166e-07] (diff relic)
                                        #8726: 1305.008499198023 [2.09315858e-05 2.85589026e-02 2.61732097e-08] (prop relic)
                                        #8726: 1576.8013299857494   [4.72178036e-07 2.46718618e-04 2.80091069e-11] (decay relic)
                                        #8726: 1521.7875692581404   [4.24780551e-07 2.32506101e-04 6.90792330e-10] (decay relic no leafs)
                                        #8726: 1508.2234650968235   [1.77856652e-06 9.42131219e-04 3.45288650e-10] (decay relic long end)0.002

    #test_zashitim_taigu_noconfirm(8021, new_lib=True) #8021: 1141.2707004903534   [1.20088960e-06 1.76751640e-03 8.75065643e-10] //уничтожают
                                        #8021: 1092.0391011884008   [1.04792882e-06 1.68113820e-03 6.24631241e-07](diff relic)
                                        #8021: 938.7724928672329   [8.65774570e-06 4.89937777e-02 4.42351514e-08] (prop relic)
                                        #8021: 1188.4756416665496   [1.65643126e-07 2.34279104e-04 4.20309287e-11] (decay relic)
                                        #8021: 1143.5294896908626   [1.39992642e-07 2.17456783e-04 6.68459337e-10] (decay relic no leafs)
                                        #8021: 1136.2820233338227   [6.01466475e-07 8.67171929e-04 4.33981031e-10] (decay relic long end) 0,0007

    #test_zashitim_taigu_noconfirm(6846, new_lib=True) #6846: 4554.498599446362   [5.74562984e-06 7.95669549e-03 1.55133128e-08]
                                        #6846: 3990.998906822731   [6.25928617e-06 1.18988232e-02 1.33504284e-06](diff relic)
                                        #6846: 3791.5200987819803   [8.88895355e-06 2.33991702e-02 1.10156181e-08] (prop relic)
                                        #6846: 4547.146407866936   [4.19012993e-07 6.01627566e-04 5.09054380e-10] (decay relic)
                                        #6846: 4225.534759233273   [1.64294767e-07 5.57329221e-04 3.55493544e-09] (decay relic no leafs)
                                        #6846: 4246.321003453807   [3.22555046e-06 5.02214778e-03 6.16394310e-09] (decay relic long end)
    #test_zashitim_taigu_noconfirm_theta_graph(8726, 2.46718618e-04, 2.80091069e-11)  2.95552181e-11

    #test_zashitim_taigu_noconfirm_multiple(post_ids=[8726])

    # Ll: 5852.5117740654605
    # Thetas: [6.102733267373096e-05, 2.2008344720548056e-05, 2.1230399434836022e-05]
    # Rhos: [1.2196174044195352e-08, 1.5572985949922855e-08, 3.853480148801193e-08]
    # Delta: 0.03545553788287585
    # ex.time: 1.4830350875854492

    test_zashitim_taigu_confirm_multiple(post_ids=[8726, 8021, 6846])

    # Ll: 5852.511774141164
    # Thetas: [6.102736122507662e-05, 2.200835149443026e-05, 2.1230405270889833e-05]
    # Rhos: [1.2196176445101582e-08, 1.5573005788541055e-08, 3.8534804780101685e-08]
    # Kappas: [-0.014811312135620952, -0.006344429471057249, 0.0037329699918025906]
    # Delta: 0.03545554334901209
    # ex.time: 2.1731643676757812

    # test_zashitim_taigu_noconfirm_converge(post_id=8726, delta=0.03545553788287585, steps=30)
    # plt.plot([0.02739020256856477, 0.02155138130489766, 0.02474050411937095, 0.030445197506719424, 0.03515563999427032,
    #  0.04101709837334917, 0.03739790326753361, 0.033025217471092314, 0.02909643044684331, 0.027140527346224706,
    #  0.026668468972426716, 0.02454061026272751, 0.025233291623893594, 0.023491086430268558, 0.02216695041757661,
    #  0.021105715981197336, 0.02024147432405466, 0.019528407059590275, 0.019467828354012437, 0.01893092765588307,
    #  0.01844309210249198, 0.01854846884030329])
    # plt.plot([1.0000271222969609e-12, 1.0000107486215244e-12, 1.0019655697078902e-12, 1.0000032678798814e-12,
    #  1.0000397179815232e-12, 1.3034072675691228e-05, 1.7433539245899118e-05, 1.304138846913933e-05,
    #  1.0558717667395266e-05, 2.6967760205337693e-05, 3.020795978320705e-05, 3.2482122284714396e-05,
    #  3.156760722780071e-05, 3.2989690956672864e-05, 2.98716958830804e-05, 2.7550493705924205e-05,
    #  2.5765733730851252e-05, 2.4359059770259785e-05, 2.3279976984260784e-05, 2.2292257442336295e-05,
    #  2.3073046284036636e-05, 2.2245934750697657e-05])
    # plt.plot([.03, .04, .06, .09, .15, .24, .28, .29, .29, .34, .38, .40, .44, .46, .46, .46, .46, .46, .47, .47, .48, .49])

    # plt.plot([0.19560677551796804, 0.11431499902041657, 0.08598176469698096, 0.06680553074876275, 0.06316498582664339,
    #  0.06125463098154666, 0.05861096109727635, 0.05560700090784941, 0.05462907122281588, 0.050766260360861654,
    #  0.04779167531045929, 0.04741899233356536, 0.04902613935837981, 0.04786776558043397, 0.046976352827453396,
    #  0.04632210866612773, 0.045548882058556076, 0.04493776287116173, 0.04374450430009595, 0.04274161655563581,
    #  0.04189294887589705, 0.04117060558909547])
    # plt.plot([0.00015855963625165554, 6.213835332011928e-05, 3.847809373804816e-05, 2.8375933510133457e-05,
    #  2.2754966103422874e-05, 1.888785880409133e-05, 1.6102997223500495e-05, 2.0984976512783566e-05,
    #  1.848853015016057e-05, 1.8409107340458753e-05, 1.686033805503604e-05, 1.5686769245164392e-05,
    #  1.4583608413792875e-05, 1.500836634566632e-05, 1.6677078490913872e-05, 1.574991215629955e-05,
    #  1.6115172360892104e-05, 1.538043487145737e-05, 1.4779884801834399e-05, 1.4286972863458885e-05,
    #  1.3878005761068671e-05, 1.3535643062559923e-05])
    # plt.plot([.29, .34, .37, .37, .41, .45, .48, .53, .56, .57, .57, .59, .63, .65, .68, .69, .71, .72, .72, .72, .72, .72])

    # plt.plot([0.044328879875009074, 0.05380817685844283, 0.03948612213030057, 0.03967461662825422, 0.037044293606201324,
    #  0.03451942134537124, 0.037712236680750896, 0.0332983228151795, 0.03136222262712941, 0.029838667519936045,
    #  0.030913565811464802, 0.031415774256050834, 0.029125643392820973, 0.028847891539600375, 0.027553940042846732,
    #  0.026762906276598667, 0.024609596786593815, 0.024569819252210356, 0.02542878978631185, 0.024429369050092384,
    #  0.024128802451419663, 0.02347071263077736])
    # plt.plot([0.0001649700156111594, 0.00012463367792365953, 9.739708322275708e-05, 6.35952302929899e-05, 5.569836292191509e-05,
    #  4.701256795247798e-05, 0.0001050851413667053, 8.657728668770435e-05, 8.223634300396807e-05, 7.793685506398366e-05,
    #  8.93770514446263e-05, 8.350666071340262e-05, 7.098383011882299e-05, 6.488145873700322e-05, 6.256593531767866e-05,
    #  5.852170122756077e-05, 5.530517525576914e-05, 5.1929608169278146e-05, 5.0361237420022506e-05,
    #  4.974967598071249e-05, 4.754158426185314e-05, 4.555535205806397e-05])
    # plt.plot([.008, .019, .024, .028, .033, .036, .072, .080, .093, .105, .142, .166, .170, .181, .195,
    #           .204, .208, .214, .226, .234, .238, .239])
    # plt.show()

    #test_zashitim_taigu_ICM_compare(6846)
    #test_zashitim_taigu_noconfirm_converge(post_id=8726, delta=0.03545553788287585, steps=30)

    #test_SI_relic(1, show=True)
    #test_convergence()

    #test_zashitim_taigu_dlldthetas(8726, 4.72178036e-07, 2.46718618e-04, 2.80091069e-11)
    #test_zashitim_taigu_dlldthetas(8021, 1.65643126e-07, 2.34279104e-04, 4.20309287e-11)
    #test_zashitim_taigu_dlldthetas(6846, 4.19012993e-07, 6.01627566e-04, 5.09054380e-10)

    #test_simulation_dlldthetas(ut_stat.make_test_network_connected(), 0.005, 0.02, 0.0008)
    #test_simulation_infections_ensemble_by_n_infections(ut_stat.make_test_network(), 0.02, 0.02, 0.001, 50, newlib=True)
    #test_simulation_infections_ensemble_by_observe_time(ut_stat.make_test_network(), 0.02, 0.02, 0.001, 25, 500, 1)
    #test_display_simulation_infections_ensemble(ut_stat.make_test_network(), 0.02, 0.02, 0.001, 10)
    #test_likelyhood_decay()
    #test_convergence_atomic()

    # plt.plot(
    #     [0.0004902194888801517, 0.0002479550616054013, 0.00017744267316065166, 0.00013466819446571586,
    #      0.00012540702905511206, 0.00011986360238044379, 0.0001125612655628841, 0.00010502531627732637,
    #      0.00010148140318080227, 9.287172125655138e-05, 8.641792973190232e-05, 8.495739040360377e-05,
    #      8.691342340036425e-05, 8.394494333307988e-05, 8.160113359267041e-05, 7.981812282512721e-05,
    #      7.756679953381795e-05, 7.571051849398011e-05, 7.304673621494225e-05, 7.084427774107558e-05,
    #      6.900583556413583e-05, 6.745899298566958e-05]
    # )
    # plt.plot(
    #     [1.5877326033164795e-07, 6.211715662011333e-08, 3.852482820713728e-08, 2.8417521254647604e-08,
    #      2.283258956087074e-08, 1.8970071650040635e-08, 1.6186043439740414e-08, 2.106954299871376e-08,
    #      1.8583507271565243e-08, 1.8506347960802074e-08, 1.6951130902426297e-08, 1.5780661002473616e-08,
    #      1.4675754944701411e-08, 1.5098205012448525e-08, 1.6775793221240408e-08, 1.5836820866668746e-08,
    #      1.6204469032121717e-08, 1.5469303916306407e-08, 1.4866916981157067e-08, 1.4372381708246923e-08,
    #      1.3962006619202325e-08, 1.3618424151470623e-08]
    # )
    #
    # y = [.29, .34, .37, .37, .41, .45, .48, .53, .56, .57, .57, .59, .63, .65, .68, .69, .71, .72, .72, .72, .72, .72]
    # for i in range(len(y)):
    #     y[i] = y[i]/15000000
    # plt.plot(y)

    # x= \
    #     [0.0011097044523624225, 0.001225979202523413, 0.0013399159269713275, 0.0013399159269713275,
    #      0.0014719583312457697, 0.0015633762889117639, 0.001564616602684993, 0.001593924701615796,
    #      0.0016294654272376017, 0.0015936821800402652, 0.0015936821800402652, 0.0016445954077462875,
    #      0.0016680772219574785, 0.001691066693298956, 0.0016985195846476128, 0.00172712671473898, 0.0016086331652746181,
    #      0.0016239233630100667, 0.0016239233630100667, 0.0016239233630100667, 0.0016239233630100667,
    #      0.0016239233630100667]
    # x= \
    #     [3.409480878214383e-07, 2.9139354016485023e-07, 2.678192907923382e-07, 2.678192907923382e-07,
    #      2.417823439953761e-07, 2.206585260545211e-07, 2.0730341272142145e-07, 2.814579327857912e-07,
    #      2.6684023088457605e-07, 2.913081278634727e-07, 2.913081278634727e-07, 2.8138892993075224e-07,
    #      2.6396240804398863e-07, 2.814524635401581e-07, 3.176772393586177e-07, 3.1318689478189026e-07,
    #      3.2811054895059265e-07, 3.234856276633057e-07, 3.234856276633057e-07, 3.234856276633057e-07,
    #      3.234856276633057e-07, 3.234856276633057e-07]
    # for i in range(len(x)):
    #     x[i] = -0.03545553788287585*math.log(1-x[i])
    # plt.plot(x)
    # plt.show()

    #simulate_diffusion_cascades_zashitim_taigu(10, 6.102733267373096e-05, 1.2196174044195352e-08, 0.03545553788287585)
