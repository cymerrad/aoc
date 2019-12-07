from collections import Counter

secret_input="206938-679128"

def is_valid(num: str):
    # six digit
    # within range
    # some two adjacent digits are the same
    # nondecreasing

    try:
        copy = list(num)
        copy.sort()
        assert "".join(copy) == num

        for c1,c2 in zip(num[:-1], num[1:]):
            if c1 == c2:
                break
        else:
            assert False

    except AssertionError:
        return False
    return True

assert is_valid("122345")
assert is_valid("111111")
assert not is_valid("223450")
assert not is_valid("123789")


def is_valid_pt_2(num: str):
    # valid
    # some weird rule

    try:
        assert is_valid(num)

        counted = Counter(num)
        for k in counted.values():
            if k == 2:
                break
        else:
            assert False

    except AssertionError:
        return False
    return True

assert is_valid_pt_2("112233")
assert not is_valid_pt_2("123444")
assert is_valid_pt_2("111122")


count_1 = 0
count_2 = 0
for num in range(206938, 679128):
    if is_valid(str(num)):
        count_1 += 1

    if is_valid_pt_2(str(num)):
        count_2 += 1