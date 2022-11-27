#!/usr/bin/env python3
import math
import sys
import queue
import random


# Read file
def readfile(file_path):
    file = open(file_path, 'r')
    line = []
    for data in file:
        line.append(data)
    file.close()

    map_size = line[0].split()
    start = line[1].split()
    end = line[2].split()
    map_detail = []
    for mapData in line[3:]:
        map_detail.append(mapData.split())
    return map_size, start, end, map_detail


# Read file
def read_path(file_path):
    file = open(file_path, 'r')
    line = []
    for data in file:
        line.append(data)
    file.close()

    map_detail = []
    map_path = []
    for mapData in line:
        map_detail.append(mapData.split())
    for m in range(len(map_detail)):
        for n in range(len(map_detail[0])):
            if map_detail[m][n] == '*':
                tem_path = [m, n]
                map_path.append(tem_path)
    return map_path


# Get all frontier
def get_start(start, x, y, map_detail):
    start_suc = queue.Queue()
    if start[0] < x:
        if start[0] == 1:
            if start[1] < y:
                # X=1,Y=1
                if start[1] == 1:
                    start_suc.put([start[0] + 1, start[1]])
                    start_suc.put([start[0], start[1] + 1])
                # X=1, 1<Y<10
                else:
                    start_suc.put([start[0] + 1, start[1]])
                    start_suc.put([start[0], start[1] - 1])
                    start_suc.put([start[0], start[1] + 1])
            # X=1, Y=10
            else:
                start_suc.put([start[0] + 1, start[1]])
                start_suc.put([start[0], start[1] - 1])
        else:
            if start[1] < y:
                # 1<X<10, Y=1
                if start[1] == 1:
                    start_suc.put([start[0] - 1, start[1]])
                    start_suc.put([start[0] + 1, start[1]])
                    start_suc.put([start[0], start[1] + 1])

                # 1<X<10, 1<Y<10
                else:
                    start_suc.put([start[0] - 1, start[1]])
                    start_suc.put([start[0] + 1, start[1]])
                    start_suc.put([start[0], start[1] - 1])
                    start_suc.put([start[0], start[1] + 1])
            # 1<X<10, Y=10
            else:
                start_suc.put([start[0] - 1, start[1]])
                start_suc.put([start[0] + 1, start[1]])
                start_suc.put([start[0], start[1] - 1])
    else:
        if start[1] < y:
            # X=10,Y=1
            if start[1] == 1:
                start_suc.put([start[0] - 1, start[1]])
                start_suc.put([start[0], start[1] + 1])
            # X=10, 1<Y<10
            else:
                start_suc.put([start[0] - 1, start[1]])
                start_suc.put([start[0], start[1] - 1])
                start_suc.put([start[0], start[1] + 1])
        # X=10, Y=10
        else:
            start_suc.put([start[0] - 1, start[1]])
            start_suc.put([start[0], start[1] - 1])
    av_start = available(start_suc, map_detail)
    tem = []
    for q in av_start.queue:
        tem.append(q)
    random.shuffle(tem)
    tem.reverse()
    random_start = queue.Queue()
    for n in tem:
        random_start.put(n)
    return random_start


# Judge node is walls
def available(start_suc, map_detail):
    tem_frontier = queue.Queue()
    while not start_suc.empty():
        tem = start_suc.get()
        if map_detail[tem[0] - 1][tem[1] - 1] != 'X':
            tem_frontier.put(tem)
    return tem_frontier


# Node is in reached
def node_is_not_reached(frontier, reached):
    tem_frontier = queue.Queue()
    while not frontier.empty():
        tem = frontier.get()
        if tem not in reached:
            tem_frontier.put(tem)
    return tem_frontier


