# Created by Gubanov Alexander (aka Derzhiarbuz) at 15.10.2019
# Contacts: derzhiarbuz@gmail.com

from da_network import Network
import random

class Simulator(object):

    __instance = None

    def __init__(self):
        if not Simulator.__instance:
            self.a = 0

    @classmethod
    def default_manager(cls):
        if not cls.__instance:
            cls.__instance = Simulator()
        return cls.__instance

    @classmethod
    def simulate_SIR_treshold(cls, underlying: Network, theta: float, infected: set = None, immunes: set = None,
                    immune_p=.0, initial_p=.0, tmax=1000.0, dt=.1, recover_rate=.0, recover_time=.0):
        susceptible = set(underlying.nodes_ids)
        outcome_infected = {}
        outcome_recovered = {}
        time = .0
        recover = False
        rec_const = False
        if recover_rate > 0 or recover_time > 0:
            recover = True
            if recover_time > 0:
                rec_const = True

        if infected is None:
            infected = set()
        if immunes is None:
            immunes = set()
        if len(infected) == 0 and initial_p > 0:
            for node_id in susceptible:
                if node_id not in immunes and random.uniform(0, 1.) < initial_p:
                    infected.add(node_id)
                    outcome_infected[node_id] = time
        if len(immunes) == 0 and immune_p > 0:
            for node_id in susceptible:
                if node_id not in infected and random.uniform(0, 1.) < immune_p:
                    immunes.add(node_id)
        susceptible -= immunes | infected
        while time < tmax:
            time += dt
            new_infected = set()
            new_recover = set()
            for node_id in susceptible:
                neighbors = underlying.get_in_neighbors_for_node(node_id)
                n_infected = len(neighbors & infected)
                if n_infected > 0:
                    if random.uniform(0, 1.) < (1. - (1. - theta)**n_infected):
                        new_infected.add(node_id)
                        outcome_infected[node_id] = time
            if recover:
                for node_id in infected:
                    inf_time = outcome_infected[node_id]
                    if rec_const:
                        if time - inf_time >= recover_time:
                            new_recover.add(node_id)
                            outcome_recovered[node_id] = (inf_time, time)
                            outcome_infected.pop(node_id)
                    else:
                        if random.uniform(0, 1.) < recover_rate:
                            new_recover.add(node_id)
                            outcome_recovered[node_id] = (inf_time, time)
                            outcome_infected.pop(node_id)
            infected |= new_infected
            susceptible -= new_infected
            if recover:
                infected -= new_recover
        if recover:
            for node_id, inf_time in outcome_infected:
                outcome_recovered[node_id] = (inf_time, -1)
            return outcome_recovered
        return outcome_infected

    @classmethod
    def simulate_treshold(cls, underlying: Network, theta: float, infected: set = None, immunes: set = None,
                    immune_p=.0, initial_p=.0, tmax=1000.0, dt=.1):
        susceptible = set(underlying.nodes_ids)

