import sys
from lark import Lark
from lark.lexer import Token
from lark.tree import Tree
from collections import defaultdict, Counter
from dataclasses import dataclass
from functools import lru_cache
from typing import *

INPUT_FILE = "input7"
data = open(INPUT_FILE).read().strip()

l = Lark(r"""
start: sentence+

sentence: description "bags contain" bags_list "."
description: WORD WORD
bag: "1" description "bag" | INT description "bags"
bags_list: "no other bags" | (bag (",")?)+

%import common (WORD, INT, WS)
%ignore WS
"""
)

tree = l.parse(data)


@dataclass(unsafe_hash=True)
class Color:
    adj: str
    name: str


@dataclass
class CoverRule:
    outside: Color
    inside: List[Tuple[Color, int]]


def parse_description(descr: Tree) -> Color:
    assert descr.data == "description"
    [adj, name] = descr.children
    return Color(adj=adj.value, name=name.value)


def parse_bag(bag: Tree) -> Tuple[Color, int]:
    assert bag.data == "bag"

    vals = bag.children
    count = 1
    if isinstance(vals[0], Token):
        count = int(vals[0].value)
        vals = vals[1:]

    return parse_description(vals[0]), count


def parse_sentence(sentence: Tree) -> CoverRule:
    assert sentence.data == "sentence"
    [out, in_list] = sentence.children

    color_out = parse_description(out)
    colors_in = [parse_bag(b) for b in in_list.children]

    return CoverRule(outside=color_out, inside=colors_in)


def parse_tree_top(tree: Tree) -> List[CoverRule]:
    return [parse_sentence(s) for s in tree.children]


parsed = parse_tree_top(tree)


def first(rules: List[CoverRule], look_for: Color):
    contained_by = defaultdict(set)
    for b in rules:
        for color, _ in b.inside:
            contained_by[color].add(b.outside)

    to_visit = {look_for}
    visited = set()
    while to_visit:
        needle = to_visit.pop()
        visited.add(needle)

        for v in contained_by.get(needle, []):
            if v not in visited:
                to_visit.add(v)

    return visited


res = first(parsed, Color("shiny", "gold"))
print(len(res) - 1)

def count_rec(haystack: Dict[Color, Dict[Color, int]], needle: Color):

    @lru_cache
    def _rec(needle: Color):
        count = 1
        for k,v in haystack[needle].items():
            count += v * _rec(k)

        return count

    return _rec(needle)

def second(rules: List[CoverRule], look_for: Color):
    contains = defaultdict(dict)
    for b in rules:
        for color, hm in b.inside:
            contains[b.outside][color] = hm

    return count_rec(contains, look_for)

res = second(parsed, Color("shiny", "gold"))
print(res - 1)