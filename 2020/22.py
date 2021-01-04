from collections import deque
from typing import *
from utils import compose

INPUT_FILE = "input22"
data = open(INPUT_FILE).read()


def parse_data(data: str):
    p1_cards, p2_cards = data.strip().split("\n\n")

    ll = lambda cards: list(map(int, cards.split("\n")[1:]))
    p1, p2 = list(map(ll, [p1_cards, p2_cards]))

    return (p1, p2)


def play_game(p1: List[int], p2: List[int]) -> Tuple[int, int]:
    "(winner, score)"
    p1 = deque(p1)
    p2 = deque(p2)

    while p1 and p2:
        c1 = p1.popleft()
        c2 = p2.popleft()

        if c1 > c2:
            p1.append(c1)
            p1.append(c2)
        else:
            p2.append(c2)
            p2.append(c1)

    winner = 1 if p1 else 2
    winner_cards = p1 if p1 else p2
    score = sum(weight * card for weight, card in enumerate(reversed(winner_cards), 1))

    return winner, score


test_data = """Player 1:
9
2
6
3
1

Player 2:
5
8
4
7
10"""


def test():
    p1, p2 = parse_data(test_data)
    assert p1 == list(map(int, "9 2 6 3 1".split())), p1
    assert p2 == list(map(int, "5 8 4 7 10".split())), p2

    winner, score = play_game(p1, p2)
    assert winner == 2
    assert score == 306, score


test()


def first():
    p1, p2 = parse_data(data)
    winner, score = play_game(p1, p2)
    print(f"Winner is {winner} with score {score}")


first()


DEBUG = True
_print = print if DEBUG else lambda _: None

def recursive_combat_game(
    seen_states: FrozenSet[Tuple[FrozenSet[int], FrozenSet[int]]],
    p1: Deque[int],
    p2: Deque[int],
    game_id = 1,
) -> Tuple[int, Deque[int], Deque[int]]:
    seen_states = frozenset()

    round = 0
    while p1 and p2:
        state = (frozenset(p1), frozenset(p2))

        round += 1
        _print(f"Game {game_id} | round {round}")

        if state in seen_states:
            return (1, p1, p2)
        else:
            seen_states = seen_states | {state}

        c1 = p1.popleft()
        c2 = p2.popleft()

        if len(p1) >= c1 and len(p2) >= c2:
            p1_copy = deque(list(p1)[:c1])
            p2_copy = deque(list(p2)[:c2])

            winner, p1_copy, p2_copy = recursive_combat_game(
                frozenset(), p1_copy, p2_copy, game_id + 1
            )

        else:
            winner = 1 if c1 > c2 else 2

        if winner == 1:
            p1.append(c1)
            p1.append(c2)
        else:
            p2.append(c2)
            p2.append(c1)

    winner = 1 if p1 else 2
    return winner, p1, p2


def play_game_v2(p1: List[int], p2: List[int]) -> Tuple[int, int]:
    "(winner, score)"
    p1 = deque(p1)
    p2 = deque(p2)

    seen_states = frozenset()
    winner, p1, p2 = recursive_combat_game(seen_states, p1, p2)

    winner_cards = p1 if winner == 1 else p2
    score = sum(weight * card for weight, card in enumerate(reversed(winner_cards), 1))

    return winner, score


def test():
    p1, p2 = parse_data(test_data)
    winner, score = play_game_v2(p1, p2)
    assert winner == 2
    assert score == 291


test()


def second():
    p1, p2 = parse_data(data)
    winner, score = play_game_v2(p1, p2)
    print(f"Winner is {winner} with score {score}")


second()