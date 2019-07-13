# Created by Gubanov Alexander (aka Derzhiarbuz) at 23.05.2019
# Contacts: derzhiarbuz@gmail.com

from da_network import Network
from da_network import NetworkOptimisation
from da_network_manager import NetworkManager
from da_ic_network_manager import ICNetworkManager
import da_vk_api as vk
import da_socnetworks_crawler as crlr
import math


class InformationConductivity(object):
    def __init__(self):
        self.cascades_network = Network()
        self.underlying = Network()
        pass

    def make_cascades_summary(self, cascade_networks, logweight=True):
        new_nodes = {}
        new_links = {}
        self.cascades_network = Network()
        for cascade in cascade_networks:
            for node_id in cascade.network.nodes_ids:
                if new_nodes.get(node_id) is None:
                    new_nodes[node_id] = 0
                new_nodes[node_id] += 1
            for from_id, to_id in cascade.network.links.keys():
                if new_links.get((from_id, to_id)) is None:
                    new_links[(from_id, to_id)] = 0
                new_links[(from_id, to_id)] += 1
        self.cascades_network.nodes_attributes.append({'id': 'w', 'title': 'LogWeight', 'type': 'float'})
        for node_id, quantity in new_nodes.items():
            self.cascades_network.add_node(node_id)
            if logweight:
                w = math.log(quantity) + 1
            else:
                w = quantity
            self.cascades_network.add_meta_for_node(node_id, {'w': w})
        for link, quantity in new_links.items():
            if logweight:
                w = math.log(quantity) + 1
            else:
                w = quantity
            self.cascades_network.add_link(link[0], link[1], mutual=False, weighted=True, weight=w)

    def make_underlying_summary(self, underlyings):
        if len(underlyings) == 1:
            self.underlying = underlyings[0].network
        else:
            self.underlying = Network(optimisation=NetworkOptimisation.id_only)
            for underlying in underlyings:
                for node_id, neighbors in underlying.network.nodes.items():
                    self.underlying.add_node(node_id)
                    self.underlying.nodes[node_id].update(neighbors)

    def nodes_summary(self):
        summary = {'in': [], 'out': [], 'in_w': [], 'out_w': [], 'degree': [], 'w': []}
        for node_id, node_data in self.cascades_network.nodes.items():
            degrees = self.cascades_network.node_degree(node_id)
            weights = self.cascades_network.node_weighted_degree(node_id)
            summary['in'].append(degrees['in'])
            summary['out'].append(degrees['out'])
            summary['in_w'].append(weights['in'])
            summary['out_w'].append(weights['out'])
            summary['degree'].append(self.underlying.node_degree(node_id)['inout'])
            summary['w'].append(self.cascades_network.meta_for_node(node_id, 'w'))
        return summary