import math
import numpy as np
from collections import UserList

with open("input10") as fr:
    task_data = fr.read().strip()


class ListOnlyPositive(UserList):
    def __init__(self, *args):
        super().__init__(*args)

    def __getitem__(self, key):
        if key < 0:
            raise IndexError
        return super().__getitem__(key)


test_data_01 = '''\n
#...#
.....
..#..
.....
#...#'''
test_ans_01 = (2, 2, 4)

test_data_1 = '''......#.#.
#..#.#....
..#######.
.#.#.###..
.#..#.....
..#....#.#
#..#....#.
.##.#..###
##...#..#.
.#....####
'''
test_ans_1 = (5, 8, 33)

test_data_2 = '''#.#...#.#.
.###....#.
.#....#...
##.#.#.#.#
....#.#.#.
.##..###.#
..#...##..
..##....##
......#...
.####.###.
'''
test_ans_2 = (1, 2, 35)

test_data_3 = '''.#..#..###
####.###.#
....###.#.
..###.##.#
##.##.#.#.
....###..#
..#.#..#.#
#..#.#.###
.##...##.#
.....#.#..
'''
test_ans_3 = (6, 3, 41)

test_data_4 = '''.#..##.###...#######
##.############..##.
.#.######.########.#
.###.#######.####.#.
#####.##.#.##.###.##
..#####..#.#########
####################
#.####....###.#.#.##
##.#################
#####.##.###..####..
..######..##.#######
####.##.####...##..#
.#####..#.######.###
##...#.##########...
#.##########.#######
.####.#.###.###.#.##
....##.##.###..#####
.#.#.###########.###
#.#.#.#####.####.###
###.##.####.##.#..##
'''
test_ans_4 = (11, 13, 210)

COMPASS_SIMPLE = {
    "N": (0, -1),
    "E": (1, 0),
    "S": (0, 1),
    "W": (-1, 0),
}

CLOCKWISE_ORDER = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]

# vvvvvvvvvvvvvv LOOOOOOOOOOOOL

# COMPASS_REV = {}
# _temp_comp = [(k, v) for k, v in COMPASS_SIMPLE.items()]
# for k,v in _temp_comp:
#     COMPASS_REV[v] = k
# for fst, snd in zip(_temp_comp, _temp_comp[1:] + [_temp_comp[0]]):
#     d = (fst[1][0] + snd[1][0], fst[1][1] + snd[1][1])
#     COMPASS_REV[d] = fst[0] + snd[0]
# for k, v in COMPASS_REV.items():
#     if v not in CLOCKWISE_ORDER:
#         _v = list(v)
#         _v.reverse()
#         _v_ = "".join(_v)
#         assert _v_ in CLOCKWISE_ORDER
#     COMPASS_REV[k] = v

COMPASS_REV = {
    (0, -1): 'N',
    (1, 0): 'E',
    (0, 1): 'S',
    (-1, 0): 'W',
    (1, -1): 'NE',
    (1, 1): 'SE',
    (-1, 1): 'SW',
    (-1, -1): 'NW',
}

COMPASS_DEGREES = {
    (0, -1): 0.0,
    (1, 0): 90.0,
    (0, 1): 180.0,
    (-1, 0): 270.0,
    (1, -1): 45.0,
    (1, 1): 135.0,
    (-1, 1): 225.0,
    (-1, -1): 315.0,
}
COMPASS_DEGREES_SORTED_LIST = [(k,v) for k,v in COMPASS_DEGREES.items()]
COMPASS_DEGREES_SORTED_LIST.sort(key=lambda x: x[1])
_pivot = COMPASS_DEGREES_SORTED_LIST.index(((0,-1), 0.0))
COMPASS_DEGREES_SORTED_LIST = COMPASS_DEGREES_SORTED_LIST[_pivot:] + COMPASS_DEGREES_SORTED_LIST[:_pivot]

COMPASS = {}
for k, v in COMPASS_REV.items():
    COMPASS[v] = k


SPACE = 0
ASTEROID = 1


def read_in_map(data: str):
    init_m = []
    for line in data.strip().split("\n"):
        init_m.append([ASTEROID if x == "#" else SPACE for x in line])

    transposed = ListOnlyPositive(
        [ListOnlyPositive(column) for column in zip(*init_m)])

    return transposed


