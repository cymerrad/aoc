from itertools import groupby, permutations
from functools import reduce
from queue import Queue

with open("input9") as fr:
    data = fr.read().strip()

class ProgramEnd(Exception):
    pass

def parse_program(s: str):
    return [int(x) for x in s.split(",")]

with open("input7") as fr:
    base_program = parse_program(fr.read().strip())


def get_op_with_code(ops: dict, code: int):
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


def save_at(memory, val, r):
    assert r >= 0
    if r >= len(memory):
        double_it = len(memory)
        for _ in range(double_it):
            memory.append(0)
        return save_at(memory, val, r)
    memory[r] = val

def read_at(memory, r):
    assert r >= 0
    if r >= len(memory):
        double_it = len(memory)
        for _ in range(double_it):
            memory.append(0)
        return read_at(memory, r)
    return memory[r]

def deref_params(memory: list, mem_slice: list, params: tuple, rb = 0):
    def deref(val, param):
        if param == 0:
            # position mode
            return read_at(memory, val)
        elif param == 1:
            # immediate mode
            return val
        elif param == 2:
            # relative mode
            return read_at(memory, rb+val)
        else:
            raise Exception("Unknown parameter mode.")

    return [deref(v, p) for v,p in zip(mem_slice, params)]

def mangle_ptrs(memory: list, mem_slice: list, params: tuple, rb = 0):
    pass

def program_closure(program, program_input, program_output_queue_pls = None):
    nonstdin = program_input
    nonstdout = []

    memory = list(program)

    ip_t = [0, False] # ip, is_dirty
    def modify_ip(ip_jmp):
        ip_t[0] = ip_jmp
        ip_t[1] = True

    rel_base = [0]
    def modify_rb(rb_change):
        rel_base[0] += rb_change

    ops = {
        1: (lambda a,b,r: save_at(memory, a + b, r), "add", 3, 1),
        2: (lambda a,b,r: save_at(memory, a * b, r), "mul", 3, 1),
        3: (lambda r: save_at(memory, nonstdin.pop(), r), "read", 1, 1),
        4: (lambda r: nonstdout.append(read_at(memory, r)), "write", 1, 1),
        5: (lambda a,b: modify_ip(b) if a != 0 else None, "jmp-t", 2, 0),
        6: (lambda a,b: modify_ip(b) if a == 0 else None, "jmp-f", 2, 0),
        7: (lambda a,b,r: save_at(memory, 1, r) if a < b else save_at(memory, 0, r), "lt", 3, 1),
        8: (lambda a,b,r: save_at(memory, 1, r) if a == b else save_at(memory, 0, r), "eq", 3, 1),
        9: (lambda a: modify_rb(a), "mod-rb", 1,0),
    }

    if type(nonstdin) == Queue:
        ops[3] = (lambda r: save_at(nonstdin.get(), r), "read", 1, 1)

    if program_output_queue_pls and type(program_output_queue_pls) == Queue:
        nonstdout = program_output_queue_pls
        ops[4] = (lambda r: nonstdout.put(memory[r]), "write", 1, 1)

    try:
        while ip_t[0] < len(memory):
            ip = ip_t[0]
            op_code, params = read_code(memory, ip)
            op_fun, op_name, op_argc, op_ptrs = get_op_with_code(ops, op_code)
            mem_slice = memory[ip+1:ip+op_argc+1]
            # arguments = mem_slice[:op_argc-op_ptrs]
            # pointers = mem_slice[op_argc-op_ptrs:]
            args_deref = deref_params(memory, mem_slice, params, rel_base[0])
            # ptrs_mangled = mangle_ptrs(memory, pointers, params[-op_ptrs:], rel_base[0])
            op_fun(*args_deref)

            if not ip_t[1]:
                ip_t[0] += op_argc + 1
            ip_t[1] = False
    except ProgramEnd:
        return nonstdout


def prog_test(input_prog, input_data = []):
    return program_closure(parse_program(input_prog), input_data)

# assert prog_test("3,9,8,9,10,9,4,9,99,-1,8", [8]) == [1] # eq8
# assert prog_test("3,9,7,9,10,9,4,9,99,-1,8", [7]) == [1] # lt8
# assert prog_test("3,3,1108,-1,8,3,4,3,99", [8]) == [1] # eq8
# assert prog_test("3,3,1107,-1,8,3,4,3,99", [7]) == [1] # lt8
# assert prog_test("3,12,6,12,15,1,13,14,13,4,13,99,-1,0,1,9", [1]) == [1]
# assert prog_test("3,12,6,12,15,1,13,14,13,4,13,99,-1,0,1,9", [0]) == [0]
# assert prog_test("3,3,1105,-1,9,1101,0,0,12,4,12,99,1", [1]) == [1]
# assert prog_test("3,3,1105,-1,9,1101,0,0,12,4,12,99,1", [0]) == [0]

test_data = "109,1,204,-1,1001,100,1,100,1008,100,16,101,1006,101,0,99"
test_res = prog_test(test_data)
assert test_res == parse_program(test_data), test_res

test_res_1 = prog_test("1102,34915192,34915192,7,4,7,99,0")
assert len(str(test_res_1[0])) == 16, test_res_1

test_data_2 = "104,1125899906842624,99"
test_res_2 = prog_test(test_data)
assert test_res_2 == int(test_data_2.split(",")[1]), test_res_2