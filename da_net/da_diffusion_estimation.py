# Created by Gubanov Alexander (aka Derzhiarbuz) at 19.11.2019
# Contacts: derzhiarbuz@gmail.com

from da_net.da_diffusion_simulation import Simulator
from da_network import Network
from da_net.da_c_libs import DiffusionEstimator
import da_net.danet as new_lib
import numpy as np
from scipy.optimize import minimize
from scipy.optimize import minimize_scalar
import time


def estimate_pvalue_SI(underlying: Network, theta: float, outcome: dict, initials: set, immunes: set = set(),
                    tmax=1000.0, dt=1, n_iterations=10000):
    est_p = Simulator.estimate_SI(underlying=underlying, theta=theta, outcome=outcome, initials=initials,
                                  tmax=tmax, dt=dt)
    n_less = 0
    for i in range(n_iterations):
        result = Simulator.simulate_SI(underlying=underlying, theta=theta, infected=initials, immunes=immunes,
                                       tmax=tmax, dt=dt)
        if result['p'] <= est_p:
            n_less += 1
    return n_less/n_iterations


def set_diffusion_data(netwf: str, outcome, counters, echo=True):
    dest = DiffusionEstimator.default(echo=echo)
    dest.load_network(netwf, counters=counters, outcome=outcome)


model_id = -1
def set_diffusion_data_newlib(netwf: str, outcome: dict, counters={}, echo=True, observe_time=-1.):
    global model_id
    if model_id >= 0:
        new_lib.DiffusionModel.default().delete_model(model_id)
    dest = new_lib.DiffusionModel.default(echo=echo)
    #dest.testParallel()
    model_id = dest.new_model(netwf, 1)
    dest.set_ncases_for_cascade(model_id, 0, len(outcome))
    for node_id, time in outcome.items():
        dest.add_case(model_id, 0, node_id, time)
    dest.set_observation_time_for_cascade(model_id, 0, observe_time)


def set_alpha_for_node(node_id, alpha):
    global model_id
    if model_id >= 0:
        new_lib.DiffusionModel.default().set_alpha_for_node(model_id, node_id, alpha)


def set_diffusion_data_ensemble(netwf: str, outcomes, counters, echo=True):
    dest = DiffusionEstimator.default(echo=echo)
    dest.load_network_inf_ensemble(netwf, counters=counters, outcomes=outcomes)


def set_diffusion_data_ensemble_newlib(netwf: str, outcomes, observe_times=None, echo=True):
    global model_id
    if model_id >= 0:
        new_lib.DiffusionModel.default().delete_model(model_id)
    dest = new_lib.DiffusionModel.default(echo=echo)
    # dest.testParallel()
    model_id = dest.new_model(netwf, len(outcomes))
    print("3 + ", str(model_id))
    for i in range(len(outcomes)):
        outcome = outcomes[i]
        dest.set_ncases_for_cascade(model_id, i, len(outcome))
        print("4"+str(i))
        for node_id, time in outcome.items():
            dest.add_case(model_id, i, node_id, time)
        if observe_times:
            dest.set_observation_time_for_cascade(model_id, i, observe_times[i])
        else:
            dest.set_observation_time_for_cascade(model_id, i, -1.)
        print("5" + str(i))


def llfunc_for_diffusion(thetas, confirms, decays, relics):
    dest = DiffusionEstimator.default(echo=True)
    ps = np.zeros((len(thetas), len(confirms), len(decays), len(relics)))
    for i in range(len(thetas)):
        for j in range(len(confirms)):
            for k in range(len(decays)):
                for l in range(len(relics)):
                    ps[i][j][k][l] = dest.loglikelyhood(thetas[i], confirms[j], decays[k], relics[l])
    return ps


