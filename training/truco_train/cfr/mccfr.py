"""MCCFR con external sampling.

En los nodos del jugador que recorre se exploran todas las acciones legales y se actualizan los
regrets; en los del rival se muestrea de la estrategia actual y se acumula la estrategia promedio;
en los de azar se muestrea. Soporta regret matching+ y promediado lineal.
"""

from __future__ import annotations

import pickle
import sys
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path
from random import Random
from typing import Any

import numpy as np
import numpy.typing as npt

from truco_train.cfr.regret_matching import normalize_average, regret_matching
from truco_train.cfr.tabular_policy import TabularPolicy
from truco_train.games.game_api import CHANCE, Game

FloatArray = npt.NDArray[np.float64]
BoolArray = npt.NDArray[np.bool_]


@dataclass(frozen=True)
class MCCFRConfig:
    regret_matching_plus: bool = True
    linear_averaging: bool = True


@dataclass
class InfoNode:
    legal: BoolArray
    regrets: FloatArray
    strategy_sum: FloatArray


@dataclass
class MCCFRStats:
    iterations: int = 0
    nodes_touched: int = 0
    history: list[dict[str, float]] = field(default_factory=list)


class ExternalSamplingMCCFR[S]:
    def __init__(self, game: Game[S], config: MCCFRConfig | None = None) -> None:
        self.game = game
        self.config = config or MCCFRConfig()
        self.nodes: dict[str, InfoNode] = {}
        self.stats = MCCFRStats()

    # -- entrenamiento -----------------------------------------------------

    def _node(self, key: str, legal: list[int]) -> InfoNode:
        node = self.nodes.get(key)
        if node is None:
            mask = np.zeros(self.game.num_actions, dtype=np.bool_)
            mask[legal] = True
            node = InfoNode(
                legal=mask,
                regrets=np.zeros(self.game.num_actions),
                strategy_sum=np.zeros(self.game.num_actions),
            )
            self.nodes[key] = node
        return node

    def iteration(self, rng: Random) -> None:
        t = self.stats.iterations + 1
        for traverser in (0, 1):
            self._traverse(self.game.initial_state(), traverser, rng, t)
        self.stats.iterations = t

    def run(
        self,
        iterations: int,
        rng: Random,
        callback: Callable[[int], None] | None = None,
        every: int = 0,
    ) -> None:
        for _ in range(iterations):
            self.iteration(rng)
            if callback is not None and every and self.stats.iterations % every == 0:
                callback(self.stats.iterations)

    def _traverse(self, state: S, traverser: int, rng: Random, t: int) -> float:
        game = self.game
        if game.is_terminal(state):
            return game.returns(state)[traverser]
        player = game.current_player(state)
        if player == CHANCE:
            return self._traverse(game.sample_chance(state, rng), traverser, rng, t)

        self.stats.nodes_touched += 1
        legal = game.legal_actions(state)
        node = self._node(game.info_key(state, player), legal)
        strategy = regret_matching(node.regrets, node.legal)

        if player == traverser:
            utils = np.zeros(game.num_actions)
            for a in legal:
                utils[a] = self._traverse(game.apply(state, a), traverser, rng, t)
            node_util = float(np.dot(strategy, utils))
            node.regrets[legal] += utils[legal] - node_util
            if self.config.regret_matching_plus:
                np.maximum(node.regrets, 0.0, out=node.regrets)
            return node_util

        weight = float(t) if self.config.linear_averaging else 1.0
        node.strategy_sum += weight * strategy
        action = _sample(strategy, legal, rng)
        return self._traverse(game.apply(state, action), traverser, rng, t)

    # -- resultados --------------------------------------------------------

    def average_policy(self) -> TabularPolicy:
        policy = TabularPolicy(self.game.num_actions)
        for key, node in self.nodes.items():
            policy.set(key, normalize_average(node.strategy_sum, node.legal))
        return policy

    def memory_bytes(self) -> int:
        """Estimación de memoria de las tablas (arrays + diccionario, sin las claves)."""
        per_node = self.game.num_actions * (8 + 8 + 1)
        return len(self.nodes) * per_node + sys.getsizeof(self.nodes)

    # -- checkpoints -------------------------------------------------------

    def save_checkpoint(self, path: Path, extra: dict[str, Any] | None = None) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "iterations": self.stats.iterations,
            "config": self.config,
            "nodes": {k: (n.legal, n.regrets, n.strategy_sum) for k, n in self.nodes.items()},
            "extra": extra or {},
        }
        with path.open("wb") as f:
            pickle.dump(payload, f, protocol=pickle.HIGHEST_PROTOCOL)

    def load_checkpoint(self, path: Path) -> dict[str, Any]:
        with path.open("rb") as f:
            payload: dict[str, Any] = pickle.load(f)
        self.stats.iterations = int(payload["iterations"])
        self.nodes = {
            k: InfoNode(legal=v[0], regrets=v[1], strategy_sum=v[2])
            for k, v in payload["nodes"].items()
        }
        extra: dict[str, Any] = payload["extra"]
        return extra


def _sample(strategy: FloatArray, legal: list[int], rng: Random) -> int:
    r = rng.random()
    acc = 0.0
    for a in legal:
        acc += float(strategy[a])
        if r < acc:
            return a
    return legal[-1]
