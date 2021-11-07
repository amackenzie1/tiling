import numpy as np
from collections import Counter 

sets = [["S", "S", "J", "J"], 
        ['Z', 'Z', "L", "L"], 
        ["I", "I", "I", "I"],
        ["O", "O", "O", "O"],
        ["T", "T", "T", "T"],
        ["J", "J", "L", "L"],
        ["T", "T", "S", "J"],
        ["T", "T", "Z", "L"],
        ["O", "O", "I", "I"],
        ["O", "O", "L", "L"],
        ["O", "O", "J", "J"],
        ["O", "J", "L", "I"],
        ["T", "T", "J", "S", "S", "S", "S", "S", "S"],
        ["T", "T", "L", "S", "S", "S", "S", "S", "S"],
        ["S", "S", "S", "S", "S", "S", "Z", "J", "L"],
        ["Z", "Z", "Z", "Z", "Z", "Z", "S", "J", "L"]]

mapping = {
    "S": 0,
    "Z": 1,
    "I": 2,
    "O": 3,
    "J": 4,
    "L": 5,
    "T": 6
}

inverse = {j : i for i, j in mapping.items()}

def to_array(square):
    square = Counter(square)
    array = []
    for i in mapping:
        if i in square:
            array.append(square[i])
        else:
            array.append(0)
    return np.array(array)


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

    if dist[3] >= 4:
        dist -= np.array([0, 0, 0, 4, 0, 0, 0])
        return dist
    if dist[4] >= 4:
        dist -= np.array([0, 0, 0, 0, 4, 0, 0])
        return dist
    if dist[5] >= 4:
        dist -= np.array([0, 0, 0, 0, 0, 4, 0])
        return dist 

    if min(dist[3], dist[4], dist[5]) == dist[3] and dist[4] >= 2 and dist[5] >= 2:
        dist -= np.array([0, 0, 0, 0, 2, 2, 0])
        return dist
    if min(dist[3], dist[4], dist[5]) == dist[4] and dist[3] >= 2 and dist[5] >= 2:
        dist -= np.array([0, 0, 0, 2, 0, 2, 0])
        return dist
    if min(dist[3], dist[4], dist[5]) == dist[5] and dist[4] >= 2 and dist[3] >= 2:
        dist -= np.array([0, 0, 0, 2, 2, 0, 0])
        return dist

    if dist[6] >= 4:
        dist -= np.array([0, 0, 0, 0, 0, 0, 4])
    
    if dist[2] >= 4:
        dist -= np.array([0, 0, 4, 0, 0, 0, 0])
    return dist


array = []
for i in sets:
    array.append(to_array(i))
print(np.array(array))

sums = []
for j in range(100):
    dist = np.random.multinomial(256, [1/7]*7)

    for i in range(100):
        dist = lessen(dist)

    if sum(dist) > 9:
        pieces = []
        for i in range(len(dist)):
            pieces += [inverse[i]] * dist[i]
        print(pieces)