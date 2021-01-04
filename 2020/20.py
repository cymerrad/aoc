from collections import defaultdict, deque
from operator import mul
import re
from typing import *
from numpy import array, rot90, copy, flipud, concatenate
from itertools import product
from functools import reduce
from pprint import pformat
from math import sqrt
from scipy.ndimage import correlate
import numpy as np

data = open("input20").read().strip()


class NoMatch(Exception):
    pass


class Tile:
    def __init__(self, id: int, data: Union[str, Any], rotated=0):
        self.id = id
        self.rotated = rotated % 4
        if isinstance(data, str):
            self.array = array(
                [[1 if x == "#" else 0 for x in line.strip()] for line in data.split("\n")]
            )

            first_len = len(self.array[0])
            assert all(len(x) == first_len for x in self.array)
        else:
            self.array = data

    def rotate(self, times=1):
        """
        Rotates counterclockwise, returns new instance.
        """
        return Tile(
            self.id, copy(rot90(self.array, k=times)), rotated=(self.rotated + times)
        )

    def flip(self):
        """
        Flips left to right. It took me hours to notice its needed for the solution. FML.
        """
        return Tile((-self.id), copy(flipud(self.array)), rotated=self.rotated)

    def edges(self) -> Tuple[Tuple, Tuple, Tuple, Tuple]:
        a = self.array

        top = tuple(a[0, :])
        left = tuple(a[:, 0])
        down = tuple(a[-1, :])
        right = tuple(a[:, -1])

        return (top, left, down, right)

    def edges_invariant(self) -> Tuple[Tuple, Tuple, Tuple, Tuple]:
        a = self.array

        top = tuple(a[0, :])
        left = tuple(reversed(a[:, 0]))
        down = tuple(reversed(a[-1, :]))
        right = tuple(a[:, -1])

        return (top, left, down, right)

    def match(self, other: "Tile") -> int:
        """
        Returns to which edge the other tile fits, if any.
        """
        s_e = self.edges()
        o_e = deque(other.edges())
        o_e.rotate(-2)

        for (i1, e1), (i2, e2) in zip(enumerate(s_e), enumerate(o_e)):
            if e1 == e2:
                return i1
        else:
            raise NoMatch(f"No matching edges")

    def rotate_till_fits(self, other: "Tile") -> Tuple["Tile", int]:
        """
        Rotates the other tile until it fits to self-Tile.
        """
        for rotations in range(4):
            for flips in range(2):
                rotated = other.rotate(times=rotations)
                if flips:
                    rotated = rotated.flip()
                try:
                    edge = self.match(rotated)
                    return rotated, edge
                except NoMatch:
                    continue
        raise NoMatch(f"{rpr(other)} doesn't fit to {rpr(self)}")


    def trim_edges(self) -> np.ndarray:
        return copy(self.array[1:-1, 1:-1])

    def __str__(self):
        return str(self.array)

    def __repr__(self):
        return self.__short_repr__() + "\n" + str(self.array)

    def __short_repr__(self) -> str:
        return f"Tile: {self.id}{' x' + str(self.rotated) if self.rotated else ''}"

    def __hash__(self) -> int:
        return self.id

def rpr(obj):
    return obj.__short_repr__()

def parse_input(data: str) -> List[Tile]:
    tiles = []
    parts = data.split("\n\n")
    tile_id_re = re.compile(r"Tile (\d+):")
    for part in parts:
        tile_id, *tile_data = part.split("\n")
        tile_id = int(tile_id_re.findall(tile_id)[0])

        tiles.append(Tile(tile_id, "\n".join(tile_data)))

    return sorted(tiles, key=lambda t: t.id)

def traverse_connecting_into_edges(connecting: Dict[int, Set[int]], start: int) -> List[Tuple[int, int]]:
    visited = set()
    def traverse(current: int) -> List[int]:
        neighbours = connecting[current]
        non_visited = neighbours - visited

        visited.add(current)
        forward_edges = [(abs(current), abs(next_)) for next_ in non_visited]
        return forward_edges + reduce(list.__add__, [traverse(next_) for next_ in non_visited], [])

    return traverse(abs(start))

