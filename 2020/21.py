from collections import defaultdict, deque
from functools import partial, reduce
from itertools import product
from lark import Lark, Transformer, Token
from typing import *
from lark.tree import Tree
from utils import compose

INPUT_FILE = "input21"
data = open(INPUT_FILE).read()

grammar = r"""
start: line+

line: ingredients "(contains" allergens ")"
ingredients: WORD+
allergens: WORD ("," WORD)*

NEWLINE: "\n"
%import common (WORD, INT, WS, DIGIT)
%ignore WS
"""


class InputTransformer(Transformer):
    start = compose(dict, enumerate)
    line = tuple
    ingredients = compose(list, partial(map, lambda w: w.value))
    allergens = ingredients


parser = Lark(
    grammar=grammar,
    transformer=InputTransformer,
    parser="lalr",
)

Product = Tuple[int, Tuple[List[str], List[str]]]

def allergen_map(products: Dict[int, Product]) -> Dict[str, str]:
    "{allergen -> ingredient}"
    possible_sources: Dict[str, Set[str]] = {}

    for product_id, product in products.items():
        ingredients, allergens = product
        for allergen in allergens:
            if not possible_sources.get(allergen, False):
                possible_sources[allergen] = set(ingredients)
            else:
                possible_sources[allergen] &= set(ingredients)

    certain = list(filter(lambda s: len(s) == 1, possible_sources.items()))
    known_sources = set(map(lambda t: list(t[1])[0], certain))
    unknown = deque(filter(lambda s: len(s) != 1, possible_sources.items()))
    while unknown:
        a, sources = unknown.popleft()
        sieved = sources - known_sources
        if len(sieved) == 1:
            known_sources.add(list(sieved)[0])
            certain.append((a, sieved))
        elif len(sieved) > 1:
            unknown.append((a, sieved))
        else:
            raise Exception("We fell below zero in number of elements")

    return {k:list(v)[0] for k,v in certain}

def get_safe_ingredients(products: Dict[int, Product], allergens_map: Dict[str, str]) -> Set[str]:
    ingredients_map = {v:k for k,v in allergens_map.items()}
    safe = set()
    for product_id, product in products.items():
        ingredients, allergens = product
        for ingredient in ingredients:
            if ingredient not in ingredients_map.keys():
                safe.add(ingredient)

    return safe

def count_occurences_of_ingredients(products: Dict[int, Product], safe_ingredients: Set[str]) -> int:
    occurences = 0
    for product_id, product in products.items():
        ingredients, allergens = product
        occurences += len(safe_ingredients & set(ingredients))

    return occurences

test_data = """
mxmxvkd kfcds sqjhc nhms (contains dairy, fish)
trh fvjkl sbzzf mxmxvkd (contains dairy)
sqjhc fvjkl (contains soy)
sqjhc mxmxvkd sbzzf (contains fish)
"""

def test():
    t = parser.parse(test_data)

    allergens_map = allergen_map(t)

    safe = get_safe_ingredients(t, allergens_map)

    assert len(safe & {'kfcds', 'nhms', 'trh', 'sbzzf'}) == 4

    count = count_occurences_of_ingredients(t, safe)

    assert count == 5

test()

def both():
    products = parser.parse(data)
    allergens_map = allergen_map(products)
    safe = get_safe_ingredients(products, allergens_map)
    count = count_occurences_of_ingredients(products, safe)

    print(f"Repeating number of occurences is {count}")

    ingredients = list((v,k) for k,v in allergens_map.items())
    canonical_ingredients = map(lambda pair: pair[0], sorted(ingredients, key=lambda pair: pair[1]))
    print(",".join(canonical_ingredients))

both()