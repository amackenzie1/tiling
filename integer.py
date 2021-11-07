import numpy as np
from collections import Counter 
from mip import * 

sets = [["S", "S", "J", "J"], 
        ['Z', 'Z', "L", "L"], 
        ["I", "I", "I", "I"],
        ["O", "O", "O", "O"],
        ["I", "I", "L", "L"],
        ["I", "I", "J", "J"],
        ["O", "O", "L", "L"],
        ["O", "O", "J", "J"],
        ["J", "J", "J", "J"],
        ["L", "L", "L", "L"],
        ["T", "T", "T", "T"],
        ["J", "J", "L", "L"],
        ["T", "T", "S", "J"],
        ["T", "T", "Z", "L"],
        ["O", "O", "I", "I"],
        ["O", "O", "L", "L"],
        ["O", "O", "J", "J"],
        ["O", "J", "L", "I"],
        ["T", "T", "J", "S", "S", "S", "S", "S"],
        ["T", "T", "L", "Z", "Z", "Z", "Z", "Z"],
        ["S", "S", "S", "S", "S", "S", "J", "J"],
        ["Z", "Z", "Z", "Z", "Z", "Z", "L", "L"],
        ['I', "I", "I", "T", "T", "T", "T", "Z"],
        ['I', "I", "I", "T", "T", "T", "T", "S"]]

def get_sets():
    return sets 

mapping = {
    "S": 0,
    "Z": 1,
    "I": 2,
    "O": 3,
    "J": 4,
    "L": 5,
    "T": 6
}

def to_array(square):
    square = Counter(square)
    array = []
    for i in mapping:
        if i in square:
            array.append(square[i])
        else:
            array.append(0)
    return array


def lessen(dist):
    if max(dist[1], dist[0]) >= 6:
        if dist[0] >= dist[1]:
            if dist[0] >= 6 and dist[1] >= 1:
                dist -= [6, 1, 0, 0, 1, 1, 0]
        else:
            if dist[1] >= 6 and dist[0] >= 1:
                dist -= [1, 6, 0, 0, 1, 1, 0]
        return dist 

    if dist[0] != 0:
        dist -= np.array([1, 0, 0, 0, 1, 0, 2])
        return dist 
    if dist[1] != 0:
        dist -= np.array([0, 1, 0, 0, 0, 1, 2])
        return dist 
    
    return dist 


array = []
for i in sets:
    array.append(to_array(i))
array = np.array(array).T


def integer(pieces):
    c = Counter(pieces)
    dist = []
    for i in mapping:
        if i in c:
            dist.append(c[i])
        else:
            dist.append(0)
    dist = np.array(dist) 

    m = Model()
    x = [m.add_var(var_type=INTEGER, lb=0, ub=200) for i in range(len(sets))]

    for i in range(7):
        m += xsum(array[i][j] * x[j] for j in range(len(sets))) <= dist[i]

    m.objective = maximize(xsum(x[i]*len(sets[i]) for i in range(len(sets))))
    status = m.optimize(max_seconds=0.1)

    if status in [OptimizationStatus.OPTIMAL, OptimizationStatus.FEASIBLE]:
        return [(i, v.x) for i, v in zip(sets, m.vars) if v.x != 0]