DEBUG = False
def solve_puzzle(tiles: List[Tile]) -> Dict[complex, Tile]:
    edges = {t.id: t.edges_invariant() for t in tiles + [t.flip() for t in tiles]}

    connecting = defaultdict(set)
    for (t1, e1), (t2, e2) in product(edges.items(), edges.items()):
        if abs(t1) == abs(t2):
            continue

        e1s = set(e1)
        e2s = set(e2)
        xing = e1s & e2s
        if xing:
            connecting[t1].add(t2)
            connecting[t2].add(t1)

    _print = print if DEBUG else lambda _: None
    max_connections = len(max(connecting.values(), key=len))
    if max_connections != 4:
        _print(f"Whoops, this isn't going to be as easy; max len {max_connections}")

    # pick any tile that's in the middle with positive id
    center_piece = next(
        (k, v) for k, v in connecting.items() if max_connections == len(v) and k > 0
    )

    aggregate_center = next(t for t in tiles if center_piece[0] == t.id)
    aggregate_position = 0j
    puzzles_count = len(tiles)

    _print(f"Starting with {aggregate_center.id} at {aggregate_position}")
    puzzles = {aggregate_position: aggregate_center}
    tiles_dict = {t.id: t for t in tiles + [t.flip() for t in tiles]}
    puzzles_locations = {aggregate_center.id: 0j}

    edges = traverse_connecting_into_edges(connecting, center_piece[0])
    for source, target in edges:
        # assuming source is always already oriented
        puzzle = tiles_dict[source]
        location = puzzles_locations[source]

        unrotated = tiles_dict[target]
        rotated, edge = puzzle.rotate_till_fits(unrotated)
        direction = 1j ** (edge + 1)
        rotated_loc = location + direction

        abs_rot_id = abs(rotated.id)
        tiles_dict[abs_rot_id] = rotated
        puzzles_locations[abs_rot_id] = rotated_loc
        puzzles[rotated_loc] = rotated

    assert len(puzzles) == puzzles_count, len(puzzles)

    return puzzles


test_data = open("input20a").read().strip()


def get_corners_ids(tiles: List[Tile]) -> List[int]:
    edges = {t.id: t.edges_invariant() for t in tiles + [t.flip() for t in tiles]}

    connecting = defaultdict(set)
    for (t1, e1), (t2, e2) in product(edges.items(), edges.items()):
        if abs(t1) == abs(t2):
            continue

        e1s = set(e1)
        e2s = set(e2)
        xing = e1s & e2s
        if xing:
            connecting[t1].add(t2)
            connecting[t2].add(t1)

    corners = set(
        [
            abs(x[0])
            for x in filter(
                lambda x: x[1] == 2,
                map(lambda x: (x[0], len(x[1])), connecting.items()),
            )
        ]
    )
    return corners, connecting


def test():
    ts = parse_input(test_data)

    t1 = Tile(1, """#.#
                    ##.
                    ... """)

    t2 = Tile(1, """#..
                    .#.
                    .#. """)

    e1 = t1.match(t2)
    assert e1 == 3

    corners, _ = get_corners_ids(ts)
    assert reduce(mul, corners, 1) == 20899048083289, f"We got {reduce(mul, corners, 1)}"


test()


def first():
    tiles = parse_input(data)
    corners, _ = get_corners_ids(tiles)
    print(reduce(mul, corners, 1))


# tiles = parse_input(test_data)
# for ind,t in enumerate(tiles):
#     exec(f"t{t.id} = tiles[{ind}]")


