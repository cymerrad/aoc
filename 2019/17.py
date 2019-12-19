from intcode import Intcode
from random import randint
from queue import Queue
from collections import defaultdict


def pretty_map(data: dict):
    max_x, max_y = (
        max(data.keys(), key=lambda z: abs(z.real)).real,
        max(data.keys(), key=lambda z: abs(z.imag)).imag,
    )
    max_x, max_y = int(abs(max_x)), int(abs(max_y))
    width, height = max_x * 2 + 1, max_y * 2 + 1

    picture = ""
    for x in range(-max_x, max_x + 1):
        line = []
        for y in range(max_y, -max_y - 1, -1):
            val = data[complex(x, y)]
            glyph = str(val) if val else UNKNOWN
            if type(val) == int:
                if val <= 15:
                    glyph = hex(val)[2:]
                else:
                    glyph = "X"
            line.append(glyph if glyph else UNKNOWN)
        picture += "".join(line) + "\n"

    return picture


def pretty_map(data: list):
    return "".join([chr(n) for n in data])


WALKWAY = "#"


def find_crossings(data: str):
    split = data.strip().split("\n")
    crossings = []

    def is_crossing(i, j):
        if split[i][j] != WALKWAY:
            return False
        for vi, vj in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
            if split[i + vi][j + vj] != WALKWAY:
                return False
        return True

    for i in range(1, len(split) - 1):
        for j in range(1, len(split[0]) - 1):
            if is_crossing(i, j):
                crossings.append((i, j))

    return crossings


def part1():
    machine = Intcode(actual_data)
    map_data = machine.wait_for_result()
    pp_map_data = pretty_map(map_data)
    xings = find_crossings(pp_map_data)

    return map_data


with open("input17") as fr:
    actual_data = fr.read().strip()


result = part1()
