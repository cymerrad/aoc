from lark import Lark, Transformer, Token
from typing import *
from collections import defaultdict

INPUT_FILE = "input16"
data = open(INPUT_FILE).read()

grammar = r"""
start: rules NEWLINE your_ticket NEWLINE nearby_tickets

rules: rule (NEWLINE rule)+ NEWLINE
rule: rule_name ":" range "or" range
rule_name: WORD+
range: INT "-" INT

your_ticket: "your ticket:" NEWLINE ticket NEWLINE
nearby_tickets: "nearby tickets:" NEWLINE ticket (NEWLINE ticket)+ NEWLINE?

ticket: INT ("," INT)*

NEWLINE: "\n"
%import common (WORD, INT, WS, DIGIT)
%ignore " "
"""

filter_out_tokens = lambda ll: [x for x in ll if not isinstance(x, Token)]
class InputTransformer(Transformer):
    start = filter_out_tokens

    range = lambda ll: tuple(int(x) for x in ll)
    rule_name = lambda ll: " ".join(str(x) for x in ll)
    rule = filter_out_tokens
    rules = lambda ll: ("rules", filter_out_tokens(ll))

    ticket = lambda ll: [int(x) for x in ll]
    your_ticket = lambda ll: ("yours", [x for x in ll if isinstance(x, list)][0])
    nearby_tickets = lambda ll: ("nearby", [x for x in ll if isinstance(x, list)])


parser = Lark(
    grammar=grammar,
    transformer=InputTransformer,
    parser="lalr",
)

test_data = """class: 1-3 or 5-7
row: 6-11 or 33-44
seat lol: 13-40 or 45-50

your ticket:
7,1,14

nearby tickets:
7,3,47
40,4,50
55,2,20
38,6,12"""

def parse_data(data):
    t = parser.parse(data)
    rules = next(x[1] for x in t if x[0] == "rules")
    yours = next(x[1] for x in t if x[0] == "yours")
    nearby = next(x[1] for x in t if x[0] == "nearby")
    return (rules, yours, nearby)

def annotate_nearby_tickets(rules, yours, nearby):
    possibilities_for_value = defaultdict(set)
    for rule in rules:
        [name, r1, r2] = rule
        for r in [r1, r2]:
            lo, hi = r
            for v in range(lo, hi + 1):
                possibilities_for_value[v].add(name)

    annotated_tickets = []
    for ticket in nearby:
        notes = [possibilities_for_value.get(value, None) for value in ticket]
        annotated_tickets.append(tuple([tuple(ticket), tuple(notes)]))

    return annotated_tickets

def first():
    annotated_tickets = annotate_nearby_tickets(*parse_data(data))

    sum_of_values = 0
    for ticket, notes in annotated_tickets:
        for v,n in zip(ticket, notes):
            if n is None:
                sum_of_values += v

    print(sum_of_values)

def filter_valid(annotated_tickets):
    for ticket, notes in annotated_tickets:
        for v,n in zip(ticket, notes):
            if n is None:
                break
        else:
            yield ticket, notes

def recursive_elimination(unknown: List[Tuple[int, Set[str]]], known: List[Tuple[int, str]], key: str):
    if len(unknown) > 0:
        to_diff = set([key])
        reduced = [(i, p.difference(to_diff)) for i,p in unknown]
        try:
            ind, singleton = next((i, p) for i,p in reduced if len(p) == 1)
            new_key = singleton.pop()
        except StopIteration:
            print(reduced, known, key)
            raise

        unknown = list(filter(lambda x: len(x[1]), reduced))
        known.append((ind, new_key))

        return recursive_elimination(unknown, known, new_key)

    return known

def second():
    rules, yours, nearby = parse_data(data)
    annotated_tickets = annotate_nearby_tickets(rules, yours, nearby)
    valid_tickets = [x for x in filter_valid(annotated_tickets)]

    ticket, notes = valid_tickets[0]

    possibilities = [s for s in notes]
    for ticket, notes in valid_tickets:
        possibilities = [s & n for s,n in zip(possibilities, notes)]

    ind,singleton = next((i,p) for i,p in enumerate(possibilities) if len(p) == 1)
    key = singleton.pop()
    unknown = [(i,p) for i,p in enumerate(possibilities) if len(p) > 0]

    decoded = recursive_elimination(unknown, [(ind,key)], key)

    departure_related = [x[0] for x in decoded if x[1].startswith("departure")]

    prod = 1
    for dp in departure_related:
        prod *= yours[dp]

    print(prod)



