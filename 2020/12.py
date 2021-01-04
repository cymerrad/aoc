from typing import *
import re
from dataclasses import dataclass
from functools import partial

data = open("input12").read()

COMPASS = {
    "S": lambda val, pos, dir: (pos + val * -1j, dir),
    "W": lambda val, pos, dir: (pos + val * -1, dir),
    "E": lambda val, pos, dir: (pos + val * 1, dir),
    "N": lambda val, pos, dir: (pos + val * 1j, dir),
    "L": lambda val, pos, dir: (pos, dir * 1j ** val),
    "R": lambda val, pos, dir: (pos, dir * (-1j) ** val),
    "F": lambda val, pos, dir: (pos + val * dir, dir),
}

Instr = Callable[[int, complex, complex], Tuple[complex, complex]]


@dataclass
class Ship:
    instructions: List[Instr]
    position: complex = 0j
    direction: complex = 1 + 0j
    current_instr: int = 0

    def __post_init__(self):
        lamb_instructions = []
        for letter, value in self.instructions:
            lamb = COMPASS[letter]
            lamb_instructions.append(partial(lamb, value))
        self.instructions = lamb_instructions

    def step(self) -> complex:
        if self.current_instr < len(self.instructions):
            move = self.instructions[self.current_instr]
            self.position, self.direction = move(self.position, self.direction)
            self.current_instr += 1
            return self.position
        return None

    def run_all(self, debug=False) -> complex:
        pos = self.position
        for pos in iter(self.step, None):
            if debug:
                print(pos)
        return pos


def parse_data(data) -> List[Tuple[str, int]]:
    line_re = re.compile(r"([SWENLRF])(\d+)")
    instructions = []

    for match in line_re.finditer(data):
        letter, value = match.groups()
        if letter in "LR":
            value = int(value) // 90
        else:
            value = int(value)

        instructions.append((letter, value))

    return instructions


def manh_dist(z: complex):
    return abs(z.imag) + abs(z.real)


test_data = """F10
N3
F7
R90
F11"""


def do_test():
    s = Ship(parse_data(test_data))
    end_pos = s.run_all(debug=True)
    end_pos_dist = manh_dist(end_pos)
    assert end_pos_dist == 25, f"We got |{end_pos}|={end_pos_dist}"


do_test()


def first():
    s = Ship(parse_data(data))
    end_pos = s.run_all()
    print(end_pos, int(manh_dist(end_pos)))


first()


@dataclass
class Waypoint:
    position: complex = 0j

    def move(self, letter, value):
        ACTIONS = {
            "S": lambda val, pos: pos + val * -1j,
            "W": lambda val, pos: pos + val * -1,
            "E": lambda val, pos: pos + val * 1,
            "N": lambda val, pos: pos + val * 1j,
            "L": lambda val, pos: pos * 1j ** val,
            "R": lambda val, pos: pos * (-1j) ** val,
        }
        lamb = ACTIONS[letter]
        self.position = lamb(value, self.position)

@dataclass
class VecShip:
    instructions: List[Tuple[str, int]]
    position: complex = 0j
    waypoint: Waypoint = Waypoint(10+1j)

    def run(self):
        for letter, value in self.instructions:
            if letter == "F":
                self.position += value * self.waypoint.position
            else:
                self.waypoint.move(letter, value)

        return self.position

def second():
    s = VecShip(parse_data(data))
    end_pos = s.run()

    print(f"{end_pos}, {int(manh_dist(end_pos))}")

second()

