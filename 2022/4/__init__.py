from typing import *
from lark import Lark, Transformer

grammar = r"""
    lines: line+
    line: pair "," pair
    pair: num "-" num

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
    pair = tuple


def parse(input: str, *args, **kwargs):
    parser = Lark(grammar, start="lines", lexer="basic")
    return OptimusPrime().transform(parser.parse(input))


def range_encompass(r1: tuple, r2: tuple):
    "Checks if r2 is fully contained in r1 or vice versa"
    if r1[0] <= r2[0]:
        if r2[1] <= r1[1]:
            return True

    else:
        if r1[1] <= r2[1]:
            return True

    return False


def overlapping_segments(r1, r2):
    if r2[0] < r1[0]:
        # disallows this
        # r1  [a  b]
        # r2 [c    d]
        return overlapping_segments(r2, r1)

    if r1[1] < r2[0]:
        # r1  [a  b]
        # r2         [c   d]
        return 0

    # r1  [a  b]
    # r2  [c     d]
    # r1  [a  b]
    # r2    [c   d]
    return r1[1] - r2[0] + 1


def solve(data, debug=False, *args, **kwargs) -> int:
    if debug:
        print(data)

    count = 0

    for pair in data:
        (r1, r2) = pair

        if range_encompass(r1, r2) or range_encompass(r2, r1):
            count += 1

    return count


def solve_2(data, debug=False, *args, **kwargs) -> int:
    count = 0

    for pair in data:
        (r1, r2) = pair

        if overlapping_segments(r1, r2):
            count += 1

    return count
