from __future__ import annotations

from pathlib import Path
from random import Random

import numpy as np
import pytest
import torch

from truco_engine import ENCODE_SIZE, NUM_ACTIONS, RulesConfig, legal_actions, new_game, observe
from truco_engine.agents.neural_agent import NeuralAgent
from truco_engine.tabular import TabularPolicy
from truco_train.deep_cfr.networks import MLP, NumpyMLP, masked_softmax_np, regret_matching_np
from truco_train.deep_cfr.reservoir import ReservoirBuffer
from truco_train.deep_cfr.trainer import DeepCFR, DeepCFRConfig
from truco_train.eval.best_response import exploitability, information_sets
from truco_train.export.to_onnx import export_with_parity, parity_error
from truco_train.games.kuhn import KuhnPoker, KuhnState

UNIFORM_KUHN_EXPLOITABILITY = 0.4583


def test_reservoir_keeps_uniform_sample() -> None:
    buf = ReservoirBuffer(capacity=100, input_size=3, num_actions=2)
    rng = Random(0)
    for i in range(10_000):
        buf.add(np.full(3, i, np.float32), np.zeros(2, np.float32), np.ones(2, bool), i, rng)
    assert buf.size == 100
    assert buf.seen == 10_000
    _, _, _, its = buf.arrays()
    # Una muestra uniforme de 0..9999 tiene media cercana a 5000.
    assert 3500 < float(its.mean()) < 6500


def test_numpy_mlp_matches_torch() -> None:
    model = MLP(9, 2, hidden=16)
    x = np.random.default_rng(0).random((5, 9), dtype=np.float32)
    with torch.no_grad():
        expected = model(torch.from_numpy(x)).numpy()
    np.testing.assert_allclose(NumpyMLP(model)(x), expected, atol=1e-5)


def test_regret_matching_and_softmax() -> None:
    adv = np.array([1.0, 3.0, -2.0], np.float32)
    assert regret_matching_np(adv, [0, 1, 2]) == [0.25, 0.75, 0.0]
    assert regret_matching_np(np.array([-1.0, -3.0], np.float32), [0, 1]) == [1.0, 0.0]
    probs = masked_softmax_np(np.array([0.0, 100.0, 0.0], np.float32), [0, 2])
    assert probs == pytest.approx([0.5, 0.5])


def _kuhn_policy_from_net(solver: DeepCFR[KuhnState], model: MLP) -> TabularPolicy:
    game = solver.game
    net = NumpyMLP(model)
    policy = TabularPolicy(game.num_actions)
    for player in (0, 1):
        for key, legal in information_sets(game, player).items():
            card, history = key.split("|")
            x = game.info_tensor(KuhnState(cards=(int(card), int(card)), history=history), 0)
            probs = np.zeros(game.num_actions)
            probs[legal] = masked_softmax_np(net(x), legal)
            policy.set(key, probs)
    return policy


def test_deep_cfr_reduces_exploitability_on_kuhn() -> None:
    game = KuhnPoker()
    cfg = DeepCFRConfig(
        iterations=25,
        traversals=150,
        hidden=32,
        advantage_capacity=20_000,
        strategy_capacity=40_000,
        advantage_steps=200,
        strategy_steps=1_500,
        batch_size=256,
        learning_rate=3e-3,
    )
    solver = DeepCFR(game, input_size=9, config=cfg, seed=3)
    model = solver.run()
    expl = exploitability(game, _kuhn_policy_from_net(solver, model))
    assert expl < UNIFORM_KUHN_EXPLOITABILITY / 2


def test_onnx_export_parity_and_neural_agent(tmp_path: Path) -> None:
    model = MLP(ENCODE_SIZE, NUM_ACTIONS, hidden=32)
    path = tmp_path / "m.onnx"
    err = export_with_parity(model, ENCODE_SIZE, path)
    assert err < 1e-4
    assert parity_error(model, path, ENCODE_SIZE, seed=1) < 1e-4

    agent = NeuralAgent.load(path, name="red")
    state = new_game(RulesConfig(), Random(4))
    legal = legal_actions(state)
    player = state.hand.current_player
    policy = agent.policy(observe(state, player), legal)
    assert set(policy) == set(legal)
    assert sum(policy.values()) == pytest.approx(1.0)
    action = agent.act(observe(state, player), legal, Random(0))
    assert action in legal
