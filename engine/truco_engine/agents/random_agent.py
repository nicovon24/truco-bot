"""RandomAgent: uniforme sobre las acciones legales."""

from __future__ import annotations

from truco_engine.actions import Action
from truco_engine.agents.base import Policy, PolicyAgent
from truco_engine.observation import Observation


class RandomAgent(PolicyAgent):
    name = "random"

    def policy(self, obs: Observation, legal: list[Action]) -> Policy:
        p = 1.0 / len(legal)
        return dict.fromkeys(legal, p)
