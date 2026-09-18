"""Mazo de 40 cartas, jerarquía de truco (14 escalones) y valor de envido.

Las cartas se representan como enteros 0..39 en orden canónico: palo mayor (espada, basto, oro,
copa) y dentro de cada palo los números 1, 2, 3, 4, 5, 6, 7, 10, 11, 12. Ese orden es parte del
contrato de `encode()` y define el desempate estable de slots.
"""

from __future__ import annotations

from enum import IntEnum
from itertools import combinations

Card = int


class Suit(IntEnum):
    ESPADA = 0
    BASTO = 1
    ORO = 2
    COPA = 3


NUMBERS: tuple[int, ...] = (1, 2, 3, 4, 5, 6, 7, 10, 11, 12)
NUM_CARDS = 40
NUM_TRUCO_RANKS = 14

SUIT_NAMES: dict[Suit, str] = {
    Suit.ESPADA: "espada",
    Suit.BASTO: "basto",
    Suit.ORO: "oro",
    Suit.COPA: "copa",
}


def make_card(number: int, suit: Suit) -> Card:
    """Devuelve el índice canónico de la carta."""
    if number not in NUMBERS:
        raise ValueError(f"número inválido para el mazo de 40: {number}")
    return int(suit) * 10 + NUMBERS.index(number)


def card_suit(card: Card) -> Suit:
    return Suit(card // 10)


def card_number(card: Card) -> int:
    return NUMBERS[card % 10]


def card_str(card: Card) -> str:
    return f"{card_number(card)} de {SUIT_NAMES[card_suit(card)]}"


def _truco_rank(number: int, suit: Suit) -> int:
    """Escalón de truco: 14 es la carta más fuerte (1 de espada) y 1 la más débil (los 4)."""
    special = {
        (1, Suit.ESPADA): 14,
        (1, Suit.BASTO): 13,
        (7, Suit.ESPADA): 12,
        (7, Suit.ORO): 11,
    }
    if (number, suit) in special:
        return special[(number, suit)]
    by_number = {3: 10, 2: 9, 1: 8, 12: 7, 11: 6, 10: 5, 7: 4, 6: 3, 5: 2, 4: 1}
    return by_number[number]


DECK: tuple[Card, ...] = tuple(range(NUM_CARDS))
TRUCO_RANK: tuple[int, ...] = tuple(_truco_rank(card_number(c), card_suit(c)) for c in DECK)
ENVIDO_VALUE: tuple[int, ...] = tuple(0 if card_number(c) >= 10 else card_number(c) for c in DECK)


def truco_rank(card: Card) -> int:
    return TRUCO_RANK[card]


def compare_cards(a: Card, b: Card) -> int:
    """1 si `a` gana, -1 si gana `b`, 0 si es parda."""
    ra, rb = TRUCO_RANK[a], TRUCO_RANK[b]
    return (ra > rb) - (ra < rb)


def envido_points(cards: tuple[Card, ...] | list[Card]) -> int:
    """Valor de envido de las cartas repartidas.

    Dos cartas del mismo palo: 20 + suma de sus valores (figuras valen 0). Sin pares del mismo
    palo: la carta de mayor valor de envido.
    """
    best = max(ENVIDO_VALUE[c] for c in cards)
    for a, b in combinations(cards, 2):
        if card_suit(a) == card_suit(b):
            best = max(best, 20 + ENVIDO_VALUE[a] + ENVIDO_VALUE[b])
    return best


def sort_slots(cards: tuple[Card, ...] | list[Card]) -> tuple[Card, ...]:
    """Ordena de menor a mayor jerarquía de truco; empates por orden canónico."""
    return tuple(sorted(cards, key=lambda c: (TRUCO_RANK[c], c)))
