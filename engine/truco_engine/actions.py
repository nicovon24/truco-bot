"""Espacio de acciones fijo de 13 acciones. Contrato versionado (ver docs/action-space.md)."""

from __future__ import annotations

from enum import IntEnum

CONTRACT_VERSION = "1"
NUM_ACTIONS = 13


class Action(IntEnum):
    PLAY_CARD_0 = 0
    PLAY_CARD_1 = 1
    PLAY_CARD_2 = 2
    ENVIDO = 3
    REAL_ENVIDO = 4
    FALTA_ENVIDO = 5
    TRUCO = 6
    RETRUCO = 7
    VALE_CUATRO = 8
    QUIERO = 9
    NO_QUIERO = 10
    FOLD = 11
    FLOR_RESERVED = 12


PLAY_ACTIONS: tuple[Action, ...] = (Action.PLAY_CARD_0, Action.PLAY_CARD_1, Action.PLAY_CARD_2)
ENVIDO_ACTIONS: tuple[Action, ...] = (Action.ENVIDO, Action.REAL_ENVIDO, Action.FALTA_ENVIDO)
TRUCO_ACTIONS: tuple[Action, ...] = (Action.TRUCO, Action.RETRUCO, Action.VALE_CUATRO)

# Nivel de truco que propone cada canto (valor de la mano si se quiere).
TRUCO_ACTION_LEVEL: dict[Action, int] = {
    Action.TRUCO: 2,
    Action.RETRUCO: 3,
    Action.VALE_CUATRO: 4,
}
LEVEL_TRUCO_ACTION: dict[int, Action] = {v: k for k, v in TRUCO_ACTION_LEVEL.items()}

assert len(Action) == NUM_ACTIONS
