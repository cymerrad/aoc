from copy import deepcopy
from typing import *
from lark import Lark, Transformer

CRATES = {
    1: ["B", "V", "W", "T", "Q", "N", "H", "D"],
    2: ["B", "W", "D"],
    3: ["C", "J", "W", "Q", "S", "T"],
    4: ["P", "T", "Z", "N", "R", "J", "F"],
    5: ["T", "S", "M", "J", "V", "P", "G"],
    6: ["N", "T", "F", "W", "B"],
    7: ["N", "V", "H", "F", "Q", "D", "L", "B"],
    8: ["R", "F", "P", "H"],
    9: ["H", "P", "N", "L", "B", "M", "S", "Z"],
}

"""
    [D]
[N] [C]
[Z] [M] [P]
 1   2   3
"""
TEST_CRATES = {1: ["N", "Z"], 2: ["D", "C", "M"], 3: ["P"]}

grammar = r"""
    lines: line+
    line: "move" num "from" num "to" num

    num: /\d+/

    %import common.ESCAPED_STRING   -> STRING
    %import common.SIGNED_NUMBER    -> NUMBER
    %import common.WS
    %ignore WS
    """


class OptimusPrime(Transformer):
    def num(self, n):
        (n,) = n
        return int(n)

    lines = list
    line = tuple


def parse(input: str, *args, **kwargs):
    parser = Lark(grammar, start="lines", lexer="basic")
    return OptimusPrime().transform(parser.parse(input.strip()))


def solve_1(data, *args, debug=False, test=False, **kwargs) -> int:
    crates = deepcopy(CRATES if not test else TEST_CRATES)

    for v in crates.values():
        v.reverse()

    for move in data:
        (how_many, from_, to_) = move
        for _ in range(how_many):
            what = crates[from_].pop()
            crates[to_].append(what)

    tops = []
    for v in crates.values():
        tops.append(v[-1])
    return "".join(tops)


def solve_2(data, *args, debug=False, test=False, **kwargs) -> int:
    crates = deepcopy(CRATES if not test else TEST_CRATES)

    for v in crates.values():
        v.reverse()

    for move in data:
        (how_many, from_, to_) = move


        buf = []
        for _ in range(how_many):
            what = crates[from_].pop()
            buf.append(what)

        buf.reverse()

        crates[to_].extend(buf)

    tops = []
    for v in crates.values():
        tops.append(v[-1])
    return "".join(tops)


TEST_INPUT = """
move 1 from 2 to 1
move 3 from 1 to 3
move 2 from 2 to 1
move 1 from 1 to 2"""


TEST_RESULT_1 = "CMZ"
TEST_RESULT_2 = "MCD"
