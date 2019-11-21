# Created by Gubanov Alexander (aka Derzhiarbuz) at 28.04.2019
# Contacts: derzhiarbuz@gmail.com

from enum import Enum
import datetime


class NetworkType(Enum):
    static = 1
    dynamic = 2


class NetworkOptimisation(Enum):
    none = 1
    id_only = 2


class Network(object):
    def __init__(self, optimisation=NetworkOptimisation.none):
        self.type = NetworkType.static
        self.timestamp = datetime.datetime.now()
        self.nodes = {}
        self.optimisation = optimisation
        if self.optimisation == NetworkOptimisation.none:
            self.links = {}
            self.network_attributes = {}
            self.nodes_attributes = []
            self.links_attributes = []
        else:
            self.links = None
            self.network_attributes = None
            self.nodes_attributes = None
            self.links_attributes = None


    @property
    def nodes_ids(self):
        return self.nodes.keys()

    def get_node(self, node_id):
        if node_id in self.nodes_ids:
            return self.nodes[node_id]
        else:
            return None

    def get_in_neighbors_for_node(self, node_id, include_mutual=True):
        if node_id in self.nodes_ids:
            if self.optimisation == NetworkOptimisation.id_only:
                return self.nodes[node_id]
            else:
                if include_mutual:
                    return self.nodes[node_id]['in'] | self.nodes[node_id]['inout']
                else:
                    return self.nodes[node_id]['in']
        else:
            return None

    def get_out_neighbors_for_node(self, node_id, include_mutual=True):
        if node_id in self.nodes_ids:
            if self.optimisation == NetworkOptimisation.id_only:
                return self.nodes[node_id]
            else:
                if include_mutual:
                    return self.nodes[node_id]['out'] | self.nodes[node_id]['inout']
                else:
                    return self.nodes[node_id]['out']
        else:
            return None

    def add_node(self, node_id):
        if node_id not in self.nodes_ids:
            if self.optimisation == NetworkOptimisation.id_only:
                self.nodes[node_id] = set()
            else:
                self.nodes[node_id] = {'in': set(), 'out': set(), 'inout': set()}

    def add_meta_for_node(self, node_id, meta):
        if self.optimisation == NetworkOptimisation.id_only:
            return
        node = self.nodes.get(node_id)
        if node is not None:
            for k, v in meta.items():
                if node.get('attrs') is None:
                    node['attrs'] = {}
                node['attrs'][k] = v

    def meta_for_node(self, node_id, key):
        if self.optimisation == NetworkOptimisation.id_only:
            return None
        node = self.nodes.get(node_id)
        if node is not None:
            if node.get('attrs') is not None:
                return node['attrs'].get(key)
        return None

    def add_link(self, node1_id, node2_id, mutual=True, weighted=False, weight=1,):
        self.add_node(node1_id)
        self.add_node(node2_id)
        if self.optimisation == NetworkOptimisation.id_only:
            self.nodes[node1_id].add(node2_id)
            if mutual:
                self.nodes[node2_id].add(node1_id)
        else:
            if (node1_id, node2_id) not in self.links:
                self.links[(node1_id, node2_id)] = {'mutual': mutual}
                if weighted:
                    self.links[(node1_id, node2_id)]['w'] = weight
            node1 = self.get_node(node1_id)
            if mutual:
                node1['inout'].add(node2_id)
                node2 = self.get_node(node2_id)
                node2['inout'].add(node1_id)
                if (node2_id, node1_id) not in self.links:
                    self.links[(node2_id, node1_id)] = {'mutual': mutual}
                    if weighted:
                        self.links[(node2_id, node1_id)]['w'] = weight
            else:
                node1['out'].add(node2_id)
                node2 = self.get_node(node2_id)
                node2['in'].add(node1_id)

    def add_links(self, edges, mutual=True):
        for edge_ids in edges:
            self.add_link(edge_ids[0], edge_ids[1], mutual)

    def add_meta_for_link(self, node1_id, node2_id, meta):
        if self.optimisation == NetworkOptimisation.id_only:
            return
        link = self.links.get((node1_id, node2_id))
        if link is not None:
            for k, v in meta.items():
                if link.get('attrs') is None:
                    link['attrs'] = {}
                link['attrs'][k] = v
            if link['mutual']:
                link2 = self.links.get((node2_id, node1_id))
                link2['attrs'] = link['attrs']

    def meta_for_link(self, node1_id, node2_id, key):
        if self.optimisation == NetworkOptimisation.id_only:
            return None
        link = self.links.get((node1_id, node2_id))
        if link is not None:
            if link.get('attrs') is not None:
                return link['attrs'].get(key)
        return None

    def export_gexf(self, path, drop_singletones = False, dynamic=False):
        file = open(path, 'w', encoding='utf-8')
        if not file:
            print('export_gexf failed')
            return
        file.write('''<?xml version="1.0" encoding="UTF-8"?>
                    <gexf xmlns="http://www.gexf.net/1.2draft" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.gexf.net/1.2draft http://www.gexf.net/1.2draft/gexf.xsd" version="1.2">
                    <meta lastmodifieddate="''' + datetime.date.today().strftime("%Y-%m-%d") + '''">
                    <creator>Derzhiarbuz</creator>
                    <description>NO DESCRIPTION</description>
                    </meta>''')
        # symbols = (u"абвгдеёжзийклмнопрстуфхцчшщъыьэюяАБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ",
        #            u"abvgdeejzijklmnoprstufhzcss_y_euaABVGDEEJZIJKLMNOPRSTUFHZCSS_Y_EUA")
        # tr = {ord(a): ord(b) for a, b in zip(*symbols)}

        file.write('\n<graph')
        if dynamic:
            file.write(' mode="dynamic" timeformat="double"')
        for aname, aval in self.network_attributes.items():
            file.write(' ' + aname + '="' + aval + '"')
        file.write('>')
        if len(self.nodes_attributes):
            file.write('\n<attributes class="node">')
            for atr in self.nodes_attributes:
                file.write('<attribute id="' + atr['id'] + '" title="' + atr['title'] + '" type="' + atr['type'] + '">')
                if atr.get('default'):
                    file.write('<default>' + atr['default'] + '</default>')
                file.write('</attribute>')
            file.write('</attributes>')

        if len(self.links_attributes):
            file.write('\n<attributes class="edge">')
            for atr in self.links_attributes:
                file.write('<attribute id="' + atr['id'] + '" title="' + atr['title'] + '" type="' + atr['type'] + '">')
                if atr.get('default'):
                    file.write('<default>' + atr['default'] + '</default>')
                file.write('</attribute>')
            file.write('</attributes>')

        if len(self.nodes):
            file.write('''\n\t\t<nodes>''')
            for node_id, node_data in self.nodes.items():
                if drop_singletones:
                    if len(node_data['in']) == 0 and len(node_data['out']) == 0 and len(node_data['inout']) == 0:
                        continue
                file.write('\n<node')
                file.write(' id="' + str(node_id) + '"')
                if dynamic:
                    node_start = self.meta_for_node(node_id, 'start')
                    node_end = self.meta_for_node(node_id, 'end')
                    if node_start is not None:
                        file.write(' start="'+str(node_start)+'"')
                    if node_end is not None:
                        file.write(' end="'+str(node_end)+'"')
                file.write('>')
                attrs = node_data.get('attrs')
                if attrs is not None:
                    file.write('''<attvalues>''')
                    for attid, attvl in attrs.items():
                        file.write('''<attvalue for="''' + str(attid) + '''" value="''' + str(attvl) + '''"/>''')
                    file.write('''</attvalues>''')
                file.write('''</node>''')
            file.write('''\n</nodes>''')

        if len(self.links):
            id = 0
            file.write('''\n\t\t<edges>''')
            for link_key, link_data in self.links.items():
                if link_data['mutual'] and link_key[0] > link_key[1]: # avoid edge duplication for undirected link
                    continue
                # file.write('''\n<edge id="'''+str(edge['id'])+'''" source="'''+str(edge['source'])
                # +'''" target="'''+str(edge['target'])+'''">''')
                file.write('\n<edge')
                file.write(' id="' + str(id) + '"')
                id += 1
                file.write(' source="' + str(link_key[0]) + '"')
                file.write(' target="' + str(link_key[1]) + '"')
                if not link_data['mutual']:
                    file.write(' type="directed"')
                if link_data.get('w'):
                    file.write(' weight="' + str(link_data['w']) + '"')
                if dynamic:
                    link_start = self.meta_for_link(link_key[0], link_key[1], 'start')
                    link_end = self.meta_for_link(link_key[0], link_key[1], 'end')
                    if link_start is not None:
                        file.write(' start="'+str(link_start)+'"')
                    if link_end is not None:
                        file.write(' end="'+str(link_end)+'"')
                file.write('>')
                file.write('''</edge>''')
            file.write('''\n</edges>''')

        file.write("\n</graph>")
        file.write("\n</gexf>")
        file.close()

    def degree_distribution(self):
        degrees = {'in': [], 'out': [], 'inout': []}
        for node_id in self.nodes.items():
            degree = self.node_degree(node_id)
            degrees['in'].append(degree['in'])
            degrees['out'].append(degree['out'])
            degrees['inout'].append(degree['inout'])
        return degrees

    def weighted_degree_distribution(self):
        weights = {'in': [], 'out': [], 'inout': []}
        for node_id in self.nodes.items():
            weight = self.node_weighted_degree(node_id)
            weights['in'].append(weight['in'])
            weights['out'].append(weight['out'])
            weights['inout'].append(weight['inout'])
        return weights

    def link_weights_distribution(self):
        weights = {'direct': [], 'indirect': []}
        for node1_id in self.nodes.keys():
            for node2_id in self.nodes.keys():
                link = self.links.get((node1_id, node2_id))
                if link is not None:
                    w = link.get('w')
                    if w is None:
                        w = 1
                    if link['mutual']:
                        if node1_id > node2_id:
                            continue
                        weights['indirect'].append(w)
                    else:
                        weights['direct'].append(w)

    def directed_link_weight_pairs(self):
        weights = []
        for node1_id in self.nodes.keys():
            for node2_id in self.nodes.keys():
                if node1_id > node2_id:
                    continue
                link1 = self.links.get((node1_id, node2_id))
                link2 = self.links.get((node2_id, node1_id))
                w1 = 0
                w2 = 0
                if link1 is not None:
                    if link1['mutual']:
                        continue
                    w1 = link1.get('w')
                    if w1 is None:
                        w1 = 1
                if link2 is not None:
                    w2 = link2.get('w')
                    if w1 is None:
                        w2 = 1
                weights.append((w1, w2))
        return weights

    def node_degree(self, node_id):
        node = self.nodes.get(node_id)
        weights = {'in': 0, 'out': 0, 'inout': 0}
        if node is not None:
            if self.optimisation == NetworkOptimisation.id_only:
                weights['inout'] = len(node)
            else:
                weights['in'] = len(node['in'])
                weights['out'] = len(node['out'])
                weights['inout'] = len(node['inout'])
        return weights

    def node_weighted_degree(self, node_id):
        node = self.nodes.get(node_id)
        weights = {'in': 0, 'out': 0, 'inout': 0}
        if node is not None:
            if self.optimisation == NetworkOptimisation.id_only:
                weights['inout'] = len(node)
            else:
                for node2_id in node['in']:
                    link = self.links.get((node2_id, node_id))
                    if link is not None:
                        w = link.get('w')
                        if w is None:
                            w = 1
                        weights['in'] += w
                for node2_id in node['out']:
                    link = self.links.get((node_id, node2_id))
                    if link is not None:
                        w = link.get('w')
                        if w is None:
                            w = 1
                        weights['out'] += w
                for node2_id in node['inout']:
                    link = self.links.get((node_id, node2_id))
                    if link is not None:
                        w = link.get('w')
                        if w is None:
                            w = 1
                        weights['inout'] += w
        return weights