def coalesce_puzzle(puzzles: Dict[complex, Tile], trim=True):
    size = int(sqrt(len(puzzles)))

    start_x = int(min(puzzles.keys(), key=lambda z: z.real).real)
    end_x = int(max(puzzles.keys(), key=lambda z: z.real).real)
    start_y = int(max(puzzles.keys(), key=lambda z: z.imag).imag)
    end_y = int(min(puzzles.keys(), key=lambda z: z.imag).imag)

    assert start_x < end_x
    assert start_y > end_y

    matrix = [[0 for _ in range(size)] for _ in range(size)]
    tiles_m = [[0 for _ in range(size)] for _ in range(size)]
    for x,y in product(range(start_x, end_x+1), range(start_y, end_y-1, -1)):
        x_i = x - start_x
        y_i = y - end_y
        z = complex(x,y)
        matrix[y_i][x_i] = puzzles[z].trim_edges() if trim else puzzles[z].array
        tiles_m[y_i][x_i] = puzzles[z]

    matrix = array(matrix)
    rows = [concatenate(list(flipud(m) for m in row), axis=1) for row in map(lambda r: matrix[r, :], range(size))]
    picture = concatenate(rows)

    return picture

SEA_MONSTER = array([[1 if c == "#" else 0 for c in line] for line in """
..................#.
#....##....##....###
.#..#..#..#..#..#...
""".strip().split("\n")])
MONSTER_PIXELS = np.sum(SEA_MONSTER)
NEGATIVE_SEA_MONSTER = (SEA_MONSTER + 1) % 2

def find_sea_monsters(picture: np.ndarray):
    monsters_count = 0
    for rotations in range(4):
        view = rot90(picture, k=rotations)
        for flips in range(2):
            if flips:
                view = flipud(view)


            masked = correlate(view, SEA_MONSTER, mode='constant', cval=0)
            monsters = np.where(masked == MONSTER_PIXELS)
            if np.any(monsters):
                monsters_count += len(list(zip(*monsters)))

    return monsters_count