def loglikelyhood(x):
    dest = DiffusionEstimator.default(echo=True)
    if x[0]<1e-12 or x[3]<1e-12 or x[2]<0 or x[1]<-1. or x[1]>1.:
        return 1e20
    ll = dest.loglikelyhood(x[0], x[1], x[2], x[3])
    print(str(-ll) + '   ' + str(x))
    return -ll


def loglikelyhood_noconfirm(x, observe_time=-1.):
    dest = DiffusionEstimator.default(echo=True)
    if x[0] < 1e-12 or x[2] < 1e-12 or x[1] < 0:
        return 1e20
    start_time = time.time()
    ll = dest.loglikelyhood(x[0], 0., x[1], x[2], observe_time)
    end_time = time.time()
    print(str(-ll) + '   ' + str(x) + '     ex. time: ' + str(end_time - start_time))
    return -ll


def loglikelyhood_noconfirm_newlib(x):
    global model_id
    if model_id < 0:
        return .0

    if x[0] < 1e-12 or x[2] < 1e-12 or x[1] < .0:
        return 1e20

    start_time = time.time()
    ll = new_lib.DiffusionModel.default().loglikelyhoodTRD(model_id, x[0], x[2], x[1])
    end_time = time.time()
    print(str(-ll) + '   ' + str(x) + '     ex. time: ' + str(end_time - start_time))
    return -ll


def loglikelyhood_noconfirm_newlib_multiple_cases(x):
    global model_id
    if model_id < 0:
        return .0

    n_cases = int((len(x)-1)/2)
    thetas = []
    rhos = []

    for i in range(n_cases):
        if x[i] < 1e-12: #thetas
            return 1e20
        if x[n_cases+i] < .0: #rhos
            return 1e20
        thetas.append(x[i])
        rhos.append(x[n_cases+i])
    if x[len(x)-1] < 1e-12:
        return 1e20

    delta = x[len(x)-1]
    start_time = time.time()
    ll = new_lib.DiffusionModel.default().loglikelyhoodTsRsD(model_id, thetas, rhos, delta)
    end_time = time.time()
    print('\nLl: ' + str(-ll))
    print('Thetas: ' + str(thetas))
    print('Rhos: ' + str(rhos))
    print('Delta: ' + str(delta))
    print('ex. time: ' + str(end_time - start_time))
    return -ll


def loglikelyhood_confirm_newlib_multiple_cases(x):
    global model_id
    if model_id < 0:
        return .0

    n_cases = int((len(x)-1)/3)
    thetas = []
    rhos = []
    kappas = []

    for i in range(n_cases):
        if x[i] < 1e-12: #thetas
            return 1e20
        if x[n_cases+i] < .0: #rhos
            return 1e20
        thetas.append(x[i])
        rhos.append(x[n_cases+i])
        kappas.append(x[2*n_cases+i])
    if x[len(x)-1] < 1e-12:
        return 1e20

    delta = x[len(x)-1]
    start_time = time.time()
    ll = new_lib.DiffusionModel.default().loglikelyhoodTsRsKsD(model_id, thetas, rhos, kappas, delta)
    end_time = time.time()
    print('\nLl: ' + str(-ll))
    print('Thetas: ' + str(thetas))
    print('Rhos: ' + str(rhos))
    print('Kappas: ' + str(kappas))
    print('Delta: ' + str(delta))
    print('ex. time: ' + str(end_time - start_time))
    return -ll


def loglikelyhood_ICM(x):
    global model_id
    if model_id < 0:
        return .0

    #if x[0] < 1e-12:
    #    return 1e20

    start_time = time.time()
    print(str(x[0]) + ' ' + str(x[1]))
    ll = new_lib.DiffusionModel.default().loglikelyhoodICM(model_id, x[0], x[1])
    end_time = time.time()
    print(str(-ll) + '   ' + str(x) + '     ex. time: ' + str(end_time - start_time))
    return -ll


