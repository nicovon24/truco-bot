"""Loop de partida completa entre dos agentes, con azar explícito y separado.

`deal_rng` solo reparte y `agent_rng` solo lo usan los agentes: así el mismo `deal_rng` produce
los mismos repartos por asiento aunque cambien los agentes (base de los repartos espejados).
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from random import Random

from truco_engine.agents.base import Agent
from truco_engine.config import RulesConfig
from truco_engine.observation import observe
from truco_engine.rules import apply, legal_actions, new_game, next_hand
from truco_engine.state import GameState, Phase


@dataclass(frozen=True, slots=True)
class GameResult:
    winner: int
    scores: tuple[int, int]
    hands: int
    decisions: int
    final_state: GameState


def play_game(
    agents: Sequence[Agent],
    config: RulesConfig,
    deal_rng: Random,
    agent_rng: Random,
    *,
    first_mano: int | None = None,
    max_hands: int = 1_000,
) -> GameResult:
    if len(agents) != 2:
        raise ValueError("se necesitan exactamente dos agentes")
    state = new_game(config, deal_rng, first_mano)
    decisions = 0
    while True:
        phase = state.phase
        if phase is Phase.GAME_OVER:
            break
        if phase is Phase.HAND_OVER:
            if state.hand_number + 1 >= max_hands:
                raise RuntimeError(f"la partida superó {max_hands} manos")
            state = next_hand(state, deal_rng)
            continue
        player = state.hand.current_player
        legal = legal_actions(state)
        action = agents[player].act(observe(state, player), legal, agent_rng)
        state = apply(state, action)
        decisions += 1
    winner = state.winner
    assert winner is not None
    return GameResult(
        winner=winner,
        scores=state.scores,
        hands=state.hand_number + 1,
        decisions=decisions,
        final_state=state,
    )
