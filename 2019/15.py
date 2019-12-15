from intcode import Intcode
from random import randint
from queue import Queue
from collections import defaultdict

# ORDER = {
#     "N": 1,
#     "S": 2,
#     "W": 3,
#     "E": 4,
# }

# ODAAAAH
ORDER = {
    1j: 1,
    -1j: 2,
    -1: 3,
    1: 4,
}

# ROSE_INV = dict(((v, k) for k, v in ORDER.items()))

RESPONSE = {
    0: None,  # wall
    1: None,  # moved successfuly
    2: None,  # moved and found target
}

GROUND = "."
WALL = "#"
UNKNOWN = "?"
TARGET = "O"

def pretty_map(data: dict):
    max_x, max_y = (max(data.keys(), key=lambda z: abs(z.real)).real,
                    max(data.keys(), key=lambda z: abs(z.imag)).imag)
    max_x, max_y = int(abs(max_x)), int(abs(max_y))
    width, height = max_x * 2 + 1, max_y * 2 + 1

    picture = ""
    for x in range(-max_x, max_x+1):
        line = []
        for y in range(max_y, -max_y - 1, -1):
            val = data[complex(x,y)]
            glyph = str(val) if val else UNKNOWN
            if type(val) == int:
                if val <= 15:
                    glyph = hex(val)[2:]
                else:
                    glyph = "X"
            line.append(glyph if glyph else UNKNOWN)
        picture += "".join(line) + "\n"

    return picture


def order_and_receive(machine: Intcode, order: int):
    machine.put(int(order))
    return machine.get()


def rec_reconnaissance(machine: Intcode, terrain: dict, current_pos: complex, direction: complex, max_radius: int, move_no: int):
    new_pos = current_pos + direction
    if terrain[new_pos]:
        return
    if abs(new_pos) > max_radius:
        return

    order = ORDER[direction]
    response = order_and_receive(machine, order)

    def venture_further():
        for direction in ORDER.keys():
            rec_reconnaissance(machine, terrain, new_pos,
                               direction, max_radius, move_no + 1)

    if response == 0:
        terrain[new_pos] = WALL
        return
    elif response == 1:
        terrain[new_pos] = GROUND
        venture_further()
    elif response == 2:
        terrain[new_pos] = TARGET
        print(f"TARGET @ {new_pos} AFTER {move_no} MOVES ")
        venture_further()
    else:
        raise Exception("Unknown response.")

    # go back
    order = ORDER[-direction]
    order_and_receive(machine, order)


def do_reconnaissance(machine: Intcode, terrain=defaultdict(lambda: None),
                      max_radius=200):
    pos = 0j
    for direction in ORDER.keys():
        rec_reconnaissance(machine, terrain, pos, direction, max_radius, 1)
    return terrain


def part1():
    '''
    What is the fewest number of movement commands
    required to reach the oxygen tank?
    '''
    machine = Intcode(actual_data)
    result = do_reconnaissance(machine)
    return result

def rec_diffuse_gas(terrain, tile, turn):
    if terrain[tile] == WALL:
        return turn

    if type(terrain[tile]) == int:
        if turn >= terrain[tile]:
            return terrain[tile]

    terrain[tile] = turn

    return max([rec_diffuse_gas(terrain, tile + direction, turn + 1) for direction in ORDER.keys()])


def diffuse_gas(terrain, start):
    terrain[start] = 0
    return max([rec_diffuse_gas(terrain, start + direction, 0) for direction in ORDER.keys()])


def part2():
    terrain = part1()
    oxygen_tank = complex(-20, 18)
    turns = diffuse_gas(terrain, oxygen_tank)

    return terrain, turns

with open("input15") as fr:
    actual_data = fr.read().strip()


result = part2()
