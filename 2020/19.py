import re
from lark import Lark, Transformer, Token
from lark.exceptions import UnexpectedToken, UnexpectedCharacters, UnexpectedEOF
from lark.tree import Tree
from typing import *

INPUT_FILE = "input19"
data = open(INPUT_FILE).read()

def parse_input(data: str):
    grammar, messages = data.split("\n\n")
    grammar = re.sub(r"(\d+)", r"id\1", grammar)

    lark_grammar = """
start: id0
{}
%import common.WS
%ignore WS
    """.format(
        grammar
    )

    parser = Lark(
        grammar=lark_grammar,
    )

    return parser, messages.strip().split("\n")


test_data = """0: 4 1 5
1: 2 3 | 3 2
2: 4 4 | 5 5
3: 4 5 | 5 4
4: "a"
5: "b"

ababbb
bababa
abbbab
aaabbb
aaaabbb"""


def count_matching(data: str, replacements=[], debug=False):
    for replacement in replacements:
        if debug:
            print("Replacing {} for {}".format(*replacement))
        data = data.replace(*replacement)

    parser, messages = parse_input(data)
    count = 0

    if debug:
        _print = print
    else:
        _print = lambda x: None

    for m in messages:
        try:
            parsed = parser.parse(m)
            count += 1
            _print(f"OK\t{m}")
        except (UnexpectedToken, UnexpectedCharacters, UnexpectedEOF):
            _print(f"FAIL\t{m}")

    return count


def test():
    count = count_matching(test_data)
    assert count == 2

test()


def first():
    count = count_matching(data)

    print(f"Matched {count}")

test_data = """42: 9 14 | 10 1
9: 14 27 | 1 26
10: 23 14 | 28 1
1: "a"
11: 42 31
5: 1 14 | 15 1
19: 14 1 | 14 14
12: 24 14 | 19 1
16: 15 1 | 14 14
31: 14 17 | 1 13
6: 14 14 | 1 14
2: 1 24 | 14 4
0: 8 11
13: 14 3 | 1 12
15: 1 | 14
17: 14 2 | 1 7
23: 25 1 | 22 14
28: 16 1
4: 1 1
20: 14 14 | 1 15
3: 5 14 | 16 1
27: 1 6 | 14 18
14: "b"
21: 14 1 | 1 14
25: 1 1 | 1 14
22: 14 14
8: 42
26: 14 22 | 1 20
18: 15 15
7: 14 5 | 1 21
24: 14 1

abbbbbabbbaaaababbaabbbbabababbbabbbbbbabaaaa
bbabbbbaabaabba
babbbbaabbbbbabbbbbbaabaaabaaa
aaabbbbbbaaaabaababaabababbabaaabbababababaaa
bbbbbbbaaaabbbbaaabbabaaa
bbbababbbbaaaaaaaabbababaaababaabab
ababaaaaaabaaab
ababaaaaabbbaba
baabbaaaabbaaaababbaababb
abbbbabbbbaaaababbbbbbaaaababb
aaaaabbaabaaaaababaa
aaaabbaaaabbaaa
aaaabbaabbaaaaaaabbbabbbaaabbaabaaa
babaaabbbaaabaababbaabababaaab
aabbbbbaabbbaaaaaabbbbbababaaaaabbaaabba
"""

replacements = [
    ["8: 42", "8: 42 | 42 8"],
    ["11: 42 31", "11: 42 31 | 42 11 31"],
]

def test():
    count = count_matching(test_data, replacements=replacements, debug=True)

    print(f"Matched {count}")

test()

def second():
    count = count_matching(data, replacements=replacements)

    print(f"Matched {count}")

# second()