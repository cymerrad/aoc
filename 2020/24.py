from collections import UserDict, defaultdict, deque
from functools import partial, reduce
from itertools import product
from lark import Lark, Transformer, Token
from typing import *
from lark.tree import Tree
from tqdm.std import tqdm
from utils import compose
import cmath

INPUT_FILE = "input24"
data = open(INPUT_FILE).read()

grammar = r"""
start: line+

line: DIRECTION+ NEWLINE

DIRECTION: "e" | "se" | "sw" | "w" | "nw" | "ne"

NEWLINE: "\n"
%import common (WORD, INT, WS, DIGIT)
"""

nth_root = lambda n: cmath.exp((n/6) * 2 * cmath.pi * 1j)

DIRECTIONS = {
    "e": 1+0j,
    "ne": nth_root(1),
    "nw": nth_root(2),
    "w": -1+0j,
    "sw": nth_root(4),
    "se": nth_root(5),
}

class InputTransformer(Transformer):
    start = list
    line = compose(list, partial(filter, None), partial(map, DIRECTIONS.get))


parser = Lark(
    grammar=grammar,
    transformer=InputTransformer,
    parser="lalr",
)

test_data = """sesenwnenenewseeswwswswwnenewsewsw
neeenesenwnwwswnenewnwwsewnenwseswesw
seswneswswsenwwnwse
nwnwneseeswswnenewneswwnewseswneseene
swweswneswnenwsewnwneneseenw
eesenwseswswnenwswnwnwsewwnwsene
sewnenenenesenwsewnenwwwse
wenwwweseeeweswwwnwwe
wsweesenenewnwwnwsenewsenwwsesesenwne
neeswseenwwswnwswswnw
nenwswwsewswnenenewsenwsenwnesesenew
enewnwewneswsewnwswenweswnenwsenwsw
sweneswneswneneenwnewenewwneswswnese
swwesenesewenwneswnwwneseswwne
enesenwswwswneneswsenwnewswseenwsese
wnwnesenesenenwwnenwsewesewsesesew
nenewswnwewswnenesenwnesewesw
eneswnwswnwsenenwnwnwwseeswneewsenese
neswnwewnwnwseenwseesewsenwsweewe
wseweeenwnesenwwwswnew
"""

Tile = complex

def are_tiles_the_same(tile1: Tile, tile2: Tile) -> bool:
    return cmath.isclose(tile1, tile2, rel_tol=0.001, abs_tol=0.001)

Color = bool
WHITE = False
BLACK = True

class Floor(UserDict[Tile, Color]):
    def __init__(self, tile_rules: Union[List[List[complex]], Dict[Tile, Color]]) -> None:
        self.representatives: Dict[Tile, Tile] = dict()

        if isinstance(tile_rules, list):
            tiles = defaultdict(lambda: WHITE)

            for directions in tile_rules:
                resultant = sum(directions, 0j)

                unique = self.get_representative(resultant)
                tiles[unique] = not tiles[unique]

            super().__init__(tiles)

        elif isinstance(tile_rules, dict):
            super().__init__(tile_rules)

    def __getitem__(self, key: Tile) -> Color:
        key = self.get_representative(key)
        try:
            return super().__getitem__(key)
        except KeyError:
            return WHITE

    def __setitem__(self, key: Tile, item: Color) -> None:
        key = self.get_representative(key)
        return super().__setitem__(key, item)

    def get_representative(self, tile: Tile) -> Tile:
        mem_repr = self.representatives.get(tile, None)
        if mem_repr:
            return mem_repr

        for repr in set(self.representatives.values()):
            if are_tiles_the_same(tile, repr):
                # found a repr
                self.representatives[tile] = repr
                return repr
        else:
            # is now it's own repr
            self.representatives[tile] = tile
            return tile

    def get_neighbours(self, tile: complex) -> List[Tuple[complex, Color]]:
        neighs = [(repr, self[repr]) for repr in (self.get_representative(tile + nth_root(i)) for i in range(6))]
        assert len(neighs) == 6
            # import ipdb; ipdb.set_trace()
            # pass
        return neighs

    def step(self) -> "Floor":
        black_neighbours = defaultdict(lambda: 0)
        for tile, is_black in self.items():
            neighbours = self.get_neighbours(tile)
            if is_black:
                for neigh_pair in neighbours:
                    black_neighbours[neigh_pair] += 1

        new_tiling = {}
        for (tile, color), black_count in black_neighbours.items():
            if color == BLACK:
                # 0, 3-6 of black -> white
                if black_count == 0 or (3 <= black_count <= 6):
                    # new_tiling[tile] = WHITE
                    pass
                else:
                    new_tiling[tile] = BLACK


            else:
                #  2 of black -> black
                if black_count == 2:
                    new_tiling[tile] = BLACK
                else:
                    # new_tiling[tile] = WHITE
                    pass


        f = Floor(new_tiling)
        f.representatives = self.representatives
        return f


def test():
    tile_rules = parser.parse(test_data)

    floor = Floor(tile_rules)
    flipped = sum(filter(lambda b: b == BLACK, floor.values()))
    assert flipped == 10, flipped

test()

def first():
    tiles = parser.parse(data)
    floor = Floor(tiles)
    flipped = sum(filter(None, floor.values()))
    print(f"Flipped {flipped}")

first()

def count_blacks(tiles) -> int:
    return sum(tiles.values())

test_results = {1: 15, 2: 12, 3: 25, 4: 14, 5: 23, 6: 28, 7: 41, 8: 37, 9: 49, 10: 37, 20: 132, 30: 259, 40: 406, 50: 566, 60: 788, 70: 1106, 80: 1373, 90: 1844, 100: 2208}

def play_game_of_life_again(tile_rules: Dict[int, List[complex]], days: int, compare: Dict[int, int]={}, debug=False):
    floor = Floor(tile_rules)

    for day in tqdm(range(1,days+1)):
        floor = floor.step()

        blacks = count_blacks(floor)
        if debug: print(f"Day {day}: {blacks}")

        if day in compare.keys():
            assert compare[day] == blacks, f"{compare[day]} != {blacks}"

    return floor

def test():
    tiles = parser.parse(test_data)

    return play_game_of_life_again(tiles, 100, compare=test_results)

# tiles, reprs = test()

smaller_test_data = """ew
e
w
"""

def smaller_test(days=0):
    tile_rules = parser.parse(smaller_test_data)

    return play_game_of_life_again(tile_rules, days, True)


test()

def second():
    tiles = parser.parse(data)

    floor = play_game_of_life_again(tiles, 100)

    black_tiles = count_blacks(floor)
    print(f"Black tiles {black_tiles}")

    return floor