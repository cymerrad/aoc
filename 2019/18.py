from typing import Dict
from collections import defaultdict
from math import inf

class Node:
    def __init__(self, value: str, n_pos: complex, *nodes: 'Node'):
        self.value = value
        self.n_pos = n_pos
        self.neighbours = set()
        for n in nodes:
            n.add_neighbour(self)
            self.add_neighbour(n)

        self.visited = False
        self.processed = False

    def add_neighbour(self, node):
        self.neighbours.add(node)


    def zero(self):
        self.visited = False
        self.processed = False
        self.distance = inf

class IS_A:
    def WALL(x): return x == "#"
    def PASSAGE(x): return x == "."
    def ENTRANCE(x): return x == "@"
    def KEY(x): return 97 <= ord(x) <= 122
    def DOOR(x): return 65 <= ord(x) <= 90


class DIR:
    UP = -1j
    LEFT = -1
    RIGHT = 1
    DOWN = 1j


def parse_data(data: str) -> Dict[complex, Node]:
    nodes_holder = defaultdict(lambda: None)
    entrance = None
    doors = 0
    dmap = data.strip().split("\n")
    for i in range(len(dmap)):
        for j in range(len(dmap[0])):
            block = dmap[i][j]
            if not IS_A.WALL(block):
                val = None
                n_pos = complex(i, j)
                if IS_A.KEY(block) or IS_A.DOOR(block) or IS_A.PASSAGE(block):
                    val = block
                    if IS_A.DOOR(block):
                        doors += 1
                if IS_A.ENTRANCE(block):
                    entrance = n_pos
                    val = "."

                possible_neighs = list(filter(None, (nodes_holder[n] for n in [
                    n_pos + DIR.UP, n_pos+DIR.LEFT])))

                n = Node(val, n_pos, *possible_neighs)
                nodes_holder[n_pos] = n

    return (nodes_holder, entrance, doors)


def dijkstra(nodes: Dict[complex, Node], start: complex, end: complex) -> int:
    pass


def solve_crap(nodes: Dict[complex, Node], entrance: complex, doors_no: int):
    pass


def part1():
    nodes, entrance, doors_no = parse_data(test_data[0][0])
    result = solve_crap(nodes, entrance, doors_no)


with open("input18") as fr:
    actual_data = fr.read().strip()

test_data = [("""########################
#...............b.C.D.f#
#.######################
#.....@.a.B.c.d.A.e.F.g#
########################""", 132, "bacdfeg"),
             ("""#################
#i.G..c...e..H.p#
########.########
#j.A..b...f..D.o#
########@########
#k.E..a...g..B.n#
########.########
#l.F..d...h..C.m#
#################""", 136, "afbjgnhdloepcikm"),
             ("""########################
#@..............ac.GI.b#
###d#e#f################
###A#B#C################
###g#h#i################
########################""", 81, "acfidgbeh")
             ]
