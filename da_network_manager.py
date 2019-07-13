# Created by Gubanov Alexander (aka Derzhiarbuz) at 03.05.2019
# Contacts: derzhiarbuz@gmail.com

from enum import Enum
from da_network import Network, NetworkOptimisation
from da_sna_data_manager import DataManager


class NetworkSource(Enum):
    vkontakte = 1


class NetworkManager(object):
    def __init__(self, net=Network(), name='', base_dir=''):
        self.network = net
        self.name = name
        self.base_dir = base_dir
        self.source = NetworkSource.vkontakte
        self.crawl_plan = []

    def load_from_file(self):
        # print('Obtaining NetworkManager from file')
        other_data = DataManager.load(self.base_dir + self.name + '_data.pkl')
        self.set_data_dict(other_data)
        if self.network.optimisation == NetworkOptimisation.id_only:
            network_dos = DataManager.load_dict_of_set_of_ints_binary(self.base_dir + self.name + '_network.dos')
            self.network.nodes = network_dos
            self.network.timestamp = other_data['dos_timestamp']
        else:
            self.network = DataManager.load(self.base_dir + self.name + '_network.pkl')

    def save_to_file(self):
        other_data = self.get_data_dict()
        if self.network.optimisation == NetworkOptimisation.id_only:
            other_data['dos_timestamp'] = self.network.timestamp
            DataManager.save_dict_of_set_of_ints_binary(self.network.nodes, self.base_dir + self.name + '_network.dos')
        else:
            DataManager.save(self.network, self.base_dir+self.name+'_network.pkl')
        DataManager.save(other_data, self.base_dir+self.name + '_data.pkl')

    def get_data_dict(self):
        data_dict = {'source': self.source,
                     'crawl_plan': self.crawl_plan}
        return data_dict

    def set_data_dict(self, data_dict):
        self.source = data_dict['source']
        self.crawl_plan = data_dict['crawl_plan']

    def continue_crawling(self):
        while self.crawl_next() > 0:
            pass
            # print('The method that continues crawling')

    def crawl_next(self):
        return 0