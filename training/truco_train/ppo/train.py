"""Entrenamiento con MaskablePPO de sb3-contrib (no implementado a mano).

El rival de cada episodio sale del pool: snapshots propios pasados (uno cada `snapshot_every`
rollouts), heurístico y random. Cada `eval_every` rollouts se mide el payoff contra el heurístico y
contra el snapshot más viejo y el más nuevo del pool: si el agente le gana al nuevo pero pierde
contra el viejo, hay ciclado estratégico (se registra en metrics.json).
"""

from __future__ import annotations

import json
import logging
import time
from collections.abc import Mapping
from pathlib import Path
from random import Random
from typing import Any

import torch
from sb3_contrib import MaskablePPO
from stable_baselines3.common.callbacks import BaseCallback
from torch import nn

from truco_engine.agents import Agent, HeuristicAgent
from truco_train.eval.hands import mirrored_hand_payoff
from truco_train.export.to_onnx import export_with_parity
from truco_train.games.truco_hand import TrucoHand, build_truco_hand
from truco_train.ppo.env import TrucoHandEnv
from truco_train.ppo.opponent_pool import OpponentPool, PolicySnapshotAgent
from truco_train.provenance import run_info

logger = logging.getLogger(__name__)


class ActorLogits(nn.Module):
    """Solo la cabeza de la política: encode -> logits (lo que se exporta a ONNX)."""

    def __init__(self, policy: Any) -> None:
        super().__init__()
        self.features = policy.pi_features_extractor
        self.mlp = policy.mlp_extractor
        self.action_net = policy.action_net

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        latent = self.mlp.forward_actor(self.features(x))
        out: torch.Tensor = self.action_net(latent)
        return out


