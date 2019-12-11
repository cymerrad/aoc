from intcode import Intcode
from collections import defaultdict
import numpy as np

with open("input11") as fr:
    task_data = fr.read().strip()

BLACK = 0
WHITE = 1

LEFT = 1j
RIGHT = -1j


def run_robot(panels):
    state = (complex(0, 0), complex(0, 1))

    def update_state(state, turn):
        new_dir = state[1] * turn
        return (state[0] + new_dir, new_dir)

    robot = Intcode(task_data)

    while robot.running:
        color_underneath = panels[state[0]]

        robot.put(color_underneath)
        color_to_paint = robot.get()
        direction = robot.get()

        turn = LEFT if direction == 0 else RIGHT

        panels[state[0]] = color_to_paint
        state = update_state(state, turn)

    return panels


def part1():
    panels = run_robot(defaultdict(int))
    return len(list(panels.keys()))


def paint_a_picture(data: dict):
    positions = list(data.keys())
    def real_part(z): return z.real
    def imag_part(z): return z.imag
    max_x, min_x, max_y, min_y = (max(positions, key=real_part).real,
                                  min(positions, key=real_part).real,
                                  max(positions, key=imag_part).imag,
                                  min(positions, key=imag_part).imag)
    normalizator = complex(-min_x, -min_y)

    fixed = defaultdict(int)
    for k,v in data.items():
        fixed[k + normalizator] = v

    dimensionz = complex(max_x, max_y) + normalizator
    width, height = int(dimensionz.real), int(dimensionz.imag)

    wut = [[0 for _ in range(width+1)] for _ in range(height+1)]
    for row in range(height+1):
        for column in range(width+1):
            addr = complex(column, row)
            wut[row][column] = fixed[addr]
    wut.reverse()

    with open("outpu11", "w") as fw:
        prettied = ["".join([" " if x == 0 else "#" for x in line]) + "\n" for line in wut]
        fw.writelines(prettied)

    return wut


def part2():
    start = defaultdict(int)
    start[complex(0, 0)] = WHITE
    panels = run_robot(start)
    return paint_a_picture(panels)
