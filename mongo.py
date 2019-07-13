# Created by Gubanov Alexander (aka Derzhiarbuz) at 09.06.2019
# Contacts: derzhiarbuz@gmail.com

import pymongo
from pymongo import MongoClient
import pprint
import da_vk_api as vk

client = MongoClient()
db = client.mongo_test
collection = db.test_collection

unit = collection.find()
for u in unit:
    pprint.pprint(u)

posts = vk.api('wall.get', {'type': 'post', 'owner_id': str(906557), 'count': 100,
                                    'owners_only': 1}, use_cache=True)
print(posts)
vk.remove_from_cache('wall.get', {'type': 'post', 'owner_id': str(906557), 'count': 100,
                                                              'owners_only': 1})
