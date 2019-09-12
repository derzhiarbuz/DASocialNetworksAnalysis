# Created by Gubanov Alexander (aka Derzhiarbuz) at 08.05.2019
# Contacts: derzhiarbuz@gmail.com

from da_ic_network_manager import ICNetworkManager
from da_connections_network_manager import ConnectionsNetworkManager
import da_socnetworks_crawler as crlr
import da_vk_api as vk
from da_sna_data_manager import DataManager


class CascadesManager(object):
    def __init__(self, name='', base_dir=''):
        self.cascades = set()
        self.summary_cascade = None
        self.underlying_net = ConnectionsNetworkManager(name=(name+'u'), base_dir=base_dir)
        self._name = name
        self.base_dir = base_dir
        self.crawl_plan = []
        self._crawl_count = 0

    def crawl_next(self):
        if len(self.crawl_plan):
            src = self.crawl_plan.pop(0)
            if 'post_ids' in src.keys():
                result = self.get_posts_for_group(src['source_id'], src['n'], post_ids=src['post_ids'])
            else:
                result = self.get_posts_for_group(src['source_id'], src['n'])
            if result == 'done':
                return 1
            else:
                self.crawl_plan.insert(0, src)
                return -1
        for cascade in self.cascades:
            res = cascade.crawl_next()
            if res != 0:
                return res
        if self.underlying_net:
            return self.underlying_net.crawl_next()
        return 0

    def get_posts_for_group(self, group_id, n, post_ids=None):
        if post_ids is None:
            posts = crlr.get_posts(-abs(group_id), n)
        else:
            posts = crlr.get_posts_by_id(-abs(group_id), post_ids)
        if vk.is_error(posts):
            print('Error: ' + str(posts['error']['error_code']) + ' ' + posts['error']['error_msg'])
            return 'error'
        for post in posts:
            cascade = ICNetworkManager()
            cascade.schedule_crawl_post_from_source(int(post['from_id']), int(post['id']))
            self.cascades.add(cascade)
        return 'done'

    def schedule_crawl_posts_for_group(self, source_id, n=0, post_ids=None):
        if post_ids is None:
            self.crawl_plan.append({'source_id': source_id, 'n': n})
        else:
            self.crawl_plan.append({'source_id': source_id, 'n': n, 'post_ids': post_ids})

    def schedule_crawl_underlying_network(self):
        nodes_to_crowl = set()
        for cascade in self.cascades:
            nodes_to_crowl.update(cascade.posters.keys())
            nodes_to_crowl.update(cascade.hiddens)
#            nodes_to_crowl.update(cascade.hiddens)
            nodes_to_crowl.update(cascade.likers)
        # print(len(nodes_to_crowl))
        for node_id in nodes_to_crowl:
            self.underlying_net.schedule_crawl_ego_network(node_id, deep=0)
        self.underlying_net.schedule_load_nodes_meta()

    def continue_crawling(self):
        while self.crawl_next() > 0:
            self._crawl_count += 1
            if self._crawl_count >= 100:
                self.save_to_file()
                self._crawl_count = 0
                # print('Saved!')
                i = 0
                for cascade in self.cascades:
                    if len(cascade.crawl_plan):
                        i += 1
                print('Saved! Cascades: ' + str(i) + ' left from total ' + str(len(self.cascades))
                      + ' Nodes: ' + str(len(self.underlying_net.network.nodes))
                      + ' Nodes to check: ' + str(len(self.underlying_net.crawl_plan)))

    def load_from_file(self):
        self.cascades = DataManager.load(self.base_dir + self._name + '_cascades.pkl')
        try:
            self.underlying_net.load_from_file()
        except IOError:
            self.underlying_net = ConnectionsNetworkManager(name=(self._name+'u'), base_dir=self.base_dir)

    def save_to_file(self):
        DataManager.save(self.cascades, self.base_dir + self._name + '_cascades.pkl')
        self.underlying_net.save_to_file()

    def update_cascades(self, uselikes=True, usehiddens=True):
        existing_links = self.underlying_net.network.nodes
        for cascade in self.cascades:
            cascade.remake_network(existing_links, uselikes, usehiddens)