# Created by Gubanov Alexander (aka Derzhiarbuz) at 29.04.2019
# Contacts: derzhiarbuz@gmail.com
import pickle as pkl
import os
from pymongo import MongoClient
import datetime
import id_anonymizer


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
    def load_dict_of_set_of_ints_binary(filename, valid_ids=None):
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
                if valid_ids is not None:
                    if key in valid_ids:
                        obj[key] = obj_key
                else:
                    obj[key] = obj_key
                if i%1000 == 0:
                    print(str(i) + "   " + str(n) + "  " + str(len(obj)))
                for j in range(n):
                    byte_arr = file.read(4)
                    obj_key.add(int.from_bytes(byte_arr, 'little', signed=True))
                if valid_ids is not None and len(obj) >= len(valid_ids):
                    break
        file.close()
        return obj

    @staticmethod
    def save_dict_of_set_of_ints_csv(obj, filename, anonymized=False):
        file = open(filename + '1', 'wt')
        if file:
            for key, value in obj.items():
                file.write(str(len(value)))
                file.write(',')
                if anonymized:
                    file.write(str(id_anonymizer.anonymize(int(key))))
                else:
                    file.write(str(int(key)))
                for val in value:
                    file.write(',')
                    if anonymized:
                        file.write(str(id_anonymizer.anonymize(int(val))))
                    else:
                        file.write(str(int(val)))
                file.write('\n')
            file.close()
            os.replace(filename + '1', filename)
            return True
        else:
            return False

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

    @staticmethod
    def recode_dict_of_set_of_ints_binary_to_csv(filename, filename_csv, anonymized=False):
        file = open(filename, 'rb')
        file2 = open(filename_csv + '1', 'wt')
        obj = {}
        byte_arr = file.read(4)
        if len(byte_arr):
            n_keys = int.from_bytes(byte_arr, 'little', signed=True)
            for i in range(n_keys):
                byte_arr = file.read(4)
                n = int.from_bytes(byte_arr, 'little', signed=True)
                file2.write(str(n))
                file2.write(',')
                byte_arr = file.read(4)
                key = int.from_bytes(byte_arr, 'little', signed=True)
                if anonymized:
                    file2.write(str(id_anonymizer.anonymize(int(key))))
                else:
                    file2.write(str(int(key)))
                for j in range(n):
                    byte_arr = file.read(4)
                    val = int.from_bytes(byte_arr, 'little', signed=True)
                    file2.write(',')
                    if anonymized:
                        file2.write(str(id_anonymizer.anonymize(int(val))))
                    else:
                        file2.write(str(int(val)))
                file2.write('\n')
        file.close()
        file2.close()
        os.replace(filename_csv + '1', filename_csv)
        return obj


if __name__ == '__main__':
    DataManager.default_manager().recode_dict_of_set_of_ints_binary_to_csv('D:/BigData/Charity/Cascades/Zhestu_network.dos',
                                                                           'D:/BigData/Network_anon6.csv',
                                                                           anonymized=True)