from typing import *
from helpers import grouper


def parse(input: str):
    return input.strip().split()


def calc_score(el):
    if "a" <= el <= "z":
        return ord(el) - ord("a") + 1
    else:
        return ord(el) - ord("A") + 27


def solve(data, debug=False, *args, **kwargs) -> int:
    score = 0
    for backpack in data:
        l, r = (backpack[: len(backpack) // 2], backpack[len(backpack) // 2 :])
        common = set(l).intersection(set(r))

        if debug:
            print(l, r, common)

        assert len(common) == 1

        score += calc_score(common.pop())

    return score


def solve_2(data, debug=False, *args, **kwargs) -> int:
    groups = grouper(data, 3)

    score = 0

    for g in groups:
        [a, b, c] = g
        common = set(a).intersection(set(b)).intersection(set(c))

        if debug:
            print(a, b, c, common)

        score += calc_score(common.pop())

    return score