def reduce_pair_gcd(pair):
    d = math.gcd(pair[0], pair[1])
    if d > 1:
        return (pair[0] // d, pair[1] // d)
    return pair


def angle(pair):
    # calculating angle from OY+, clockwise
    z = complex(pair[0], pair[1])
    ang_OX = np.angle(z, deg=True)
    i_seriously_fitted_the_transformation_to_data = ang_OX + 90.0
    return np.fmod(i_seriously_fitted_the_transformation_to_data + 360.0, 360.0)
    # return ang_OY_rev

for direction, asimuth in COMPASS_DEGREES_SORTED_LIST:
    # print(f"{direction} -> should be {asimuth} | real {np.angle(complex(*direction), deg=True)} | calculated {angle(direction)}")
    assert angle(direction) == asimuth, f"{direction} {asimuth}"

def get_all_lines_of_sight(m: list, pos_x: int, pos_y: int):
    width = len(m[0])
    height = len(m)
    # N E S W
    dist_rose = (pos_y, width-pos_x-1, height-pos_y-1, pos_x)

    lines = {}

    # TODO make them sorted

    # in quadrants
    for dx in [1, -1]:
        for dy in [-1, 1]:
            x_to = max(dx, dx * width)
            y_to = max(dy, dy * height)

            all_positions_relative = (
                (x-pos_x, y-pos_y) for x in range(pos_x+dx, x_to, dx) for y in range(pos_y+dy, y_to, dy))
            reduced = (reduce_pair_gcd(pair)
                       for pair in all_positions_relative)
            l_o_s = set(reduced)
            los_list = list(l_o_s)
            los_list.sort(key=lambda x: angle(x))
            lines[COMPASS_REV[(dx, dy)]] = los_list

    for lol in COMPASS_SIMPLE.values():
        lines[COMPASS_REV[lol]] = set([lol])

    return lines


def visible_on_los_from_point(m: list, los: dict, pos_x: int, pos_y: int):
    width = len(m[0])
    height = len(m)

    def look_for_asteroid(dir_x: int, dir_y: int):
        try:
            for i in range(1, max(width, height)):
                l_x = pos_x + i * dir_x
                l_y = pos_y + i * dir_y
                if m[l_x][l_y] == ASTEROID:
                    m[l_x][l_y] = 8
                    m[l_x][l_y] = ASTEROID
                    return True
            else:
                return False
        except IndexError:
            return False
        return False

    count_visible = 0
    for asimuth in CLOCKWISE_ORDER:
        directions = los[asimuth]
        for direction in directions:
            found = look_for_asteroid(direction[0], direction[1])
            if found:
                count_visible += 1

    return count_visible


def find_best_for_map(m: list):
    width = len(m[0])
    height = len(m)

    best = (0, 0, 0)
    for x in range(width):
        for y in range(height):
            if m[x][y] == ASTEROID:
                los = get_all_lines_of_sight(m, x, y)
                count = visible_on_los_from_point(m, los, x, y)
                if count > best[2]:
                    best = (x, y, count)

    return best


def calculate_crap(s: str):
    return find_best_for_map(read_in_map(s))


t_data = [x for x in locals().items() if x[0].startswith("test_data")]
t_anss = [x for x in locals().items() if x[0].startswith("test_ans")]
t_data.sort(key=lambda x: x[0])
t_anss.sort(key=lambda x: x[0])

for t_d, t_a in zip(t_data, t_anss):
    res = calculate_crap(t_d[1])
    assert res == t_a[1], f"Calcumalated {res} != expected {t_a[1]} for {t_d[0]}"


def part1():
    return calculate_crap(task_data)


best = part1()
assert best == (26, 36, 347)


def destroy_asteroids_in_order(m: list, pos_x: int, pos_y: int, goal=200):
    los = get_all_lines_of_sight(m, pos_x, pos_y)
    width = len(m[0])
    height = len(m)

    def shoot_at_direction(dir_x: int, dir_y: int):
        try:
            for i in range(1, max(width, height)):
                l_x = pos_x + i * dir_x
                l_y = pos_y + i * dir_y
                if m[l_x][l_y] == ASTEROID:
                    m[l_x][l_y] = 0
                    return (l_x, l_y)
            else:
                return False
        except IndexError:
            return False
        return False

    count_destroyed = 0
    for asimuth in CLOCKWISE_ORDER:
        directions = los[asimuth]
        for direction in directions:
            destroyed = shoot_at_direction(direction[0], direction[1])
            if destroyed:
                count_destroyed += 1
            if count_destroyed == goal:
                return destroyed

    return None


test_result_longest = (11,13,210)
trl_200th = destroy_asteroids_in_order(read_in_map(test_data_4),
                                  test_result_longest[0],
                                  test_result_longest[1])
assert trl_200th == (8,2), trl_200th

def part2():
    m = read_in_map(task_data)
    return destroy_asteroids_in_order(m, best[0], best[1])

kurwa_mać = part2()

assert kurwa_mać == (8,29)
