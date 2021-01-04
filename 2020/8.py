import re
from typing import *

data = open("input8").read().strip()


instr_line_re = re.compile(r"(\w+) (\+|-)(\d+)")


def parse_ops(data: str) -> List[Tuple[str, int]]:
    ops = []
    for m in instr_line_re.finditer(data):
        (op, sign, value) = m.groups()
        ops.append((op, (1 if sign == "+" else -1) * int(value)))

    return ops


ops = parse_ops(data)


def first(ops: List[Tuple[str, int]]):
    acc = 0
    pc = 0

    visited = set()
    while pc < len(ops):
        op, val = ops[pc]

        if pc in visited:
            print(f"{pc}: {op} {val} | {acc}")
            print(f"VISITING {pc} 2nd TIME")
            break
        else:
            visited.add(pc)

        if op == "acc":
            acc += val
        elif op == "nop":
            pass
        elif op == "jmp":
            pc += val
            continue

        else:
            assert False, f"unknown op {op} @ {pc}"

        pc += 1

    return acc, pc


class Loop(Exception):
    ...


def execute_ops(ops: List[Tuple[str, int]]) -> Tuple[int, int]:
    acc = 0
    pc = 0

    visited = set()
    while pc < len(ops):
        op, val = ops[pc]

        if pc in visited:
            raise Loop
        else:
            visited.add(pc)

        if op == "acc":
            acc += val
        elif op == "nop":
            pass
        elif op == "jmp":
            pc += val
            continue

        else:
            assert False, f"unknown op {op} @ {pc}"

        pc += 1

    return acc, pc


def second(ops: List[Tuple[str, int]]):
    ops = [x for x in ops]
    for ind in range(len(ops)):
        cur_op = tuple(ops[ind])

        if ops[ind][0] == "nop":
            ops[ind] = ("jmp", ops[ind][1])

        elif ops[ind][0] == "jmp":
            ops[ind] = ("nop", ops[ind][1])

        try:
            (acc, pc) = execute_ops(ops)
            print(f"Flipped {ind} to {ops[ind]} | {acc} {pc}")
            break
        except Loop:
            pass
        finally:
            ops[ind] = cur_op


second(ops)
