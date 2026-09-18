"""Pool de rivales: checkpoints propios pasados, heurístico y random, con pesos configurables.

Las entradas `self` se reparten el peso de la categoría entre todos los snapshots guardados; si
todavía no hay snapshots, ese peso se redistribuye proporcionalmente entre el resto.
"""

from __future__ import annotations

from collections.abc import Mapping
from random import Random
from typing import Any

import numpy as np
import torch

from truco_engine import Action, encode
from truco_engine.agents import Agent, HeuristicAgent, Policy, PolicyAgent, RandomAgent
from truco_engine.observation import Observation


class PolicySnapshotAgent(PolicyAgent):
    """Copia congelada de la política de MaskablePPO; muestrea de su distribución enmascarada."""

    def __init__(self, policy: Any, name: str) -> None:
        # Copia por construcción + state_dict (deepcopy de una policy de sb3 falla con tensores
        # que no son hojas del grafo).
        clone = policy.__class__(**policy._get_constructor_parameters())
        clone.load_state_dict(policy.state_dict())
        self.policy_net = clone.to("cpu").eval()
        self.name = name

    def policy(self, obs: Observation, legal: list[Action]) -> Policy:
        x = torch.from_numpy(encode(obs)[None, :])
        mask = np.zeros((1, self.policy_net.action_space.n), dtype=np.bool_)
        mask[0, [int(a) for a in legal]] = True
        with torch.no_grad():
            dist = self.policy_net.get_distribution(x, action_masks=mask)
            probs = dist.distribution.probs[0].numpy()
        return {a: float(probs[int(a)]) for a in legal}


class OpponentPool:
    def __init__(self, weights: Mapping[str, float], max_snapshots: int = 10) -> None:
        self.weights = dict(weights)
        self.max_snapshots = max_snapshots
        self.fixed: dict[str, Agent] = {}
        if self.weights.get("heuristic", 0.0) > 0:
            self.fixed["heuristic"] = HeuristicAgent()
        if self.weights.get("random", 0.0) > 0:
            self.fixed["random"] = RandomAgent()
        self.snapshots: list[Agent] = []

    def add_fixed(self, name: str, agent: Agent, weight: float) -> None:
        self.fixed[name] = agent
        self.weights[name] = weight

    def add_snapshot(self, agent: Agent) -> None:
        self.snapshots.append(agent)
        if len(self.snapshots) > self.max_snapshots:
            self.snapshots.pop(0)

    def sample(self, rng: Random) -> tuple[str, Agent]:
        options: list[tuple[str, Agent, float]] = [
            (name, agent, self.weights.get(name, 0.0)) for name, agent in self.fixed.items()
        ]
        self_weight = self.weights.get("self", 0.0)
        if self.snapshots and self_weight > 0:
            share = self_weight / len(self.snapshots)
            options += [(f"self:{a.name}", a, share) for a in self.snapshots]
        total = sum(w for _, _, w in options)
        if total <= 0:
            raise ValueError("el pool de rivales no tiene peso positivo")
        r = rng.random() * total
        acc = 0.0
        for name, agent, w in options:
            acc += w
            if r < acc:
                return name, agent
        name, agent, _ = options[-1]
        return name, agent
