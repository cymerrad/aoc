from collections import deque
from typing import *
from funktools import *
import numpy as np

import importlib

mod_9 = importlib.import_module("9")
Grid = mod_9.Grid


def parse(input: str, *args, **kwargs):
    return [line.split() for line in input.strip().split("\n")]


def solve_1(data, *args, debug=False, test=False, **kwargs) -> int:
    """
    20th, 60th, 100th, 140th, 180th, and 220th
    """
    thresholds = deque([20, 60, 100, 140, 180, 220])
    threshold_values = []
    cycle = 1
    rX = 1

    def do_during_cycles():
        if len(thresholds) and cycle == thresholds[0]:
            t = thresholds.popleft()
            signal_value = t * rX
            print(f"{t=} {rX=}")
            threshold_values.append((t, signal_value))

        # 6 x 40
        hor_pos = (cycle - 1) % 240
        crt_pos = (hor_pos // 40, hor_pos)

    for instr, *val in data:
        if instr == "addx":
            do_during_cycles()
            cycle += 1
            do_during_cycles()
            rX += int(val[0])
            cycle += 1
        elif instr == "noop":
            do_during_cycles()
            cycle += 1

    res = reduce(add, map(lambda x: x[1], threshold_values), 0)
    print(res)

    return res


def solve_2(data, *args, debug=False, test=False, **kwargs) -> int:
    cycle = 1
    rx = 1

    M = 6
    N = 40
    PIXELS = M * N
    screen = np.repeat(".", PIXELS).reshape((M, N))

    def do_during_cycles():
        # 6 x 40
        off = (cycle - 1) % PIXELS
        crt_pos = (off // N, off % N)

        sprite_pixels = [rx - 1, rx, rx + 1]
        if crt_pos[1] in sprite_pixels:
            screen[crt_pos] = "#"

    for instr, *val in data:
        if instr == "addx":
            do_during_cycles()
            cycle += 1
            do_during_cycles()
            rx += int(val[0])
            cycle += 1
        elif instr == "noop":
            do_during_cycles()
            cycle += 1

    return Grid.arr_to_str(screen).strip()


def test(*args, debug=False, test=False, **kwargs):
    raise NotImplementedError


TEST_INPUT = """
addx 15
addx -11
addx 6
addx -3
addx 5
addx -1
addx -8
addx 13
addx 4
noop
addx -1
addx 5
addx -1
addx 5
addx -1
addx 5
addx -1
addx 5
addx -1
addx -35
addx 1
addx 24
addx -19
addx 1
addx 16
addx -11
noop
noop
addx 21
addx -15
noop
noop
addx -3
addx 9
addx 1
addx -3
addx 8
addx 1
addx 5
noop
noop
noop
noop
noop
addx -36
noop
addx 1
addx 7
noop
noop
noop
addx 2
addx 6
noop
noop
noop
noop
noop
addx 1
noop
noop
addx 7
addx 1
noop
addx -13
addx 13
addx 7
noop
addx 1
addx -33
noop
noop
noop
addx 2
noop
noop
noop
addx 8
noop
addx -1
addx 2
addx 1
noop
addx 17
addx -9
addx 1
addx 1
addx -3
addx 11
noop
noop
addx 1
noop
addx 1
noop
noop
addx -13
addx -19
addx 1
addx 3
addx 26
addx -30
addx 12
addx -1
addx 3
addx 1
noop
noop
noop
addx -9
addx 18
addx 1
addx 2
noop
noop
addx 9
noop
noop
noop
addx -1
addx 2
addx -37
addx 1
addx 3
noop
addx 15
addx -21
addx 22
addx -6
addx 1
noop
addx 2
addx 1
noop
addx -10
noop
noop
addx 20
addx 1
addx 2
addx 2
addx -6
addx -11
noop
noop
noop
"""

TEST_RESULT_1 = 13140
TEST_RESULT_2 = """
##..##..##..##..##..##..##..##..##..##..
###...###...###...###...###...###...###.
####....####....####....####....####....
#####.....#####.....#####.....#####.....
######......######......######......####
#######.......#######.......#######.....
""".strip()
