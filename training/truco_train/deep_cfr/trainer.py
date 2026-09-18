"""Deep CFR (Brown et al., 2019) sobre la interfaz `Game`.

Por iteración t y por jugador p:
1. K recorridos con external sampling usando las redes de ventajas actuales. En los nodos de p se
   exploran todas las acciones legales y se guarda (tensor, t, regrets muestreados) en el buffer
   de ventajas de p. En los del rival se guarda (tensor, t, estrategia) en el buffer de estrategia
   y se muestrea una acción.
2. La red de ventajas de p se reentrena desde cero con MSE ponderado por t.
Al final se entrena la red de estrategia con el buffer de estrategia: esa red es el bot final.
"""

from __future__ import annotations

import logging
from collections.abc import Callable
from dataclasses import dataclass, field
from random import Random
from typing import Any

import numpy as np
import numpy.typing as npt
import torch
from torch import nn

from truco_train.deep_cfr.networks import MLP, NumpyMLP, masked_softmax_np, regret_matching_np
from truco_train.deep_cfr.reservoir import ReservoirBuffer
from truco_train.games.game_api import CHANCE, Game

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class DeepCFRConfig:
    iterations: int = 20
    traversals: int = 300
    hidden: int = 256
    advantage_capacity: int = 200_000
    strategy_capacity: int = 300_000
    advantage_steps: int = 1_500
    strategy_steps: int = 4_000
    batch_size: int = 1_024
    learning_rate: float = 1e-3


@dataclass
class DeepCFRState:
    iteration: int = 0
    history: list[dict[str, float]] = field(default_factory=list)


class DeepCFR[S]:
    def __init__(self, game: Game[S], input_size: int, config: DeepCFRConfig, seed: int) -> None:
        self.game = game
        self.input_size = input_size
        self.config = config
        self.rng = Random(seed)
        torch.manual_seed(seed)
        self.torch_gen = torch.Generator().manual_seed(seed)
        n = game.num_actions
        self.advantage_buffers = [
            ReservoirBuffer(config.advantage_capacity, input_size, n) for _ in range(2)
        ]
        self.strategy_buffer = ReservoirBuffer(config.strategy_capacity, input_size, n)
        self.advantage_nets: list[NumpyMLP | None] = [None, None]
        self.state = DeepCFRState()

    # -- recorridos ----------------------------------------------------------

    def _strategy(self, player: int, x: npt.NDArray[np.float32], legal: list[int]) -> list[float]:
        net = self.advantage_nets[player]
        if net is None:
            return [1.0 / len(legal)] * len(legal)
        return regret_matching_np(net(x), legal)

    def _mask(self, legal: list[int]) -> npt.NDArray[np.bool_]:
        mask = np.zeros(self.game.num_actions, dtype=np.bool_)
        mask[legal] = True
        return mask

    def _traverse(self, state: S, traverser: int, t: int) -> float:
        game = self.game
        if game.is_terminal(state):
            return game.returns(state)[traverser]
        player = game.current_player(state)
        if player == CHANCE:
            return self._traverse(game.sample_chance(state, self.rng), traverser, t)

        legal = game.legal_actions(state)
        x = game.info_tensor(state, player)
        strategy = self._strategy(player, x, legal)

        if player == traverser:
            utils = [self._traverse(game.apply(state, a), traverser, t) for a in legal]
            node_util = sum(p * u for p, u in zip(strategy, utils, strict=True))
            regrets = np.zeros(game.num_actions, dtype=np.float32)
            for a, u in zip(legal, utils, strict=True):
                regrets[a] = u - node_util
            self.advantage_buffers[traverser].add(x, regrets, self._mask(legal), t, self.rng)
            return node_util

        probs = np.zeros(game.num_actions, dtype=np.float32)
        for a, p in zip(legal, strategy, strict=True):
            probs[a] = p
        self.strategy_buffer.add(x, probs, self._mask(legal), t, self.rng)
        r = self.rng.random()
        acc = 0.0
        action = legal[-1]
        for a, p in zip(legal, strategy, strict=True):
            acc += p
            if r < acc:
                action = a
                break
        return self._traverse(game.apply(state, action), traverser, t)

    # -- entrenamiento de redes ------------------------------------------------

    def _fit(self, buffer: ReservoirBuffer, steps: int, strategy: bool) -> MLP:
        cfg = self.config
        model = MLP(self.input_size, self.game.num_actions, cfg.hidden)
        if buffer.size == 0:
            return model
        xs, ys, masks, its = buffer.arrays()
        x_t = torch.from_numpy(xs)
        y_t = torch.from_numpy(ys)
        m_t = torch.from_numpy(masks.astype(np.float32))
        w_t = torch.from_numpy(its / max(float(its.max()), 1.0))
        opt = torch.optim.Adam(model.parameters(), lr=cfg.learning_rate)
        n = buffer.size
        for _ in range(steps):
            idx = torch.randint(0, n, (min(cfg.batch_size, n),), generator=self.torch_gen)
            out = model(x_t[idx])
            if strategy:
                # Entropía cruzada contra la estrategia observada, sobre acciones legales.
                logits = out.masked_fill(m_t[idx] == 0, -1e9)
                logp = torch.log_softmax(logits, dim=-1)
                per_sample = -(y_t[idx] * logp).sum(dim=-1)
            else:
                per_sample = (((out - y_t[idx]) * m_t[idx]) ** 2).sum(dim=-1)
            loss = (w_t[idx] * per_sample).mean()
            opt.zero_grad()
            loss.backward()  # type: ignore[no-untyped-call]
            nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            opt.step()
        return model

    def iteration(self) -> dict[str, float]:
        t = self.state.iteration + 1
        losses: dict[str, float] = {"iteration": float(t)}
        for p in (0, 1):
            for _ in range(self.config.traversals):
                self._traverse(self.game.initial_state(), p, t)
            model = self._fit(
                self.advantage_buffers[p], self.config.advantage_steps, strategy=False
            )
            self.advantage_nets[p] = NumpyMLP(model)
            losses[f"advantage_buffer_{p}"] = float(self.advantage_buffers[p].size)
        losses["strategy_buffer"] = float(self.strategy_buffer.size)
        self.state.iteration = t
        return losses

    def train_strategy(self) -> MLP:
        return self._fit(self.strategy_buffer, self.config.strategy_steps, strategy=True)

    def run(self, callback: Callable[[int, dict[str, float]], None] | None = None) -> MLP:
        for _ in range(self.config.iterations):
            row = self.iteration()
            if callback is not None:
                callback(self.state.iteration, row)
        return self.train_strategy()


def strategy_probs(model: MLP) -> Callable[[npt.NDArray[np.float32], list[int]], list[float]]:
    """Política de la red de estrategia sobre acciones legales (para evaluar sin exportar)."""
    fast = NumpyMLP(model)

    def probs(x: npt.NDArray[np.float32], legal: list[int]) -> list[float]:
        return masked_softmax_np(fast(x), legal)

    return probs


def config_from(data: dict[str, Any]) -> DeepCFRConfig:
    fields = DeepCFRConfig.__dataclass_fields__
    return DeepCFRConfig(**{k: v for k, v in data.items() if k in fields})