def loglikelyhood_noconfirm_ensemble(x, observe_time=-1):
    dest = DiffusionEstimator.default(echo=True)
    if (x[0] < 1e-12 and x[2] < 1e-12) or x[1] < 0:
        return 1e20
    ll = dest.loglikelyhood_ensemble(x[0], 0., x[1], x[2], observe_time)
    #print(str(-ll) + '   ' + str(x))
    return -ll


def loglikelyhood_SI_relic(x):
    dest = DiffusionEstimator.default(echo=True)
    if x[0] < 1e-12 or x[1] < 1e-12:
        return 1e20
    ll = dest.loglikelyhood(x[0], 0., 0., x[1])
    #print(str(-ll) + '   ' + str(x))
    return -ll


def loglikelyhood_SI_relic_newlib(x, delta=.0):
    global model_id
    if model_id < 0:
        return .0

    if x[0] < 1e-12 or x[1] < 1e-12:
        return 1e20
    ll = new_lib.DiffusionModel.default().loglikelyhoodTRD(model_id, x[0], x[1], delta)
    print(str(-ll) + '   ' + str(x) + '  ' + str(delta))
    return -ll


def loglikelyhood_SI_decay_newlib(x, _delta=.0):
    global model_id
    if model_id < 0:
        return .0

    delta = .0
    if x[0] < 1e-12:
        return 1e20
    if len(x)==2:
        delta = x[1]
        if delta < 0:
            return 1e20
    else:
        delta = _delta

    ll = new_lib.DiffusionModel.default().loglikelyhoodTRD(model_id, x[0], .0, delta)
    print(str(-ll) + '   ' + str(x))
    return -ll


def loglikelyhood_ICM_newlib(x):
    global model_id
    if model_id < 0:
        return .0

    rho = .0
    if x[0] < 1e-12:
        return 1e20
    if len(x)==2:
        rho = x[1]
        if rho < 1e-12:
            return 1e20
    ll = new_lib.DiffusionModel.default().loglikelyhoodICM(model_id, x[0], rho)
    print(str(-ll) + '   ' + str(x))
    return -ll


def loglikelyhood_by_node_theta(x, node_id, theta, decay, relic, observe_time):
    dest = DiffusionEstimator.default(echo=True)
    ll = dest.loglikelyhood_by_node_theta(x, node_id, theta, .0, decay, relic, observe_time)
    #print(str(-ll) + '   ' + str(x))
    return -ll


def llmax_for_diffusion(theta0, confirm0, decay0, relic0):
    dest = DiffusionEstimator.default(echo=True)
    x0 = np.array([theta0, confirm0, decay0, relic0])
    res = minimize(loglikelyhood, x0, method='nelder-mead', options={'xtol': 1e-11, 'disp': True})
    return {'theta' : res.x[0], 'confirm' : res.x[1], 'decay' : res.x[2], 'relic' : res.x[3]}

def llmax_for_diffusion_noconfirm(theta0, decay0, relic0, observe_time=-1, disp=True, new_lib=False):
    x0 = np.array([theta0, decay0, relic0])
    if new_lib:
        res = minimize(loglikelyhood_noconfirm_newlib, x0, method='nelder-mead', options={'xtol': 1e-11, 'disp': disp})
    else:
        res = minimize(loglikelyhood_noconfirm, x0, method='nelder-mead', options={'xtol': 1e-11, 'disp': disp})
    return {'theta' : res.x[0], 'decay' : res.x[1], 'relic' : res.x[2]}


def llmax_for_diffusion_noconfirm_multiple_cases(thetas0, decay0, relics0, disp=True):
    dest = DiffusionEstimator.default(echo=disp)
    sx = thetas0 + relics0 + [decay0]
    x0 = np.array(sx)
    res = minimize(loglikelyhood_noconfirm_newlib_multiple_cases, x0, method='nelder-mead', options={'xtol': 1e-11, 'disp': disp})
    return {'theta' : res.x[0], 'decay' : res.x[1], 'relic' : res.x[2]}


