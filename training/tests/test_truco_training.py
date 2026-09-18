from __future__ import annotations

import json
from pathlib import Path
from random import Random
from typing import Any

import numpy as np
import pytest

from truco_engine import NUM_ACTIONS, Action, RulesConfig, new_game, observe
from truco_engine.actions import ENVIDO_ACTIONS
from truco_engine.agents import HeuristicAgent, RandomAgent
from truco_engine.agents.tabular_agent import TabularAgent, tabular_key
from truco_engine.tabular import TabularPolicy
from truco_train.cfr.mccfr import ExternalSamplingMCCFR
from truco_train.eval.hands import mirrored_hand_payoff
from truco_train.eval.plots import curve_points, plot_curves, plot_matrix
from truco_train.export.model import export_model
from truco_train.games.game_api import CHANCE
from truco_train.games.truco_hand import TrucoHand
from truco_train.ppo.env import TrucoHandEnv
from truco_train.ppo.opponent_pool import OpponentPool


@pytest.mark.parametrize("variant", ["sin_envido", "completo"])
def test_truco_hand_is_zero_sum_and_terminates(variant: str) -> None:
    game = TrucoHand(variant)
    rng = Random(0)
    for _ in range(200):
        state = game.initial_state()
        assert game.current_player(state) == CHANCE
        state = game.sample_chance(state, rng)
        while not game.is_terminal(state):
            legal = game.legal_actions(state)
            assert legal
            if variant == "sin_envido":
                assert not set(legal) & {int(a) for a in ENVIDO_ACTIONS}
            state = game.apply(state, rng.choice(legal))
        r0, r1 = game.returns(state)
        # Suma cero; puede dar 0 si el envido y el truco se los llevan jugadores distintos.
        assert r0 == -r1


def test_truco_hand_info_key_matches_tabular_agent() -> None:
    game = TrucoHand("sin_envido")
    state = game.sample_chance(None, Random(3))
    assert state is not None
    player = game.current_player(state)
    key = game.info_key(state, player)
    assert key == tabular_key(observe(state, player), "sin_envido")
    assert "|e=-|" in key
    assert "|s=0-0|" in key


def test_tabular_agent_normalizes_score_and_falls_back() -> None:
    state = new_game(RulesConfig(), Random(1))
    player = state.hand.current_player
    obs = observe(state, player)
    probs = np.zeros(NUM_ACTIONS)
    probs[int(Action.TRUCO)] = 1.0
    table = TabularPolicy(NUM_ACTIONS)
    table.set(tabular_key(obs, "completo"), probs)
    agent = TabularAgent(table, "completo")
    from dataclasses import replace

    later = replace(obs, scores=(9, 4))
    legal = [Action.TRUCO, Action.FOLD, Action.PLAY_CARD_0]
    assert agent.policy(later, legal)[Action.TRUCO] == pytest.approx(1.0)
    assert agent.fallbacks == 0
    unseen = replace(obs, my_envido=obs.my_envido + 1)
    policy = agent.policy(unseen, legal)
    assert agent.fallbacks == 1
    assert sum(policy.values()) == pytest.approx(1.0)


def test_mccfr_runs_on_truco_hand_and_prunes_export() -> None:
    solver = ExternalSamplingMCCFR(TrucoHand("sin_envido"))
    solver.run(30, Random(0))
    assert solver.num_infosets > 100
    assert len(solver.average_policy(min_visits=0)) == solver.num_infosets
    assert len(solver.average_policy(min_visits=5)) < solver.num_infosets


def test_mirrored_hand_payoff_is_antisymmetric() -> None:
    game = TrucoHand("completo")
    a, b = HeuristicAgent(), RandomAgent()
    ab = mirrored_hand_payoff(game, a, b, 50, 9)
    ba = mirrored_hand_payoff(game, b, a, 50, 9)
    assert ab > 0
    assert ab == pytest.approx(-ba, abs=0.5)


def test_ppo_env_masks_and_rewards() -> None:
    pool = OpponentPool({"heuristic": 1.0})
    env = TrucoHandEnv(TrucoHand("completo"), pool, seed=4)
    obs, info = env.reset(seed=4)
    assert obs.shape == env.observation_space.shape
    assert info["opponent"] == "heuristic"
    rng = Random(0)
    total = 0.0
    for _ in range(200):
        mask = env.action_masks()
        assert mask.any()
        action = rng.choice([i for i, ok in enumerate(mask) if ok])
        obs, reward, done, truncated, _ = env.step(action)
        total += reward
        assert not truncated
        if done:
            assert -1.5 <= reward <= 1.5
            env.reset()
    assert total != 0


def test_pool_redistributes_missing_self_weight() -> None:
    pool = OpponentPool({"self": 0.9, "heuristic": 0.1})
    names = {pool.sample(Random(i))[0] for i in range(20)}
    assert names == {"heuristic"}


def test_curve_points_and_plots(tmp_path: Path) -> None:
    metrics: list[dict[str, Any]] = [
        {"iteration": 1, "payoff_vs_heuristic": -0.2},
        {"iteration": 2},
        {"timesteps": 10, "payoff_vs_heuristic_actual": 0.1},
    ]
    name, xs, ys = curve_points(metrics)
    assert xs == [1.0, 10.0]
    assert ys == [-0.2, 0.1]
    assert name == "timesteps"
    run = tmp_path / "run"
    run.mkdir()
    (run / "metrics.json").write_text(
        json.dumps({"name": "x", "metrics": metrics}), encoding="utf-8"
    )
    assert plot_curves([run], tmp_path / "c.png").exists()
    results = {
        "agents": [{"id": "a"}, {"id": "b"}, {"id": "c"}],
        "results": [
            {"agent_a": "a", "agent_b": "b", "win_rate_a": 0.7},
            {"agent_a": "a", "agent_b": "c", "win_rate_a": 0.4},
            {"agent_a": "b", "agent_b": "c", "win_rate_a": 0.5},
        ],
    }
    (tmp_path / "r.json").write_text(json.dumps(results), encoding="utf-8")
    assert plot_matrix(tmp_path / "r.json", tmp_path / "m.png").exists()


def test_export_tabular_model(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(tmp_path)
    run = tmp_path / "runs" / "cfr"
    run.mkdir(parents=True)
    table = TabularPolicy(NUM_ACTIONS)
    table.set("k", np.full(NUM_ACTIONS, 1 / NUM_ACTIONS))
    table.save(run / "policy.msgpack", {"game": {"variant": "sin_envido"}})
    (run / "metrics.json").write_text(
        json.dumps({"config": {"seed": 5}, "iterations": 10, "metrics": [{"iteration": 10}]}),
        encoding="utf-8",
    )
    out = export_model(
        {
            "name": "cfr",
            "output_dir": str(run),
            "export": {"name": "cfr-x", "type": "tabular", "version": "1.2.3"},
        }
    )
    meta = json.loads(out.read_text(encoding="utf-8"))
    assert meta["contract"] == {"version": "1", "num_actions": 13, "encode_size": 317}
    assert meta["seed"] == 5
    assert meta["artifact"]["filename"] == "policy.msgpack"
    assert (tmp_path / ".model_cache" / "cfr-x" / "1.2.3" / "policy.msgpack").exists()
    assert (tmp_path / "artifacts" / "cfr-x" / "1.2.3" / "policy.msgpack").exists()
