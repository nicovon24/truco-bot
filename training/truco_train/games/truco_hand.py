"""Adaptador: UNA mano de truco como juego de suma cero.

- El nodo inicial es de azar: reparte las cartas y sortea quién es mano (queda en el info set).
- Payoff = puntos ganados − puntos perdidos en la mano (truco + envido + punto de mazo).
- Se ignora el marcador: la mano arranca 0-0 y la falta envido vale `falta_envido` (fijo).
- Variantes: `sin_envido` (los cantos de envido son ilegales) y `completo`.

Ver ADR 0003 y ADR 0013.
"""

from __future__ import annotations

from collections.abc import Mapping
from random import Random
from typing import Any

import numpy as np
import numpy.typing as npt

from truco_engine import (
    Action,
    GameState,
    Phase,
    RulesConfig,
    apply,
    encode,
    legal_actions,
    new_game,
    observe,
)
from truco_engine.actions import ENVIDO_ACTIONS, NUM_ACTIONS
from truco_engine.agents.tabular_agent import VARIANTS, tabular_key
from truco_train.games.game_api import CHANCE

# El estado previo al reparto se representa con None.
TrucoHandState = GameState | None


class TrucoHand:
    name = "truco_hand"
    num_actions = NUM_ACTIONS

    def __init__(self, variant: str = "sin_envido", falta_envido: int = 6) -> None:
        if variant not in VARIANTS:
            raise ValueError(f"variante desconocida: {variant}")
        self.variant = variant
        self.config = RulesConfig(falta_envido_fixed=falta_envido)

    def initial_state(self) -> TrucoHandState:
        return None

    def current_player(self, state: TrucoHandState) -> int:
        if state is None:
            return CHANCE
        player = state.current_player
        assert player is not None
        return player

    def legal_actions(self, state: TrucoHandState) -> list[int]:
        if state is None or self.is_terminal(state):
            return []
        legal = legal_actions(state)
        if self.variant == "sin_envido":
            legal = [a for a in legal if a not in ENVIDO_ACTIONS]
        return [int(a) for a in legal]

    def apply(self, state: TrucoHandState, action: int) -> TrucoHandState:
        if state is None:
            raise ValueError("el reparto se hace con sample_chance")
        return apply(state, Action(action))

    def is_terminal(self, state: TrucoHandState) -> bool:
        return state is not None and state.phase is not Phase.PLAYING

    def returns(self, state: TrucoHandState) -> tuple[float, float]:
        assert state is not None
        p0, p1 = state.hand.points
        return (float(p0 - p1), float(p1 - p0))

    def info_key(self, state: TrucoHandState, player: int) -> str:
        assert state is not None
        return tabular_key(observe(state, player), self.variant)

    def info_tensor(self, state: TrucoHandState, player: int) -> npt.NDArray[np.float32]:
        assert state is not None
        return encode(observe(state, player))

    def chance_outcomes(self, state: TrucoHandState) -> list[tuple[int, float]]:
        raise NotImplementedError("el reparto de truco no se enumera; usar sample_chance")

    def sample_chance(self, state: TrucoHandState, rng: Random) -> TrucoHandState:
        return new_game(self.config, rng)


def build_truco_hand(spec: Mapping[str, Any]) -> TrucoHand:
    return TrucoHand(
        variant=str(spec.get("variant", "sin_envido")),
        falta_envido=int(spec.get("falta_envido", 6)),
    )


def truco_hand_evaluator(game: TrucoHand, spec: Mapping[str, Any]) -> Any:
    """Payoff medio por mano de la estrategia promedio contra el heurístico (asientos espejados)."""
    from truco_engine.agents import HeuristicAgent
    from truco_engine.agents.tabular_agent import TabularAgent
    from truco_train.eval.hands import mirrored_hand_payoff

    hands = int(spec.get("eval_hands", 500))
    seed = int(spec.get("eval_seed", 12345))

    def evaluate(solver: Any) -> dict[str, float]:
        min_visits = int(spec.get("eval_min_visits", 0))
        agent = TabularAgent(solver.average_policy(min_visits), game.variant, name="mccfr")
        payoff = mirrored_hand_payoff(game, agent, HeuristicAgent(), hands, seed)
        return {
            "payoff_vs_heuristic": payoff,
            "fallback_rate": agent.fallbacks / max(1, agent.lookups),
        }

    return evaluate
