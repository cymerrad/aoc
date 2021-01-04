import re
from lark import Lark, Transformer, Token
from typing import *
from operator import mul, add

from lark.tree import Tree

INPUT_FILE = "input18"
data = open(INPUT_FILE).read()

grammar = r"""
start: expr+

expr: multiplication | addition | atom
atom: VALUE | "(" expr ")"
VALUE: INT

multiplication: expr "*" atom
addition: expr "+" atom

NEWLINE: "\n"
%import common (WORD, INT, WS, DIGIT)
%ignore WS
"""


class InputTransformer(Transformer):
    # start = lambda ll: [x for x in ll if not isinstance(x, Token)]
    start = list
    multiplication = lambda x: (mul,) + tuple(x)
    addition = lambda x: (add,) + tuple(x)
    expr = lambda x: list(x)[0]

    def atom(values):
        try:
            return int(values[0])
        except TypeError:
            return tuple(values[0])


parser = Lark(
    grammar=grammar,
    transformer=InputTransformer,
    parser="lalr",
)

t = parser.parse(data)

'''
expr_line_re = re.compile(
    r"""(?mx)
(?:
    (?P<number>\d+)|
    (?P<add>\+)|
    (?P<mul>\*)|
    (?P<lparen>\()|
    (?P<rparen>\))
)
"""
)

def parse_line(line: str):
    # (op, left, right)
    tree = []
    stack = []
    matches = list(expr_line_re.finditer(line))

    for match in matches:
        term, value = [(t, v) for t, v in match.groupdict().items() if v][0]
        if term == "lparen":
            pass
        elif term == "rparen":
            pass
        elif term == "number":
            pass
        elif term == "add":
            pass
        elif term == "mul":
            pass
        else:
            raise Exception("Unknown term")
'''


def eval_tree(tree: Union[Tuple, int]):
    if isinstance(tree, tuple):
        op, l, r = tree
        return op(eval_tree(l), eval_tree(r))
    elif isinstance(tree, int):
        return tree
    else:
        raise ValueError(f"Unknown {tree}")


test_data = {"1 + 2 * 3 + 4 * 5 + 6": 71, "1 + (2 * 3) + (4 * (5 + 6))": 51}


def test():
    for line, r in test_data.items():
        t = parser.parse(line)

        res = eval_tree(t[0])
        assert res == r, f"Should be {r} we got {res}"


test()


def first():
    ts = parser.parse(data)
    evald = [eval_tree(t) for t in ts]
    print(sum(evald))


first()

grammar_v2 = r"""
start: expr+

expr: multiplication | addition | atom
atom: VALUE | "(" expr ")"
VALUE: INT

multiplication: expr "*" expr
addition: expr "+" atom

NEWLINE: "\n"
%import common (WORD, INT, WS, DIGIT)
%ignore WS
"""

parser_v2 = Lark(
    grammar=grammar_v2,
    transformer=InputTransformer,
    parser="lalr",
)

test_data = {
    "1 + 2 * 3 + 4 * 5 + 6": 231,
    "1 + (2 * 3) + (4 * (5 + 6))": 51,
    "2 * 3 + (4 * 5)": 46,
    "5 + (8 * 3 + 9 + 3 * 4 * 3)": 1445,
    "5 * 9 * (7 * 3 * 3 + 9 * 3 + (8 + 6 * 4))": 669060,
    "((2 + 4 * 9) * (6 + 9 * 8 + 6) + 6) + 2 + 4 * 2": 23340,
}


def test():
    for line, r in test_data.items():
        t = parser_v2.parse(line)

        res = eval_tree(t[0])
        assert res == r, f"{line} should be {r}; we got {res}"


test()


def second():
    ts = parser_v2.parse(data)
    evald = [eval_tree(t) for t in ts]
    print(sum(evald))


second()