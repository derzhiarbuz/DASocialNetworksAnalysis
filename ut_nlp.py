# Created by Gubanov Alexander (aka Derzhiarbuz) at 17.10.2019
# Contacts: derzhiarbuz@gmail.com

import da_nlpbase
import pickle
from scipy.cluster.hierarchy import dendrogram, linkage
from matplotlib import pyplot as plt

file = open("D:/BigData/Guber/httpsvkcomriatomskcsv.pkl", "rb")
tokenized_posts = pickle.load(file)
file.close()
#bows = da_nlpbase.bag_of_words_dict(tokenized_posts)
#bou = da_nlpbase.bag_of_usage(bows)
bow = da_nlpbase.bag_of_words_sets(tokenized_posts)
dists, ord_dict = da_nlpbase.condensed_sets_similarity(bow)
# testdict = {1:{1,2,3,4}, 2:{1,2,3,4}, 3:{3,4,5,6}, 4:{1,2}}
# dists = da_nlpbase.condensed_sets_similarity(testdict)
# for d in dists:
#     print(d)
print(dists)
Z = linkage(dists, 'ward')
print('linkage completed')
print(ord_dict)


