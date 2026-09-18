"""Evaluación rápida por manos sueltas con repartos espejados."""

from __future__ import annotations

from random import Random

from truco_engine import Action, observe
from truco_engine.agents import Agent
from truco_train.games.truco_hand import TrucoHand


def play_hand(
    game: TrucoHand, seats: tuple[Agent, Agent], deal_seed: str, agent_seed: str
) -> float:
    """Juega una mano y devuelve el payoff del asiento 0."""
    rng = Random(agent_seed)
    state = game.sample_chance(game.initial_state(), Random(deal_seed))
    while not game.is_terminal(state):
        player = game.current_player(state)
        legal = [Action(a) for a in game.legal_actions(state)]
        assert state is not None
        action = seats[player].act(observe(state, player), legal, rng)
        state = game.apply(state, int(action))
    return game.returns(state)[0]


def mirrored_hand_payoff(
    game: TrucoHand, agent: Agent, rival: Agent, hands: int, seed: int
) -> float:
    """Payoff medio por mano de `agent`: cada reparto se juega desde ambos asientos."""
    total = 0.0
    for i in range(hands):
        deal = f"{seed}:hand:{i}"
        total += play_hand(game, (agent, rival), deal, f"{deal}:a")
        total -= play_hand(game, (rival, agent), deal, f"{deal}:b")
    return total / (2 * hands)
