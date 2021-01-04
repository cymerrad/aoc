from typing import *
import sys

data = open(sys.argv[1]).read()


class OutOfBounds(Exception):
    ...


T = TypeVar("T")


class World:
    def __init__(self, data: Union[List[List[T]], str]):
        if isinstance(data, str):
            data = [[x for x in l] for l in data.strip().split()]

        self.height = len(data)
        self.width = len(data[0])
        assert all(len(x) == self.width for x in data)

        self.data = [[x for x in l] for l in data]
        self.abs_pos = (0, 0)
        self.rel_pos = (0, 0)

    def move_by(self, vec: Tuple[int, int]):
        new_abs_pos = tuple(sum(x) for x in zip(self.abs_pos, vec))
        self.abs_pos = new_abs_pos

        self.rel_pos = (self.abs_pos[0] % self.width, self.abs_pos[1])

        if self.rel_pos[1] >= self.height:
            raise OutOfBounds

    def get_xy(self, x: int, y: int):
        return self.data[y][x]

    def set_xy(self, x: int, y: int, val: Any):
        self.data[y][x] = val

    def check_pos(self):
        return self.get_xy(*self.rel_pos)

    def set_pos(self, val):
        self.set_xy(*self.rel_pos, val)

    def print(self):
        for line in self.data:
            print("".join(line))


def first():
    world = World(data)
    trees = 0

    world.print()

    while True:
        try:
            world.move_by((3, 1))
        except OutOfBounds:
            break
        field = world.check_pos()
        if field == "#":
            world.set_pos("X")
            trees += 1
        else:
            world.set_pos("O")

    print(f"Trees encountered {trees}")

    world.print()


def count_trees_by_slope(world: World, delta: Tuple[int, int]) -> int:
    trees = 0
    while True:
        try:
            world.move_by(delta)
        except OutOfBounds:
            break
        field = world.check_pos()
        if field == "#":
            trees += 1

    return trees


def second():
    result = 1
    for delta in [(1, 1), (3, 1), (5, 1), (7, 1), (1, 2)]:
        world = World(data)
        trees = count_trees_by_slope(world, delta)
        print(f"{delta} -> {trees}")

        result *= trees

    print(result)


second()