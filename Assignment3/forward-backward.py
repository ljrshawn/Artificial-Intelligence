#!/usr/bin/env python3

import sys
import math
import numpy as np


# Read file
def readfile(file_path):
    file = open(file_path, 'r')
    line = []
    for data in file:
        line.append(data.split())
    file.close()

    map_size = line[0]
    map_detail = []
    for mapData in line[1:int(map_size[0])+1]:
        map_detail.append(mapData)
    observation_num = line[int(map_size[0])+1][0]
    observation = []
    for mapData in line[int(map_size[0])+2:-1]:
        observation.append(mapData)
    error = line[-1][0]
    return map_size, map_detail, observation_num, observation, error


# Get initial probability
def initial_arr(map_detail):
    available = 0
    for i in map_detail:
        for j in i:
            if j == '0':
                available += 1
    rate = float(1/available)
    traversable = {}
    for i in range(len(map_detail)):
        for j in range(len(map_detail[i])):
            if map_detail[i][j] == '0':
                key = str(i) + ' ' + str(j)
                traversable[key] = rate
    return traversable


# Get neighbours
def get_neighbours(map_detail, row, column):
    nei = ['1', '1', '1', '1']
    if row == 0:
        if column == 0:
            if map_detail[row][column + 1] == '0':
                nei[1] = '0'
            if map_detail[row + 1][column] == '0':
                nei[2] = '0'
        elif column == len(map_detail[0])-1:
            if map_detail[row + 1][column] == '0':
                nei[2] = '0'
            if map_detail[row][column - 1] == '0':
                nei[3] = '0'
        else:
            if map_detail[row][column + 1] == '0':
                nei[1] = '0'
            if map_detail[row + 1][column] == '0':
                nei[2] = '0'
            if map_detail[row][column - 1] == '0':
                nei[3] = '0'
    elif row == len(map_detail)-1:
        if column == 0:
            if map_detail[row - 1][column] == '0':
                nei[0] = '0'
            if map_detail[row][column + 1] == '0':
                nei[1] = '0'
        elif column == len(map_detail[0])-1:
            if map_detail[row - 1][column] == '0':
                nei[0] = '0'
            if map_detail[row][column - 1] == '0':
                nei[3] = '0'
        else:
            if map_detail[row - 1][column] == '0':
                nei[0] = '0'
            if map_detail[row][column + 1] == '0':
                nei[1] = '0'
            if map_detail[row][column-1] == '0':
                nei[3] = '0'
    else:
        if column == 0:
            if map_detail[row - 1][column] == '0':
                nei[0] = '0'
            if map_detail[row][column + 1] == '0':
                nei[1] = '0'
            if map_detail[row + 1][column] == '0':
                nei[2] = '0'
        elif column == len(map_detail[0])-1:
            if map_detail[row - 1][column] == '0':
                nei[0] = '0'
            if map_detail[row + 1][column] == '0':
                nei[2] = '0'
            if map_detail[row][column - 1] == '0':
                nei[3] = '0'
        else:
            if map_detail[row - 1][column] == '0':
                nei[0] = '0'
            if map_detail[row][column + 1] == '0':
                nei[1] = '0'
            if map_detail[row + 1][column] == '0':
                nei[2] = '0'
            if map_detail[row][column-1] == '0':
                nei[3] = '0'
    return nei


# Get transition matrix
def transition(map_detail, key):
    size_k = len(key)
    matrix = []
    for i in key:
        key_row = [float(0)] * size_k
        position = i.split(' ')
        row = int(position[0])
        column = int(position[1])
        neighbor = get_neighbours(map_detail, row, column)
        rate = float(0)
        if neighbor.count('0') != 0:
            rate = float(1/neighbor.count('0'))
        for j in range(len(neighbor)):
            if neighbor[j] == '0':
                if j == 0:
                    tem_key = str(row - 1) + ' ' + str(column)
                elif j == 1:
                    tem_key = str(row) + ' ' + str(column + 1)
                elif j == 2:
                    tem_key = str(row + 1) + ' ' + str(column)
                else:
                    tem_key = str(row) + ' ' + str(column - 1)
                key_index = key.index(tem_key)
                key_row[key_index] = rate
        matrix.append(key_row)
    return matrix


# Get emission matrix
def emission(map_detail, key, space, error):
    matrix = {}
    for i in key:
        position = i.split(' ')
        row = int(position[0])
        column = int(position[1])
        neighbor = get_neighbours(map_detail, row, column)
        rate_list = []
        for j in space:
            error_sensor = 0
            for k in range(4):
                if j[k] != neighbor[k]:
                    error_sensor += 1
            all_error_rate = math.pow(1 - float(error), 4 - error_sensor) * math.pow(float(error), error_sensor)
            rate_list.append(all_error_rate)
        matrix[i] = rate_list
    return matrix


