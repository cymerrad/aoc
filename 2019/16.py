import numpy as np
from itertools import cycle, repeat
from cmath import exp, pi


def parse_data(data: str):
    return np.array([int(x) for x in data])


def generate_pattern(reps):
    #   v (reps) times
    # 0 1 0 -1 0
    # ^ (reps - 1) times
    phase_complex = 0-1j
    phase = int(phase_complex.real)

    def phase_shift():
        shift = 1j
        nonlocal phase_complex
        nonlocal phase
        phase_complex *= shift
        phase = int(phase_complex.real)

    for _ in range(reps-1):
        yield phase

    phase_shift()
    while True:
        for _ in range(reps):
            yield phase
        phase_shift()


def generate_phaser(length):
    phaser = np.zeros((length, length), dtype=int)
    for i in range(length):
        # i amount of zeroes,
        # then alternating (i+1) 1,0,-1
        for j, amp in zip(range(length), generate_pattern(i+1)):
            phaser[i, j] = amp

    return phaser


def task_fft(signal: list, till: int):
    phaser = generate_phaser(len(signal))
    curr_step = 0
    curr_result = signal

    def step_fun():
        nonlocal curr_result
        nonlocal curr_step

        curr_result = phaser @ curr_result
        curr_result = np.array([abs(n) % 10 for n in curr_result])

        curr_step += 1

    while curr_step < till:
        step_fun()

    return curr_result


def part1():
    signal = parse_data(actual_data)
    result = task_fft(signal, 100)
    stringified = arr_to_str(result)
    return stringified[:8]


def arr_to_str(arr):
    return "".join([str(x) for x in arr])


def do_tests():
    for t_d, milestones in test_data:
        for milestone, expected in milestones.items():
            input_signal = parse_data(t_d)
            result = task_fft(input_signal, milestone)

            stringified = arr_to_str(result)
            equal = stringified == expected
            first_eight = stringified[:8] == expected
            assert equal or first_eight, f"{stringified} != {expected}"


def iterate_over_and_over(signal: input):
    view = np.flip(signal, 0)
    np.cumsum(view, 0, out=view)
    np.abs(signal, out=signal)
    signal %= 10


def part2():
    actual_len = len(actual_data)
    offset = int(actual_data[:7])  # 5973857
    signal_len = actual_len * 10000  # 6500000
    offset_mod = offset % actual_len
    # signal = parse_data(actual_data)
    faux_signal = parse_data(actual_data)
    a_lot_left = signal_len - (offset + (actual_len - offset_mod))
    actual_signal = "".join((str(x) for x in faux_signal[offset_mod:])) + "".join(
        (str(x) for _, x in zip(range(a_lot_left), cycle(faux_signal))))
    assert len(actual_signal) == (signal_len - offset)
    actual_signal_for_real_this_time = parse_data(actual_signal)

    for i in range(100):
        iterate_over_and_over(actual_signal_for_real_this_time)

    print(actual_signal_for_real_this_time[:8])

    return actual_signal_for_real_this_time


with open("input16") as fr:
    actual_data = fr.read().strip()

test_data = [('12345678',
              {1: '48226158', 2: '34040438', 3: '03415518',  4: '01029498'}),
             ('80871224585914546619083218645595', {100: '24176176'}),
             ('19617804207202209144916044189917', {100: '73745418'}),
             ('69317163492948606335995924319873', {100: '52432133'})]

do_tests()

# part2()
