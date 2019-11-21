# Created by Gubanov Alexander (aka Derzhiarbuz) at 19.11.2019
# Contacts: derzhiarbuz@gmail.com

from da_diffusion_simulation import Simulator
from da_network import Network


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
