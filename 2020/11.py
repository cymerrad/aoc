from enum import Enum, auto
from typing import *
from itertools import product
import ipdb

data = open("input11").read().strip()

DEBUG = False


class Position(Enum):
    FLOOR = auto()
    FREE = auto()
    OCCUPIED = auto()

    def __str__(self) -> str:
        return POS_TO_CHR[self]


CHR_TO_POS = {
    ".": Position.FLOOR,
    "L": Position.FREE,
    "#": Position.OCCUPIED,
}
POS_TO_CHR = {v: k for k, v in CHR_TO_POS.items()}


SeatMap = Tuple[Tuple[Optional[Position]]]


def seat_map_str(smap: SeatMap) -> str:
    return "\n".join(["".join(str(x) if x else "." for x in row) for row in smap])


class SimulationLoop(Exception):
    pass


class Simulation:
    matrix: SeatMap
    seen_states: Set[SeatMap]

    def __init__(self, data: str) -> None:
        self.matrix = self.parse_map(data)
        self.seen_states = set([self.matrix])

        self.DEBUG = False

    @staticmethod
    def parse_map(data: str) -> SeatMap:
        matrix = []
        for line in data.strip().split("\n"):
            matrix.append(tuple([CHR_TO_POS.get(x, None) for x in line]))

        first_len = len(matrix[0])
        assert all(len(x) == first_len for x in matrix)

        return tuple(matrix)

    def get_pos(self, x: int, y: int) -> Optional[Position]:
        if x < 0 or y < 0:
            raise IndexError
        return self.matrix[y][x]

    def count_occupied_neighbours(self, row: int, col: int) -> int:
        occupied = 0
        for (dx, dy) in product([-1, 0, 1], [-1, 0, 1]):
            if dx == 0 and dy == 0:
                continue
            x, y = col + dx, row + dy
            try:
                s = self.get_pos(x, y)
            except IndexError:
                continue
            if s == Position.OCCUPIED:
                occupied += 1

        return occupied

    def is_seat_crowded(self, row: int, col: int) -> bool:
        return self.count_occupied_neighbours(row, col) >= 4

    def is_seat_clear(self, row: int, col: int) -> bool:
        return self.count_occupied_neighbours(row, col) == 0

    def step(self):
        new_state = []
        for y, row in enumerate(self.matrix):
            new_row = []
            for x, el in enumerate(row):
                if el == Position.OCCUPIED and self.is_seat_crowded(y, x):
                    new_row.append(Position.FREE)

                elif el == Position.FREE and self.is_seat_clear(y, x):
                    new_row.append(Position.OCCUPIED)

                else:
                    new_row.append(el)

            new_state.append(new_row)

        self.matrix = tuple([tuple(row) for row in new_state])

        if self.matrix in self.seen_states:
            raise SimulationLoop
        else:
            self.seen_states.add(self.matrix)

    def run_till_loop(self) -> int:
        count = 0
        while True:
            try:
                self.step()
            except SimulationLoop:
                break
            count += 1

        return count

    def __str__(self):
        return seat_map_str(self.matrix)

    __repr__ = __str__


test_states = [
    """L.LL.LL.LL
LLLLLLL.LL
L.L.L..L..
LLLL.LL.LL
L.LL.LL.LL
L.LLLLL.LL
..L.L.....
LLLLLLLLLL
L.LLLLLL.L
L.LLLLL.LL""",
    """#.##.##.##
#######.##
#.#.#..#..
####.##.##
#.##.##.##
#.#####.##
..#.#.....
##########
#.######.#
#.#####.##""",
    """#.LL.L#.##
#LLLLLL.L#
L.L.L..L..
#LLL.LL.L#
#.LL.LL.LL
#.LLLL#.##
..L.L.....
#LLLLLLLL#
#.LLLLLL.L
#.#LLLL.##""",
    """#.##.L#.##
#L###LL.L#
L.#.#..#..
#L##.##.L#
#.##.LL.LL
#.###L#.##
..#.#.....
#L######L#
#.LL###L.L
#.#L###.##""",
    """#.#L.L#.##
#LLL#LL.L#
L.L.L..#..
#LLL.##.L#
#.LL.LL.LL
#.LL#L#.##
..L.L.....
#L#LLLL#L#
#.LLLLLL.L
#.#L#L#.##""",
    """#.#L.L#.##
#LLL#LL.L#
L.#.L..#..
#L##.##.L#
#.#L.LL.LL
#.#L#L#.##
..L.L.....
#L#L##L#L#
#.LLLLLL.L
#.#L#L#.##""",
]