# Breadth-First Search
def bfs(start, end, map_detail, x, y, reached):
    node = [-1, -1]
    start = list(map(lambda s: s + 1, start))
    end = list(map(lambda s: s + 1, end))
    reached.append(start)
    if start == end:
        return start
    else:
        frontier = get_start(start, x, y, map_detail)
        solution = []
        while not frontier.empty():
            node = frontier.get()
            if node == end:
                break
            else:
                reached.append(node)
            tem_frontier = node_is_not_reached(get_start(node, x, y, map_detail), reached)
            asad = []
            for q in tem_frontier.queue:
                asad.append(q)
                frontier.put(q)
                reached.append(q)
            node_sub = [node, asad]
            solution.append(node_sub)

    if node != end:
        return None
    else:
        leng = len(solution)
        path_node = end
        sol_path = []
        # sol_path = [list(map(lambda s: s - 1, end))]
        for l1 in range(leng):
            if path_node in solution[leng - l1 - 1][1]:
                path_node = solution[leng - l1 - 1][0]
                tem_path_node = list(map(lambda s: s - 1, path_node))
                sol_path.append(tem_path_node)
        sol_path.append(list(map(lambda s: s - 1, start)))
        return sol_path


# Random local adjustment on path
def rand_local_adjust(ini_path, dis, map_detail, x, y):
    length = len(ini_path)
    n = random.randint(0, length - 1)
    start = ini_path[n]
    reached_node = []
    if n + dis > length - 1:
        end = ini_path[length - 1]
    else:
        end = ini_path[n + dis]
    b = ini_path.index(end)
    path_s = bfs(start, end, map_detail, x, y, reached_node)
    path_s.reverse()
    c = b - n
    for m in range(c):
        ini_path[n + m] = path_s[m]
    return ini_path


# Get cost
def get_cost(p, map_detail):
    length = len(p)
    cost = 0
    for m in range(1, length):
        node = p[m]
        pre_node = p[m - 1]
        num1 = int(map_detail[pre_node[0]][pre_node[1]])
        num2 = int(map_detail[node[0]][node[1]])
        if num2 > num1:
            num = 1 + num2 - num1
        else:
            num = 1
        cost = cost + num
    return cost


# Optimisation
def optimisation(ini_path, map_detail, x, y, t_ini, t_fin, a, dis):
    t = t_ini
    path_iii = ini_path.copy()
    cost_pre = get_cost(ini_path, map_detail)
    solution_ini = [t_ini, cost_pre]
    solution = [solution_ini]
    while t > t_fin:
        p = rand_local_adjust(ini_path, dis, map_detail, x, y)
        cost = get_cost(p, map_detail)
        d_cost = cost_pre - cost
        if d_cost > 0:
            ini_path = p
            cost_pre = cost
        else:
            e = math.exp(d_cost / t)
            r = math.exp((-2) / t)
            if r < e:
                ini_path = p
                cost_pre = cost
        t = t * a
        solution_ph = [t, cost_pre]
        solution.append(solution_ph)
    del solution[len(solution)-1]
    if solution[len(solution)-1][1] != 23:
        return optimisation(path_iii, map_detail, x, y, t_ini, t_fin, a, dis)
    else:
        return ini_path, solution


# Draw standard output
def draw(sol_path, map_detail):
    for n in range(len(sol_path)):
        x = sol_path[n][0]
        y = sol_path[n][1]
        map_detail[x][y] = '*'

    for u in range(len(map_detail)):
        for v in range(len(map_detail[0])):
            print(map_detail[u][v], end="")
            if v != len(map_detail[0]) - 1:
                print(' ', end='')
        print()


# main
# Get map information
filepath = sys.argv[1]
fileData = readfile(filepath)

size = fileData[0]
rows = int(size[0])
columns = int(size[1])

initial = fileData[1]
goal = fileData[2]
int_initial = []
int_goal = []
for i in range(len(initial)):
    int_initial.append(int(initial[i]))
    int_goal.append(int(goal[i]))
mapDetail = fileData[3]

# Get path
filepath = sys.argv[2]
path_Data = read_path(filepath)

tini = float(sys.argv[3])
tfin = float(sys.argv[4])
alpha = float(sys.argv[5])
d = int(sys.argv[6])

result = optimisation(path_Data, mapDetail, rows, columns, tini, tfin, alpha, d)
path = result[0]
draw(path, mapDetail)

t_cost = result[1]
for res in t_cost:
    print('T = %f, cost = %d' %(res[0], res[1]))
