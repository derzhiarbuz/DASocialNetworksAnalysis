# Created by Gubanov Alexander (aka Derzhiarbuz) at 29.04.2019
# Contacts: derzhiarbuz@gmail.com
import pickle as pkl
import os
from pymongo import MongoClient
import datetime


class DataManager(object):

    __instance = None

    def __init__(self):
        if not DataManager.__instance:
            self._client = MongoClient()
            self._db = self._client.vk_cache

    @classmethod
    def default_manager(cls):
        if not cls.__instance:
            cls.__instance = DataManager()
        return cls.__instance

    @staticmethod
    def save(obj, filename):
        file = open(filename+'1', 'wb')
        if file:
            pkl.dump(obj, file)
            file.close()
            os.replace(filename+'1', filename)
            return True
        else:
            return False

    @staticmethod
    def load(filename):
        file = open(filename, 'rb')
        obj = pkl.load(file)
        file.close()
        return obj

    @staticmethod
    def save_dict_of_set_of_ints_binary(obj, filename):
        file = open(filename+'1', 'wb')
        if file:
            file.write(len(obj).to_bytes(4, 'little', signed=True))
            for key, value in obj.items():
                file.write(len(value).to_bytes(4, 'little', signed=True))
                file.write(int(key).to_bytes(4, 'little', signed=True))
                for val in value:
                    file.write(int(val).to_bytes(4, 'little', signed=True))
            file.close()
            os.replace(filename+'1', filename)
            return True
        else:
            return False

    @staticmethod
    def load_dict_of_set_of_ints_binary(filename):
        file = open(filename, 'rb')
        obj = {}
        byte_arr = file.read(4)
        if len(byte_arr):
            n_keys = int.from_bytes(byte_arr, 'little', signed=True)
            for i in range(n_keys):
                byte_arr = file.read(4)
                n = int.from_bytes(byte_arr, 'little', signed=True)
                byte_arr = file.read(4)
                key = int.from_bytes(byte_arr, 'little', signed=True)
                obj_key = set()
                obj[key] = obj_key
                for i in range(n):
                    byte_arr = file.read(4)
                    obj_key.add(int.from_bytes(byte_arr, 'little', signed=True))
        file.close()
        return obj

    @staticmethod
    def query_from_cache(query_string, collection_string, date_utc=None):
        dm = DataManager.default_manager()
        collection = dm._db[collection_string]
        result = collection.find_one({'query': query_string})
        if result is not None:
            if date_utc is not None:
                if result['date'] < date_utc:
                    return None
            return result['response']
        return None

    @staticmethod
    def cache_query(query_string, collection_string, response):
        dm = DataManager.default_manager()
        collection = dm._db[collection_string]
        collection.replace_one({'query': query_string},
                               {
                                   'query': query_string,
                                   'response': response,
                                   'date': datetime.datetime.utcnow()
                               },
                               upsert=True)