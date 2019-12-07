import numpy as np
from functools import reduce
import json


wires_data0 = ["R8,U5,L5,D3".split(","), "U7,R6,D4,L4".split(",")]

wires_data1 = [x.split(",") for x in "R98,U47,R26,D63,R33,U87,L62,D20,R33,U53,R51\n"
              "U98,R91,D20,R16,D67,R40,U7,R15,U6,R7".split("\n")]

wires_data2 = ["R75,D30,R83,U83,L12,D49,R71,U7,L72".split(","),
              "U62,R66,U55,R34,D71,R55,D58,R83".split(",")]


wires_data_final = []
with open("input3") as fr:
    for line in fr:
        directions = line.strip().split(",")
        wires_data_final.append(directions)

# with open("input3_2") as fr:
#     intersections_precomp = json.load(fr)


def parse_instruction(instruction: str):
    "Returns a vector (X,Y)"
    direction = instruction[0]
    value = int(instruction[1:])
    if direction == "R":
        return np.array([value, 0])
    elif direction == "L":
        return np.array([-value, 0])
    elif direction == "U":
        return np.array([0, value])
    elif direction == "D":
        return np.array([0, -value])
    else:
        raise Exception("Invalid instruction.")


_loop_test = "U100,R100,D100,L100"
_instrs = [parse_instruction(x) for x in _loop_test.split(",")]
_res = sum(_instrs)
assert _res[0] == 0 and _res[1] == 0


def foldl_sum(acc, new):
    s = new + acc[-1]
    return acc + [s]

def calculate_for_wires(wires_data):
    zero = np.array([0, 0])

    first = [parse_instruction(x) for x in wires_data[0]]
    second = [parse_instruction(x) for x in wires_data[1]]
    # first_p = reduce(foldl_sum, first, [zero])
    # second_p = reduce(foldl_sum, second, [zero])

    # max_abs_x = max(first_p + second_p, key=lambda x: abs(x[0]))[0]
    # max_abs_y = max(first_p + second_p, key=lambda x: abs(x[1]))[1]

    # grid_x = round(max_abs_x + 51, -2)
    # grid_y = round(max_abs_y + 51, -2)

    # grid = np.zeros([grid_x, grid_y], dtype=bool)
    grid = {}
    zero = np.array([0, 0])
    # zero = np.array([grid_x//2, grid_y//2])

    grid[tuple(zero)] = 0
    moves = 0

    pos = np.copy(zero)
    for nmv in first:
        moves -= 1
        begin = pos
        end = pos + nmv
        # x1, x2 = min(begin[0], end[0]), max(begin[0], end[0])
        # y1, y2 = min(begin[1], end[1]), max(begin[1], end[1])
        x1, x2, sx = begin[0], end[0], 1 if end[0] >= begin[0] else -1
        y1, y2, sy = begin[1], end[1], 1 if end[1] >= begin[1] else -1
        x2 += sx
        y2 += sy
        for x in range(x1, x2, sx):
            for y in range(y1, y2, sy):
                moves += 1
                try:
                    grid[(x, y)]
                except KeyError:
                    grid[(x, y)] = moves

        # gv = grid[x1:(x2+1), y1:(y2+1)]
        # for ind, _ in np.ndenumerate(gv):
        #     gv[tuple(ind)] += 1
        pos = np.copy(end)

    intersections = []

    moves = 0
    pos = np.copy(zero)
    for nmv in second:
        moves -= 1
        begin = pos
        end = pos + nmv
        x1, x2, sx = begin[0], end[0], 1 if end[0] >= begin[0] else -1
        y1, y2, sy = begin[1], end[1], 1 if end[1] >= begin[1] else -1
        x2 += sx
        y2 += sy
        for x in range(x1, x2, sx):
            for y in range(y1, y2, sy):
                moves += 1
                try:
                    grid[(x, y)]
                    # intersections.append((x,y))
                    intersections.append((x, y, grid[(x, y)], moves))
                except KeyError:
                    continue

        # gv = grid[x1:(x2+1), y1:(y2+1)]
        # for ind, _ in np.ndenumerate(gv):
        #     gv[tuple(ind)] += 1
            # if gv[tuple(ind)] == 1:
            #     intersections.append(...)
        pos = np.copy(end)

    try:
        intersections.remove((0, 0, 0, 0))
    except ValueError:
        pass
    # intersections = [np.array(x) for x in intersections]
    # intersections = [x - zero for x in intersections]

    # distances = [abs(x[0]) + abs(x[1]) for x in intersections]
    # result = min(zip(distances, intersections), key=lambda x: x[0])

    result = min(intersections, key=lambda four: four[2] + four[3])
    return result

if __name__ == "__main__":
    results = [
        calculate_for_wires(p[1]) for p in filter(lambda p: p[0].startswith("wires_data"), locals().items())
    ]
    print([x[2] + x[3] for x in results])