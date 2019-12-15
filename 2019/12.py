import numpy as np
import re
from itertools import combinations
import time

triangle_re = re.compile(r"<x=(-?\d+), y=(-?\d+), z=(-?\d+)>")
test_line = "<x=-0, y=0, z=000000000>"


def parse_input_data(data: str):
    finds = triangle_re.findall(data)
    return [np.array([int(s) for s in tpl]) for tpl in finds]


def uglify_arr(arr):
    return "<x={}, y={}, z={}>".format(*arr)


def apply_gravity(positions, velocities):
    for c1, c2 in combinations(range(len(positions)), 2):
        p1, v1 = positions[c1], velocities[c1]
        p2, v2 = positions[c2], velocities[c2]

        for pos in range(3):
            change = 0
            if p1[pos] != p2[pos]:
                change = 1 if p1[pos] < p2[pos] else -1  # move closer together
            v1[pos] += change
            v2[pos] += -change


def apply_velocity(positions, velocities):
    # for i in range(len(positions)):
    #     positions[i] += velocities
    for p, v in zip(positions, velocities):
        p += v


def total_energy(positions, velocities):
    return sum([
        potential * kinetic for potential, kinetic in (
            (sum((abs(u) for u in pos)),
             sum((abs(u) for u in vel)))
            for pos, vel in zip(positions, velocities)
        )
    ])


def step_repr(step, positions, velocities):
    return f"After {step} steps:\n" + \
        "\n".join([
            "pos={}, vel={}".format(
                  uglify_arr(pos),
                  uglify_arr(vel)
                  ) for pos, vel in zip(positions, velocities)
        ])


def simulate_system(data, goal=1000, last=1, debug=False):
    positions = parse_input_data(data)
    velocities = [np.array([0, 0, 0]) for _ in range(len(positions))]

    step = 0
    # milestone_size = 2**16
    while step < goal + 1:
        if debug and step > goal - last:
            printout = step_repr(step, positions, velocities)
            print(printout)

            total_en = total_energy(positions, velocities)
            print(f"Energy: {total_en}")
        apply_gravity(positions, velocities)
        apply_velocity(positions, velocities)

        step += 1
        # input()
        # if step > goal / milestone_size:
        #     milestone_size /= 2
        #     print(f"{step}/{goal}")

    return positions, velocities


with open("input12") as fr:
    actual_data = fr.read().strip()


def part1():
    pos_vel = simulate_system(actual_data, 1000)
    printout = step_repr(1000, *pos_vel)
    total_en = total_energy(*pos_vel)
    print(printout)
    print(f"Energy: {total_en}")


def parse_input_data_into_matrix(data: str):
    ll = parse_input_data(data)
    return np.array(ll)


def compare_update(source, target):
    for i in range(4):
        for j in range(i+1, 4):
            diff = np.sign(source[i] - source[j])
            target[i] -= diff
            target[j] += diff
    source += target

# def step_func(positions, velocities):
#     for d in range(3):
#         compare_update(positions[:,d], velocities[:,d])

def part2():
    positions = parse_input_data_into_matrix(actual_data)
    velocities = np.zeros_like(positions)

    steps_per_dimension = []

    for d in range(3):
        pos = positions[:,d]
        vel = velocities[:,d]
        p_copy = np.copy(pos)
        v_copy = np.copy(vel)

        step = 0
        while True:
            compare_update(pos, vel)
            step += 1

            if np.array_equal(p_copy, pos) and np.array_equal(v_copy, vel):
                break

        steps_per_dimension.append(step)

    return np.lcm.reduce(steps_per_dimension)

test_data_1 = '''<x=-1, y=0, z=2>
<x=2, y=-10, z=-7>
<x=4, y=-8, z=8>
<x=3, y=5, z=-1>'''

test_data_2 = '''<x=-8, y=-10, z=0>
<x=5, y=5, z=10>
<x=2, y=-7, z=3>
<x=9, y=-8, z=-3>'''

actual_output = '''After 1000 steps:
pos=<x=-11, y=65, z=38>, vel=<x=8, y=-1, z=-1>
pos=<x=-43, y=-60, z=8>, vel=<x=6, y=-14, z=10>
pos=<x=102, y=29, z=24>, vel=<x=-19, y=-1, z=-4>
pos=<x=-55, y=12, z=-103>, vel=<x=5, y=16, z=-5>'''

test_output_1 = '''After 1000 steps:
pos=<x=-1, y=-7, z=-3>, vel=<x=-3, y=-5, z=-4>
pos=<x=3, y=0, z=0>, vel=<x=2, y=4, z=-4>
pos=<x=3, y=-2, z=1>, vel=<x=0, y=5, z=4>
pos=<x=3, y=-4, z=4>, vel=<x=1, y=-4, z=4>'''

test_output_2 = '''After 1000 steps:
pos=<x=-23, y=59, z=-22>, vel=<x=3, y=14, z=9>
pos=<x=70, y=9, z=-4>, vel=<x=-17, y=-14, z=8>
pos=<x=-32, y=-16, z=-28>, vel=<x=1, y=-14, z=-4>
pos=<x=-7, y=-72, z=64>, vel=<x=13, y=14, z=-13>'''


def sanity_check():
    for data, expected in [(actual_data, actual_output), (test_data_1, test_output_1), (test_data_2, test_output_2)]:
        assert step_repr(1000, *simulate_system(data, 1000)
                         ).strip() == expected


lol = part2()