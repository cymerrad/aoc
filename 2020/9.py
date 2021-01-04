from typing import *
from collections import deque
from itertools import product

data = open("input9").read().strip().split("\n")
data = [int(x) for x in data]

def is_valid(number, preamble):
    # it has to be a sum of some two different numbers
    sums = set(x+y for x,y in product(preamble, preamble) if x != y)
    return number in sums

def xmas(code: List[int], preamble_length=25):
    preamble = deque(code[:preamble_length])
    code = deque(code[preamble_length:])
    el = None

    while code:
        el = code.popleft()

        if is_valid(el, preamble):
            preamble.popleft()
            preamble.append(el)

        else:
            break


    print(preamble, code, el)


def second():
    weakness = 675280050
    for frame_size in range(2, 100):
        for lo in range(len(data) - frame_size):
            frame = data[lo:lo+frame_size]

            if sum(frame) == weakness:
                print(frame)
                res = sorted(frame)
                print(res[0], res[-1], res[0] + res[-1])


def group_into_n(iterable, n=1):
    it = iter(iterable)
    yield from zip(*((it,) * n))