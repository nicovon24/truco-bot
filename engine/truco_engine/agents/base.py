"""Protocol Agent: policy() y act()."""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Mapping
from random import Random
from typing import Protocol, runtime_checkable

from truco_engine.actions import Action
from truco_engine.observation import Observation

Policy = dict[Action, float]


@runtime_checkable
class Agent(Protocol):
    name: str

    def policy(self, obs: Observation, legal: list[Action]) -> Policy: ...

    def act(self, obs: Observation, legal: list[Action], rng: Random) -> Action: ...


def sample_policy(policy: Mapping[Action, float], rng: Random) -> Action:
    """Muestrea una acción de la policy en orden de índice, consumiendo un solo `rng.random()`."""
    items = sorted((a, p) for a, p in policy.items() if p > 0.0)
    if not items:
        raise ValueError("policy sin masa de probabilidad")
    total = sum(p for _, p in items)
    r = rng.random() * total
    acc = 0.0
    for action, p in items:
        acc += p
        if r < acc:
            return action
    return items[-1][0]


def normalize(weights: Mapping[Action, float], legal: list[Action]) -> Policy:
    """Normaliza pesos sobre las acciones legales; si no queda masa, reparte uniforme."""
    clean = {a: max(0.0, weights.get(a, 0.0)) for a in legal}
    total = sum(clean.values())
    if total <= 0.0:
        return {a: 1.0 / len(legal) for a in legal}
    return {a: w / total for a, w in clean.items()}


class PolicyAgent(ABC):
    """Base para agentes que eligen muestreando de `policy()` (nunca argmax)."""

    name: str

    @abstractmethod
    def policy(self, obs: Observation, legal: list[Action]) -> Policy: ...

    def act(self, obs: Observation, legal: list[Action], rng: Random) -> Action:
        return sample_policy(self.policy(obs, legal), rng)
