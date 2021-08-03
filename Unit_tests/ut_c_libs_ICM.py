# Created by Gubanov Alexander (aka Derzhiarbuz) at 12.01.2021
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
import json

def test_zashitim_taigu_ICM(post_id):
    casman = CascadesManager(name='Zashitim_taigu_-164443025_8726_8021_6846', base_dir='D:/BigData/Charity/Cascades/')
    casman.load_from_file()

    cascade = casman.get_cascade_by_id(post_id)
    outcome_old = cascade.get_outcome(normalization_factor=3600)
    #outcome = cascade.get_outcome(normalization_factor=3600)
    outcome = cascade.get_outcome_connected_only(casman.underlying_net.network.nodes, normalization_factor=3600)
    print("Outcome total size: " + str(len(outcome_old)))
    print("Outcome giant size: " + str(len(outcome)))
    print(outcome)
    print(casman.get_underlying_path())

    tmax = max(outcome.values())
    tmax *= 1.5

    est.set_diffusion_data_newlib(casman.get_underlying_path(), outcome=outcome, observe_time=tmax)
    #result = est.llmax_for_diffusion_ICM(0.001, 0.001)
    result = est.llmax_for_diffusion_ICM(0.001)
    print(result)


def test_zashitim_taigu_ICM_CG_maximization(post_ids=None):
    casman = CascadesManager(name='Zashitim_taigu_-164443025_8726_8021_6846', base_dir='D:/BigData/Charity/Cascades/')
    casman.load_from_file()
    cascades = []
    outcomes = []
    tmaxs = []
    node_ids = set()
    if post_ids is None:
        cascades = casman.cascades
    else:
        for post_id in post_ids:
            cascade = casman.get_cascade_by_id(post_id)
            cascades.append(casman.get_cascade_by_id(post_id))
            outcome = cascade.get_outcome(normalization_factor=3600)
    for cascade in cascades:
        outcome = cascade.get_outcome(normalization_factor=3600)
        # outcome = cascade.get_outcome_connected_only(casman.underlying_net.network.nodes, normalization_factor=3600)
        print(len(outcome))
        outcomes.append(outcome)
        tmaxs.append(1.5 * max(outcome.values()))
        for node_id in outcome.keys():
            node_ids.add(node_id)

    print(casman.get_underlying_path())
    est.set_diffusion_data_ensemble_newlib(casman.get_underlying_path(), outcomes=outcomes, observe_times=tmaxs)
    thetas = [0.001766310313898732, 0.0006220037483077741, 0.0006039983607293529]
    relics = [3.098132753601853e-07, 4.3642396881118776e-07, 1.081983134799611e-06]
    alphas = [1., 1., 1.]
    node_ids = [5932908, 26000687, -164443025]
    est.set_alphas_pattern(node_ids)
    res = est.llmax_gradient_ICM(thetas+relics+alphas, nodes=node_ids)
    print(res)



def test_zashitim_taigu_ICM_gradient(post_ids=None):
    casman = CascadesManager(name='Zashitim_taigu_-164443025_8726_8021_6846', base_dir='D:/BigData/Charity/Cascades/')
    casman.load_from_file()
    cascades = []
    outcomes = []
    tmaxs = []
    node_ids = set()
    if post_ids is None:
        cascades = casman.cascades
    else:
        for post_id in post_ids:
            cascade = casman.get_cascade_by_id(post_id)
            cascades.append(casman.get_cascade_by_id(post_id))
            outcome = cascade.get_outcome(normalization_factor=3600)
    for cascade in cascades:
        #outcome = cascade.get_outcome(normalization_factor=3600)
        outcome = cascade.get_outcome_connected_only(casman.underlying_net.network.nodes, normalization_factor=3600)
        print(len(outcome))
        outcomes.append(outcome)
        tmaxs.append(1.5 * max(outcome.values()))
        for node_id in outcome.keys():
            node_ids.add(node_id)

    print(casman.get_underlying_path())
    est.set_diffusion_data_ensemble_newlib(casman.get_underlying_path(), outcomes=outcomes, observe_times=tmaxs)
    #thetas = [1.76631131e-03, 6.22004748e-04, 6.03998761e-04]
    #relics = [3.098131172e-07, 4.36424345e-07, 1.081983813e-06]
    thetas = [0.0019349592887878445, 0.0006143192291259756, 0.0011128020422363283]
    relics = [0, 0, 0]
    nodes = list(node_ids)
    alphas = [1. for i in range(len(nodes))]
    result = est.gradient_ICM(thetas, relics, alphas, nodes)
    print(result)
    lll = []
    for i in range(len(nodes)):
        lll.append((nodes[i], result['dalphas'][i]))
    lll.sort(key=lambda x: x[1])
    print(lll)
    dalparr = np.array(result['dalphas'])
    print("Mean: " + str(dalparr.mean()))
    plt.hist(dalparr+1, bins=100)
    plt.show()



if __name__ == '__main__':
    #test_zashitim_taigu_ICM(8726)
    test_zashitim_taigu_ICM_gradient([8726, 8021, 6846])
    #test_zashitim_taigu_ICM_CG_maximization([8726, 8021, 6846])

#8726: {'theta': 0.001766310313898732, 'relic': 3.098132753601853e-07}
#8021: {'theta': 0.0006220037483077741, 'relic': 4.3642396881118776e-07}
#6846: {'theta': 0.0006039983607293529, 'relic': 1.081983134799611e-06}

#8726: {'theta': 0.0019350092887878445}
#8021: {'theta': 0.0006143192291259756}
#6846: {'theta': 0.0011128120422363283}

# [1.76631031e-03 6.22003748e-04 6.03998361e-04 3.09813059e-07
#  4.36424213e-07 1.08198382e-06 1.00000000e+00 1.00000000e+00
#  1.00000000e+00]
