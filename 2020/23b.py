from collections import deque
from typing import *
from utils import compose
from functools import reduce
from tqdm import trange

data = "156794823"

class Wheel:
    def __init__(self, data: str, debug=False) -> None:
        cups = list(map(int, data))
        self.lo = min(cups)
        self.hi = max(cups)
        self.cups = deque(cups, maxlen=len(cups))
        self.current_ind = 0

        self.move_no = 0
        self.rotations = 0
        self.debug = debug
        if debug:
            self.debug_info = [None, None, None, None]

    def move(self):
        label = self.cups[self.current_ind]

        self.move_no += 1

        self.cups.rotate(-self.current_ind)
        self.rotations -= self.current_ind
        removed_3 = self.cups.popleft(), self.cups.popleft(), self.cups.popleft()

        highest_next = label - 1
        while highest_next in removed_3:
            highest_next -= 1

        if highest_next < self.lo:
            highest_next = self.hi
            while highest_next in removed_3:
                highest_next -= 1

        where_next = self.cups.index(highest_next)
        for ind,cup in enumerate(removed_3, where_next+1):
            self.cups.insert(ind,cup)

        self.current_ind = where_next + 1


    def cups_after_1(self):
        dq_copy = deque(self.cups)
        where = dq_copy.index(1)
        dq_copy.rotate(-where)
        dq_copy.popleft()
        return "".join(map(str, dq_copy))

    def __repr__(self):
        copy = deque(self.cups)
        copy.rotate(-self.rotations)
        marked = " ".join(str(x)  for x in enumerate(copy))
        return "-- move {} --\ncups: {}\npicks up: {}\ndestination: {}".format(
            self.move_no,

        )


def test():
    test_data = "389125467"
    wheel = Wheel(test_data)
    for _ in range(10):
        wheel.move()
        # print(wheel)
        # print()

    string = wheel.cups_after_1()
    assert string == "92658374", f"10 moves: {string}"

    for _ in range(90):
        wheel.move()

    string = wheel.cups_after_1()
    assert string == "67384529", f"100 moves: {string}"


test()

def first():
    wheel = Wheel(data)
    for _ in range(100):
        wheel.move()

    print(wheel.cups_after_1())

first()

class MillionWheel(Wheel):
    def __init__(self, data: str) -> None:
        intz = list(map(int, data))
        next_number = max(intz)
        data = intz + list(range(next_number, 1_000_000 + 1))

        super().__init__(data)

def test():
    test_data = "389125467"
    wheel = MillionWheel(test_data)

    for _ in trange(10_000_000):
        wheel.move()

    return wheel