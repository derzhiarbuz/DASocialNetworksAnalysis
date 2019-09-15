# Created by Gubanov Alexander (aka Derzhiarbuz) at 29.04.2019
# Contacts: derzhiarbuz@gmail.com

from da_network import Network, NetworkOptimisation
from da_network_manager import NetworkSource, NetworkManager
import da_vk_api as vk
import da_socnetworks_crawler as crlr
from da_sna_data_manager import DataManager


class ConnectionsNetworkManager(NetworkManager):
    def __init__(self, net=Network(optimisation=NetworkOptimisation.id_only), name='', base_dir=''):
        super().__init__(net, name, base_dir)
        self.nodes_meta = {}
        self.crawled_nodes = set()

    def get_data_dict(self):
        data_dict = super().get_data_dict()
        data_dict['nodes_meta'] = self.nodes_meta
        data_dict['scanned_nodes'] = self.crawled_nodes
        return data_dict

    def set_data_dict(self, data_dict):
        super().set_data_dict(data_dict)
        self.nodes_meta = data_dict['nodes_meta']
        self.crawled_nodes = data_dict['scanned_nodes']

    def load_from_file(self, crowled_only=False):
        if crowled_only:
            # this dirty hack is just to be able to load large network (>3700000nds) without unscanned nodes
            other_data = DataManager.load(self.base_dir + self.name + '_data.pkl')
            self.set_data_dict(other_data)
            if self.network.optimisation == NetworkOptimisation.id_only:
                network_dos = DataManager.load_dict_of_set_of_ints_binary(self.base_dir + self.name + '_network.dos',
                                                                          valid_ids=self.crawled_nodes)
                self.network.nodes = network_dos
                self.network.timestamp = other_data['dos_timestamp']
            return
        super().load_from_file()

    def schedule_crawl_ego_network(self, source_id, deep=1, force=False):
        crawler = {'type': 'ego',
                   'deep': deep,
                   'left': [{source_id}]}
        for i in range(0, deep):
            crawler['left'].append(set())
        self.crawl_plan.append(crawler)
        if force is True:
            if source_id in self.crawled_nodes:
                self.crawled_nodes.remove(source_id)

    def schedule_load_nodes_meta(self):
        nodes_to_load = self.crawled_nodes - self.nodes_meta.keys()
        if len(nodes_to_load):
            users_left = set()
            groups_left = set()
            for node_id in nodes_to_load:
                if node_id < 0:
                    groups_left.add(node_id)
                else:
                    users_left.add(node_id)
            crawler = {'type': 'meta',
                       'users_left': users_left,
                       'groups_left': groups_left}
            self.crawl_plan.append(crawler)

    def crawl_next(self):
        while len(self.crawl_plan) != 0:
            result = 'done'
            crawler = self.crawl_plan[0]
            if crawler['type'] == 'ego':
                if len(crawler['left']) > 1:
                    print('left' + str(len(crawler['left'][1])))
                result = self.crawl_ego(crawler)
            elif crawler['type'] == 'meta':
                result = self.crawl_meta(crawler)

            if result == 'empty':
                self.crawl_plan.pop(0)
            if result == 'done':
                return 1
            elif result == 'error':
                return -1
        print('Crawl plan is length of zero')
        return 0

    def crawl_ego(self, crawler):
        empty = True
        deep = crawler['deep']
        left = crawler['left']
        i = 0
        for layer in left:
            #i = 0
            while len(layer) and empty:
                node_id = layer.pop()
                print(node_id)
                if node_id not in self.crawled_nodes:
                    if self.source == NetworkSource.vkontakte:
                        neighbors = set()
                        if node_id < 0:
                            # print('Crawling started from group ' + str(source_id))
                            neighbors = crlr.get_members_for_vk_group(abs(node_id), meta=False)
                        else:
                            # print('Crawling started from user ' + str(source_id))
                            neighbors = crlr.get_friends_for_vk_user(node_id, meta=False)
                        if vk.is_error(neighbors):  # douwnloading error occured
                            ec = neighbors['error']['error_code']
                            print('Error: ' + str(ec) + ' ' +
                                  neighbors['error']['error_msg'])
                            if ec <= 10:    # connection or access error (accident stop)
                                print('Error: ' + str(ec) + ' ' +
                                      neighbors['error']['error_msg'])
                                layer.add(node_id)
                                return 'error'
                            else:   # node closed or dead, so mark as crawled
                                self.crawled_nodes.add(node_id)
                            empty = False
                            continue
                        empty = False
                        # updating crawl plan
                        unscanned = self.add_vk_neighbors(node_id, neighbors)
                        if i < deep:
                            for lyr in left:
                                unscanned -= lyr
                            if len(unscanned):
                                left[i + 1] |= unscanned
            i += 1
        # print(self.crawl_plan)
        if empty:
            return 'empty'
        return 'done'

    def crawl_meta(self, crawler):
        users_left = crawler['users_left']
        groups_left = crawler['groups_left']
        ids_to_crawl = set()
        if self.source == NetworkSource.vkontakte:
            i = 0
            if len(users_left):
                while i < 1000 and len(users_left):
                    ids_to_crawl.add(users_left.pop())
                    i += 1
                users = crlr.get_vk_users(ids_to_crawl)
                if vk.is_error(users):  # douwnloading error occured
                    ec = users['error']['error_code']
                    print('Error: ' + str(ec) + ' ' +
                          users['error']['error_msg'])
                    if ec <= 10:    # connection or access error (accident stop)
                        print('Error: ' + str(ec) + ' ' +
                              users['error']['error_msg'])
                        users_left.update(ids_to_crawl)
                        return 'error'
                else:
                    self.add_vk_users_meta(users)
            elif len(groups_left):
                while i < 500 and len(groups_left):
                    ids_to_crawl.add(groups_left.pop())
                    i += 1
                groups = crlr.get_vk_groups(ids_to_crawl)
                if vk.is_error(groups):  # douwnloading error occured
                    ec = groups['error']['error_code']
                    print('Error: ' + str(ec) + ' ' +
                          groups['error']['error_msg'])
                    if ec <= 10:    # connection or access error (accident stop)
                        print('Error: ' + str(ec) + ' ' +
                              groups['error']['error_msg'])
                        groups_left.update(ids_to_crawl)
                        return 'error'
                else:
                    self.add_vk_groups_meta(groups)
            else:
                return 'empty'

    def add_vk_neighbors(self, node_id, neighbors, meta=False):
        self.crawled_nodes.add(node_id)
        new_neighbors = set()
        for nbr in neighbors:
            if meta:
                nbr_id = int(nbr['id'])
                self.nodes_meta[nbr_id] = nbr
            else:
                nbr_id = int(nbr)
            self.network.add_link(node_id, nbr_id, mutual=True)
            if nbr_id not in self.crawled_nodes:
                new_neighbors.add(nbr_id)
        return new_neighbors  # return set of nodes that not crawled yet

    def add_vk_users_meta(self, users):
        for user in users:
            uid = int(user['id'])
            self.nodes_meta[uid] = user

    def add_vk_groups_meta(self, groups):
        for group in groups:
            gid = -int(group['id'])
            self.nodes_meta[gid] = group