from itertools import groupby, permutations
from functools import reduce
from queue import Queue
from threading import Thread

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


def program_closure(program, program_input, program_output_queue_pls = None):
    nonstdin = program_input
    nonstdout = []

    memory = list(program)
    def save_at(val, r):
        memory[r] = val

    ip_t = [0, False] # ip, is_dirty
    def modifiy_ip(ip_jmp):
        ip_t[0] = ip_jmp
        ip_t[1] = True

    ops = {
        1: (lambda a,b,r: save_at(a + b, r), "add", 3, 1),
        2: (lambda a,b,r: save_at(a * b, r), "mul", 3, 1),
        3: (lambda r: save_at(nonstdin.pop(), r), "read", 1, 1),
        4: (lambda r: nonstdout.append(memory[r]), "write", 1, 1),
        5: (lambda a,b: modifiy_ip(b) if a != 0 else None, "jmp-t", 2, 0),
        6: (lambda a,b: modifiy_ip(b) if a == 0 else None, "jmp-f", 2, 0),
        7: (lambda a,b,r: save_at(1, r) if a < b else save_at(0, r), "lt", 3, 1),
        8: (lambda a,b,r: save_at(1, r) if a == b else save_at(0, r), "eq", 3, 1),
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
            arguments = mem_slice[:op_argc-op_ptrs]
            pointers = mem_slice[op_argc-op_ptrs:]
            args_deref = deref_params(memory, arguments, params)
            op_fun(*args_deref, *pointers)

            if not ip_t[1]:
                ip_t[0] += op_argc + 1
            ip_t[1] = False
    except ProgramEnd:
        return nonstdout


def prog_test(input_prog, input_data):
    return program_closure(parse_program(input_prog), input_data)

assert prog_test("3,9,8,9,10,9,4,9,99,-1,8", [8]) == [1] # eq8
assert prog_test("3,9,7,9,10,9,4,9,99,-1,8", [7]) == [1] # lt8
assert prog_test("3,3,1108,-1,8,3,4,3,99", [8]) == [1] # eq8
assert prog_test("3,3,1107,-1,8,3,4,3,99", [7]) == [1] # lt8
assert prog_test("3,12,6,12,15,1,13,14,13,4,13,99,-1,0,1,9", [1]) == [1]
assert prog_test("3,12,6,12,15,1,13,14,13,4,13,99,-1,0,1,9", [0]) == [0]
assert prog_test("3,3,1105,-1,9,1101,0,0,12,4,12,99,1", [1]) == [1]
assert prog_test("3,3,1105,-1,9,1101,0,0,12,4,12,99,1", [0]) == [0]


class Amplifier():
    program = list(base_program)

    def __init__(self, name, phase):
        self.name = name
        self.phase = phase

    def run(self, inp):
        [result] = program_closure(self.program, [inp, self.phase])
        return result

_AMPS = ["A", "B", "C", "D", "E"]

def part1():
    max_pair = (0, None)

    phase_settings = permutations(range(5), 5)
    for setting in phase_settings:
        amplifiers = [Amplifier(name, phase) for name,phase in zip(_AMPS, setting)]
        result = reduce(lambda val, amp: amp.run(val), amplifiers, 0)

        if result > max_pair[0]:
            max_pair = (result, setting)

    return max_pair

class AmplifierThread(Thread):
    program = list(base_program)

    def __init__(self, name, phase, input_queue, output_queue, done_queue):
        super(AmplifierThread, self).__init__()
        self.name = name
        self.phase = phase

        self.input_queue = input_queue
        self.output_queue = output_queue
        self.done_queue = done_queue

        self.daemon = True
        self.start()

    def run(self):
        self.input_queue.put(self.phase)
        finish = program_closure(self.program, self.input_queue, self.output_queue)

        self.done_queue.get()
        self.done_queue.task_done()


def part2():
    max_pair = (0, None)

    phase_settings = permutations(range(5,10), 5)
    for setting in phase_settings:
        pipes = [Queue() for _ in range(5)]
        done = Queue(5)
        for _ in range(5):
            done.put(True)

        q_map = {
            "B": (0,1),
            "C": (1,2),
            "D": (2,3),
            "E": (3,4),
            "A": (4,0),
        }

        for name, phase in zip(_AMPS, setting):
            qs_ind = q_map[name]
            AmplifierThread(name, phase, pipes[qs_ind[0]], pipes[qs_ind[1]], done)

        pipes[0].put(0)

        done.join()
        [pipe_out] = list(filter(lambda x: not x.empty(), pipes))
        result = pipe_out.get()

        if result > max_pair[0]:
            max_pair = (result, setting)

    return max_pair

if __name__ == "__main__":
    assert part1() == (929800, (3, 4, 2, 1, 0))
    assert part2() == (15432220, (5, 7, 6, 8, 9))