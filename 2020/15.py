data = open("input15").read().strip()
numbers = [int(x) for x in data.split(",")]

def find_last_ind(haystack, needle):
    ind = len(haystack) - 1
    while ind > 0:
        val = haystack[ind]
        if val == needle:
            return ind

        ind -= 1

    return ind

def run_game(starting_numbers, runs):
    said = [x for x in starting_numbers]
    turn = len(said) + 1

    while turn <= runs:
        previous = said[-1]

        to_say = 0
        if previous not in said[:-1]:
            # first time it was said
            to_say = 0
        else:
            ind = find_last_ind(said[:-1], previous)
            assert ind >= 0
            that_turn = ind + 1
            previous_turn = turn - 1

            to_say = previous_turn - that_turn

        said.append(to_say)

        turn += 1

    return said

res = run_game(numbers, 2020)

def run_game_v2(starting_numbers, runs):
    said = {x:(-1,ind) for ind,x in enumerate(starting_numbers, 1)}
    turn = len(starting_numbers) + 1
    previous = starting_numbers[-1]

    if runs <= len(starting_numbers):
        return {}, starting_numbers[runs - 1]

    while turn <= runs:
        (last_last_ind, last_ind) = said.get(previous)

        if last_last_ind == -1:
            to_say = 0
        else:
            to_say = last_ind - last_last_ind

        if to_say not in said.keys():
            said[to_say] = (-1, turn)
        else:
            (_, last_same) = said.get(to_say)
            said[to_say] = (last_same, turn)

        previous = to_say
        turn += 1

    return said, previous

for turn, expected in enumerate(res, 1):
    dd, res_2 = run_game_v2(numbers, turn)

    assert res_2 == expected
    # if res_2 == expected:
    #     print(f"{turn}: {res_2} == {expected}")
    # else:
    #     print(res[:turn])
    #     print(dd)
    #     break

_, res_2 = run_game_v2(numbers, 30000000)