def test():
    tiles = parse_input(test_data)
    puzzles = solve_puzzle(tiles)

    picture_with_borders = coalesce_puzzle(puzzles, trim=False)
    test_output = array([[1, 0, 0, 0, 1, 1, 0, 1, 0, 0, 0, 0, 1, 1, 1, 0, 0, 1, 1, 1, 1, 0, 1, 0, 1, 1, 1, 1, 1, 0],
       [0, 0, 1, 0, 1, 0, 0, 1, 0, 1, 1, 1, 1, 0, 0, 0, 1, 0, 1, 0, 0, 1, 0, 0, 1, 1, 1, 1, 1, 1],
       [0, 1, 1, 1, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0],
       [1, 1, 1, 0, 1, 1, 0, 1, 1, 0, 0, 1, 0, 1, 0, 1, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0],
       [0, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 1, 0, 1, 1, 1, 1, 1, 1, 1, 0, 1, 0, 0, 1, 0],
       [0, 1, 1, 0, 1, 0, 0, 0, 0, 1, 1, 1, 0, 1, 1, 0, 1, 1, 1, 0, 0, 1, 0, 0, 0, 1, 0, 1, 1, 0],
       [1, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 0, 0, 0, 1, 1, 0, 1, 1, 1, 1, 1, 0, 1, 1],
       [0, 0, 0, 0, 0, 1, 0, 0, 1, 1, 1, 0, 0, 0, 1, 1, 0, 0, 1, 0, 0, 0, 1, 0, 1, 1, 1, 0, 0, 0],
       [1, 0, 1, 1, 1, 1, 0, 0, 0, 1, 1, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0],
       [1, 0, 1, 1, 0, 0, 0, 1, 1, 0, 0, 0, 1, 1, 0, 1, 0, 0, 1, 0, 0, 0, 1, 0, 1, 1, 1, 0, 0, 0],
       [1, 0, 1, 1, 0, 0, 0, 1, 1, 0, 0, 0, 1, 1, 0, 1, 0, 0, 1, 0, 0, 0, 1, 0, 1, 1, 1, 0, 0, 0],
       [1, 1, 0, 0, 1, 0, 1, 1, 0, 0, 0, 0, 1, 0, 0, 1, 1, 1, 0, 1, 1, 1, 0, 1, 1, 0, 0, 0, 0, 1],
       [1, 1, 0, 1, 1, 1, 1, 0, 0, 0, 0, 1, 0, 1, 1, 1, 1, 0, 1, 0, 0, 0, 1, 0, 1, 1, 1, 0, 0, 1],
       [1, 1, 1, 1, 0, 1, 0, 1, 0, 0, 0, 0, 0, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 0, 0, 1, 1, 1],
       [0, 1, 0, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 1, 1, 0, 0, 1, 1, 1, 1, 1, 1, 0, 1, 1],
       [0, 1, 1, 0, 0, 1, 1, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 1, 1, 0, 1, 0, 1, 0, 1, 0, 0, 0],
       [0, 0, 0, 0, 1, 0, 0, 1, 0, 1, 1, 0, 1, 0, 1, 0, 1, 1, 0, 1, 1, 0, 1, 1, 1, 0, 1, 1, 1, 0],
       [0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 1, 0, 1, 1, 0, 1, 0, 0, 1, 1, 0, 1, 1, 1, 0, 1, 1, 0, 0],
       [1, 1, 1, 1, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 1, 1, 0, 0, 0, 1, 1, 1, 1, 1, 1, 0, 0, 0],
       [0, 0, 0, 1, 0, 1, 0, 1, 0, 1, 1, 1, 1, 0, 1, 1, 0, 1, 0, 0, 0, 1, 1, 0, 0, 0, 1, 1, 1, 1],
       [0, 0, 0, 1, 0, 1, 0, 1, 0, 1, 1, 1, 1, 0, 1, 1, 0, 1, 0, 0, 0, 1, 1, 0, 0, 0, 1, 1, 1, 1],
       [0, 0, 1, 0, 1, 0, 1, 1, 1, 0, 0, 0, 1, 1, 0, 1, 1, 0, 1, 1, 1, 0, 0, 1, 0, 1, 1, 0, 0, 1],
       [0, 0, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 0, 1, 0, 0, 0, 1, 1, 0, 0, 1, 0, 1, 0, 0, 1, 0, 1, 1],
       [1, 0, 0, 1, 0, 1, 0, 0, 1, 0, 0, 0, 0, 1, 0, 1, 0, 1, 0, 0, 0, 1, 1, 1, 1, 0, 1, 1, 1, 0],
       [0, 1, 0, 0, 1, 1, 1, 1, 0, 1, 1, 0, 0, 1, 0, 1, 0, 1, 0, 1, 1, 1, 1, 1, 0, 1, 1, 1, 0, 0],
       [0, 1, 1, 1, 1, 1, 0, 0, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 1, 0, 0, 1, 1, 0, 0, 0, 0, 1, 1, 0],
       [1, 1, 0, 1, 1, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 1, 1, 1, 1, 0, 0, 0, 1, 0],
       [1, 0, 1, 0, 1, 1, 1, 0, 0, 0, 0, 1, 1, 0, 0, 1, 1, 0, 0, 0, 0, 1, 1, 1, 1, 0, 1, 1, 0, 1],
       [1, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 1, 1, 1, 1],
       [0, 0, 1, 0, 1, 0, 0, 0, 0, 1, 1, 1, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0]])
    assert np.array_equal(test_output, picture_with_borders)

    picture = coalesce_puzzle(puzzles)

    monster_infested_picture = rot90(flipud(picture), k=3)

    monsters = find_sea_monsters(picture)
    assert monsters == 2
    other_pixels = np.sum(picture) - (monsters * MONSTER_PIXELS)
    assert other_pixels == 273

# test()

def second():
    tiles = parse_input(data)
    puzzles = solve_puzzle(tiles)

    picture = coalesce_puzzle(puzzles)

    monsters = find_sea_monsters(picture)
    other_pixels = np.sum(picture) - (monsters * MONSTER_PIXELS)
    print(other_pixels)

second()
