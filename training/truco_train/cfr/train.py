"""Corrida reproducible de MCCFR desde una config YAML.

Escribe en `output_dir`: `metrics.json` (curva por evaluación), checkpoints periódicos y la
estrategia promedio en `policy.msgpack`.
"""

from __future__ import annotations

import json
import logging
import time
from collections.abc import Callable, Mapping
from pathlib import Path
from random import Random
from typing import Any

from truco_train.cfr.mccfr import ExternalSamplingMCCFR, MCCFRConfig
from truco_train.games.game_api import Game
from truco_train.games.kuhn import GAME_VALUE_P0, KuhnPoker
from truco_train.provenance import git_commit, run_info

logger = logging.getLogger(__name__)

Evaluator = Callable[[ExternalSamplingMCCFR[Any]], dict[str, float]]


def build_game(spec: Mapping[str, Any]) -> tuple[Game[Any], Evaluator | None]:
    name = spec["name"]
    if name == "kuhn":
        game = KuhnPoker()
        return game, _kuhn_evaluator(game)
    if name == "truco_hand":
        from truco_train.games.truco_hand import build_truco_hand, truco_hand_evaluator

        truco = build_truco_hand(spec)
        return truco, truco_hand_evaluator(truco, spec)
    raise ValueError(f"juego desconocido: {name}")


def _kuhn_evaluator(game: KuhnPoker) -> Evaluator:
    from truco_train.eval.best_response import (
        expected_returns,
        exploitability,
        policy_strategy,
    )

    def evaluate(solver: ExternalSamplingMCCFR[Any]) -> dict[str, float]:
        policy = solver.average_policy()
        value = expected_returns(game, policy_strategy(policy))[0]
        return {
            "value_p0": value,
            "value_error": abs(value - GAME_VALUE_P0),
            "exploitability": exploitability(game, policy),
        }

    return evaluate


def run_mccfr(config: Mapping[str, Any], config_path: str | None = None) -> Path:
    out = Path(config.get("output_dir", f"runs/{config['name']}"))
    out.mkdir(parents=True, exist_ok=True)
    seed = int(config["seed"])
    rng = Random(seed)
    game, evaluator = build_game(config["game"])
    mc = config.get("mccfr") or {}
    solver: ExternalSamplingMCCFR[Any] = ExternalSamplingMCCFR(
        game,
        MCCFRConfig(
            regret_matching_plus=bool(mc.get("regret_matching_plus", True)),
            linear_averaging=bool(mc.get("linear_averaging", True)),
        ),
    )
    iterations = int(config["iterations"])
    eval_every = int(config.get("eval_every", max(1, iterations // 10)))
    checkpoint_every = int(config.get("checkpoint_every", 0))
    metrics: list[dict[str, float]] = []
    start = time.perf_counter()

    def on_step(it: int) -> None:
        row: dict[str, float] = {
            "iteration": it,
            "infosets": len(solver.nodes),
            "memory_mb": solver.memory_bytes() / 1e6,
            "seconds": time.perf_counter() - start,
        }
        if evaluator is not None:
            row.update(evaluator(solver))
        metrics.append(row)
        logger.info("mccfr %s", row)
        if checkpoint_every and it % checkpoint_every == 0:
            solver.save_checkpoint(out / "checkpoints" / f"iter_{it:09d}.pkl", {"seed": seed})

    solver.run(iterations, rng, callback=on_step, every=eval_every)
    if not metrics or metrics[-1]["iteration"] != solver.stats.iterations:
        on_step(solver.stats.iterations)

    policy = solver.average_policy()
    meta = {
        "name": config["name"],
        "game": dict(config["game"]),
        "seed": seed,
        "iterations": solver.stats.iterations,
        "commit": git_commit(),
    }
    policy.save(out / "policy.msgpack", meta)
    summary = {
        **run_info(config, config_path),
        "iterations": solver.stats.iterations,
        "infosets": len(solver.nodes),
        "elapsed_seconds": round(time.perf_counter() - start, 2),
        "metrics": metrics,
    }
    (out / "metrics.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    return out
