import json
import pandas as pd
from classes.Block import Block  # the block class
import networkx as nx
from IPython.display import display
import itertools
from collections import Counter, OrderedDict, defaultdict
import matplotlib.pyplot as plt
import numpy as np
import os

import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

stop_words = set(stopwords.words('english'))
nltk.download('punkt')
path = os.getcwd()

# Opening JSON file
f1 = open(f'{path}/data/entityCol1.json')
f2 = open(f'{path}/data/entityCol2.json')

# returns JSON object as
# a dictionary
ec1 = json.load(f1)
ec2 = json.load(f2)


def stem_clean(arr):
    arr = [str(i) for i in arr]
    joint_words = ' '.join(arr)
    joint_words = str(joint_words).lower()
    val = word_tokenize(joint_words)
    valTok = list(set([w for w in val if not w.lower() in stop_words]))
    return valTok


def extract_unique_key_val(start_ind: int, ec):
    all_att_e = []
    all_val_e = []
    dict_E = {}
    ep_ids = []
    x = start_ind
    for d in ec:
        values_EP = []
        for key, val in (d.items()):
            if (key != 'id'):  # exclude id into the calculation. ID is just for marking
                all_att_e.append(key)  # allKey
                treatedVal = str(val).lower()
                values_EP.append(treatedVal)
                all_val_e.append(treatedVal)  # allVal - treat number as string
            else:

                ep_ids.append(str(val).lower())

        values_EP = stem_clean(values_EP)
        dict_E[x] = values_EP
        x = x + 1

    att_e_keys = list(set(all_att_e))
    val_e_tokens = list(set(stem_clean(all_val_e)))

    return (att_e_keys, val_e_tokens, dict_E, ep_ids)


attE1Keys, val_e1_tokens, dict_E1, e1_ep_ids = extract_unique_key_val(1, ec1)
attE2Keys, val_e2_tokens, dict_E2, e2_ep_ids = extract_unique_key_val(101, ec2)
all_ids = e1_ep_ids + e2_ep_ids


def token_blocking(val_e1_tokens, val_e2_tokens, dict_E1, dict_E2):
    # common token
    # Only take token that exists in both

    common_token = set(val_e1_tokens) & set(val_e2_tokens)

    # from the common token create find all entity profile
    # that has contains the token
    e1_dict_token = {}

    for t in common_token:
        x = [ep for ep in dict_E1 if t in dict_E1[ep]]
        e1_dict_token[t] = x

    e2_dict_token = {}
    for t in common_token:
        x = [ep for ep in dict_E2 if t in dict_E2[ep]]
        e2_dict_token[t] = x

    all_blocks = []
    for ct in common_token:
        new_block = Block(ct, e1_dict_token[ct], e2_dict_token[ct])
        all_blocks.append(new_block)

    all_blocks.sort(key=lambda x: x.b_cardinality, reverse=True)  # sort based on its cardinality

    return all_blocks


token_blocks_all = token_blocking(val_e1_tokens, val_e2_tokens, dict_E1, dict_E2)

token_blocks_df = pd.DataFrame([x.as_dict() for x in token_blocks_all])
token_blocks_df.head(20)


attE2Keys.remove('age')
attE2Keys.remove('year')

attribute_blocks_ec1 = {}
attribute_blocks_ec2 = {}

# get all values for the attributes
for attribute in attE1Keys:
    attribute_blocks_ec1[attribute] = stem_clean(list(set([att[attribute] for att in ec1 if attribute in att.keys()])))

for attribute in attE2Keys:
    attribute_blocks_ec2[attribute] = stem_clean(list(set([att[attribute] for att in ec2 if attribute in att.keys()])))


# Similarity Calculation

def jaccard_set(list1, list2):
    """Define Jaccard Similarity function for two sets"""
    intersection = len(list(set(list1).intersection(list2)))
    union = (len(list1) + len(list2)) - intersection
    return float(intersection) / union


sim_ec1_ec2 = {}
for each in attribute_blocks_ec1:
    dict_temp = {}
    for every in attribute_blocks_ec2:
        similarity = jaccard_set(attribute_blocks_ec1[each], attribute_blocks_ec2[every])
        if similarity > 0:
            dict_temp[every] = similarity
    if (bool(dict_temp)):  # check if the dictionary is not empty
        max_key = max(dict_temp, key=dict_temp.get)
        sim_ec1_ec2[each] = max_key

