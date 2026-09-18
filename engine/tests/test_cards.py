from __future__ import annotations

import pytest

from truco_engine.cards import (
    DECK,
    NUMBERS,
    TRUCO_RANK,
    Suit,
    card_number,
    card_str,
    compare_cards,
    envido_points,
    make_card,
    sort_slots,
    truco_rank,
)

E, B, O, C = Suit.ESPADA, Suit.BASTO, Suit.ORO, Suit.COPA


def test_deck_has_40_cards_without_8_and_9() -> None:
    assert len(DECK) == 40
    assert len(set(DECK)) == 40
    numbers = {card_number(c) for c in DECK}
    assert 8 not in numbers
    assert 9 not in numbers
    assert numbers == set(NUMBERS)


def test_canonical_order() -> None:
    assert make_card(1, E) == 0
    assert make_card(12, E) == 9
    assert make_card(1, B) == 10
    assert make_card(12, C) == 39
    assert card_str(make_card(7, O)) == "7 de oro"


def test_hierarchy_has_14_steps_in_order() -> None:
    expected: list[list[tuple[int, Suit]]] = [
        [(1, E)],
        [(1, B)],
        [(7, E)],
        [(7, O)],
        [(3, s) for s in Suit],
        [(2, s) for s in Suit],
        [(1, O), (1, C)],
        [(12, s) for s in Suit],
        [(11, s) for s in Suit],
        [(10, s) for s in Suit],
        [(7, C), (7, B)],
        [(6, s) for s in Suit],
        [(5, s) for s in Suit],
        [(4, s) for s in Suit],
    ]
    assert sum(len(g) for g in expected) == 40
    for i, group in enumerate(expected):
        for number, suit in group:
            assert truco_rank(make_card(number, suit)) == 14 - i
    assert sorted(set(TRUCO_RANK)) == list(range(1, 15))


@pytest.mark.parametrize(
    ("a", "b", "expected"),
    [
        ((1, E), (1, B), 1),
        ((7, O), (7, E), -1),
        ((3, C), (3, E), 0),
        ((1, O), (1, C), 0),
        ((7, C), (7, B), 0),
        ((4, E), (5, C), -1),
        ((12, O), (1, C), -1),
    ],
)
def test_compare_cards(a: tuple[int, Suit], b: tuple[int, Suit], expected: int) -> None:
    assert compare_cards(make_card(*a), make_card(*b)) == expected


@pytest.mark.parametrize(
    ("hand", "value"),
    [
        ([(7, O), (6, O), (1, E)], 33),
        ([(12, C), (5, C), (4, E)], 25),
        ([(7, O), (6, C), (4, B)], 7),
        ([(10, E), (11, E), (12, B)], 20),
        ([(10, E), (11, B), (12, O)], 0),
        ([(7, E), (6, E), (5, E)], 33),
        ([(1, E), (2, E), (7, B)], 23),
    ],
)
def test_envido_points(hand: list[tuple[int, Suit]], value: int) -> None:
    assert envido_points([make_card(n, s) for n, s in hand]) == value


def test_sort_slots_is_stable_by_rank_then_canonical() -> None:
    three_copa, three_espada, one_espada = make_card(3, C), make_card(3, E), make_card(1, E)
    assert sort_slots([one_espada, three_copa, three_espada]) == (
        three_espada,
        three_copa,
        one_espada,
    )
