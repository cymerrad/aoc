from collections import deque
from typing import *
from utils import compose
from functools import reduce
from tqdm import trange

data = "156794823"

class Wheel:
    def __init__(self, data: str) -> None:
        cups = list(map(int, data))
        self.lo = min(cups)
        self.hi = max(cups)
        self.cups = deque(cups)

        self.move_no = 0
        self.debug_info = [None, None, None, None]

    def move(self) -> "Wheel":
        current = self.cups.popleft()

        self.move_no += 1
        self.debug_info[0] = current
        self.debug_info[1] = list(self.cups)

        removed_3 = [self.cups.popleft() for _ in range(3)]
        self.debug_info[2] = list(removed_3)

        label = current
        self.cups.appendleft(current)

        highest_next = label - 1
        while highest_next in removed_3:
            highest_next -= 1

        if highest_next < self.lo:
            highest_next = self.hi
            while highest_next in removed_3:
                highest_next -= 1

        where = self.cups.index(highest_next)
        self.debug_info[3] = highest_next
        self.cups.rotate(-where - 1)
        for cup in removed_3:
            self.cups.append(cup)

        where = self.cups.index(current)
        self.cups.rotate(-where - 1)

        return self

    def cups_after_1(self):
        dq_copy = deque(self.cups)
        where = dq_copy.index(1)
        dq_copy.rotate(-where)
        dq_copy.popleft()
        return "".join(map(str, dq_copy))

    def __repr__(self):
        self.debug_info[1] = " ".join(map(str,self.debug_info[1]))
        self.debug_info[2] = ", ".join(map(str,self.debug_info[2]))
        return "-- move {} --\ncups: ({}) {}\npicks up: {}\ndestination: {}".format(
            self.move_no,
            *self.debug_info,
        )


def test():
    test_data = "389125467"
    wheel = Wheel(test_data)
    for _ in range(10):
        wheel.move()
        # print(wheel)
        # print()

    string = wheel.cups_after_1()
    assert string == "92658374"

    for _ in range(90):
        wheel.move()

    string = wheel.cups_after_1()
    assert string == "67384529"


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