"""Corrida reproducible de Deep CFR desde una config YAML."""

from __future__ import annotations

import json
import logging
import time
from collections.abc import Callable, Mapping
from pathlib import Path
from typing import Any

import numpy as np
import numpy.typing as npt
import torch

from truco_engine import ENCODE_SIZE, Action, encode
from truco_engine.agents import HeuristicAgent, Policy, PolicyAgent
from truco_engine.observation import Observation
from truco_train.deep_cfr.networks import regret_matching_np
from truco_train.deep_cfr.trainer import DeepCFR, config_from, strategy_probs
from truco_train.eval.hands import mirrored_hand_payoff
from truco_train.games.truco_hand import build_truco_hand
from truco_train.provenance import run_info

logger = logging.getLogger(__name__)

ProbsFn = Callable[[npt.NDArray[np.float32], list[int], int], list[float]]


class FunctionAgent(PolicyAgent):
    """Agente a partir de una función (tensor, legales, asiento) -> probabilidades."""

    def __init__(self, probs: ProbsFn, name: str) -> None:
        self.probs = probs
        self.name = name

    def policy(self, obs: Observation, legal: list[Action]) -> Policy:
        values = self.probs(encode(obs), [int(a) for a in legal], obs.player)
        return dict(zip(legal, values, strict=True))


def run_deep_cfr(config: Mapping[str, Any], config_path: str | None = None) -> Path:
    out = Path(config.get("output_dir", f"runs/{config['name']}"))
    out.mkdir(parents=True, exist_ok=True)
    seed = int(config["seed"])
    game_spec = config["game"]
    game = build_truco_hand(game_spec)
    cfg = config_from(dict(config.get("deep_cfr") or {}))
    eval_every = int(config.get("eval_every", 5))
    eval_hands = int(game_spec.get("eval_hands", 300))
    eval_seed = int(game_spec.get("eval_seed", 777))
    solver = DeepCFR(game, ENCODE_SIZE, cfg, seed)
    metrics: list[dict[str, float]] = []
    start = time.perf_counter()

    def current_policy_payoff() -> float:
        nets = solver.advantage_nets

        def probs(x: npt.NDArray[np.float32], legal: list[int], seat: int) -> list[float]:
            # Estrategia actual (regret matching sobre ventajas) del asiento que decide.
            net = nets[seat]
            if net is None:
                return [1.0 / len(legal)] * len(legal)
            return regret_matching_np(net(x), legal)

        agent = FunctionAgent(probs, "deep_cfr_actual")
        return mirrored_hand_payoff(game, agent, HeuristicAgent(), eval_hands, eval_seed)

    def on_iteration(it: int, row: dict[str, float]) -> None:
        row["seconds"] = time.perf_counter() - start
        if it % eval_every == 0 or it == cfg.iterations:
            row["payoff_vs_heuristic_actual"] = current_policy_payoff()
        metrics.append(row)
        logger.info("deep_cfr %s", row)

    model = solver.run(on_iteration)
    torch.save(model.state_dict(), out / "strategy.pt")
    strategy = strategy_probs(model)
    final_agent = FunctionAgent(lambda x, legal, _seat: strategy(x, legal), "deep_cfr")
    final_payoff = mirrored_hand_payoff(game, final_agent, HeuristicAgent(), eval_hands, eval_seed)
    summary = {
        **run_info(config, config_path),
        "seed": seed,
        "iterations": solver.state.iteration,
        "hidden": cfg.hidden,
        "input_size": ENCODE_SIZE,
        "final_payoff_vs_heuristic": final_payoff,
        "elapsed_seconds": round(time.perf_counter() - start, 2),
        "metrics": metrics,
    }
    (out / "metrics.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    logger.info("deep_cfr final payoff vs heurístico: %.4f", final_payoff)
    return out
