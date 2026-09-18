"""Propiedades sobre partidas random vs random completas."""

from __future__ import annotations

from random import Random

from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st

from truco_engine.actions import Action
from truco_engine.config import RulesConfig
from truco_engine.rules import apply, legal_actions, new_game, next_hand
from truco_engine.state import Phase

MAX_DECISIONS = 5_000


def _play_random_game(seed: int, config: RulesConfig) -> None:
    rng = Random(seed)
    state = new_game(config, rng)
    decisions = 0
    while state.phase is not Phase.GAME_OVER:
        if state.phase is Phase.HAND_OVER:
            before = state.scores
            state = next_hand(state, rng)
            assert state.scores == before
            continue
        legal = legal_actions(state)
        assert legal, "estado no terminal sin acciones legales"
        assert Action.FLOR_RESERVED not in legal
        assert len(set(legal)) == len(legal)
        before_total = sum(state.scores)
        state = apply(state, rng.choice(legal))
        assert sum(state.scores) >= before_total
        decisions += 1
        assert decisions < MAX_DECISIONS, "la partida no termina"
    assert state.winner is not None
    assert legal_actions(state) == []
    assert max(state.scores) >= config.target_score


@settings(max_examples=5_000, deadline=None, suppress_health_check=[HealthCheck.too_slow])
@given(seed=st.integers(min_value=0, max_value=2**63 - 1))
def test_random_games_always_finish(seed: int) -> None:
    _play_random_game(seed, RulesConfig())


@settings(max_examples=200, deadline=None)
@given(seed=st.integers(min_value=0, max_value=2**63 - 1), bonus=st.booleans())
def test_random_games_variants(seed: int, bonus: bool) -> None:
    _play_random_game(seed, RulesConfig(target_score=30, fold_envido_bonus=bonus))
    _play_random_game(seed, RulesConfig(falta_envido_fixed=3))
