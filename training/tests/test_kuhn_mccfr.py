from __future__ import annotations

from pathlib import Path
from random import Random

import numpy as np
import pytest

from truco_train.cfr.mccfr import ExternalSamplingMCCFR, MCCFRConfig
from truco_train.cfr.regret_matching import regret_matching
from truco_train.cfr.tabular_policy import TabularPolicy
from truco_train.eval.best_response import expected_returns, exploitability, policy_strategy
from truco_train.games.game_api import CHANCE
from truco_train.games.kuhn import BET, GAME_VALUE_P0, PASS, KuhnPoker, KuhnState


def _nash(alpha: float = 0.0) -> TabularPolicy:
    """Equilibrio conocido de Kuhn (familia paramétrica con alpha = 0)."""
    p = TabularPolicy(2)
    bet = {0: alpha, 1: 0.0, 2: 3 * alpha}  # primer jugador abre apostando
    for c in range(3):
        p.set(f"{c}|", np.array([1 - bet[c], bet[c]]))
    call_after_check_bet = {0: 0.0, 1: alpha + 1 / 3, 2: 1.0}
    for c in range(3):
        p.set(f"{c}|pb", np.array([1 - call_after_check_bet[c], call_after_check_bet[c]]))
    # Segundo jugador.
    p.set("0|p", np.array([2 / 3, 1 / 3]))
    p.set("1|p", np.array([1.0, 0.0]))
    p.set("2|p", np.array([0.0, 1.0]))
    p.set("0|b", np.array([1.0, 0.0]))
    p.set("1|b", np.array([2 / 3, 1 / 3]))
    p.set("2|b", np.array([0.0, 1.0]))
    return p


def test_kuhn_rules() -> None:
    g = KuhnPoker()
    s = g.initial_state()
    assert g.current_player(s) == CHANCE
    assert sum(p for _, p in g.chance_outcomes(s)) == pytest.approx(1.0)
    s = KuhnState(cards=(2, 0))
    assert g.current_player(s) == 0
    s = g.apply(g.apply(s, BET), PASS)
    assert g.is_terminal(s)
    assert g.returns(s) == (1.0, -1.0)
    s = g.apply(g.apply(KuhnState(cards=(0, 2)), BET), BET)
    assert g.returns(s) == (-2.0, 2.0)
    assert g.info_key(s, 1) == "2|bb"


def test_known_equilibrium_value_and_zero_exploitability() -> None:
    g = KuhnPoker()
    nash = _nash()
    assert expected_returns(g, policy_strategy(nash))[0] == pytest.approx(GAME_VALUE_P0)
    assert exploitability(g, nash) == pytest.approx(0.0, abs=1e-9)


def test_regret_matching() -> None:
    mask = np.array([True, True, False])
    assert regret_matching(np.array([1.0, 3.0, 5.0]), mask).tolist() == [0.25, 0.75, 0.0]
    assert regret_matching(np.array([-1.0, -1.0, 5.0]), mask).tolist() == [0.5, 0.5, 0.0]


def test_mccfr_converges_on_kuhn() -> None:
    g = KuhnPoker()
    solver = ExternalSamplingMCCFR(g, MCCFRConfig())
    solver.run(2_000, Random(1))
    early = exploitability(g, solver.average_policy())
    solver.run(28_000, Random(2))
    policy = solver.average_policy()
    late = exploitability(g, policy)
    assert late < early
    assert late < 0.02
    assert expected_returns(g, policy_strategy(policy))[0] == pytest.approx(GAME_VALUE_P0, abs=0.01)
    assert len(solver.nodes) == 12


def test_mccfr_is_reproducible() -> None:
    def run() -> dict[str, list[float]]:
        s = ExternalSamplingMCCFR(KuhnPoker())
        s.run(500, Random(7))
        p = s.average_policy()
        return {k: p.get(k).tolist() for k in p}  # type: ignore[union-attr]

    assert run() == run()


def test_policy_and_checkpoint_roundtrip(tmp_path: Path) -> None:
    solver = ExternalSamplingMCCFR(KuhnPoker())
    solver.run(300, Random(3))
    path = tmp_path / "p.msgpack"
    solver.average_policy().save(path, {"seed": 3})
    loaded, meta = TabularPolicy.load(path)
    assert meta == {"seed": 3}
    assert len(loaded) == 12
    ckpt = tmp_path / "c.pkl"
    solver.save_checkpoint(ckpt)
    other = ExternalSamplingMCCFR(KuhnPoker())
    other.load_checkpoint(ckpt)
    assert other.stats.iterations == 300
    solver.run(10, Random(9))
    other.run(10, Random(9))
    a, b = solver.average_policy(), other.average_policy()
    assert all(np.allclose(a.get(k), b.get(k)) for k in a)  # type: ignore[arg-type]