sim_ec2_ec1 = {}
for each in attribute_blocks_ec2:
    dict_temp = {}
    for every in attribute_blocks_ec1:
        similarity = jaccard_set(attribute_blocks_ec2[each], attribute_blocks_ec1[every])
        if similarity > 0:
            dict_temp[every] = similarity
    if (bool(dict_temp)):  # check if the dictionary is not empty
        max_key = max(dict_temp, key=dict_temp.get)
        sim_ec2_ec1[each] = max_key

G = nx.Graph()

for each in sim_ec1_ec2:
    G.add_node(each)
    G.add_node(sim_ec1_ec2[each])
    G.add_edge(each, sim_ec1_ec2[each])
for each in sim_ec2_ec1:
    G.add_node(each)
    G.add_node(sim_ec2_ec1[each])
    G.add_edge(each, sim_ec2_ec1[each])

G_nodes = list(G.nodes)
aaabd = list(G.edges)

transitive_closures = {}
count = 0
for each in G_nodes:
    cluster = nx.node_connected_component(G, each)
    for every in cluster:
        G_nodes.remove(every)
    transitive_closures[count] = cluster
    count += 1


"""
Token Blocking by Attribute Clusters
"""


def tokenize_by_attribute(ec, attcol):
    attribute_cluster_token_temp = {}
    for every in attcol:
        liste = []
        for each in ec:
            if every in each:
                wtokens = nltk.word_tokenize(each[every])
                for word in wtokens:
                    liste.append(word)
        liste = stem_clean(liste)
        attribute_cluster_token_temp[every] = liste
    return attribute_cluster_token_temp


attribute_cluster_token_temp_ec1 = tokenize_by_attribute(ec1, attE1Keys)
attribute_cluster_token_temp_ec2 = tokenize_by_attribute(ec2, attE2Keys)


common_token_test = {}
for each in transitive_closures:
    liste = []
    for every in transitive_closures[each]:
        if every in attribute_cluster_token_temp_ec1:
            for word in attribute_cluster_token_temp_ec1[every]:
                liste.append(word)
        if every in attribute_cluster_token_temp_ec2:
            for word in attribute_cluster_token_temp_ec2[every]:
                liste.append(word)
    common_token_test[each] = set(liste)


def create_token_dict_by_attribute(ec1, transitive_closures):
    dict_att = []
    for each in ec1:
        att_dict = {}
        for every in each:
            if every == "id":
                att_dict[every] = each[every]
            for attclu in transitive_closures:
                if every in transitive_closures[attclu]:
                    tmp = stem_clean(nltk.word_tokenize(each[every]))
                    att_dict[every] = tmp
        dict_att.append(att_dict)
    return dict_att


ec1_token_dict_by_attribute = create_token_dict_by_attribute(ec1, transitive_closures)
ec2_token_dict_by_attribute = create_token_dict_by_attribute(ec2, transitive_closures)

print("**************")
for mmms in common_token_test:
    print(len(common_token_test[mmms]))
print("****************")

## Token Blocking by Attribute Clusters


e1_dict_token = {}
for cluster in common_token_test:
    for token in common_token_test[cluster]:
        liste = []
        for entity in ec1_token_dict_by_attribute:
            for each in entity:
                if each != 'id' and token in entity[each]:
                    liste.append(entity['id'])
        e1_dict_token[str(cluster)+token] = list(liste)


e2_dict_token = {}
for cluster in common_token_test:
    for token in common_token_test[cluster]:
        liste = []
        for entity in ec2_token_dict_by_attribute:
            for each in entity:
                if each != 'id' and token in entity[each]:
                    liste.append(entity['id'])
        e2_dict_token[str(cluster)+token] = list(liste)

all_blocks = []
for cluster in common_token_test:
    for token in common_token_test[cluster]:
        if len(e1_dict_token[str(cluster)+token]) > 0 and len(e2_dict_token[str(cluster)+token]) > 0:
            new_block = Block(str(cluster)+token, e1_dict_token[str(cluster)+token], e2_dict_token[str(cluster)+token])
            all_blocks.append(new_block)
all_blocks.sort(key=lambda x: x.b_cardinality, reverse=True)
token_blocks_by_attribute_df = pd.DataFrame([x.as_dict() for x in all_blocks])
display(token_blocks_by_attribute_df)
"""for cluster in transitive_closures:
    for attribute in transitive_closures[cluster]:
        liste = []
        for entity in ec2_token_dict_by_attribute:
            if attribute in entity:
                for word in common_token_test[cluster]:
                    if word in entity[attribute]:
                        liste.append(entity["id"])
                    e1_dict_token[str(cluster)+word] = list(liste)"""




print("test")