def llmax_for_diffusion_confirm_multiple_cases(thetas0, decay0, relics0, confirms0, disp=True):
    dest = DiffusionEstimator.default(echo=disp)
    sx = thetas0 + relics0 + confirms0 + [decay0]
    x0 = np.array(sx)
    res = minimize(loglikelyhood_confirm_newlib_multiple_cases, x0, method='nelder-mead', options={'xtol': 1e-11, 'disp': disp})
    return {'theta' : res.x[0], 'decay' : res.x[1], 'relic' : res.x[2]}


def llmax_for_diffusion_noconfirm_ensemble(theta0, decay0, relic0, observe_time=-1, disp=True, new_lib=False):
    dest = DiffusionEstimator.default(echo=disp)
    x0 = np.array([theta0, decay0, relic0])
    if new_lib:
        res = minimize(loglikelyhood_noconfirm_ensemble, x0, args=(observe_time,), method='nelder-mead',
                       options={'xtol': 1e-11, 'disp': disp})
    else:
        res = minimize(loglikelyhood_noconfirm_ensemble, x0, args=(observe_time,), method='nelder-mead',
                       options={'xtol': 1e-11, 'disp': disp})
    return {'theta' : res.x[0], 'decay' : res.x[1], 'relic' : res.x[2]}


def llmax_for_diffusion_SI_relic(theta0, relic0, delta=.0, new_lib=False):
    dest = DiffusionEstimator.default(echo=True)
    x0 = np.array([theta0, relic0])
    if new_lib:
        res = minimize(loglikelyhood_SI_relic_newlib, x0, args=(delta,), method='nelder-mead',
                       options={'xtol': 1e-11, 'disp': True})
    else:
        res = minimize(loglikelyhood_SI_relic, x0, method='nelder-mead', options={'xtol': 1e-11, 'disp': True})
    return {'theta' : res.x[0], 'relic' : res.x[1]}


def llmax_for_diffusion_ICM(theta0, relic0 = .0):
    dest = DiffusionEstimator.default(echo=True)
    if relic0 == .0:
        x0 = np.array([theta0])
        res = minimize(loglikelyhood_ICM_newlib, x0, method='nelder-mead',
                        options={'xtol': 1e-11, 'disp': True})
        return {'theta' : res.x[0]}
    else:
        x0 = np.array([theta0, relic0])
        res = minimize(loglikelyhood_ICM_newlib, x0, method='nelder-mead',
                       options={'xtol': 1e-11, 'disp': True})
        return {'theta': res.x[0], 'relic' : res.x[1]}


def llmax_for_diffusion_SI_decay(theta0, delta0=.0, fixed_delta=False):
    dest = DiffusionEstimator.default(echo=True)
    if fixed_delta == True:
        x0 = np.array([theta0])
        res = minimize(loglikelyhood_SI_decay_newlib, x0, method='nelder-mead',
                        options={'xtol': 1e-11, 'disp': True}, args=(delta0,))
        return {'theta' : res.x[0]}
    else:
        x0 = np.array([theta0, delta0])
        res = minimize(loglikelyhood_SI_decay_newlib, x0, method='nelder-mead',
                       options={'xtol': 1e-11, 'disp': True})
        return {'theta': res.x[0], 'decay': res.x[1]}

def dlldthetas_noconfirm(theta, decay, relic, ids, observe_time=.0):
    dest = DiffusionEstimator.default(echo=True)
    dll = dest.thetas_derivatives(theta, .0, decay, relic, ids, observe_time)
    #print(str(dll) + '   ' + str(x))
    return dll

def llmax_for_diffusion_noconfirm_by_node_theta(node_id, theta, decay, relic, bounds, observe_time=0, disp=True):
    dest = DiffusionEstimator.default(echo=True)
    res = minimize_scalar(loglikelyhood_by_node_theta, bounds=bounds, method='bounded',
                          args=(node_id, theta, decay, relic, observe_time))
    return res.x