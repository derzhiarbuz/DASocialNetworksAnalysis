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
    def simulate_SI(cls, underlying: Network, theta: float, infected: set = None, immunes: set = None,
                    immune_p=.0, initial_p=.0, tmax=1000.0, dt=1):
        susceptible = set(underlying.nodes_ids)
        outcome_infected = {}
        time = .0
        probability = 1.
        my_infected = infected.copy()

        if my_infected is None:
            my_infected = set()
        if immunes is None:
            immunes = set()
        if len(my_infected) == 0 and initial_p > 0:
            for node_id in susceptible:
                if node_id not in immunes and random.uniform(0, 1.) < initial_p:
                    my_infected.add(node_id)
                    outcome_infected[node_id] = time
        if len(immunes) == 0 and immune_p > 0:
            for node_id in susceptible:
                if node_id not in my_infected and random.uniform(0, 1.) < immune_p:
                    immunes.add(node_id)
        susceptible -= immunes | my_infected
        while time < tmax:
            time += dt
            new_infected = set()
            for node_id in susceptible:
                neighbors = underlying.get_in_neighbors_for_node(node_id)
                n_infected = len(neighbors & my_infected)
                if n_infected > 0:
                    p_not_infected = (1. - theta*dt)**n_infected
                    if random.uniform(0, 1.) < (1. - p_not_infected):
                        new_infected.add(node_id)
                        outcome_infected[node_id] = time
                        probability *= 1. - p_not_infected
                    else:
                        probability *= p_not_infected
            my_infected |= new_infected
            susceptible -= new_infected
            # print(str(probability) + ' ' + str(infected))
        return {'outcome': outcome_infected, 'p': probability}

    @classmethod
    def estimate_SI(cls, underlying: Network, theta: float, outcome: dict, initials: set, immunes: set = set(),
                    tmax=1000.0, dt=1):
        time = .0
        my_outcome = outcome.copy()
        susceptible = set(underlying.nodes_ids)
        probability = 1.
        infected = set()
        infected |= initials
        susceptible -= immunes | infected
        while time < tmax:
            time += dt
            new_infected = set()
            for node_id in susceptible:
                neighbors = underlying.get_in_neighbors_for_node(node_id)
                n_infected = len(neighbors & infected)
                if n_infected > 0 or (node_id in my_outcome.keys() and my_outcome[node_id] < time):
                    p_not_infected = (1. - theta * dt) ** n_infected
                    if node_id in my_outcome.keys() and my_outcome[node_id] <= time:
                        probability *= 1.0 - p_not_infected
                        new_infected.add(node_id)
                    else:
                        probability *= p_not_infected
            for node_id in new_infected:
                my_outcome.pop(node_id)
            susceptible -= new_infected
            infected |= new_infected
            # print(str(probability) + ' ' + str(infected))
        return probability

    @classmethod
    def simulate_SIR(cls, underlying: Network, theta: float, infected: set = None, immunes: set = None,
                              immune_p=.0, initial_p=.0, tmax=1000.0, dt=.1, recover_rate=.0, recover_time=.0):
        susceptible = set(underlying.nodes_ids)
        outcome_infected = {}
        outcome_recovered = {}
        time = .0
        rec_const = False
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
                    if random.uniform(0, 1.) < (1. - (1. - theta*dt) ** n_infected):
                        new_infected.add(node_id)
                        outcome_infected[node_id] = time
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
            infected -= new_recover
        for node_id, inf_time in outcome_infected:
            outcome_recovered[node_id] = (inf_time, -1)
        return outcome_recovered


    @classmethod
    def simulate_treshold(cls, underlying: Network, theta: float, infected: set = None, immunes: set = None,
                    immune_p=.0, initial_p=.0, tmax=1000.0, dt=.1):
        susceptible = set(underlying.nodes_ids)

