"""Kuhn poker para validar algoritmos.

Tres cartas (J=0, Q=1, K=2), un pozo inicial de 1 por jugador y acciones 0 = pasar/no ir y
1 = apostar/ir. Valor del juego para el primer jugador: -1/18.
"""

from __future__ import annotations

from dataclasses import dataclass
from itertools import permutations
from random import Random

import numpy as np
import numpy.typing as npt

from truco_train.games.game_api import CHANCE

PASS, BET = 0, 1
DEALS: tuple[tuple[int, int], ...] = tuple(permutations(range(3), 2))
GAME_VALUE_P0 = -1.0 / 18.0


@dataclass(frozen=True, slots=True)
class KuhnState:
    cards: tuple[int, int] | None = None
    history: str = ""


_TERMINAL = {"pp", "bp", "bb", "pbp", "pbb"}


class KuhnPoker:
    name = "kuhn"
    num_actions = 2

    def initial_state(self) -> KuhnState:
        return KuhnState()

    def current_player(self, state: KuhnState) -> int:
        if state.cards is None:
            return CHANCE
        return len(state.history) % 2

    def legal_actions(self, state: KuhnState) -> list[int]:
        if state.cards is None or self.is_terminal(state):
            return []
        return [PASS, BET]

    def apply(self, state: KuhnState, action: int) -> KuhnState:
        if state.cards is None:
            return KuhnState(cards=DEALS[action])
        move = "p" if action == PASS else "b"
        return KuhnState(cards=state.cards, history=state.history + move)

    def is_terminal(self, state: KuhnState) -> bool:
        return state.history in _TERMINAL

    def returns(self, state: KuhnState) -> tuple[float, float]:
        assert state.cards is not None
        assert self.is_terminal(state)
        h = state.history
        if h == "bp":
            return (1.0, -1.0)
        if h == "pbp":
            return (-1.0, 1.0)
        stake = 2.0 if "bb" in h else 1.0
        winner = 0 if state.cards[0] > state.cards[1] else 1
        return (stake, -stake) if winner == 0 else (-stake, stake)

    def info_key(self, state: KuhnState, player: int) -> str:
        assert state.cards is not None
        return f"{state.cards[player]}|{state.history}"

    def info_tensor(self, state: KuhnState, player: int) -> npt.NDArray[np.float32]:
        assert state.cards is not None
        x = np.zeros(3 + 2 * 3, dtype=np.float32)
        x[state.cards[player]] = 1.0
        for i, ch in enumerate(state.history[:3]):
            x[3 + 2 * i + (1 if ch == "b" else 0)] = 1.0
        return x

    def chance_outcomes(self, state: KuhnState) -> list[tuple[int, float]]:
        return [(i, 1.0 / len(DEALS)) for i in range(len(DEALS))]

    def sample_chance(self, state: KuhnState, rng: Random) -> KuhnState:
        return self.apply(state, rng.randrange(len(DEALS)))