def side_by_side(map1: SeatMap, map2: SeatMap) -> SeatMap:
    return tuple([row1 + (" ",) + row2 for row1, row2 in zip(map1, map2)])


def do_test(cls, test_states: List[str], debug=False):
    s = cls(test_states[0])
    for ind, new_state in enumerate(test_states[1:], 1):
        s.step()
        pm = cls.parse_map(new_state)

        sbs = side_by_side(s.matrix, pm)
        if debug:
            print(seat_map_str(sbs))
            print("~" * (len(s.matrix[0]) * 2 + 1))

        if s.matrix != pm:
            print(f"ERROR {ind}")
            break


do_test(Simulation, test_states)


def first():
    s = Simulation(data)
    count = s.run_till_loop()

    print(f"Stopped after {count} iterations")
    print(s)

    occupied_seats = sum(row.count(Position.OCCUPIED) for row in s.matrix)
    print(f"Occupied {occupied_seats}")


class Simulation2(Simulation):
    def count_occupied_neighbours(self, row: int, col: int) -> int:
        if self.DEBUG:
            ipdb.set_trace()
        sight_range = max(len(self.matrix), len(self.matrix[0]))
        occupied = 0
        for (dx, dy) in product([-1, 0, 1], [-1, 0, 1]):
            if dx == 0 and dy == 0:
                continue

            for r in range(1, sight_range):
                x, y = col + (r * dx), row + (r * dy)
                try:
                    s = self.get_pos(x, y)
                except IndexError:
                    # OUT OF BOUNDS
                    break
                if s == Position.FLOOR:
                    continue
                elif s == Position.OCCUPIED:
                    occupied += 1
                break

        return occupied

    def is_seat_crowded(self, row: int, col: int) -> bool:
        return self.count_occupied_neighbours(row, col) >= 5

    def is_seat_clear(self, row: int, col: int) -> bool:
        return self.count_occupied_neighbours(row, col) == 0


test_states_2 = """L.LL.LL.LL
LLLLLLL.LL
L.L.L..L..
LLLL.LL.LL
L.LL.LL.LL
L.LLLLL.LL
..L.L.....
LLLLLLLLLL
L.LLLLLL.L
L.LLLLL.LL

#.##.##.##
#######.##
#.#.#..#..
####.##.##
#.##.##.##
#.#####.##
..#.#.....
##########
#.######.#
#.#####.##

#.LL.LL.L#
#LLLLLL.LL
L.L.L..L..
LLLL.LL.LL
L.LL.LL.LL
L.LLLLL.LL
..L.L.....
LLLLLLLLL#
#.LLLLLL.L
#.LLLLL.L#

#.L#.##.L#
#L#####.LL
L.#.#..#..
##L#.##.##
#.##.#L.##
#.#####.#L
..#.#.....
LLL####LL#
#.L#####.L
#.L####.L#

#.L#.L#.L#
#LLLLLL.LL
L.L.L..#..
##LL.LL.L#
L.LL.LL.L#
#.LLLLL.LL
..L.L.....
LLLLLLLLL#
#.LLLLL#.L
#.L#LL#.L#

#.L#.L#.L#
#LLLLLL.LL
L.L.L..#..
##L#.#L.L#
L.L#.#L.L#
#.L####.LL
..#.#.....
LLL###LLL#
#.LLLLL#.L
#.L#LL#.L#

#.L#.L#.L#
#LLLLLL.LL
L.L.L..#..
##L#.#L.L#
L.L#.LL.L#
#.LLLL#.LL
..#.L.....
LLL###LLL#
#.LLLLL#.L
#.L#LL#.L#
""".split(
    "\n\n"
)

do_test(Simulation2, test_states_2)


def second():
    s = Simulation2(data)
    count = s.run_till_loop()

    print(f"Stopped after {count} iterations")
    print(s)

    occupied_seats = sum(row.count(Position.OCCUPIED) for row in s.matrix)
    print(f"Occupied {occupied_seats}")
