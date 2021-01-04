from typing import *
from functools import reduce


data = open("input13").read().strip()


def parse_data_first(data: str):
    [timestamp, data] = data.split()
    buses = [int(x) for x in data.split(",") if x != "x"]
    return int(timestamp), buses


def find_closest_modulo_space(x, *modulos) -> Tuple[int, int]:
    # x + t = 0 mod m
    # find smallest t for all m
    remainders = [x % m for m in modulos]

    ts_m = [(x - y, x) for x, y in zip(modulos, remainders)]
    return min(ts_m, key=lambda x: x[0])


test_data = """939
7,13,x,x,59,x,31,19"""


def test():
    timestamp, buses = parse_data_first(test_data)
    t, m = find_closest_modulo_space(timestamp, *buses)
    earliest = timestamp + t
    assert earliest == 944
    assert t * m == 295


test()


def first():
    timestamp, buses = parse_data_first(data)
    t, m = find_closest_modulo_space(timestamp, *buses)
    earliest = timestamp + t

    print(m * t)


first()


def parse_data_second(data: str):
    [_, data] = data.split()
    return [(int(x), i) for i, x in enumerate(data.split(",")) if x != "x"]


def chinese_remainder(n, a):
    sum = 0
    prod = reduce(lambda a, b: a * b, n)
    for n_i, a_i in zip(n, a):
        p = prod // n_i
        sum += a_i * mul_inv(p, n_i) * p
    return sum % prod


def mul_inv(a, b):
    b0 = b
    x0, x1 = 0, 1
    if b == 1:
        return 1
    while a > 1:
        q = a // b
        a, b = b, a % b
        x0, x1 = x1 - q * x0, x0
    if x1 < 0:
        x1 += b0
    return x1


def find_timestamp(offsets: List[Tuple[int, int]]):
    # offsets = [(m,i), ...]
    # find t s.t.
    # t + i = 0 mod m
    m, i = list(zip(*offsets))
    i = [m_x - i_x for m_x, i_x in zip(m, i)]
    t = chinese_remainder(m, i)
    return t


def test():
    bus_offsets = parse_data_second(test_data)
    t = find_timestamp(bus_offsets)
    assert t == 1068781, f"We got {t}"


test()


def second():
    bus_offsets = parse_data_second(data)
    t = find_timestamp(bus_offsets)
    print(t)


second()