"""Ayudas para tests: construir estados con cartas conocidas."""

from __future__ import annotations

from collections.abc import Sequence

from truco_engine.actions import Action
from truco_engine.cards import Suit, envido_points, make_card, sort_slots
from truco_engine.config import RulesConfig
from truco_engine.rules import apply
from truco_engine.state import GameState, HandState

E, B, O, C = Suit.ESPADA, Suit.BASTO, Suit.ORO, Suit.COPA


def cards(*specs: tuple[int, Suit]) -> tuple[int, int, int]:
    s = sort_slots([make_card(n, suit) for n, suit in specs])
    return (s[0], s[1], s[2])


def build(
    h0: Sequence[tuple[int, Suit]],
    h1: Sequence[tuple[int, Suit]],
    mano: int = 0,
    scores: tuple[int, int] = (0, 0),
    config: RulesConfig | None = None,
) -> GameState:
    a, b = cards(*h0), cards(*h1)
    hand = HandState(
        mano=mano,
        hands=(a, b),
        envido_values=(envido_points(a), envido_points(b)),
        play_turn=mano,
    )
    return GameState(config=config or RulesConfig(), scores=scores, hand_number=0, hand=hand)


def play(state: GameState, *actions: Action) -> GameState:
    for a in actions:
        state = apply(state, a)
    return state


def slot_of(state: GameState, player: int, number: int, suit: Suit) -> Action:
    return Action(state.hand.hands[player].index(make_card(number, suit)))
