# Created by Gubanov Alexander (aka Derzhiarbuz) at 02.05.2019
# Contacts: derzhiarbuz@gmail.com

from da_network import Network
from da_network_manager import NetworkManager
import da_vk_api as vk
import da_socnetworks_crawler as crlr
import datetime


class ICNetworkManager(NetworkManager):
    def __init__(self, net=Network(), name='', base_dir=''):
        super().__init__(net, name, base_dir)
        self.post_meta = {}
        self.posters = {}
        self.hiddens = set()
        self.likers = set()
        self.timestamp = datetime.datetime.now()

    def get_data_dict(self):
        data_dict = super().get_data_dict()
        data_dict['post_meta'] = self.post_meta
        data_dict['posters'] = self.posters
        data_dict['hiddens'] = self.hiddens
        data_dict['likers'] = self.likers
        data_dict['timestamp'] = self.timestamp
        return data_dict

    def set_data_dict(self, data_dict):
        super().set_data_dict(data_dict)
        self.post_meta = data_dict['post_meta']
        self.posters = data_dict['posters']
        self.hiddens = data_dict['hiddens']
        self.likers = data_dict['likers']
        self.timestamp = data_dict['timestamp']

    def crawl_next(self):
        if len(self.crawl_plan) == 0:
            # print('Crawl plan is length of zero')
            return 0

        crawler = self.crawl_plan[0]
        result = self.crawl_post(crawler)

        if result == 'empty':
            self.crawl_plan.pop(0)
        if result != 'error':
            return 1
        else:
            return -1

    def crawl_post(self, crawler):
        if crawler['stage'] == 0:
            source_id = crawler['source_id']
            post_id = crawler['post_id']
            meta = crlr.get_root_post_for_wall_with_meta(source_id, post_id)
            if vk.is_error(meta):
                print('Error: ' + str(meta['error']['error_code']) + ' ' + meta['error']['error_msg'])
                return 'error'
            self.post_meta = meta
            self.posters[source_id] = self.post_meta['postinfo']
            if self.posters[source_id].get('likes') is not None:
                crawler['likes_to_process'] |= self.posters[source_id]['likes']
                crawler['stage'] = 1
                return 'done'
            return 'empty'
        elif crawler['stage'] == 1:
            source_id = crawler['source_id']
            likes_to_process = crawler['likes_to_process']
            likes_processed = crawler['likes_processed']
            if len(likes_to_process) == 0:
                return 'empty'
            user_id = likes_to_process.pop()
            content_md5 = self.post_meta['md5']
            search_string = self.post_meta['search_string']
            source_date = self.post_meta['postinfo']['date']
            new_post_info = crlr.find_post_on_wall(user_id, content_md5, search_string, source_id,
                                                   source_date,
                                                   use_cache=True,
                                                   cache_date_utc=(self.timestamp.timestamp()-25200))
            if vk.is_error(new_post_info):
                likes_to_process.add(user_id)
                print('Error: ' + str(new_post_info['error']['error_code']) + ' ' + new_post_info['error']['error_msg'])
                return 'error'
            if new_post_info['type'] == 'poster':
                print(new_post_info)
                if vk.is_error(new_post_info['likes']):
                    if vk.error_code(new_post_info['likes']) == 15:
                        new_post_info['likes'] = set()
                self.posters[user_id] = new_post_info
                likes_processed.add(user_id)
                if len(new_post_info['likes']):
                    likes_to_process |= new_post_info['likes'] - likes_processed
            elif new_post_info['type'] == 'hidden':
                self.hiddens.add(user_id)
            elif new_post_info['type'] == 'liker':
                self.likers.add(user_id)

    def schedule_crawl_post_from_source(self, source_id, post_id):
        self.post_meta = {}
        self.posters = {}
        self.hiddens = set()
        self.likers = set()

        crawler = {'type': 'post',
                   'stage': 0,
                   'source_id': source_id,
                   'post_id': post_id,
                   'likes_to_process': set(),
                   'likes_processed': set()}

        self.crawl_plan.append(crawler)

    def remake_network(self, possible_links: dict, uselikes=True, usehiddens=True):
        # print('This method updates network from post_meta, hiddens, likers etc.')
        self.network = Network()
        if usehiddens:
            for node_id in self.hiddens:
                self.network.add_node(node_id)
        if uselikes:
            for node_id in self.likers:
                self.network.add_node(node_id)
        nodes = self.posters.keys()
        for node_id in nodes:
            self.network.add_node(node_id)
            date = self.posters[node_id]['date']
            for node2_id in nodes:
                if node2_id != node_id:
                    date2 = self.posters[node2_id]['date']
                    if date < date2:
                        neighs_set = possible_links.get(node_id)
                        if neighs_set and node2_id in neighs_set:
                            self.network.add_link(node_id, node2_id, mutual=False)
                        # print('Link: ' + str(node_id) + ' -> ' + str(node2_id))
            # print(str(node_id) + ' : ' + str(self.posters[node_id]))


'''

        self.post_meta = crlr.get_root_post_for_wall_with_meta(source_id, post_id)
        if self.post_meta is not None:
            content_md5 = self.post_meta['md5']
            search_string = self.post_meta['search_string']
            postinfo = self.post_meta['postinfo']
            posters[source_id] = postinfo
            source_date = postinfo['date']
            if posters[source_id].get('likes') is not None:
                likes_to_process |= posters[source_id]['likes']
                while len(likes_to_process):
                    user_id = likes_to_process.pop()
                    postinfo = crlr.find_post_on_wall(user_id, content_md5, search_string, source_id, source_date)
                    if postinfo['type'] == 'poster':
                        posters[user_id] = postinfo
                        likes_processed.add(user_id)
                        likes_to_process |= postinfo['likes'] - likes_processed
                    elif postinfo['type'] == 'hidden':
                        hiddens.add(user_id)
                    elif postinfo['type'] == 'liker':
                        likers.add(user_id)
                    print("Crawling post, posts left: ", str(len(likes_to_process)))
        return {'posters': posters, 'hiddens': hiddens, 'likers': likers}

'''