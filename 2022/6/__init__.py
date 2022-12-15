from collections import deque
from typing import *


def parse(input: str, *args, **kwargs):
    return input.strip()


def generalize(data, start_of_message_len=4, debug=False):
    q = deque(maxlen=start_of_message_len)
    for i, c in enumerate(data):
        q.appendleft(c)
        if debug:
            print(q, set(q))
        if len(set(q)) == start_of_message_len:
            break
    else:
        print("No solution found")

    return i + 1


def solve_1(data, *args, debug=False, test=False, **kwargs) -> int:
    return generalize(data, debug=debug)


def solve_2(data, *args, debug=False, test=False, **kwargs) -> int:
    return generalize(data, start_of_message_len=14, debug=debug)


def test(*args, debug=False, test=False, **kwargs):
    success = True

    for tc, tr in TESTS.items():
        trr = solve_1(parse(tc), debug=debug)
        if trr != tr:
            print(f"Got {trr} != {tr} for: {tc}")
            success = False

    return success


TESTS = {
    "bvwbjplbgvbhsrlpgdmjqwftvncz": 5,
    "nppdvjthqldpwncqszvftbrmjlhg": 6,
    "nznrnfrfntjfmvfwmzdfjlvtqnbhcprsg": 10,
    "zcfzfwzzqfrljwzlrfnpqdbhtmscgvjw": 11,
}


TEST_INPUT = """
bvwbjplbgvbhsrlpgdmjqwftvncz
"""

TEST_RESULT_1 = 5
TEST_RESULT_2 = 23
