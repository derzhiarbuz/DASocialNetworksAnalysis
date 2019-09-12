# Created by Gubanov Alexander (aka Derzhiarbuz) at 28.11.2018
# Contacts: derzhiarbuz@gmail.com

import requests
import json
from pymongo import MongoClient
import datetime

API_BASE = 'https://api.vk.com/method/'
API_VERSION = '5.92'

APP_ID1 = '6759333' #me
TOKEN_REQUEST1 = 'https://oauth.vk.com/authorize?client_id=6759333&display=page&redirect_uri=https://oauth.vk.com/blank.html&scope=friends&response_type=token&v=5.92'

APP_ID2 = '7041015' #adventist8day@gmail.com Qwerty12345
TOKEN_REQUEST2 = 'https://oauth.vk.com/authorize?client_id=7041015&display=page&redirect_uri=https://oauth.vk.com/blank.html&scope=friends&response_type=token&v=5.92'

APP_ID3 = '7041050' #adventist9day@gmail.com Qwerty12345
TOKEN_REQUEST3 = 'https://oauth.vk.com/authorize?client_id=7041050&display=page&redirect_uri=https://oauth.vk.com/blank.html&scope=friends&response_type=token&v=5.92'

APP_ID4 = '7041056' #adventist10day@gmail.com Qwerty12345
TOKEN_REQUEST4 = 'https://oauth.vk.com/authorize?client_id=7041056&display=page&redirect_uri=https://oauth.vk.com/blank.html&scope=friends&response_type=token&v=5.92'

APP_ID5 = '7041064' #adventist11day@gmail.com Qwerty12345
TOKEN_REQUEST5 = 'https://oauth.vk.com/authorize?client_id=7041064&display=page&redirect_uri=https://oauth.vk.com/blank.html&scope=friends&response_type=token&v=5.92'


ACCESS_TOKEN = '57a837765997b5bfc8b7ef168f84d813090c96b59b84debb5af9b952e059d9bc79161a300de5ab7287328'

ACCESS_TOKENS = ['6505df628defb8b4951ac67a0440aac5d63239e103632dbc5b0bad2705fa16425c9f2ccc0f7cbd6ed83a9',
                 '23f8c58730c797daaa3c8b4fd3e02ee97cd58c4838d5e036549c801bf29fd2389ea57274688a5752e7566',
                 '6a1998326ab1326863e142e3955992b1ad0b835b3a08eb1b325ba5427354231fdc259f60bbdc58191d6a4',
                 '7b97ae6f96a863a36d5c7f8b089adf3a1e4b732638b49b7da9a66f27bb1fa7331637642e2ff76e525ea80',
                 '70caa38d0c68494dcfd2a9fb306651916541c7a66b98a4ac6cd5c696a4494de64d3c851d6b4c4432dd181'
                 ]
TOKEN_I = 0

_cache_client = None
_cache_db = None

"""
vk_API is a method for making request to VK API. return value us dictionary {'response': ...} or {'error': ...}
example vk_API('users.get',{'user_ids':906554})
"""

