#!/usr/bin/env python3
import queue
import sys


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


# Get search algorithm
def algorithm(search_alg):
    if search_alg == 'bfs':
        return 1
    elif search_alg == 'ucs':
        return 2
    elif search_alg == 'astar':
        return 3


# Get A star heuristic
def heuristic(heu):
    if heu == 'euclidean':
        return 0
    elif heu == 'manhattan':
        return 1


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
    return av_start


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
        sol_path = [end]
        for l in range(leng):
            if path_node in solution[leng - l - 1][1]:
                path_node = solution[leng - l - 1][0]
                sol_path.append(path_node)
        sol_path.append(start)
        return sol_path


# Get ucs cost of node
def ucs_process_frontier(start, frontier, map_detail):
    tem_frontier = []
    start_child = []
    for f in frontier.queue:
        tem = [f]
        start_child.append(f)
        num1 = int(map_detail[start[0][0] - 1][start[0][1] - 1])
        num2 = int(map_detail[f[0]-1][f[1]-1])
        if num2 > num1:
            num2 = 1 + num2 - num1
        else:
            num2 = 1
        num = start[1] + num2
        tem.append(num)
        tem_frontier.append(tem)
    tem_frontier = rank_cost(tem_frontier)
    start_child_s = [start[0], start_child]
    return tem_frontier, start_child_s


# Sorting
def rank_cost(frontier):
    for length in range(len(frontier)-1):
        for m in range(len(frontier)-1-length):
            if frontier[m][1] > frontier[m+1][1]:
                tem = frontier[m]
                frontier[m] = frontier[m+1]
                frontier[m + 1] = tem
    return frontier


# Get less cost frontier
def get_less_cost_frontier(tem_frontier_1, tem_frontier, solution_path):
    tem = []
    for t in tem_frontier:
        tem.append(t[0])
    for f in tem_frontier_1:
        if f[0] in tem:
            index = tem.index(f[0])
            if f[1] < tem_frontier[index][1]:
                tem_frontier[index] = f
                for g in range(len(solution_path)-1):
                    if f[0] in solution_path[g][1]:
                        solution_path[g][1].remove(f[0])
                        break
            else:
                solution_path[len(solution_path)-1][1].remove(f[0])
        else:
            tem_frontier.append(f)
    tem_frontier = rank_cost(tem_frontier)
    return tem_frontier, solution_path


# Uniform-Cost Search
def ucs(start, end, map_detail, x, y, reached):
    node_p = [-1, -1]
    solution_path = []
    if start == end:
        return start
    else:
        tem_start = [start, 0]
        frontier = get_start(start, x, y, map_detail)
        tem_frontier_r = ucs_process_frontier(tem_start, frontier, map_detail)
        tem_frontier = tem_frontier_r[0]
        solution = tem_frontier_r[1]
        solution_path.append(solution)
        while len(tem_frontier) != 0:
            node = tem_frontier[0]
            tem_frontier.pop(0)
            if node[0] == end:
                node_p = node[0]
                break
            else:
                reached.append(node[0])
                frontier = node_is_not_reached(get_start(node[0], x, y, map_detail), reached)
                tem_frontier_t = ucs_process_frontier(node, frontier, map_detail)
                tem_frontier_1 = tem_frontier_t[0]
                solution_path.append(tem_frontier_t[1])
                tem_less = get_less_cost_frontier(tem_frontier_1, tem_frontier, solution_path)
                tem_frontier = tem_less[0]
                solution_path = tem_less[1]

        if node_p != end:
            return None
        else:
            length = len(solution_path)
            path_node = end
            sol_path = [end]
            for ln in range(length):
                if path_node in solution_path[length - ln - 1][1]:
                    path_node = solution_path[length - ln - 1][0]
                    sol_path.append(path_node)
            return sol_path


# Euclidean distance
def euclidean(start, end):
    x = (end[0]-1) - (start[0]-1)
    y = (end[1]-1) - (start[1]-1)
    distance = x ** 2 + y ** 2
    return distance ** 0.5


# Manhattan distance
def manhattan(start, end):
    x = end[0] - start[0]
    y = end[1] - start[1]
    distance = abs(x) + abs(y)
    return distance


# Get astar cost of node
def astar_process_frontier(start, frontier, map_detail, heu, end):
    tem_frontier = []
    start_child = []
    for f in frontier.queue:
        tem = [f]
        start_child.append(f)
        num1 = int(map_detail[start[0][0] - 1][start[0][1] - 1])
        num2 = int(map_detail[f[0] - 1][f[1] - 1])
        if num2 > num1:
            num2 = 1 + num2 - num1
        else:
            num2 = 1
        if heu == 0:
            distance = euclidean(f, end)
        else:
            distance = manhattan(f, end)
        num = start[2] + num2
        distance = num + distance
        tem.append(distance)
        tem.append(num)
        tem_frontier.append(tem)
    tem_frontier = rank_cost(tem_frontier)
    start_child_s = [start[0], start_child]
    return tem_frontier, start_child_s


# A* Search
def astar(start, end, map_detail, x, y, reached, heu):
    node_p = [-1, -1]
    solution_path = []
    if start == end:
        return start
    else:
        tem_start = [start, 0, 0]
        frontier = get_start(start, x, y, map_detail)
        tem_frontier_r = astar_process_frontier(tem_start, frontier, map_detail, heu, end)
        tem_frontier = tem_frontier_r[0]
        solution = tem_frontier_r[1]
        solution_path.append(solution)
        while len(tem_frontier) != 0:
            node = tem_frontier[0]
            tem_frontier.pop(0)
            if node[0] == end:
                node_p = node[0]
                break
            else:
                reached.append(node[0])
                frontier = node_is_not_reached(get_start(node[0], x, y, map_detail), reached)
                tem_frontier_t = astar_process_frontier(node, frontier, map_detail, heu, end)
                tem_frontier_1 = tem_frontier_t[0]
                solution_path.append(tem_frontier_t[1])
                tem_less = get_less_cost_frontier(tem_frontier_1, tem_frontier, solution_path)
                tem_frontier = tem_less[0]
                solution_path = tem_less[1]

        if node_p != end:
            return None
        else:
            length = len(solution_path)
            path_node = end
            sol_path = [end]
            for ln in range(length):
                if path_node in solution_path[length - ln - 1][1]:
                    path_node = solution_path[length - ln - 1][0]
                    sol_path.append(path_node)
            return sol_path


def draw(sol_path, map_detail):
    for n in range(len(sol_path)):
        x = sol_path[n][0]
        y = sol_path[n][1]
        map_detail[x-1][y-1] = '*'

    for u in range(len(map_detail)):
        for v in range(len(map_detail[0])):
            print(map_detail[u][v], end="")
            if v != len(map_detail[0])-1:
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


# Get algorithm
alg = algorithm(sys.argv[2])
path = []

reached_node = [int_initial]

if alg == 1:
    path = bfs(int_initial, int_goal, mapDetail, rows, columns, reached_node)
elif alg == 2:
    path = ucs(int_initial, int_goal, mapDetail, rows, columns, reached_node)
elif alg == 3:
    h = heuristic(sys.argv[3])
    path = astar(int_initial, int_goal, mapDetail, rows, columns, reached_node, h)

if path is not None:
    draw(path, mapDetail)
else:
    print('null')
