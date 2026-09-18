"""Entorno Gymnasium de una mano de truco con `action_masks()` para MaskablePPO.

En cada episodio se reparte una mano, el agente toma un asiento al azar y el rival sale del
pool. Las jugadas del rival se aplican dentro del entorno hasta que vuelve a decidir el agente.
Recompensa = payoff de la mano / `REWARD_SCALE` (solo al final).
"""

from __future__ import annotations

from random import Random
from typing import Any

import gymnasium as gym
import numpy as np
import numpy.typing as npt

from truco_engine import ENCODE_SIZE, NUM_ACTIONS, Action, GameState, encode, observe
from truco_engine.agents import Agent
from truco_train.games.truco_hand import TrucoHand
from truco_train.ppo.opponent_pool import OpponentPool

# Payoff máximo razonable de una mano (vale cuatro + falta fija + punto de mazo) para normalizar.
REWARD_SCALE = 10.0


class TrucoHandEnv(gym.Env[npt.NDArray[np.float32], int]):
    def __init__(self, game: TrucoHand, pool: OpponentPool, seed: int = 0) -> None:
        super().__init__()
        self.game = game
        self.pool = pool
        self.rng = Random(seed)
        self.observation_space = gym.spaces.Box(0.0, 1.0, shape=(ENCODE_SIZE,), dtype=np.float32)
        self.action_space = gym.spaces.Discrete(NUM_ACTIONS)
        self.state: GameState | None = None
        self.seat = 0
        self.opponent: Agent | None = None
        self.opponent_name = ""

    # -- API de Gymnasium --------------------------------------------------

    def reset(
        self, *, seed: int | None = None, options: dict[str, Any] | None = None
    ) -> tuple[npt.NDArray[np.float32], dict[str, Any]]:
        super().reset(seed=seed)
        if seed is not None:
            self.rng = Random(seed)
        # Si el rival cierra la mano antes de que decida el agente, no hay decisión: se reparte otra.
        while True:
            self.seat = self.rng.randrange(2)
            self.opponent_name, self.opponent = self.pool.sample(self.rng)
            self.state = self.game.sample_chance(None, self.rng)
            self._play_opponent()
            if not self.game.is_terminal(self.state):
                return self._obs(), {"opponent": self.opponent_name}

    def step(
        self, action: int
    ) -> tuple[npt.NDArray[np.float32], float, bool, bool, dict[str, Any]]:
        assert self.state is not None
        self.state = self.game.apply(self.state, int(action))
        self._play_opponent()
        done = self.game.is_terminal(self.state)
        reward = self.game.returns(self.state)[self.seat] / REWARD_SCALE if done else 0.0
        return self._obs(), reward, done, False, {"opponent": self.opponent_name}

    def action_masks(self) -> npt.NDArray[np.bool_]:
        mask = np.zeros(NUM_ACTIONS, dtype=np.bool_)
        if self.state is not None and not self.game.is_terminal(self.state):
            mask[self.game.legal_actions(self.state)] = True
        else:
            mask[int(Action.FOLD)] = True  # estado terminal: máscara no vacía por contrato de sb3
        return mask

    # -- internos -----------------------------------------------------------

    def _play_opponent(self) -> None:
        state = self.state
        opponent = self.opponent
        assert state is not None
        assert opponent is not None
        while not self.game.is_terminal(state):
            player = self.game.current_player(state)
            if player == self.seat:
                break
            legal = [Action(a) for a in self.game.legal_actions(state)]
            action = opponent.act(observe(state, player), legal, self.rng)
            next_state = self.game.apply(state, int(action))
            assert next_state is not None
            state = next_state
        self.state = state

    def _obs(self) -> npt.NDArray[np.float32]:
        assert self.state is not None
        return encode(observe(self.state, self.seat))
