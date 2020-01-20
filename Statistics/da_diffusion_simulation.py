# Created by Gubanov Alexander (aka Derzhiarbuz) at 15.10.2019
# Contacts: derzhiarbuz@gmail.com

from da_network import Network
import math
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
    def estimate_SI_continuous(cls, underlying: Network, theta: float, outcome: dict, initials: set, immunes: set = set(),
                    tmax=1000.0):
        time = .0
        my_outcome = outcome.copy()
        susceptible = set(underlying.nodes_ids)
        loglikelyhood = .0
        infected = set()
        infected |= initials
        susceptible -= immunes | infected

        prev_time = .0

        for newinf_id, inf_time in my_outcome.items():
            dt = inf_time - prev_time
            prev_time = inf_time
            neighbors = underlying.get_in_neighbors_for_node(newinf_id)
            n_infected = len(neighbors & infected)
            loglikelyhood += math.log(n_infected * theta)
            for sus_id in susceptible:
                sus_neighbors = underlying.get_in_neighbors_for_node(sus_id)
                sus_n_infected = len(sus_neighbors & infected)
                if sus_n_infected:
                    loglikelyhood += sus_n_infected*theta*dt
            infected.add(newinf_id)
            if newinf_id in susceptible:
                susceptible.remove(newinf_id)
        return loglikelyhood

    @classmethod
    def simulate_SI_decay(cls, underlying: Network, theta: float, decay: float, infected: set = None,
                          immunes: set = None, immune_p=.0, initial_p=.0, tmax=1000.0, dt=1):
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
                infected_nbrs = neighbors & my_infected
                if len(infected_nbrs) > 0:
                    p_not_infected = 1.
                    for neighbor_id in infected_nbrs:
                        time_gone = outcome_infected.get(neighbor_id)
                        if time_gone:
                            time_gone = time - time_gone
                        else: #initialy infected
                            time_gone = time
                        p_not_infected *= (1. - theta * dt * (1./(time_gone ** decay)))
                        #p_not_infected *= (1. - theta * dt * (1. / math.exp(time_gone * decay/10.)))
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
    def estimate_SI_decay(cls, underlying: Network, theta: float, decay: float, outcome: dict, initials: set,
                          immunes: set = set(), tmax=1000.0, dt=1):
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
                infected_nbrs = neighbors & infected
                if len(infected_nbrs) > 0 or (node_id in my_outcome.keys() and my_outcome[node_id] == time):
                    p_not_infected = 1.
                    for neighbor_id in infected_nbrs:
                        time_gone = my_outcome.get(neighbor_id)
                        if time_gone:
                            time_gone = time - time_gone
                        else:  # initialy infected
                            time_gone = time
                        p_not_infected *= (1. - theta * dt * (1. / (time_gone ** decay)))
                        #p_not_infected *= (1. - theta * dt * (1. / math.exp(time_gone * decay/10.)))
                    if node_id in my_outcome.keys() and my_outcome[node_id] <= time:
                        probability *= 1.0 - p_not_infected
                        new_infected.add(node_id)
                    else:
                        probability *= p_not_infected
            # for node_id in new_infected:
            #     my_outcome.pop(node_id)
            susceptible -= new_infected
            infected |= new_infected
            # print(str(probability) + ' ' + str(infected))
        return probability

    @classmethod
    def simulate_SI_recover(cls, underlying: Network, theta: float, recover_time: float, infected: set = None,
                          rec_factor=0.1, immunes: set = None, immune_p=.0, initial_p=.0, tmax=1000.0, dt=1):
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
                infected_nbrs = neighbors & my_infected
                if len(infected_nbrs) > 0:
                    p_not_infected = 1.
                    for neighbor_id in infected_nbrs:
                        time_gone = outcome_infected.get(neighbor_id)
                        if time_gone:
                            time_gone = time - time_gone
                        else:  # initialy infected
                            time_gone = time
                        theta_r = theta
                        if time_gone > recover_time:
                            theta_r = theta * rec_factor
                        p_not_infected *= 1. - theta_r * dt
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
    def estimate_SI_recover(cls, underlying: Network, theta: float, recover_time: float, outcome: dict, initials: set,
                            rec_factor=0.1, immunes: set = set(), tmax=1000.0, dt=1):
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
                infected_nbrs = neighbors & infected
                if len(infected_nbrs) > 0 or (node_id in my_outcome.keys() and my_outcome[node_id] == time):
                    p_not_infected = 1.
                    for neighbor_id in infected_nbrs:
                        time_gone = my_outcome.get(neighbor_id)
                        if time_gone:
                            time_gone = time - time_gone
                        else:  # initialy infected
                            time_gone = time
                        theta_r = theta
                        if time_gone > recover_time:
                            theta_r = theta * rec_factor
                        p_not_infected *= 1. - theta_r * dt
                    if node_id in my_outcome.keys() and my_outcome[node_id] <= time:
                        probability *= 1.0 - p_not_infected
                        new_infected.add(node_id)
                    else:
                        probability *= p_not_infected
            #for node_id in new_infected:
            #    my_outcome.pop(node_id)
            susceptible -= new_infected
            infected |= new_infected
            # print(str(probability) + ' ' + str(infected))
        return probability

    @classmethod
    def simulate_SI_halflife(cls, underlying: Network, theta: float, halflife: float, infected: set = None,
                            immunes: set = None, immune_p=.0, initial_p=.0, tmax=1000.0, dt=1):
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
                infected_nbrs = neighbors & my_infected
                if len(infected_nbrs) > 0:
                    p_not_infected = 1.
                    for neighbor_id in infected_nbrs:
                        time_gone = outcome_infected.get(neighbor_id)
                        if time_gone:
                            time_gone = time - time_gone
                        else:  # initialy infected
                            time_gone = time
                        theta_r = theta
                        t = time_gone - halflife
                        while t > 0:
                            theta_r /= 2
                            t -= halflife
                        p_not_infected *= 1. - theta_r * dt
                    if random.uniform(0, 1.) < (1. - p_not_infected):
                        new_infected.add(node_id)
                        outcome_infected[node_id] = time
                        probability *= 1. - p_not_infected
                    else:
                        probability *= p_not_infected
            my_infected |= new_infected
            susceptible -= new_infected
            #print(str(probability) + ' ' + str(my_infected) + ' ' + str(time))
        return {'outcome': outcome_infected, 'p': probability}

    @classmethod
    def estimate_SI_halflife(cls, underlying: Network, theta: float, halflife: float, outcome: dict, initials: set,
                            immunes: set = set(), tmax=1000.0, dt=1):
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
                infected_nbrs = neighbors & infected
                if len(infected_nbrs) > 0 or (node_id in my_outcome.keys() and my_outcome[node_id] == time):
                    p_not_infected = 1.
                    for neighbor_id in infected_nbrs:
                        time_gone = my_outcome.get(neighbor_id)
                        if time_gone:
                            time_gone = time - time_gone
                        else:  # initialy infected
                            time_gone = time
                        theta_r = theta
                        t = time_gone - halflife
                        while t > 0:
                            theta_r /= 2
                            t -= halflife
                        p_not_infected *= 1. - theta_r * dt
                    if node_id in my_outcome.keys() and my_outcome[node_id] <= time:
                        probability *= 1.0 - p_not_infected
                        new_infected.add(node_id)
                    else:
                        probability *= p_not_infected
            #for node_id in new_infected:
            #    my_outcome.pop(node_id)
            susceptible -= new_infected
            infected |= new_infected
            #print(str(probability) + ' ' + str(infected) + ' ' + str(time))
        return probability

    @classmethod
    def simulate_SI_confirm(cls, underlying: Network, theta: float, confirm: float, infected: set = None,
                          immunes: set = None, immune_p=.0, initial_p=.0, tmax=1000.0, dt=1):
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
                    p_not_infected = (1. - theta * dt) ** (n_infected ** (confirm+1))
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
    def estimate_SI_confirm(cls, underlying: Network, theta: float, confirm: float, outcome: dict, initials: set,
                          immunes: set = set(), tmax=1000.0, dt=1):
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
                    p_not_infected = (1. - theta * dt) ** (n_infected ** (confirm+1))
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
    def simulate_SI_relic(cls, underlying: Network, theta: float, relic: float, infected: set = None,
                          immunes: set = None, immune_p=.0, initial_p=.0, tmax=1000.0, dt=1):
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
                p_not_infected = 1.0
                if n_infected > 0:
                    p_not_infected = (1. - relic * dt) * (1. - theta * dt) ** n_infected
                else:
                    p_not_infected = (1. - relic * dt)
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
    def estimate_SI_relic(cls, underlying: Network, theta: float, relic: float, outcome: dict, initials: set,
                          immunes: set = set(), tmax=1000.0, dt=1, echo = False):
        time = .0
        my_outcome = outcome.copy()
        susceptible = set(underlying.nodes_ids)
        probability = 1.
        infected = set()
        infected |= initials
        susceptible -= immunes | infected
        i = 0
        while time < tmax:
            time += dt
            new_infected = set()
            for node_id in susceptible:
                neighbors = underlying.get_in_neighbors_for_node(node_id)
                n_infected = len(neighbors & infected)
                p_not_infected = 1.0
                if n_infected > 0:
                    p_not_infected = (1. - relic * dt) * (1. - theta * dt) ** n_infected
                else:
                    p_not_infected = (1. - relic * dt)
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
            if echo:
                print(str(time) + ' ' + str(probability))
        return probability

    @classmethod
    def estimate_SI_relic_continuous(cls, underlying: Network, theta: float, relic: float, outcome: dict,
                                     initials: set, immunes: set = set(), tmax=1000.0, echo = False):
        time = .0
        my_outcome = []
        for key, value in outcome.items():
            my_outcome.append((key, value))
        my_outcome.sort(key=lambda x: x[1])

        susceptible = set(underlying.nodes_ids)
        loglikelyhood = .0
        infected = set()
        infected |= initials
        susceptible -= immunes | infected
        leafs_dict = {}
        n_no_inf_neighbors = 0

        nn = 0
        for node_id in underlying.nodes_ids: #make separate storage for leafs never infected (>99% of al nodes)
            neighbors = underlying.get_in_neighbors_for_node(node_id)
            if len(neighbors) == 1 and node_id not in outcome.keys():
                for n in neighbors:
                    if n in outcome.keys():
                        if n not in leafs_dict.keys():
                            leafs_dict[n] = 0
                        leafs_dict[n] += 1
                    else:
                        n_no_inf_neighbors += 1
                    nn += 1
                    susceptible.remove(node_id)
                    break
        prev_time = .0

        for newinf_id, inf_time in my_outcome:
            if inf_time == 0.0:
                continue
            dt = inf_time - prev_time
            prev_time = inf_time
            neighbors = underlying.get_in_neighbors_for_node(newinf_id)
            n_infected = len(neighbors & infected)
            loglikelyhood += math.log(n_infected * theta + relic)
            for sus_id in susceptible:
                sus_neighbors = underlying.get_in_neighbors_for_node(sus_id)
                sus_n_infected = len(sus_neighbors & infected)
                if sus_n_infected > 0:
                    loglikelyhood -= (sus_n_infected * theta + relic) * dt
                else:
                    loglikelyhood -= relic * dt
            for nonleaf_id, n_leafs in leafs_dict.items():
                if nonleaf_id in infected:
                    loglikelyhood -= n_leafs * (theta + relic) * dt
                else:
                    loglikelyhood -= n_leafs * relic * dt
            loglikelyhood -= n_no_inf_neighbors * relic * dt

            infected.add(newinf_id)
            if newinf_id in susceptible:
                susceptible.remove(newinf_id)
            if echo:
                print(str(time) + ' ' + str(loglikelyhood))
        return loglikelyhood

    @classmethod
    def estimate_SI_relic_halflife_continuous(cls, underlying: Network, theta: float, relic: float, halflife: float,
                                              outcome: dict, initials: set, immunes: set = set(),
                                              tmax=1000.0, echo=False):
        time = .0
        my_outcome = []
        for key, value in outcome.items():
            my_outcome.append((key, value))
        my_outcome.sort(key=lambda x: x[1])

        susceptible = set(underlying.nodes_ids)
        loglikelyhood = .0
        infected = set()
        infected |= initials
        susceptible -= immunes | infected
        leafs_dict = {}
        n_no_inf_neighbors = 0

        nn = 0
        for node_id in underlying.nodes_ids:  # make separate storage for leafs never infected (>99% of al nodes)
            neighbors = underlying.get_in_neighbors_for_node(node_id)
            if len(neighbors) == 1 and node_id not in outcome.keys():
                for n in neighbors:
                    if n in outcome.keys():
                        if n not in leafs_dict.keys():
                            leafs_dict[n] = 0
                        leafs_dict[n] += 1
                    else:
                        n_no_inf_neighbors += 1
                    nn += 1
                    susceptible.remove(node_id)
                    break
        prev_time = .0

        for newinf_id, inf_time in my_outcome:
            if inf_time == 0.0:
                continue
            dt = inf_time - prev_time
            prev_time = inf_time
            neighbors = underlying.get_in_neighbors_for_node(newinf_id)
            n_infected = len(neighbors & infected)
            loglikelyhood += math.log(n_infected * theta + relic)
            for sus_id in susceptible:
                sus_neighbors = underlying.get_in_neighbors_for_node(sus_id)
                sus_n_infected = len(sus_neighbors & infected)
                if sus_n_infected > 0:
                    loglikelyhood -= (sus_n_infected * theta + relic) * dt
                else:
                    loglikelyhood -= relic * dt
            for nonleaf_id, n_leafs in leafs_dict.items():
                if nonleaf_id in infected:
                    loglikelyhood -= n_leafs * (theta + relic) * dt
                else:
                    loglikelyhood -= n_leafs * relic * dt
            loglikelyhood -= n_no_inf_neighbors * relic * dt

            infected.add(newinf_id)
            if newinf_id in susceptible:
                susceptible.remove(newinf_id)
            if echo:
                print(str(time) + ' ' + str(loglikelyhood))
        return loglikelyhood

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

