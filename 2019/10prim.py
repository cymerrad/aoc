import numpy as np
from itertools import permutations, cycle

def angle(z: complex):
    # calculating angle from OY+, clockwise
    return np.fmod(np.angle(z, deg=True) + 450.0, 360.0)

def order_by_argument_then_modulus(z: complex):
    return (angle(z), abs(z))

def order_in_spiral(central_asteroid: complex, asteroids: list) -> (list, dict):
    asteroid_vectors = [asteroid - central_asteroid for asteroid in asteroids if asteroid != central_asteroid]

    asteroid_vectors.sort(key=order_by_argument_then_modulus)
    strates = dict()
    arguments_ordered = []
    for asteroid in asteroid_vectors:
        ang = angle(asteroid)
        try:
            strates[ang].append(asteroid)
        except KeyError:
            strates[ang] = [asteroid]
            arguments_ordered.append(ang)

    return arguments_ordered, strates

SPACE = 0
ASTEROID = 1
def extract_asteroids(data: str):
    asteroid_map_transposed = [[ASTEROID if x == "#" else SPACE for x in line] for line in data.strip().split("\n")]
    asteroid_map = [list(column) for column in zip(*asteroid_map_transposed)]
    asteroids = [complex(x,y) for x,row in enumerate(asteroid_map) for y,field in enumerate(row) if field == ASTEROID]
    return asteroids

def part1(data: str):
    asteroids = extract_asteroids(data)

    best = (0,0,0)
    for central_asteroid in asteroids:
        arguments_ord, _ = order_in_spiral(central_asteroid, asteroids)

        one_turn_len = len(arguments_ord)

        if one_turn_len > best[2]:
            best = (int(central_asteroid.real), int(central_asteroid.imag), one_turn_len)
    return best

def part2(data: str):
    asteroids = extract_asteroids(data)
    best = part1(data)

    counter, goal, result = 0, 200, 0j
    central_asteroid = complex(best[0], best[1])
    arguments_ord, strates = order_in_spiral(central_asteroid, asteroids)
    for asimuth in cycle(arguments_ord):
        try:
            in_sight = strates[asimuth]
            result, in_sight = in_sight[0], in_sight[1:]
            strates[asimuth] = in_sight
            counter += 1
            if counter == goal:
                goalth = result + central_asteroid
                return (int(goalth.real), int(goalth.imag))
        except IndexError:
            continue
    else:
        raise Exception(f"There were less than {goal} asteroids.")

    return


with open("input10") as fr:
    task_data = fr.read().strip()

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

def check_for_rounding_errors():
    for p,q in permutations([1,2,3,4,5,6,7,9,10,11,12,13,14,15,16,17,18,19,20,21], 2):
        if np.gcd(p,q) == 1:
            for mult in range(2,8):
                for x, y in [(p,q), (-p,q), (p,-q), (-p,-q)]:
                    source = complex(x, y)
                    source_ang = angle(source)
                    assert source_ang == angle(mult * source), f"{source} -> {mult * source}"

def check_correctness_part1():
    t_data = [x for x in globals().items() if x[0].startswith("test_data")]
    t_anss = [x for x in globals().items() if x[0].startswith("test_ans")]
    t_data.sort(key=lambda x: x[0])
    t_anss.sort(key=lambda x: x[0])

    for t_d, t_a in zip(t_data, t_anss):
        res = part1(t_d[1])
        assert res == t_a[1], f"Calcumalated {res} != expected {t_a[1]} for {t_d[0]}"

    assert part1(task_data) == (26,36,347)

def check_correctness_part2():
    result = part2(task_data)
    assert result == (8,29), f"Got {result}"