def api(method: str, params: dict, isjson=True, ispost=False, use_cache=False, cache_date_utc=None):
    global ACCESS_TOKENS
    global TOKEN_I
    global ACCESS_TOKEN
    cache_string = None
    add_to_cache = None
    req_text = None
    while TOKEN_I<5:
        ACCESS_TOKEN = ACCESS_TOKENS[TOKEN_I]
        req_string = API_BASE+method+'?v='+API_VERSION+'&access_token='+ACCESS_TOKEN
        cache_string = 'vk/' + method
        add_to_cache = False
        req_text = None
        status_code = 200
        if not ispost:
            for k, v in params.items():
                req_string += '&'+str(k)+'='+str(v)
                if use_cache:
                    cache_string += '&'+str(k)+'='+str(v)
            if use_cache:
                req_text = query_from_cache_db(cache_string, 'wall_cache2', date_utc=cache_date_utc)
                # req = cache.get(cache_string)      # trying to obtain data from cache
                if req_text is None:
                    req = requests.get(req_string)
                    status_code = req.status_code
                    req_text = req.text
                    add_to_cache = True
                else:
                    print('From cache')
            else:
                req = requests.get(req_string)
                status_code = req.status_code
                req_text = req.text
        else:
            req_string = API_BASE+method+'?v='+API_VERSION+'&access_token='+ACCESS_TOKEN
            req_dict = {}
            for k, v in params.items():
                req_dict[str(k)] = str(v)
                if use_cache:
                    cache_string += '&'+str(k)+'='+str(v)
            if use_cache:   # trying to obtain data from cache
                req_text = query_from_cache_db(cache_string, 'wall_cache2', date_utc=cache_date_utc)
                # req = cache.get(cache_string)
                if req_text is None:
                    req = requests.post(req_string, req_dict)
                    status_code = req.status_code
                    req_text = req.text
                    add_to_cache = True
                else:
                    print('From cache')
            else:
                req = requests.post(req_string, req_dict)
                status_code = req.status_code
                req_text = req.text

        if status_code != 200:
            if isjson:
                return {'error': {'error_code': -1, 'error_msg': ('Status code is '+str(status_code))}}
            else:
                return "{'error':{'error_code':-1,'error_msg':'Status code is "+str(status_code)+"'}}"

        if isjson and isinstance(req_text, str):
            req_text = json.loads(req_text)
        if not isjson and not isinstance(req_text, str):
            req_text = json.dumps(req_text)

        if is_error(req_text):
            if error_code(req_text) == 29 or error_code(req_text) == 5:
                TOKEN_I += 1
                print('Need to change token number to '+str(TOKEN_I))
                continue
        break

    if use_cache and add_to_cache:
        cache_query_db(cache_string, 'wall_cache2', req_text)
        # cache[cache_string] = req

    return req_text


def set_token(token: str):
    global ACCESS_TOKEN
    ACCESS_TOKEN = token


def set_version(version: str):
    global API_VERSION
    API_VERSION = version


def check(response: dict):
    if response.get('response')is not None:
        return True
    return False


def is_error(response: dict):
    if response.__class__ is not dict:
        return False
    if response.get('error')is not None:
        return True
    return False


def error_code(response: dict):
    if is_error(response):
        return response['error']['error_code']
    return None


def remove_from_cache(method: str, params: dict):
    cache_string = 'vk/' + method
    for k, v in params.items():
        cache_string += '&' + str(k) + '=' + str(v)
    remove_from_cache_db(cache_string, 'wall_cache')
    # if cache.get(cache_string):
    #     cache.pop(cache_string)


def cache_db():
    global _cache_client
    global _cache_db
    if _cache_client is None:
        _cache_client = MongoClient()
        _cache_db = _cache_client.vk_cache
    return _cache_db


def query_from_cache_db(query_string, collection_string, date_utc=None):
    collection = cache_db()[collection_string]
    result = collection.find_one({'query': query_string})
    if result is not None:
        if date_utc is not None:
            if result['date'].timestamp() < date_utc:
                print('Cache is old ' + str(result['date'].timestamp()) + " " + str(date_utc) + " " + str(datetime.datetime.utcnow().timestamp()))
                return None
        return result['response']
    return None


def cache_query_db(query_string, collection_string, response):
    collection = cache_db()[collection_string]
    collection.replace_one({'query': query_string},
                           {
                               'query': query_string,
                               'response': response,
                               'date': datetime.datetime.utcnow()
                           }, True)


def remove_from_cache_db(query_string, collection_string):
    collection = cache_db()[collection_string]
    collection.delete_one({'query': query_string})


if __name__ == '__main__':
    print(api('likes.getList',{'owner_id': 76428402, 'item_id': 1444, 'type': 'post', 'count': 1000}))
    #print(api('users.get',{'user_ids':906554, 'fields':'first_name,last_name,counters,photo_100'}))