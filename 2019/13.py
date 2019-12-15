from intcode import Intcode
import numpy as np
from queue import Empty
import time

EMPTY = 0
WALL = 1
BLOCK = 2
PADDLE = 3
BALL = 4
TILES = {
    0: " ",
    1: "#",
    2: "@",
    3: "_",
    4: "o",
}

with open("input13") as fr:
    actual_data = fr.read().strip()

def group_in_triples():
    machine = Intcode(actual_data)
    result = machine.wait_for_result()
    grouped = zip(*(iter(result),) * 3)
    return list(grouped)

def part1():
    triples = group_in_triples()
    return len(set(filter(lambda t: t[2] == BLOCK, triples)))

def _display_tile(tile):
    return TILES[tile]

def _display_line(line):
    return "".join((_display_tile(tile) for tile in line))

def display(screen, score):
    return "\n".join([
        _display_line(line) for line in screen
    ]) + "\n" + str(score)

def read_n_triples(m: Intcode, n):
    for _ in range(n):
        yield (m.get(),m.get(), m.get())

def read_greedy(m: Intcode):
    try:
        while True:
            yield tuple((m.nonstdout.get(block=False) for _ in range(3)))
    except Empty:
        return

CONTROLS = {
    "a": -1,
    "d": 1,
    "": 0,
}

def lets_play_a_game(step_time=0.1, show=True):
    # dimensions first
    triples = group_in_triples()
    max_x = max(triples, key=lambda t: t[0])[0]
    max_y = max(triples, key=lambda t: t[1])[1]
    # 45 x 24
    width, height = max_x + 1, max_y + 1
    screen = np.zeros((height, width), dtype=int)
    score = 0

    program = Intcode.parse_program(actual_data)
    program[0] = 2
    machine = Intcode(program)
    time.sleep(1)
    ball_pos_x = 0
    paddle_pos_x = 0
    while machine.running:
        read_in = 0
        for triple in read_greedy(machine):
            read_in += 1

            if triple[0] == -1:
                score = triple[2]
                continue
            if triple[2] == BALL:
                ball_pos_x = triple[0]
            if triple[2] == PADDLE:
                paddle_pos_x = triple[0]

            if show:
                screen[triple[1], triple[0]] = triple[2]

        if show:
            print(display(screen, score))

        move = 0
        if ball_pos_x > paddle_pos_x:
            move = 1
        if ball_pos_x < paddle_pos_x:
            move = -1

        machine.put(move)
        time.sleep(step_time)

    try:
        [final_score] = filter(lambda tr: tr[0] == -1, read_greedy(machine))
        score = final_score[2]
    except ValueError:
        pass

    return machine, score

def part2():
    _, res = lets_play_a_game(step_time=0.03, show=False)
    return res
