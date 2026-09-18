from __future__ import annotations

from random import Random

import pytest

from truco_engine.actions import Action
from truco_engine.agents import (
    Agent,
    HeuristicAgent,
    HeuristicConfig,
    RandomAgent,
    sample_policy,
)
from truco_engine.config import RulesConfig
from truco_engine.game import play_game
from truco_engine.observation import observe
from truco_engine.rules import apply, legal_actions, new_game, next_hand
from truco_engine.state import Phase
from truco_engine.testing import B, C, E, O, build, play

AGENTS: list[Agent] = [RandomAgent(), HeuristicAgent()]


def support(policy: dict[Action, float]) -> dict[Action, float]:
    return {a: p for a, p in policy.items() if p > 0.0}


@pytest.mark.parametrize("agent", AGENTS, ids=lambda a: a.name)
def test_policy_is_distribution_over_legal(agent: Agent) -> None:
    rng = Random(3)
    for seed in range(30):
        state = new_game(RulesConfig(), Random(seed))
        while state.phase is not Phase.GAME_OVER:
            if state.phase is Phase.HAND_OVER:
                state = next_hand(state, rng)
                continue
            p = state.hand.current_player
            legal = legal_actions(state)
            policy = agent.policy(observe(state, p), legal)
            assert set(policy) <= set(legal)
            assert all(v >= 0.0 for v in policy.values())
            assert sum(policy.values()) == pytest.approx(1.0)
            state = apply(state, agent.act(observe(state, p), legal, rng))


def test_games_are_reproducible_with_same_seeds() -> None:
    def run(seed: int) -> tuple[tuple[int, int], int]:
        r = play_game([HeuristicAgent(), RandomAgent()], RulesConfig(), Random(seed), Random(-seed))
        return r.scores, r.decisions

    assert run(11) == run(11)
    assert run(11) != run(12) or run(13) != run(11)


def test_sample_policy_respects_zero_mass() -> None:
    rng = Random(0)
    policy = {Action.QUIERO: 0.0, Action.NO_QUIERO: 1.0}
    assert all(sample_policy(policy, rng) is Action.NO_QUIERO for _ in range(100))
    with pytest.raises(ValueError, match="masa"):
        sample_policy({Action.QUIERO: 0.0}, rng)


def test_heuristic_calls_envido_with_high_points() -> None:
    s = build([(7, O), (6, O), (4, E)], [(1, E), (3, C), (12, B)])
    agent = HeuristicAgent(HeuristicConfig(bluff_probability=0.0))
    policy = agent.policy(observe(s, 0), legal_actions(s))
    assert support(policy) == {Action.FALTA_ENVIDO: 1.0}


def test_heuristic_rejects_envido_with_low_points() -> None:
    s = play(build([(7, O), (6, O), (4, E)], [(1, E), (3, C), (12, B)]), Action.ENVIDO)
    agent = HeuristicAgent()
    policy = agent.policy(observe(s, 1), legal_actions(s))
    assert support(policy) == {Action.NO_QUIERO: 1.0}


def test_heuristic_accepts_truco_with_strong_hand_and_bluffs_explicitly() -> None:
    s = build([(4, C), (5, O), (6, B)], [(1, E), (1, B), (7, O)])
    agent = HeuristicAgent(HeuristicConfig(bluff_probability=0.1))
    # La mano débil abre con la menor carta, con farol de truco explícito.
    policy = agent.policy(observe(s, 0), legal_actions(s))
    assert policy[Action.TRUCO] == pytest.approx(0.1)
    assert policy[Action.PLAY_CARD_0] == pytest.approx(0.9)
    s = play(s, Action.TRUCO)
    policy = agent.policy(observe(s, 1), legal_actions(s))
    assert support(policy) == {Action.RETRUCO: 1.0}


def test_heuristic_beats_random_on_average() -> None:
    wins = 0
    n = 200
    for seed in range(n):
        seats: list[Agent] = [HeuristicAgent(), RandomAgent()]
        if seed % 2:
            seats.reverse()
        r = play_game(seats, RulesConfig(), Random(seed), Random(seed + 10_000))
        wins += int(seats[r.winner].name == "heuristic")
    assert wins / n > 0.7
