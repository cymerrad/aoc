from typing import *
from helpers import grouper

"""
0 loss
3 draw
6 win
"""


def determine_outcome(P1: str, P2: str) -> int:
    "Assuming 1 character strings, outcome is -1 if P1 wins, +1 if P2, 0 for draw"

    edge_orientation = (ord(P2) - ord(P1)) % 3
    if edge_orientation == 1:
        return 1
    elif edge_orientation == 2:
        return -1
    else:
        return 0


def input_based_on_outcome(P1: str, outcome: int) -> str:
    norm = ord(P1) - ord("A")
    if outcome == "X":
        return chr(((2 + norm) % 3) + ord("A"))
    elif outcome == "Z":
        return chr(((1 + norm) % 3) + ord("A"))
    else:
        return P1


def parse(input: str):
    return list(grouper(input.strip().split(), 2))


def solve(data, debug=False) -> int:
    WEIGHTS = {
        "X": 1,
        "Y": 2,
        "Z": 3,
    }

    REPLACEMENTS = {
        "A": "X",  # rock
        "B": "Y",  # paper
        "C": "Z",  # scissors
    }

    same_letter_set = [(REPLACEMENTS[x], y) for (x, y) in data]

    score = 0

    for round in same_letter_set:
        (p1, p2) = round
        outcome = determine_outcome(p1, p2)
        partial = ((outcome + 1) * 3, WEIGHTS[p2])
        if debug:
            print(round, partial)
        score += sum(partial)

    return score


def solve_2(data, debug=False) -> int:
    WEIGHTS = {
        "A": 1,
        "B": 2,
        "C": 3,
    }

    score = 0

    for round in data:
        (p1, outcome) = round
        p2 = input_based_on_outcome(p1, outcome)
        partial = (((ord(outcome) - ord("X"))) * 3, WEIGHTS[p2])
        if debug:
            print(round, partial)
        score += sum(partial)

    return score
