# Created by Gubanov Alexander (aka Derzhiarbuz) at 17.10.2019
# Contacts: derzhiarbuz@gmail.com

import pymorphy2
import re
from nltk.corpus import stopwords
import pandas
import pickle
import numpy as np


def stop_words():
    sw = stopwords.words('russian')
    sw.extend(['-'])
    return sw


def tokenize(text: str, nonumbers = False):
    morphy = pymorphy2.MorphAnalyzer()
    new_words = []
    words = re.sub(r"\S*[/\\@]\S*", " ", text)
    if nonumbers:
        words = re.findall(r"[A-Za-zА-Яа-яёЁ#_-]+", words)
    else:
        words = re.findall(r"[A-Za-zА-Яа-яёЁ0-9#_-]+", words)
    for w in words:
        new_words.append((morphy.parse(w)[0]).normal_form)
    return new_words


def tokenize_posts_to_file(source_file, dest_file):
    topics = pandas.read_csv(source_file)
    i = 0
    total = len(topics['text'])
    tokenized_posts = {}
    for txt in topics.iterrows():
        if not pandas.isna(txt[1]['text']):
            tokenized_posts[txt[0]] = tokenize(txt[1]['text'], nonumbers=True)
            print(i / total)
        i += 1
    print(tokenized_posts)
    file = open(dest_file, "wb")
    pickle.dump(tokenized_posts, file)
    file.close()


def bag_of_words(text: str = None, tokens_list=None):
    if text is None and tokens_list is None:
        return None
    if text is not None:
        words = tokenize(text, nonumbers=True)
    else:
        words = tokens_list
    bow = {}
    stwords = stop_words()
    for word in words:
        n = bow.get(word)
        if n is None:
            if word not in stwords:
                bow[word] = 1
        else:
            bow[word] = n+1
    return bow


def bag_of_words_dict(dict_of_tokens_lists: dict):
    bow_dict = {}
    for text_id, tokens_list in dict_of_tokens_lists.items():
        bow_dict[text_id] = bag_of_words(tokens_list=tokens_list)
    return bow_dict


def bag_of_words_sets(dict_of_tokens_lists: dict):
    bow_dict = {}
    for text_id, tokens_list in dict_of_tokens_lists.items():
        bow_dict[text_id] = set(bag_of_words(tokens_list=tokens_list).keys())
    return bow_dict


def bag_of_usage(bags_of_words: dict):
    bag_of_usage = {}
    for text_id, bow in bags_of_words.items():
        for word in bow.keys():
            ids = bag_of_usage.get(word)
            if not ids:
                ids = set()
                bag_of_usage[word] = ids
            ids.add(text_id)
    return bag_of_usage


def condensed_sets_similarity(bag_of_sets: dict):
    ord_dict = []
    for k, v in bag_of_sets.items():
        if len(v) > 1:
            ord_dict.append((k, v))
    # ord_dict = list(bag_of_sets.items())
    n = len(ord_dict)
    dists = np.empty(int(n * (n - 1) / 2))
    print(len(dists))
    k = 0
    for i in range(n-1):
        for j in range(i+1, n):
            a = ord_dict[i]
            b = ord_dict[j]
            c = len(a[1] & b[1])
            if c == 0:
                dists[k] = 0
            else:
                dists[k] = c / len(a[1] | b[1])
            k += 1
    return dists, ord_dict


def bag_of_probabilities(bag_of_usg: dict, n_texts: int):
    words = bag_of_usg.keys()
    probs1 = {}
    probs2 = {}
    probs3 = {}
    probs4 = {}
    probs5 = {}
    for word in words:
        probs1[word] = len(bag_of_usg[word])/n_texts
    for word1 in words:
        for word2 in words:
            if word1 > word2:
                card = len(bag_of_usg[word1] & bag_of_usg[word2])
                p = card/n_texts
                if card > 1:
                    probs2[(word1, word2)] = p
                    print(word1 + ' ' + word2)
    print(len(probs2))
    # word_pairs = probs2.keys()
    # for word1, word2 in word_pairs:
    #     for word3 in words:
    #         if word2 > word3:
    #             card = len(bag_of_usg[word1] & bag_of_usg[word2] & bag_of_usg[word3])
    #             p = card / n_texts
    #             if card > 1 and p > probs1[word1] * probs1[word2] * probs1[word3] * 10:
    #                 probs3[(word1, word2, word3)] = p
    #                 print(word1 + ' ' + word2 + ' ' + word3)
    # print(len(probs3))
    # word_triples = probs3.keys()
    # for word1, word2, word3 in word_triples:
    #     for word4 in words:
    #         if word3 > word4:
    #             card = len(bag_of_usg[word1] & bag_of_usg[word2] & bag_of_usg[word3] & bag_of_usg[word4])
    #             p = card / n_texts
    #             if card > 1 and p > probs1[word1] * probs1[word2] * probs1[word3] * probs1[word4] * 10:
    #                 probs4[(word1, word2, word3, word4)] = p
    #                 print(word1 + ' ' + word2 + ' ' + word3 + ' ' + word4)
    # print(len(probs4))
    # word_quadres = probs4.keys()
    # for word1, word2, word3, word4 in word_quadres:
    #     for word5 in words:
    #         if word4 > word5:
    #             card = len(bag_of_usg[word1] & bag_of_usg[word2] & bag_of_usg[word3]
    #                        & bag_of_usg[word4] & bag_of_usg[word5])
    #             p = card / n_texts
    #             if card > 1 and p > probs1[word1] * probs1[word2] * probs1[word3] * probs1[word4] * probs1[word5] * 10:
    #                 probs5[(word1, word2, word3, word4, word5)] = p
    #                 print(word1 + ' ' + word2 + ' ' + word3 + ' ' + word4 + ' ' + word5)
    # print(len(probs5))
    return probs1, probs2
