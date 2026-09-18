from __future__ import annotations

import pytest

from truco_engine.actions import Action
from truco_engine.scoring import (
    envido_accepted_points,
    envido_rejected_points,
    envido_winner,
    falta_envido_value,
    hand_winner,
)
from truco_engine.state import PARDA

A, B = 0, 1
E, R, F = Action.ENVIDO, Action.REAL_ENVIDO, Action.FALTA_ENVIDO


@pytest.mark.parametrize(
    ("results", "mano", "winner"),
    [
        ((A,), A, None),
        ((PARDA, B), A, B),
        ((PARDA, PARDA), A, None),
        ((PARDA, PARDA, B), A, B),
        ((PARDA, PARDA, PARDA), A, A),
        ((PARDA, PARDA, PARDA), B, B),
        ((A, PARDA), B, A),
        ((A, A), B, A),
        ((A, B), A, None),
        ((A, B, B), A, B),
        ((A, B, PARDA), B, A),
        ((B, A, PARDA), A, B),
    ],
)
def test_hand_winner(results: tuple[int, ...], mano: int, winner: int | None) -> None:
    assert hand_winner(results, mano) == winner


@pytest.mark.parametrize(
    ("calls", "accepted", "rejected"),
    [
        ((E,), 2, 1),
        ((E, E), 4, 2),
        ((R,), 3, 1),
        ((E, R), 5, 2),
        ((E, E, R), 7, 4),
        ((F,), 99, 1),
        ((E, F), 99, 2),
        ((E, E, F), 99, 4),
        ((R, F), 99, 3),
        ((E, R, F), 99, 5),
        ((E, E, R, F), 99, 7),
    ],
)
def test_envido_chain_points(calls: tuple[Action, ...], accepted: int, rejected: int) -> None:
    assert envido_accepted_points(calls, falta=99) == accepted
    assert envido_rejected_points(calls, falta=99) == rejected


def test_falta_envido_value() -> None:
    assert falta_envido_value((3, 10), 15, None) == 5
    assert falta_envido_value((7, 7), 15, None) == 8
    assert falta_envido_value((0, 0), 30, None) == 30
    assert falta_envido_value((14, 2), 15, None) == 1
    assert falta_envido_value((14, 2), 15, 6) == 6


def test_envido_tie_goes_to_mano() -> None:
    assert envido_winner((29, 29), mano=1) == 1
    assert envido_winner((30, 29), mano=1) == 0
