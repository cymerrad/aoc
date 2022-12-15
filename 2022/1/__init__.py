from typing import *


def parse(input: str):
    chunks = input.strip().split("\n")
    return [[int(y) for y in chunk.split()] for chunk in chunks]


def solve_1(data) -> int:
    return max([sum(chunks) for chunks in data])

def solve_2(data) -> int:
    decreasing = sorted([sum(chunks) for chunks in data], reverse=True)
    return sum(decreasing[:3])
