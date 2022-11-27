#!/usr/bin/env python3

import sys
import collections
import math
import random


class Node(object):
    def __init__(self, attribute):
        self.attribute = attribute
        self.label = None
        self.split_val = 0
        self.left = None
        self.right = None


# Read file
def readfile(file_path):
    file = open(file_path, 'r')
    line = []
    for data in file:
        line.append(data.split())

    data_attributes = line[0]
    del line[0]
    data_examples = line

    file.close()
    return data_attributes, data_examples


# Process input data
def process(examples, attributes):
    datadict = []
    for exs in examples:
        att = 0
        example = {}
        for ex in exs:
            example[attributes[att]] = ex
            att += 1
        datadict.append(example)
    return datadict


# Predict RFL
def predict_rfl(node, data):
    label = []
    for n in node:
        quality = predict_dtl(n, data)
        label.append(quality)
    votes = collections.Counter(label).most_common(1)
    return votes[0][0]


# RFL
def rfl(data, min_leaf, n_trees, rand_seed):
    nodes = []
    length = len(data)
    sample_indexes = get_sample_index(n_trees, length, rand_seed)
    count = 0
    while count < n_trees:
        examples = []
        for i in sample_indexes[count]:
            examples.append(data[i])
        tree = dtl(examples, min_leaf)
        nodes.append(tree)
        count += 1
    return nodes


# Get random indexes
def get_sample_index(n_trees, length, rand_seed):
    random.seed(rand_seed)
    indexes = []
    i = 0
    while i < n_trees:
        j = 0
        index = []
        while j < length:
            index.append(random.randint(0, length-1))
            j += 1
        indexes.append(index)
        i += 1
    return indexes


# Predict DTL
def predict_dtl(node, data):
    while node.attribute != 'leaf_node':
        attribute = node.attribute
        if float(data[attribute]) <= node.split_val:
            node = node.left
        else:
            node = node.right
    return node.label


# DTL
def dtl(data, min_leaf):
    x_equal = equivalent(data, 'x')
    y_equal = equivalent(data, 'y')
    if len(data) < min_leaf or y_equal or x_equal:
        fre_val = get_most_fqt_val(data)
        node = Node('leaf_node')
        if len(fre_val) == 2:
            if fre_val[0][1] == fre_val[1][1]:
                node.label = 'unknown'
            else:
                node.label = fre_val[0][0]
        else:
            node.label = fre_val[0][0]
        return node
    else:
        split_data = choose_split(data)
        best_attr = split_data[0]
        best_split_val = split_data[1]
        node = Node(best_attr)
        node.split_val = best_split_val
        node.left = dtl(split_data[2], min_leaf)
        node.right = dtl(split_data[3], min_leaf)
        return node


# Get most frequent value in y
def get_most_fqt_val(data):
    attributes = list(data[0].keys())
    value = []
    for ex in data:
        value.append(ex[attributes[-1]])
    coll_train = collections.Counter(value)
    most_fqt_val = coll_train.most_common(2)
    return most_fqt_val


# Equal
def equivalent(data, index):
    attributes = list(data[0].keys())
    if index == 'y':
        value = []
        for ex in data:
            value.append(ex[attributes[-1]])
        return equal_in(value)
    else:
        i = 0
        j = 0
        while j < len(attributes)-1:
            value = []
            for ex in data:
                value.append(ex[attributes[j]])
            if equal_in(value):
                i += 1
            j += 1
        if i == j:
            return True
        else:
            return False


# Equal inter
def equal_in(val):
    if len(set(val)) == 1:
        return True
    else:
        return False


# Choose Split
def choose_split(data):
    best_gain = 0
    best_attr = ''
    best_split_val = 0
    left_data = []
    right_data = []
    attributes = list(data[0].keys())
    del attributes[-1]
    i_root = information_content(data)
    for k in attributes:
        sort_data = sorted(data, key=lambda x: x[k])
        for i in range(0, len(sort_data)-1):
            split_val = 0.5 * (float(sort_data[i][k]) + float(sort_data[i+1][k]))
            info_gain = information_gain(k, split_val, sort_data, i_root)
            gain = info_gain[0]
            if gain > best_gain:
                best_gain = gain
                best_attr = k
                best_split_val = split_val
                left_data = info_gain[1]
                right_data = info_gain[2]
    return best_attr, best_split_val, left_data, right_data


# Information content
def information_content(data):
    if len(data) == 0:
        return 0
    else:
        attributes = list(data[0].keys())
        value = []
        for ex in data:
            value.append(ex[attributes[-1]])
        sum_label = len(value)
        labels = collections.Counter(value).most_common()
        i_root = 0
        for label in labels:
            p = label[1] / sum_label
            i_root -= p * math.log2(p)
        return i_root


# Information gain
def information_gain(key, split_val, data, i_root):
    data_small = []
    data_big = []
    for ex in data:
        if float(ex[key]) <= split_val:
            data_small.append(ex)
        else:
            data_big.append(ex)
    small_gain = information_content(data_small)
    big_gain = information_content(data_big)
    gain = i_root - (len(data_small) / len(data)) * small_gain - (len(data_big) / len(data)) * big_gain
    return gain, data_small, data_big


# main
# Build tree
filepath_train = sys.argv[1]
fileData_train = readfile(filepath_train)
file_attributes_train = fileData_train[0]
file_examples_train = fileData_train[1]
datadict_train = process(file_examples_train, file_attributes_train)
forest = rfl(datadict_train, int(sys.argv[3]), int(sys.argv[4]), int(sys.argv[5]))

# Predict
filepath_test = sys.argv[2]
fileData_test = readfile(filepath_test)
file_attributes_test = fileData_test[0]
file_examples_test = fileData_test[1]
datadict_test = process(file_examples_test, file_attributes_test)
for test in datadict_test:
    qualities = predict_rfl(forest, test)
    print(qualities)
