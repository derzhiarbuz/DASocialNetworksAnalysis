# Created by Gubanov Alexander (aka Derzhiarbuz) at 19.11.2019
# Contacts: derzhiarbuz@gmail.com

from Statistics.da_diffusion_simulation import Simulator
from da_network import Network
from da_c_libs import DiffusionEstimator
import numpy as np
from scipy.optimize import minimize


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


def set_diffusion_data(netwf: str, outcome, counters):
    dest = DiffusionEstimator.default(echo=True)
    dest.load_netwotk(netwf, counters=counters, outcome=outcome)


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


def loglikelyhood_noconfirm(x):
    dest = DiffusionEstimator.default(echo=True)
    if x[0] < 1e-12 or x[2] < 1e-12 or x[1] < 0:
        return 1e20
    ll = dest.loglikelyhood(x[0], 0., x[1], x[2])
    print(str(-ll) + '   ' + str(x))
    return -ll


def loglikelyhood_SI_relic(x):
    dest = DiffusionEstimator.default(echo=True)
    if x[0] < 1e-12 or x[1] < 1e-12:
        return 1e20
    ll = dest.loglikelyhood(x[0], 0., 0., x[1])
    #print(str(-ll) + '   ' + str(x))
    return -ll


def llmax_for_diffusion(theta0, confirm0, decay0, relic0):
    dest = DiffusionEstimator.default(echo=True)
    x0 = np.array([theta0, confirm0, decay0, relic0])
    res = minimize(loglikelyhood, x0, method='nelder-mead', options={'xtol': 1e-11, 'disp': True})
    return {'theta' : res.x[0], 'confirm' : res.x[1], 'decay' : res.x[2], 'relic' : res.x[3]}

def llmax_for_diffusion_noconfirm(theta0, decay0, relic0):
    dest = DiffusionEstimator.default(echo=True)
    x0 = np.array([theta0, decay0, relic0])
    res = minimize(loglikelyhood_noconfirm, x0, method='nelder-mead', options={'xtol': 1e-11, 'disp': True})
    return {'theta' : res.x[0], 'decay' : res.x[1], 'relic' : res.x[2]}

def llmax_for_diffusion_SI_relic(theta0, relic0):
    dest = DiffusionEstimator.default(echo=True)
    x0 = np.array([theta0, relic0])
    res = minimize(loglikelyhood_SI_relic, x0, method='nelder-mead', options={'xtol': 1e-11, 'disp': True})
    return {'theta' : res.x[0], 'relic' : res.x[1]}