# Forward
def forward(sensor_m, transition_m, recursion, position, time):
    parents = []
    for i in range(len(transition_m[position])):
        if transition_m[position][i] != 0:
            parents.append(i)
    fr = 0
    if len(parents) != 0:
        for i in parents:
            fr += transition_m[position][i] * recursion[i][time-1]
        fr *= sensor_m
    return fr


# Backward
def backward(emission_m, observe_space_str, key, observation, transition_m, recursion, position, time):
    children = []
    for i in range(len(transition_m[position])):
        if transition_m[position][i] != 0:
            children.append(i)
    b = 0
    if len(children) != 0:
        for i in children:
            i_emission = emission_m.get(key[i])
            pos = observe_space_str.index(observation[time - 1][0])
            b += i_emission[pos] * transition_m[position][i] * recursion[i][len(observation) - time]
    return b


# Forward-backward algorithm for smoothing
def forward_algorithm(map_detail, observation, error):
    observe_space = []
    for i in range(16):
        tem_observe = []
        bi = bin(i)
        tem_bi = bi[2:].zfill(4)
        for j in tem_bi:
            tem_observe.append(j)
        observe_space.append(tem_observe)
    observe_space_str = []
    for i in observe_space:
        observe_space_str.append(''.join(i))
    initial_proba = initial_arr(map_detail)
    key = list(initial_proba.keys())
    transition_m = transition(map_detail, key)
    emission_m = emission(map_detail, key, observe_space, error)
    fv_matrix = []
    for i in range(len(key)):
        fv_matrix.append([initial_proba[key[i]]])
    for j in range(1, len(observation) + 1):
        # tem_sum = float(0)
        for i in range(len(key)):
            i_emission = emission_m.get(key[i])
            pos = observe_space_str.index(observation[j - 1][0])
            tem = forward(i_emission[pos], transition_m, fv_matrix, i, j)
            fv_matrix[i].append(tem)
            # tem_sum += tem
        # for i in range(len(key)):
        #     fv_matrix[i][-1] = float(fv_matrix[i][-1]/tem_sum)
    # print(fv_matrix[1][6])
    sv_matrix = []
    b = []
    for i in range(len(key)):
        sv_matrix.append([])
        b.append([float(1)])
    for j in range(len(observation), 0, -1):
        tem_sum = float(0)
        for i in range(len(key)):
            tem = b[i][len(observation)-j] * fv_matrix[i][j]
            sv_matrix[i].append(tem)
            tem_sum += tem
        for i in range(len(key)):
            sv_matrix[i][-1] = float(sv_matrix[i][-1]/tem_sum)
        # tem_sum = float(0)
        for i in range(len(key)):
            tem = backward(emission_m, observe_space_str, key, observation, transition_m, b, i, j)
            b[i].append(tem)
            # tem_sum += tem
        # for i in range(len(key)):
        #     b[i][-1] = float(b[i][-1] / tem_sum)
    for i in range(len(sv_matrix)):
        sv_matrix[i].reverse()
        # print(sv_matrix[i])
    # print(sv_matrix[1][5])
    return sv_matrix


# Get map array
def get_result(map_detail, matrix, row, column):
    result = []
    for length in range(len(matrix[0])):
        tem_res = []
        k = 0
        for i in range(len(map_detail)):
            for j in range(len(map_detail[i])):
                if map_detail[i][j] == '0':
                    tem_res.append(matrix[k][length])
                    # tem_res.append(round(matrix[k][length], 8))
                    k += 1
                else:
                    tem_res.append(float(0))
                    # tem_res.append(round(float(0), 8))
        # print(tem_res)
        tem = np.array(tem_res).reshape(row, column)
        result.append(tem)
    return result


# main
filepath = sys.argv[1]
size, mapDetail, observ_num, observ_val, error_rate = readfile(filepath)
rows = int(size[0])
columns = int(size[1])
sv = forward_algorithm(mapDetail, observ_val, error_rate)
res_map = get_result(mapDetail, sv, rows, columns)
np.savez("output.npz", *res_map)
# path = "/Users/shawnl/Library/Mobile Documents/com~apple~CloudDocs/Shawn.Lyu/Study/" \
#        "University of Adelaide/Artificial Intelligence/Assignment/Assignment3/output.npz"
# data = np.load(path)
# print(data['arr_5'][0])
# path = "/Users/shawnl/Desktop/debug_output.npz"
# data = np.load(path)
# print(data['arr_5'][0])
