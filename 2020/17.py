from collections import defaultdict
from enum import Enum, auto
from typing import *
from itertools import product
from pprint import pformat
import ipdb

data = open("input17").read().strip()


class Cell(Enum):
    INACTIVE = auto()
    ACTIVE = auto()

    def __str__(self) -> str:
        return CELL_TO_CHR[self]


CHR_TO_CELL = {
    ".": Cell.INACTIVE,
    "#": Cell.ACTIVE,
}
CELL_TO_CHR = {v: k for k, v in CHR_TO_CELL.items()}


def tuple_add(t1, t2):
    return tuple(x1 + x2 for x1, x2 in zip(t1, t2))


def tuple_sub(t1, t2):
    return tuple(x1 - x2 for x1, x2 in zip(t1, t2))


Vector = Iterable[int]


class Grid(defaultdict):
    def __init__(self, *args, dim=3) -> None:
        super().__init__(lambda: Cell.INACTIVE, *args)
        self.dim = dim
        self.origin = (0,) * dim
        self.focus_next = set()
        self.max_ranges = ((0, 0),) * dim

    def neighbours_of(self, vector: Vector) -> Iterator[Vector]:
        for dw in product(*[[-1, 0, 1] for _ in range(self.dim)]):
            if dw == self.origin:
                continue
            yield tuple_add(vector, dw)

    def count_occupied_neighbours(self, vector: Vector) -> int:
        occupied = 0
        for neigh in self.neighbours_of(vector):
            if self.is_active(neigh):
                occupied += 1

        return occupied

    def is_active(self, vector: Vector) -> bool:
        return self[vector] == Cell.ACTIVE

    def shall_die(self, vector: Vector) -> bool:
        return not (2 <= self.count_occupied_neighbours(vector) <= 3)

    def shall_become_alive(self, vector: Vector) -> bool:
        return self.count_occupied_neighbours(vector) == 3

    def kill(self, vector: Vector):
        self[vector] = Cell.INACTIVE

        self.update_ranges(vector)

    def make_alive(self, vector: Vector):
        self[vector] = Cell.ACTIVE

        # all alive cells are interesting
        self.update_focus(vector)
        for neigh in self.neighbours_of(vector):
            # everything around alive cells is interesting
            self.update_focus(neigh)

    def update_focus(self, vector: Vector):
        self.focus_next.add(vector)
        self.update_ranges(vector)

    def update_ranges(self, vector: Vector):
        self.max_ranges = tuple(
            (min(a, c), max(b, c)) for (a, b), c in zip(self.max_ranges, vector)
        )

    def focus(self) -> Set[Cell]:
        return self.focus_next

    def ranges(self) -> Iterable[Tuple[int, int]]:
        # (ax,bx), (ay,by), (az,bz) = self.max_ranges
        return self.max_ranges


class Simulation:
    def __init__(self, data: str, dim=3):
        self.grid = Grid(dim=dim)
        self.dim = dim

        layer = self.parse_map(data)
        for row_ind, row in enumerate(layer):
            for col_ind, el in enumerate(row):
                if el == Cell.ACTIVE:
                    vector = self.row_col_to_vector(row_ind, col_ind)
                    self.grid.make_alive(vector)

        self.focus = self.grid.focus()

    def parse_map(self, data: str) -> Dict[Vector, Cell]:
        layer = []
        for line in data.strip().split("\n"):
            layer.append(tuple([CHR_TO_CELL.get(x, Cell.INACTIVE) for x in line]))

        first_len = len(layer[0])
        assert all(len(x) == first_len for x in layer)

        return layer

    def row_col_to_vector(self, row, col) -> Vector:
        return (col, row) + ((0,) * (self.dim - 2))

    def step(self):
        new_grid = Grid(dim=self.dim)
        for vector in self.focus:
            if self.grid.is_active(vector):
                if self.grid.shall_die(vector):
                    new_grid.kill(vector)
                else:
                    new_grid.make_alive(vector)

            else:
                if self.grid.shall_become_alive(vector):
                    new_grid.make_alive(vector)

        self.grid = new_grid
        self.focus = new_grid.focus()

    def __str__(self):
        if self.dim == 3:
            [(ax, bx), (ay, by), (az, bz)] = self.grid.ranges()

            def normalize(vector: Vector) -> Vector:
                return tuple_sub(vector, (ax, ay, az))

            (mx, my, mz) = normalize((bx, by, bz))

            grid = [
                [[str(Cell.INACTIVE) for _x in range(mx)] for _y in range(my)]
                for _z in range(mz)
            ]

            for vector, c in self.grid.items():
                (x, y, z) = normalize(vector)
                try:
                    grid[z][y][x] = str(c)
                except IndexError:
                    print(self.grid)
                    print(vector)
                    print(x, y, z)
                    raise

            return (
                "\n\n".join(
                    "\n".join("".join(str(_x) for _x in _y) for _y in _z) for _z in grid
                )
                + "\n"
            )
        else:
            return str(pformat(self.grid))

    __repr__ = __str__


test_data = """.#.
..#
###"""


def step_and_count(s: Simulation, cycles: int = 6, debug=False):
    for cycle in range(cycles):
        if debug:
            print(f"Cycle {cycle}")
            print(s)
        s.step()

    count = 0
    for _, c in s.grid.items():
        if c == Cell.ACTIVE:
            count += 1

    return s, count


def test():
    s = Simulation(test_data)

    _, count = step_and_count(s)
    assert count == 112


test()


def first():
    s = Simulation(data)

    _, count = step_and_count(s)
    assert count == 384


first()


def test():
    s = Simulation(test_data, dim=4)

    _, count = step_and_count(s)
    assert count == 848


test()


def second():
    s = Simulation(data, dim=4)
    _, count = step_and_count(s)
    print(f"Alive {count}")


second()
