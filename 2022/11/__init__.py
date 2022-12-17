from collections import defaultdict, deque, namedtuple
from dataclasses import dataclass, field
from operator import mul
from typing import *
from lark import Lark, Transformer
import tqdm
from math import floor, sqrt


@dataclass
class Monke:
    id: int
    items: deque[int]
    op: Callable
    div_t: int
    if_t: int
    if_f: int

    def __post_init__(self):
        self.op = eval("lambda old:" + " ".join(str(x) for x in self.op[1:]))
        self.items = deque(self.items)
        self.inspections = 0

    def __repr__(self):
        return f"Monkey {self.id}: " + ", ".join(str(x) for x in self.items)

    def turn(self, verbose=True):
        "Results in a throw to Monke with some id"
        try:
            # output = f"Monkey {self.id}:\n"
            item = self.items.popleft()
            self.inspections += 1
            # output += f"  Monkey inspects an item with a worry level of {item}.\n"
            worry = self.op(item)
            # output += f"    Worry level is multiplied by 19 to 1501."
            worry = worry // 3
            # output += f"    Monkey gets bored with item. Worry level is divided by 3 to 500."
            throw_target = self.if_t if worry % self.div_t == 0 else self.if_f
            # output += f"    Current worry level is not divisible by 23."
            # output += f"    Item with worry level 500 is thrown to monkey 3."
            return (worry, throw_target)
        except IndexError:
            return None

    def receive(self, item):
        self.items.append(item)

    def repr_inspections(self):
        return f"Monkey {self.id} inspected items {self.inspections} times."


# @dataclass
# class Item:
#     val: int
#     passed = 0
#     idgaf = False

#     IDGAF_THRESHOLD = 2 ** 32

#     def __post_init__(self):
#         self.init_worry = self.val

#     def __add__(self, n: int):
#         self.passed += 1

#         if self.idgaf:
#             return self

#         self.val += n
#         return self

#     def __mul__(self, arg: int | "Item"):
#         self.passed += 1

#         if self.idgaf:
#             return self

#         if type(arg) is Item:
#             self.val *= arg.val
#         else:
#             self.val *= arg

#         if self.val >= self.IDGAF_THRESHOLD:
#             self.idgaf = True

#         return self

class MonkeFast(Monke):
    # def __post_init__(self):
    #     self.op = eval("lambda old:" + " ".join(str(x) for x in self.op[1:]))
    #     self.items = deque(Item(i) for i in self.items)
    #     self.inspections = 0

    def turn(self):
        try:
            item = self.items.popleft()
            self.inspections += 1
            worry = self.op(item)
            throw_target = self.if_t if worry % self.div_t == 0 else self.if_f
            return (worry, throw_target)
        except IndexError:
            return None


@dataclass
class Game:
    monkeys: list[Monke]
    ms: dict[int, Monke] = field(init=False)

    def __post_init__(self):
        self.ms = {}
        self.mod_all = 1
        for m in self.monkeys:
            self.ms[m.id] = m

            self.mod_all *= m.div_t


    def round(self):
        for m in self.monkeys:
            while res := m.turn():
                (item, target) = res

                item_m = item % self.mod_all
                # print(f"{item} -> {item_m}")

                self.ms[target].receive(item_m)

    def __repr__(self):
        return "\n".join(str(m) for m in self.monkeys)


class OptimusPrime(Transformer):
    def num(self, n):
        (n,) = n
        return int(n)

    start = list

    monkey = tuple

    items = list
    op = tuple
    test = num
    if_true = num
    if_false = num
    OP = str
    CNAME = str
    NUMBER = int


grammar = r"""
    start: monkey+
    monkey: "Monkey" NUMBER ":" items op test if_true if_false

    items: "Starting" "items" ":" (NUMBER ",")* NUMBER
    op: "Operation" ":" CNAME "=" (CNAME|NUMBER) OP (CNAME|NUMBER)
    test: "Test" ":" "divisible" "by" NUMBER
    if_true: "If" "true" ":" "throw" "to" "monkey" NUMBER
    if_false: "If" "false" ":" "throw" "to" "monkey" NUMBER

    OP: ("+"|"*")

    %import common.ESCAPED_STRING   -> STRING
    %import common.INT              -> NUMBER
    %import common.CNAME

    %import common.WS
    %import common.WS_INLINE
    %import common.NEWLINE
    %ignore WS
    """


def parse(input: str, *args, **kwargs):
    parser = Lark(grammar, start="start", lexer="basic")

    # return parser.parse(input.strip())
    return OptimusPrime().transform(parser.parse(input.strip()))


def solve_1(data: list, *args, debug=False, test=False, **kwargs):
    monkeys = [Monke(*m) for m in data]
    g = Game(monkeys)

    for _ in range(20):
        g.round()

    if test:
        return "\n".join([m.repr_inspections() for m in g.monkeys])

    else:
        inspx = [m.inspections for m in g.monkeys]
        inspx.sort(reverse=True)
        return mul(*inspx[:2])


def solve_2(data, *args, debug=False, test=False, **kwargs):
    monkeys = [MonkeFast(*m) for m in data]
    g = Game(monkeys)

    for r in tqdm.trange(10_000):
        g.round()

    inspx = [m.inspections for m in g.monkeys]
    inspx.sort(reverse=True)

    print("\n".join([m.repr_inspections() for m in g.monkeys]))

    return mul(*inspx[:2])


def test(*args, debug=False, test=False, **kwargs):
    raise NotImplementedError


TEST_INPUT = """
Monkey 0:
  Starting items: 79, 98
  Operation: new = old * 19
  Test: divisible by 23
    If true: throw to monkey 2
    If false: throw to monkey 3

Monkey 1:
  Starting items: 54, 65, 75, 74
  Operation: new = old + 6
  Test: divisible by 19
    If true: throw to monkey 2
    If false: throw to monkey 0

Monkey 2:
  Starting items: 79, 60, 97
  Operation: new = old * old
  Test: divisible by 13
    If true: throw to monkey 1
    If false: throw to monkey 3

Monkey 3:
  Starting items: 74
  Operation: new = old + 3
  Test: divisible by 17
    If true: throw to monkey 0
    If false: throw to monkey 1
"""

TEST_RESULT_1 = """
Monkey 0 inspected items 101 times.
Monkey 1 inspected items 95 times.
Monkey 2 inspected items 7 times.
Monkey 3 inspected items 105 times.
""".strip()

TEST_RESULT_2 = 2713310158
