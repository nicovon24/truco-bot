from __future__ import annotations

import json
from pathlib import Path

import pytest
from typer.testing import CliRunner

from truco_engine import RulesConfig
from truco_train.cli import app
from truco_train.eval.tournament import (
    AgentSpec,
    TournamentConfig,
    build_agent,
    play_matchup,
    run_tournament,
    wilson_interval,
)


def _config(tmp_path: Path, pairs: int = 20) -> TournamentConfig:
    return TournamentConfig(
        name="t",
        seed=1,
        pairs=pairs,
        agents=(AgentSpec("random", "random"), AgentSpec("heuristic", "heuristic")),
        output_dir=str(tmp_path / "out"),
    )


def test_wilson_interval() -> None:
    low, high = wilson_interval(50, 100)
    assert low == pytest.approx(0.4038, abs=1e-3)
    assert high == pytest.approx(0.5962, abs=1e-3)
    assert wilson_interval(0, 0) == (0.0, 1.0)


def test_mirrored_self_play_is_symmetric_in_games() -> None:
    spec = AgentSpec("random", "random")
    r = play_matchup(
        lambda: build_agent(spec), lambda: build_agent(spec), ("a", "b"), RulesConfig(), 5, 30
    )
    assert r.games == 60
    assert r.wins_a + r.wins_b == 60


def test_tournament_is_reproducible(tmp_path: Path) -> None:
    cfg = _config(tmp_path)
    assert run_tournament(cfg) == run_tournament(cfg)


def test_heuristic_beats_random_in_tournament(tmp_path: Path) -> None:
    (result,) = run_tournament(_config(tmp_path, pairs=100))
    assert result.agent_b == "heuristic"
    assert result.win_rate_a < 0.3


def test_cli_writes_reports(tmp_path: Path) -> None:
    cfg = tmp_path / "cfg.yaml"
    out = tmp_path / "rep"
    cfg.write_text(
        "name: cli\nseed: 3\npairs: 5\nagents:\n  - {id: r, type: random}\n"
        f"  - {{id: h, type: heuristic}}\noutput_dir: {out.as_posix()}\n",
        encoding="utf-8",
    )
    res = CliRunner().invoke(app, ["eval", "tournament", "--config", str(cfg)])
    assert res.exit_code == 0, res.output
    assert (out / "tournament.md").exists()
    data = json.loads((out / "results.json").read_text(encoding="utf-8"))
    assert data["seed"] == 3
    assert data["results"][0]["games"] == 10


def test_unknown_agent_type() -> None:
    with pytest.raises(ValueError, match="desconocido"):
        build_agent(AgentSpec("x", "nope"))
