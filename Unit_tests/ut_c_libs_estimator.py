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
#    for i in range(100):
    thetas = {}
    for j in netman.network.nodes_ids:
        thetas[j] = theta * math.exp((0.5 - random.random()) * 4)
    l = list(thetas.items())
    l.sort(key=lambda i: i[1])
    for el in l:
        print(str(el[0])+' : '+str(el[1]))
    result = Simulator.simulate_SI_decay_confirm_relicexp_hetero(underlying=netwrk, theta=theta, relic=relic,
                                                             confirm=.0, decay=decay, infected={1}, tmax=300,
                                                             dt=0.01, thetas=thetas)
    result['outcome'][1] = .0
    print(result)
    est.set_diffusion_data(netman.get_dos_filepath(), counters={}, outcome=result['outcome'])
    estimation = est.llmax_for_diffusion_noconfirm(theta, decay, relic, disp=False)
    #estimation = est.llmax_for_diffusion_SI_relic(theta, relic)
    print('Max: ' + str(estimation))
    dlldthetas = est.dlldthetas_noconfirm(estimation['theta'], estimation['decay'],
                                          estimation['relic'], result['outcome'].keys())
    print(sp_stat.spearmanr(a=list(thetas.values()), b=list(dlldthetas.values())))
    show_dlldthetas(dlldthetas)
    ntest = sp_stat.normaltest(list(dlldthetas.values()))
    print('P-value: ' + str(ntest[1]))


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

    test_simulation_dlldthetas(ut_stat.make_test_network(), 0.01, 0.02, 0.002)