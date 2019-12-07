from itertools import groupby
from random import shuffle

class ProgramEnd(Exception):
    pass

base_program = []
with open("input3") as fr:
    nums = fr.read().strip().split(',')
    base_program = [int(x) for x in nums]

ops = {
    1: lambda a,b: a + b,
    2: lambda a,b: a * b,
}

def get_op_with_code(code: int):
    try:
        return ops[code]
    except KeyError:
        if code == 99:
            raise ProgramEnd
        else:
            raise

def new_program_copy():
    return [x for x in base_program]

def show_program(prog: list):
    end = prog.index(99)
    grouped = zip(*(iter(program[:end]),) * 4)
    for group in grouped:
        print(",".join([str(x) for x in group]))
    print(prog[end+1:])

def run_program(program: list, noun = None, verb = None):
    noun = noun or base_program[1]
    verb = verb or base_program[2]

    program[1] = noun
    program[2] = verb

    ip = 0 # instruction pointer
    try:
        while ip < len(program):
            op_code = program[ip]
            op = get_op_with_code(op_code)
            ax = program[ip + 1]
            bx = program[ip + 2]
            rx = program[ip + 3]

            program[rx] = op(program[ax], program[bx])

            ip += 4
    except ProgramEnd:
        # show_program(program)
        return program[0]


WANTED = 19690720

class Success(Exception):
    pass

if __name__ == "__main__":
    # text_data = "1,9,10,3,2,3,11,0,99,30,40,50"
    # program = [int(x) for x in text_data.split(',')]

    # 4576384
    # print(run_program(new_program_copy(), 12, 2))

    pairs = [(m,n) for m in range(1,100) for n in range(1,100)]
    shuffle(pairs)

    for noun,verb in pairs:
        result = run_program(new_program_copy(), noun, verb)
        if result == WANTED:
            raise Success(f"SUCCESS {noun} {verb} -> {100 * noun + verb}")


    raise Exception("Failure")