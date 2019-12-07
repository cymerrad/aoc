

with open("input6") as fr:
    orbit_data = [line for line in fr.read().strip().split("\n")]

test_data = '''COM)B
B)C
C)D
D)E
E)F
B)G
G)H
D)I
E)J
J)K
K)L'''.split("\n")


class Node():
    def __init__(self, tag, *children):
        self.tag = tag
        self.children = list(children)

    def is_leaf(self):
        return len(self.children) == 0


_STARTING_POINT = "COM"


def parse_data(data: list):
    def split(s: str):
        return s.split(")")
    orbits = {}
    for orb_center, orbiter in (split(s) for s in data):
        try:
            orbits[orb_center].append(orbiter)
        except KeyError:
            orbits[orb_center] = [orbiter]

    return orbits


def construct_graph(data_d: dict):
    def constr_rec(data_d: dict, orb_center: str):
        try:
            if data_d[orb_center]:
                children = [constr_rec(data_d, tag)
                            for tag in data_d[orb_center]]
                return Node(orb_center, *children)
        except KeyError:
            return Node(orb_center)
    return constr_rec(data_d, _STARTING_POINT)


def count_orbits_rec(node: Node, level=0):
    if node.is_leaf():
        return level
    return level + sum((count_orbits_rec(child, level+1) for child in node.children))


test_graph = construct_graph(parse_data(test_data))
assert count_orbits_rec(test_graph) == 42
task_graph = construct_graph(parse_data(orbit_data))
assert count_orbits_rec(task_graph) == 453028

test_orbital_data = '''COM)B
B)C
C)D
D)E
E)F
B)G
G)H
D)I
E)J
J)K
K)L
K)YOU
I)SAN'''.split("\n")
test_orbital_graph = construct_graph(parse_data(test_orbital_data))


def send_probe(node: Node, search_for: str):
    if search_for in (n.tag for n in node.children):
        return [node.tag]
    probes = (send_probe(child, search_for) for child in node.children)
    successful = list(filter(None, probes))
    if successful:
        copy = list(successful[0])
        copy.append(node.tag)
        return copy
    return []


def longest_suffix(chain1: list, chain2: list):
    chain1.reverse()
    chain2.reverse()
    count = 0
    for c1, c2 in zip(chain1, chain2):
        if c1 == c2:
            count += 1
            continue
        else:
            break
    return count


def count_orbital_hops(graph: Node):
    you = send_probe(graph, "YOU")
    san = send_probe(graph, "SAN")
    divergence_level = longest_suffix(you, san)
    return (len(you) - divergence_level) + (len(san) - divergence_level)


assert count_orbital_hops(test_orbital_graph) == 4
answer = count_orbital_hops(task_graph)
assert answer == 562
