from functools import reduce
import math

from tqdm.std import tqdm

data = [16616892, 14505727]

test_data = [5764801, 17807724]

SOME_PRIME = 20201227

SUBJECT_NUMBER = 7

def loop(start_number: int, subject_number: int) -> int:
    return start_number * subject_number % SOME_PRIME

def find_loop_number(public_key: int, max_loops = 100000000) -> int:
    start_number = 1
    for loop_no in tqdm(range(1, max_loops)):
        start_number = loop(start_number, SUBJECT_NUMBER)

        if start_number == public_key:
            return loop_no

    return None

def calculate_encryption_key(public_key: int, other_loop_size: int) -> int:
    return reduce(lambda cur, _: loop(cur, public_key), range(other_loop_size), 1)

def bueeeh(a,b):
    ln = find_loop_number(a)
    if not ln:
        raise Exception("Loop number not found")

    ek = calculate_encryption_key(b, ln)

    return ek

def test():
    ek = bueeeh(*test_data)
    assert ek == 14897079
test()

def first():
    ek = bueeeh(*data)
    print(f"Result {ek}")
first()
