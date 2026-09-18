"""MCCFR con external sampling.

En los nodos del jugador que recorre se exploran todas las acciones legales y se actualizan los
regrets; en los del rival se muestrea de la estrategia actual y se acumula la estrategia promedio;
en los de azar se muestrea. Soporta regret matching+ y promediado lineal.

Las tablas son compactas: un diccionario `info_key -> fila` y dos matrices float32 contiguas
(regrets y estrategia acumulada) que crecen por duplicación. En truco hay millones de
information sets y un objeto por nodo no entra en memoria (ver docs/experiments).
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from random import Random

import numpy as np
import numpy.typing as npt

from truco_engine.tabular import TabularPolicy
from truco_train.games.game_api import CHANCE, Game

FloatArray = npt.NDArray[np.float32]

_INITIAL_CAPACITY = 1024


@dataclass(frozen=True)
class MCCFRConfig:
    regret_matching_plus: bool = True
    linear_averaging: bool = True


@dataclass
class MCCFRStats:
    iterations: int = 0
    nodes_touched: int = 0


class ExternalSamplingMCCFR[S]:
    def __init__(self, game: Game[S], config: MCCFRConfig | None = None) -> None:
        self.game = game
        self.config = config or MCCFRConfig()
        self.index: dict[str, int] = {}
        self.legal_rows: list[tuple[int, ...]] = []
        self.regrets: FloatArray = np.zeros((_INITIAL_CAPACITY, game.num_actions), np.float32)
        self.strategy_sum: FloatArray = np.zeros((_INITIAL_CAPACITY, game.num_actions), np.float32)
        # Veces que el info set acumuló estrategia promedio (nodos del rival del que recorre).
        self.visits: npt.NDArray[np.uint32] = np.zeros(_INITIAL_CAPACITY, np.uint32)
        self.stats = MCCFRStats()

    @property
    def num_infosets(self) -> int:
        return len(self.index)

    # -- tablas --------------------------------------------------------------

    def _row(self, key: str, legal: list[int]) -> int:
        row = self.index.get(key)
        if row is not None:
            return row
        row = len(self.index)
        if row >= self.regrets.shape[0]:
            grow = self.regrets.shape[0]
            pad = np.zeros((grow, self.game.num_actions), np.float32)
            self.regrets = np.concatenate([self.regrets, pad])
            self.strategy_sum = np.concatenate([self.strategy_sum, pad.copy()])
            self.visits = np.concatenate([self.visits, np.zeros(grow, np.uint32)])
        self.index[key] = row
        self.legal_rows.append(tuple(legal))
        return row

    def _strategy(self, row: int, legal: list[int]) -> list[float]:
        positive = [max(float(self.regrets[row, a]), 0.0) for a in legal]
        total = sum(positive)
        if total > 0.0:
            return [p / total for p in positive]
        return [1.0 / len(legal)] * len(legal)

    # -- entrenamiento -------------------------------------------------------

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
        row = self._row(game.info_key(state, player), legal)
        strategy = self._strategy(row, legal)

        if player == traverser:
            utils = [self._traverse(game.apply(state, a), traverser, rng, t) for a in legal]
            node_util = sum(p * u for p, u in zip(strategy, utils, strict=True))
            regrets = self.regrets[row]
            for a, u in zip(legal, utils, strict=True):
                r = float(regrets[a]) + (u - node_util)
                regrets[a] = max(r, 0.0) if self.config.regret_matching_plus else r
            return node_util

        weight = float(t) if self.config.linear_averaging else 1.0
        sums = self.strategy_sum[row]
        self.visits[row] += 1
        for a, p in zip(legal, strategy, strict=True):
            sums[a] += weight * p
        r = rng.random()
        acc = 0.0
        action = legal[-1]
        for a, p in zip(legal, strategy, strict=True):
            acc += p
            if r < acc:
                action = a
                break
        return self._traverse(game.apply(state, action), traverser, rng, t)

    # -- resultados ----------------------------------------------------------

    def average_policy(self, min_visits: int = 0) -> TabularPolicy:
        """Estrategia promedio; omite info sets con menos de `min_visits` visitas."""
        policy = TabularPolicy(self.game.num_actions)
        for key, row in self.index.items():
            if self.visits[row] < min_visits:
                continue
            legal = list(self.legal_rows[row])
            sums = self.strategy_sum[row, legal].astype(np.float64)
            total = float(sums.sum())
            probs = np.zeros(self.game.num_actions)
            probs[legal] = sums / total if total > 0.0 else 1.0 / len(legal)
            policy.set(key, probs)
        return policy

    def memory_bytes(self) -> int:
        """Memoria de las matrices más una estimación del índice y sus claves."""
        n = self.num_infosets
        arrays = self.regrets.nbytes + self.strategy_sum.nbytes + self.visits.nbytes
        keys = sum(len(k) for k in self.index) + n * (49 + 104)
        return arrays + keys

    # -- checkpoints ---------------------------------------------------------

    def save_checkpoint(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        n = self.num_infosets
        keys = np.array(list(self.index), dtype=object)
        legal = np.array(
            ["".join(chr(65 + a) for a in row) for row in self.legal_rows], dtype=object
        )
        np.savez_compressed(
            path,
            iterations=np.array(self.stats.iterations),
            keys=keys,
            legal=legal,
            regrets=self.regrets[:n],
            strategy_sum=self.strategy_sum[:n],
            visits=self.visits[:n],
        )

    def load_checkpoint(self, path: Path) -> None:
        with np.load(path, allow_pickle=True) as data:
            self.stats.iterations = int(data["iterations"])
            keys = [str(k) for k in data["keys"]]
            self.index = {k: i for i, k in enumerate(keys)}
            self.legal_rows = [tuple(ord(c) - 65 for c in s) for s in data["legal"]]
            self.regrets = np.array(data["regrets"], dtype=np.float32)
            self.strategy_sum = np.array(data["strategy_sum"], dtype=np.float32)
            self.visits = np.array(data["visits"], dtype=np.uint32)
        if self.regrets.shape[0] == 0:
            self.regrets = np.zeros((_INITIAL_CAPACITY, self.game.num_actions), np.float32)
            self.strategy_sum = np.zeros((_INITIAL_CAPACITY, self.game.num_actions), np.float32)
            self.visits = np.zeros(_INITIAL_CAPACITY, np.uint32)