class PoolCallback(BaseCallback):
    def __init__(
        self,
        game: TrucoHand,
        pool: OpponentPool,
        snapshot_every: int,
        eval_every: int,
        eval_hands: int,
        eval_seed: int,
        metrics: list[dict[str, Any]],
    ) -> None:
        super().__init__()
        self.game = game
        self.pool = pool
        self.snapshot_every = snapshot_every
        self.eval_every = eval_every
        self.eval_hands = eval_hands
        self.eval_seed = eval_seed
        self.metrics = metrics
        self.rollouts = 0
        self.start = time.perf_counter()

    def _on_step(self) -> bool:
        return True

    def _on_rollout_end(self) -> None:
        self.rollouts += 1
        model = self.model
        if self.rollouts % self.snapshot_every == 0:
            self.pool.add_snapshot(PolicySnapshotAgent(model.policy, f"r{self.rollouts}"))
        if self.rollouts % self.eval_every == 0:
            self.metrics.append(self.evaluate())

    def evaluate(self) -> dict[str, Any]:
        agent = PolicySnapshotAgent(self.model.policy, "actual")
        row: dict[str, Any] = {
            "rollout": self.rollouts,
            "timesteps": int(self.num_timesteps),
            "seconds": time.perf_counter() - self.start,
            "payoff_vs_heuristic": mirrored_hand_payoff(
                self.game, agent, HeuristicAgent(), self.eval_hands, self.eval_seed
            ),
        }
        if self.pool.snapshots:
            oldest, newest = self.pool.snapshots[0], self.pool.snapshots[-1]
            hands = max(50, self.eval_hands // 3)
            row["payoff_vs_oldest_snapshot"] = mirrored_hand_payoff(
                self.game, agent, oldest, hands, self.eval_seed + 1
            )
            row["payoff_vs_newest_snapshot"] = mirrored_hand_payoff(
                self.game, agent, newest, hands, self.eval_seed + 2
            )
            row["snapshots"] = [s.name for s in self.pool.snapshots]
        logger.info("ppo %s", {k: v for k, v in row.items() if k != "snapshots"})
        return row


def train_maskable_ppo(
    game: TrucoHand,
    pool: OpponentPool,
    ppo_cfg: Mapping[str, Any],
    seed: int,
    total_timesteps: int,
    callback: BaseCallback | None = None,
) -> MaskablePPO:
    env = TrucoHandEnv(game, pool, seed=seed)
    model = MaskablePPO(
        "MlpPolicy",
        env,
        seed=seed,
        n_steps=int(ppo_cfg.get("n_steps", 2048)),
        batch_size=int(ppo_cfg.get("batch_size", 256)),
        n_epochs=int(ppo_cfg.get("n_epochs", 5)),
        learning_rate=float(ppo_cfg.get("learning_rate", 3e-4)),
        gamma=float(ppo_cfg.get("gamma", 1.0)),
        gae_lambda=float(ppo_cfg.get("gae_lambda", 0.95)),
        ent_coef=float(ppo_cfg.get("ent_coef", 0.01)),
        policy_kwargs={"net_arch": list(ppo_cfg.get("net_arch", [256, 256]))},
        device="cpu",
        verbose=0,
    )
    model.learn(total_timesteps=total_timesteps, callback=callback)
    return model


def run_ppo(config: Mapping[str, Any], config_path: str | None = None) -> Path:
    out = Path(config.get("output_dir", f"runs/{config['name']}"))
    out.mkdir(parents=True, exist_ok=True)
    seed = int(config["seed"])
    game_spec = config["game"]
    game = build_truco_hand(game_spec)
    pool_cfg = config.get("pool") or {}
    pool = OpponentPool(
        pool_cfg.get("weights", {"self": 0.5, "heuristic": 0.35, "random": 0.15}),
        max_snapshots=int(pool_cfg.get("max_snapshots", 8)),
    )
    ppo_cfg = config.get("ppo") or {}
    eval_hands = int(game_spec.get("eval_hands", 300))
    eval_seed = int(game_spec.get("eval_seed", 777))
    metrics: list[dict[str, Any]] = []
    callback = PoolCallback(
        game,
        pool,
        snapshot_every=int(pool_cfg.get("snapshot_every", 5)),
        eval_every=int(config.get("eval_every", 10)),
        eval_hands=eval_hands,
        eval_seed=eval_seed,
        metrics=metrics,
    )
    start = time.perf_counter()
    torch.manual_seed(seed)
    model = train_maskable_ppo(
        game, pool, ppo_cfg, seed, int(config["total_timesteps"]), callback=callback
    )
    model.save(out / "maskable_ppo.zip")
    actor = ActorLogits(model.policy).eval()
    parity = export_with_parity(actor, game_spec_input_size(), out / "policy.onnx")

    final_agent: Agent = PolicySnapshotAgent(model.policy, "ppo")
    final_payoff = mirrored_hand_payoff(game, final_agent, HeuristicAgent(), eval_hands, eval_seed)
    summary = {
        **run_info(config, config_path),
        "seed": seed,
        "total_timesteps": int(model.num_timesteps),
        "final_payoff_vs_heuristic": final_payoff,
        "onnx_parity_max_abs_error": parity,
        "elapsed_seconds": round(time.perf_counter() - start, 2),
        "metrics": metrics,
    }
    (out / "metrics.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    logger.info("ppo final payoff vs heurístico: %.4f", final_payoff)
    return out


def game_spec_input_size() -> int:
    from truco_engine import ENCODE_SIZE

    return ENCODE_SIZE


def exploiter_payoff(
    target: Agent,
    game: TrucoHand,
    timesteps: int,
    seed: int,
    eval_hands: int = 300,
    ppo_cfg: Mapping[str, Any] | None = None,
) -> float:
    """Explotabilidad aproximada: entrena un MaskablePPO solo contra `target` congelado y devuelve
    su payoff medio por mano contra él (repartos espejados)."""
    pool = OpponentPool({"target": 1.0})
    pool.add_fixed("target", target, 1.0)
    model = train_maskable_ppo(game, pool, ppo_cfg or {}, seed, timesteps)
    exploiter = PolicySnapshotAgent(model.policy, "explotador")
    return mirrored_hand_payoff(game, exploiter, target, eval_hands, Random(seed).randrange(10**9))
