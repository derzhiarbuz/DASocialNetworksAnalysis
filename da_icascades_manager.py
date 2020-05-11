# Created by Gubanov Alexander (aka Derzhiarbuz) at 08.05.2019
# Contacts: derzhiarbuz@gmail.com

from da_ic_network_manager import ICNetworkManager
from da_connections_network_manager import ConnectionsNetworkManager
import da_socnetworks_crawler as crlr
import da_vk_api as vk
from da_sna_data_manager import DataManager
import datetime
from time import sleep


class CascadesManager(object):
    def __init__(self, name='', base_dir=''):
        self.cascades = set()
        self.summary_cascade = None
        self.underlying_net = ConnectionsNetworkManager(name=(name+'u'), base_dir=base_dir)
        self._name = name
        self.base_dir = base_dir
        self.crawl_plan = []
        self._crawl_count = 0

    def get_cascade_by_id(self, cas_id):
        for cascade in self.cascades:
            if cascade.post_meta['postinfo']['id'] == cas_id:
                return cascade

    def get_underlying_path(self):
        return self.base_dir + self._name+'u_network.dos'

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
            sleep(0.1)
            res = cascade.crawl_next()
            if res != 0:
                return res
        if self.underlying_net:
            sleep(0.1)
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

    def load_from_file(self, crowled_only=False):
        self.cascades = DataManager.load(self.base_dir + self._name + '_cascades.pkl')
        try:
            self.underlying_net.load_from_file(crowled_only=crowled_only)
        except IOError:
            self.underlying_net = ConnectionsNetworkManager(name=(self._name+'u'), base_dir=self.base_dir)

    def save_to_file(self):
        DataManager.save(self.cascades, self.base_dir + self._name + '_cascades.pkl')
        self.underlying_net.save_to_file()

    def update_cascades(self, uselikes=True, usehiddens=True, dynamic=True, logdyn=False, start_from_zero=False):
        existing_links = self.underlying_net.network.nodes
        for cascade in self.cascades:
            cascade.remake_network(existing_links, uselikes, usehiddens, dynamic, logdyn, start_from_zero)

    def write_gexf(self, fname, trim_unchecked_nodes = True): #this function makes gexf for cascade
        file = open(fname, "w", encoding='utf-8')
        file.write('''<?xml version="1.0" encoding="UTF-8"?>
                    <gexf xmlns="http://www.gexf.net/1.2draft" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.gexf.net/1.2draft http://www.gexf.net/1.2draft/gexf.xsd" version="1.2">
                    <meta lastmodifieddate="''' + datetime.date.today().strftime("%Y-%m-%d") + '''">
                    <creator>''' + "Derzhiarbuz" + '''</creator>
                    <description>''' + self._name + " group cascade" + '''</description>
                    </meta>''')
        file.write('\n<graph>')

        file.write('\n<attributes class="node">')
        file.write('<attribute id="1" title="actual_degree" type="int"></attribute>')
        if len(self.cascades) == 1:
            file.write('<attribute id="2" title="liker" type="boolean"></attribute>')
            file.write('<attribute id="3" title="hidden" type="boolean"></attribute>')
        file.write('</attributes>')

        file.write('\n<attributes class="edge">')
        file.write('<attribute id="33" title="type" type="int"></attribute>')
        file.write('</attributes>')

        print(len(self.underlying_net.network.nodes))
        nodes = self.underlying_net.network.nodes
        keys = nodes.keys()
        single_cascade = None
        for cascade in self.cascades:
            cascade.remake_network(possible_links=nodes, uselikes=False, usehiddens=False)
            if len(self.cascades) == 1:
                single_cascade = cascade

        if len(nodes):
            file.write('''\n\t\t<nodes>''')
            for node_id, node_neighbors in nodes.items():
                file.write('\n<node')
                file.write(' id="' + str(node_id) + '"')
                file.write('>')
                file.write('''\n<attvalues>''')
                file.write('''<attvalue for="1" value="''' + str(len(node_neighbors)) + '''"/>''')
                if single_cascade:
                    if node_id in single_cascade.likers or node_id in single_cascade.hiddens:
                        file.write('''<attvalue for="2" value="true"/>''')
                    else:
                        file.write('''<attvalue for="2" value="false"/>''')
                    if node_id in single_cascade.hiddens:
                        file.write('''<attvalue for="3" value="true"/>''')
                    else:
                        file.write('''<attvalue for="3" value="false"/>''')
                file.write('''</attvalues>''')
                file.write('''\n</node>''')
            file.write('''\n</nodes>''')

        edge_id = 0
        file.write('''\n\t\t<edges>''')
        if len(nodes):
            for node_id, node_neighbors in nodes.items():
                for neighbor_id in node_neighbors:
                    if node_id < neighbor_id and neighbor_id in keys:
                        file.write('\n<edge')
                        file.write(' id="' + str(edge_id) + '"')
                        edge_id += 1
                        file.write(' source="' + str(node_id) + '"')
                        file.write(' target="' + str(neighbor_id) + '"')
                        file.write(' type="undirected"')
                        file.write('>')
                        file.write('''\n<attvalues>''')
                        file.write('''<attvalue for="33" value="0"/>''')
                        file.write('''</attvalues>''')
                        file.write('''\n</edge>''')
        cascade_n = 1
        for cascade in self.cascades:
            print(len(cascade.network.nodes))
            for link in cascade.network.links.keys():
                file.write('\n<edge')
                file.write(' id="' + str(edge_id) + '"')
                edge_id += 1
                file.write(' source="' + str(link[0]) + '"')
                file.write(' target="' + str(link[1]) + '"')
                file.write(' type="directed"')
                file.write('>')
                file.write('''\n<attvalues>''')
                file.write('''<attvalue for="33" value="''' + str(cascade_n) + '''"/>''')
                file.write('''</attvalues>''')
                file.write('''\n</edge>''')
            cascade_n += 1
        file.write('''\n</edges>''')

        file.write("\n</graph>")
        file.write("\n</gexf>")
        file.close()

    def write_stat_csv(self, fname):
        file = open(fname, "w", encoding='utf-8')

        print(len(self.underlying_net.network.nodes))
        nodes = self.underlying_net.network.nodes
        keys = nodes.keys()
        for cascade in self.cascades:
            cascade.remake_network(possible_links=nodes, uselikes=False, usehiddens=False)

        file.write('UserID,Degree,')
        i = 1
        for cascade in self.cascades:
            file.write('Out' + str(i) + ',')
            file.write('In' + str(i) + ',')
            file.write('Likes' + str(i) + ',')
            file.write('Views' + str(i) + ',')
            file.write('Reposts' + str(i) + ',')
            file.write('Timestamp' + str(i) + ',')
            i += 1
        file.write('\n')
        for key in keys:
            exist = False
            for cascade in self.cascades:
                node_cascade = cascade.network.nodes.get(key)
                if node_cascade is not None:
                    exist = True

            if exist:
                file.write(str(key)+',')
                node_underlying = self.underlying_net.network.nodes[key]
                file.write(str(len(node_underlying)) + ',')
                for cascade in self.cascades:
                    node_cascade = cascade.network.nodes.get(key)
                    if node_cascade is not None:
                        file.write(str(len(node_cascade['out'])) + ',')
                        file.write(str(len(node_cascade['in'])) + ',')
                        post_info = cascade.posters[key]
                        file.write(str(len(post_info['likes'])) + ',')
                        file.write(str(post_info['views']) + ',')
                        file.write(str(post_info['reposts']) + ',')
                        file.write(str(post_info['date']) + ',')

                file.write('\n')

        file.close()

    def write_diffusion_speed_csv(self, fname, post_id, derivative=False):
        file = open(fname, "w", encoding='utf-8')
        for cascade in self.cascades:
            if cascade.post_meta['postinfo']['id'] == post_id:
                dates = []
                for post_info in cascade.posters.values():
                    dates.append(post_info['date'])
                dates.sort()
                mindate = dates[0]
                t = 0
                dt = 7200
                k = 1
                if derivative:
                    for i in range(len(dates)):
                        time = dates[i] - mindate
                        if time >= t and time < t + dt:
                            k += 1
                        else:
                            file.write(str(t + mindate) + ',' + str(k) + '\n')
                            k = 1
                            t = (time // dt) * dt
                else:
                    for i in range(len(dates)):
                        file.write(str(dates[i])+','+str(i)+'\n')
                # file.write('\n')
                # for i in range(len(dates)):
                #     file.write(str(i+1) + ',')
                # file.write('\n')
        file.close()