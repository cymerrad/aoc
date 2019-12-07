from itertools import groupby
from random import shuffle

class ProgramEnd(Exception):
    pass

def parse_program(s: str):
    return [int(x) for x in s.split(",")]

base_program = []
with open("input5") as fr:
    base_program = parse_program(fr.read().strip())

def new_program_copy():
    return [x for x in base_program]


nonstdinput = []
nonstdoutput = []

mem = []
def save_at(val, r):
    global mem
    mem[r] = val

ip = 0
skip_ip_inc = False
def modifiy_ip(set_to):
    global ip
    global skip_ip_inc
    skip_ip_inc = True
    ip = set_to

ops = {
    1: (lambda a,b,r: save_at(a + b, r), "add", 3, 1),
    2: (lambda a,b,r: save_at(a * b, r), "mul", 3, 1),
    3: (lambda r: save_at(nonstdinput.pop(), r), "read", 1, 1),
    4: (lambda r: nonstdoutput.append(mem[r]), "write", 1, 1),
    5: (lambda a,b: modifiy_ip(b) if a != 0 else None, "jmp-t", 2, 0),
    6: (lambda a,b: modifiy_ip(b) if a == 0 else None, "jmp-f", 2, 0),
    7: (lambda a,b,r: save_at(1, r) if a < b else save_at(0, r), "lt", 3, 1),
    8: (lambda a,b,r: save_at(1, r) if a == b else save_at(0, r), "eq", 3, 1),
}

def get_op_with_code(code: int):
    try:
        return ops[code]
    except KeyError:
        if code == 99:
            raise ProgramEnd
        else:
            raise

def read_code(program: list, ip: int):
    val = program[ip]
    if val < 100:
        return (val, (0, 0, 0))
    full = "{:05d}".format(val)
    op_c = int(full[3:])
    op_pars = list(full[:3])
    op_pars.reverse()
    return (op_c, tuple([int(x) for x in op_pars]))

assert read_code([1], 0) == (1, (0,0,0))
assert read_code([101], 0) == (1, (1,0,0))
assert read_code([111], 0) == (11, (1,0,0))

def deref_params(program: list, mem_slice: list, params: tuple):
    def deref(val, param):
        if param == 0:
            # position mode
            return program[val]
        elif param == 1:
            # immediate mode
            return val
        else:
            raise Exception("Unknown parameter mode.")

    return [deref(v, p) for v,p in zip(mem_slice, params)]


def run_program(program: list, input_vals: list):
    global mem
    mem = program

    global nonstdinput
    global nonstdoutput

    nonstdinput = list(input_vals)
    nonstdoutput = []

    global ip
    global skip_ip_inc
    try:
        while ip < len(program):
            op_code, params = read_code(program, ip)
            op_fun, op_name, op_argc, op_ptrs = get_op_with_code(op_code)
            mem_slice = program[ip+1:ip+op_argc+1]
            arguments = mem_slice[:op_argc-op_ptrs]
            pointers = mem_slice[op_argc-op_ptrs:]
            args_deref = deref_params(program, arguments, params)
            op_fun(*args_deref, *pointers)

            if not skip_ip_inc:
                ip += op_argc + 1
            skip_ip_inc = False
    except ProgramEnd:
        wtf = [x for x in nonstdoutput]
        return wtf

# assert run_program(parse_program("3,9,8,9,10,9,4,9,99,-1,8"), [8]) == [1] # eq8
# assert run_program(parse_program("3,9,7,9,10,9,4,9,99,-1,8"), [7]) == [1] # lt8
# assert run_program(parse_program("3,3,1108,-1,8,3,4,3,99"), [8]) == [1] # eq8
# assert run_program(parse_program("3,3,1107,-1,8,3,4,3,99"), [7]) == [1] # lt8
# assert run_program(parse_program("3,12,6,12,15,1,13,14,13,4,13,99,-1,0,1,9"), [1]) == [1]
# assert run_program(parse_program("3,12,6,12,15,1,13,14,13,4,13,99,-1,0,1,9"), [0]) == [0]
# assert run_program(parse_program("3,3,1105,-1,9,1101,0,0,12,4,12,99,1"), [1]) == [1]
# assert run_program(parse_program("3,3,1105,-1,9,1101,0,0,12,4,12,99,1"), [0]) == [0]


if __name__ == "__main__":
    prog = new_program_copy()
    # prog = parse_program("3,21,1008,21,8,20,1005,20,22,107,8,21,20,1006,20,31,"
    #                     "1106,0,36,98,0,0,1002,21,125,20,4,20,1105,1,46,104,"
    #                     "999,1105,1,46,1101,1000,1,20,4,20,1105,1,46,98,99")
    res = run_program(prog, [5])
    print(res)