from collections import UserList, deque
from typing import *
from utils import compose
from functools import reduce
from tqdm import trange

data = "156794823"

class Wheel:
    def __init__(self, data: str, debug=False) -> None:
        self.cups = deque(map(int, data), maxlen=len(data))
        self.lo = min(self.cups)
        self.hi = max(self.cups)

        # self.cup_to_place = list(self.place_to_cup)
        # for i,c in enumerate(self.place_to_cup[:10]):
        #     self.cup_to_place[c] = i

        self.current_ind = 0
        self.move_no = 0
        self.debug_info = [None, None, None]
        self.debug = debug

    def move(self):
        self.move_no += 1

        current_ind = self.current_ind
        current = self.cups[current_ind]

        removed_3 = list(self.cups[current_ind:current_ind+3])
        for _ in range(3):
            del self.cups[current_ind]

        highest_next = current - 1
        while highest_next in removed_3:
            highest_next -= 1

        if highest_next < self.lo:
            highest_next = self.hi
            while highest_next in removed_3:
                highest_next -= 1

        where_cut = self.cups.index(highest_next)

        cut_out = self.cups[:where_cut] + self.cups[where_cut+3:]

        where_paste = cut_out.index(current)
        self.cups.rotate(-where - 1)

        if self.debug:
            self.debug_info[0] = self.current_ind
            self.debug_info[1] = removed_3
            self.debug_info[2] = highest_next

    def cups_after_1(self):
        dq_copy = deque(self.cups)
        where = dq_copy.index(1)
        dq_copy.rotate(-where)
        dq_copy.popleft()
        return "".join(map(str, dq_copy))

    def __repr__(self):
        cups = " ".join(str(x) if i != self.debug_info[0] else f"({x})" for i,x in enumerate(self.cups))
        picks = ", ".join(map(str,self.debug_info[1]))
        dest = self.debug_info[2]

        return "-- move {} --\ncups: {cups}\npicks up: {picks}\ndestination: {dest}".format(
            self.move_no,
            cups=cups,
            picks=picks,
            dest=dest,
        )


def test():
    test_data = "389125467"
    wheel = Wheel(test_data, debug=True)
    for _ in range(10):
        wheel.move()
        print(wheel)
        print()

    string = wheel.cups_after_1()
    assert string == "92658374"

    for _ in range(90):
        wheel.move()

    string = wheel.cups_after_1()
    assert string == "67384529"


# test()

def first():
    wheel = Wheel(data)
    for _ in range(100):
        wheel.move()

    print(wheel.cups_after_1())

# first()

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

# wheel = test()
