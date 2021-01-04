from lark import Lark, Transformer
from itertools import combinations, chain

INPUT_FILE = "input14"
data = open(INPUT_FILE).read().strip()

grammar = r"""
start: instrs+

instrs: bitmask assignment+
bitmask: "mask" "=" DIGITS_OR_X
assignment: "mem[" INT "]" "=" INT

DIGITS_OR_X: ("0" | "1" | "X")+

%import common (WORD, INT, WS, DIGIT)
%ignore WS
"""

class FirstTransformer(Transformer):
    start = list
    instrs = tuple

    @staticmethod
    def bitmask(values):
        mask = values[0].value
        mask_1_or = int("".join("1" if x == "1" else "0" for x in mask), 2)
        mask_0_and = int("".join("0" if x == "0" else "1" for x in mask), 2)
        return (mask_1_or, mask_0_and)

    @staticmethod
    def assignment(values):
        return (int(values[0].value), int(values[1].value))


parser = Lark(
    grammar=grammar,
    transformer=FirstTransformer,
    parser="lalr",
)

test_data = """mask = XXXXXXXXXXXXXXXXXXXXXXXXXXXXX1XXXX0X
mem[8] = 11
mem[7] = 101
mem[8] = 0
mask = XXXXXXXXXXXXXXXXXXXXXXXXXXXXX1XXXX0X
mem[8] = 11
mem[7] = 101
mem[8] = 0"""


def parse_data(data):
    return parser.parse(data)

def run_instrs(instrs):
    mem = {}
    for instr in instrs:
        (mask_1_or, mask_0_and), *assigns = instr
        for ind, val in assigns:
            corrected = (val | mask_1_or) & mask_0_and
            mem[ind] = corrected
    return mem

def test():
    instrs = parse_data(test_data)
    mem = run_instrs(instrs)
    assert sum(mem.values()) == 165
test()

def first():
    instrs = parse_data(data)
    mem = run_instrs(instrs)
    print(sum(mem.values()))

first()

class SecondTransformer(Transformer):
    start = list
    instrs = tuple

    @staticmethod
    def bitmask(values):
        s = values[0].value
        mask = int("".join(x if x in "01" else "0" for x in s), 2)
        floating_bits = [ind for ind,x in enumerate(s) if x == "X"]
        return (mask, floating_bits)

    @staticmethod
    def assignment(values):
        return (int(values[0].value), int(values[1].value))


parser_v2 = Lark(
    grammar=grammar,
    transformer=SecondTransformer,
    parser="lalr",
)

instrs = parser_v2.parse(test_data)

def powerset(iterable):
    "powerset([1,2,3]) --> () (1,) (2,) (3,) (1,2) (1,3) (2,3) (1,2,3)"
    s = list(iterable)
    return chain.from_iterable(combinations(s, r) for r in range(len(s)+1))

def floating_masks(floating_bits):
    bit_flips = [int("".join(["1" if i == ind else "0" for i in range(36)]), 2) for ind in floating_bits]
    for flips in powerset(bit_flips):
        start = 0b000000000000000000000000000000000000
        for f in flips:
            start |= f
        yield start

test_data = """mask = 000000000000000000000000000000X1001X
mem[42] = 100
mask = 00000000000000000000000000000000X0XX
mem[26] = 1"""

def run_instrs_v2(instrs):
    mem = {}
    for instr in instrs:
        (mask, floating_bits), *assigns = instr
        for address, val in assigns:
            corrected = address | mask

            # print(floating_bits)
            # print(f"{corrected:036b}")
            # print()
            for f_mask in floating_masks(floating_bits):
                corrected_again = corrected ^ f_mask

                # print(f"{f_mask:036b}")
                # print(f"{corrected_again:036b}")
                # print(f"{corrected:036b}")
                mem[corrected_again] = val
    return mem

def test():
    instrs = parser_v2.parse(test_data)
    mem = run_instrs_v2(instrs)
    assert sum(mem.values()) == 208, mem
test()

def second():
    instrs = parser_v2.parse(data)
    mem = run_instrs_v2(instrs)
    return mem

