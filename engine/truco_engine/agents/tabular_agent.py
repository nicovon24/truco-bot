"""TabularAgent: carga política tabular (msgpack).

La política se entrena sobre una sola mano (`truco_hand`), sin marcador. Para consultarla en una
partida completa la clave se normaliza igual que en el entrenamiento: marcador en 0-0 y, en la
variante `sin_envido`, sin valor de envido privado. Si la clave no está en la tabla (o la policy
no da masa a ninguna acción legal) se usa el heurístico y se cuenta el fallback.
"""

from __future__ import annotations

import logging
from dataclasses import replace
from pathlib import Path

from truco_engine.actions import Action
from truco_engine.agents.base import Policy, PolicyAgent, normalize
from truco_engine.agents.heuristic_agent import HeuristicAgent
from truco_engine.observation import Observation, info_key
from truco_engine.tabular import TabularPolicy

logger = logging.getLogger(__name__)

VARIANTS = ("sin_envido", "completo")


def tabular_key(obs: Observation, variant: str) -> str:
    """Clave del information set tal como la ve el entrenamiento de una mano."""
    if variant not in VARIANTS:
        raise ValueError(f"variante desconocida: {variant}")
    normalized = replace(obs, scores=(0, 0))
    if variant == "sin_envido":
        normalized = replace(normalized, envido_resolved=True)
    return info_key(normalized)


class TabularAgent(PolicyAgent):
    name = "tabular"

    def __init__(
        self,
        policy: TabularPolicy,
        variant: str,
        fallback: PolicyAgent | None = None,
        name: str | None = None,
    ) -> None:
        if variant not in VARIANTS:
            raise ValueError(f"variante desconocida: {variant}")
        self.table = policy
        self.variant = variant
        self.fallback = fallback or HeuristicAgent()
        if name is not None:
            self.name = name
        self.lookups = 0
        self.fallbacks = 0

    @classmethod
    def load(cls, path: Path, name: str | None = None) -> TabularAgent:
        policy, meta = TabularPolicy.load(path)
        game = meta.get("game") or {}
        variant = str(game.get("variant", "sin_envido"))
        return cls(policy, variant, name=name)

    def policy(self, obs: Observation, legal: list[Action]) -> Policy:
        self.lookups += 1
        probs = self.table.get(tabular_key(obs, self.variant))
        if probs is not None:
            weights = {a: float(probs[int(a)]) for a in legal}
            if sum(weights.values()) > 0.0:
                return normalize(weights, legal)
        self.fallbacks += 1
        if self.fallbacks in (1, 10, 100) or self.fallbacks % 1000 == 0:
            logger.info(
                "TabularAgent %s: %d fallbacks al heurístico de %d consultas",
                self.name,
                self.fallbacks,
                self.lookups,
            )
        return self.fallback.policy(obs, legal)
