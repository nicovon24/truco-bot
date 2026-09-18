"""Torneo todos contra todos con repartos espejados.

Cada par espejado juega el mismo reparto dos veces: en la segunda partida los agentes cambian de
asiento, así que cada uno recibe las cartas y la condición de mano que tuvo el otro. El azar de
repartos (`deal_rng`) está separado del azar de los agentes para que el espejo sea exacto.
"""

from __future__ import annotations

import json
import math
import platform
import time
from collections.abc import Callable, Mapping, Sequence
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from functools import partial
from itertools import combinations
from pathlib import Path
from random import Random
from typing import Any

from truco_engine import CONTRACT_VERSION, RulesConfig
from truco_engine.agents import Agent, HeuristicAgent, HeuristicConfig, RandomAgent
from truco_engine.game import play_game
from truco_train.provenance import git_commit

AgentFactory = Callable[[], Agent]


@dataclass(frozen=True)
class AgentSpec:
    id: str
    type: str
    params: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class TournamentConfig:
    name: str
    seed: int
    pairs: int
    agents: tuple[AgentSpec, ...]
    rules: RulesConfig = field(default_factory=RulesConfig)
    output_dir: str = "reports"
    confidence: float = 0.95

    @staticmethod
    def from_dict(data: Mapping[str, Any]) -> TournamentConfig:
        agents = tuple(
            AgentSpec(id=a["id"], type=a["type"], params=dict(a.get("params") or {}))
            for a in data["agents"]
        )
        if len({a.id for a in agents}) != len(agents):
            raise ValueError("los ids de agentes deben ser únicos")
        return TournamentConfig(
            name=str(data["name"]),
            seed=int(data["seed"]),
            pairs=int(data["pairs"]),
            agents=agents,
            rules=RulesConfig(**(data.get("rules") or {})),
            output_dir=str(data.get("output_dir", f"reports/{data['name']}")),
            confidence=float(data.get("confidence", 0.95)),
        )


def build_agent(spec: AgentSpec) -> Agent:
    if spec.type == "random":
        return RandomAgent()
    if spec.type == "heuristic":
        return HeuristicAgent(HeuristicConfig(**spec.params))
    if spec.type == "tabular":
        from truco_engine.agents.tabular_agent import TabularAgent

        return TabularAgent.load(Path(spec.params["path"]), name=spec.id)
    raise ValueError(f"tipo de agente desconocido: {spec.type}")


@dataclass(frozen=True)
class MatchupResult:
    agent_a: str
    agent_b: str
    pairs: int
    games: int
    wins_a: int
    wins_b: int
    win_rate_a: float
    ci_low: float
    ci_high: float
    mean_point_diff_a: float
    mean_hands: float


_Z = {0.90: 1.6448536269514722, 0.95: 1.959963984540054, 0.99: 2.5758293035489004}


def wilson_interval(wins: int, n: int, confidence: float = 0.95) -> tuple[float, float]:
    """Intervalo de Wilson para una proporción binomial."""
    if n == 0:
        return (0.0, 1.0)
    z = _Z[confidence]
    p = wins / n
    denom = 1 + z * z / n
    center = (p + z * z / (2 * n)) / denom
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / denom
    return (max(0.0, center - half), min(1.0, center + half))


def play_matchup(
    make_a: AgentFactory,
    make_b: AgentFactory,
    ids: tuple[str, str],
    rules: RulesConfig,
    seed: int,
    pairs: int,
    confidence: float = 0.95,
) -> MatchupResult:
    agent_a, agent_b = make_a(), make_b()
    wins_a = wins_b = 0
    point_diff = 0
    hands = 0
    for i in range(pairs):
        deal_seed = f"{seed}:{ids[0]}:{ids[1]}:{i}"
        for side, seats in enumerate(((agent_a, agent_b), (agent_b, agent_a))):
            result = play_game(
                seats,
                rules,
                Random(deal_seed),
                Random(f"{deal_seed}:agents:{side}"),
            )
            a_seat = 0 if side == 0 else 1
            hands += result.hands
            point_diff += result.scores[a_seat] - result.scores[1 - a_seat]
            if result.winner == a_seat:
                wins_a += 1
            else:
                wins_b += 1
    games = 2 * pairs
    low, high = wilson_interval(wins_a, games, confidence)
    return MatchupResult(
        agent_a=ids[0],
        agent_b=ids[1],
        pairs=pairs,
        games=games,
        wins_a=wins_a,
        wins_b=wins_b,
        win_rate_a=wins_a / games if games else 0.0,
        ci_low=low,
        ci_high=high,
        mean_point_diff_a=point_diff / games if games else 0.0,
        mean_hands=hands / games if games else 0.0,
    )


def run_tournament(config: TournamentConfig) -> list[MatchupResult]:
    specs = {s.id: s for s in config.agents}
    results = []
    for a, b in combinations(specs, 2):
        sa, sb = specs[a], specs[b]
        results.append(
            play_matchup(
                partial(build_agent, sa),
                partial(build_agent, sb),
                (a, b),
                config.rules,
                config.seed,
                config.pairs,
                config.confidence,
            )
        )
    return results


def render_markdown(config: TournamentConfig, results: Sequence[MatchupResult]) -> str:
    pct = int(config.confidence * 100)
    lines = [
        f"# Torneo `{config.name}`",
        "",
        f"- Semilla: `{config.seed}` · pares espejados por cruce: {config.pairs}",
        f"- Partidas a {config.rules.target_score} · contrato v{CONTRACT_VERSION}",
        f"- Intervalo: Wilson {pct}% sobre partidas (aproximado: los pares espejados no son "
        "independientes)",
        "",
        f"| A | B | Partidas | Victorias A | Victorias B | Win rate A | IC {pct}% | "
        "Dif. media pts A | Manos/partida |",
        "|---|---|---:|---:|---:|---:|---|---:|---:|",
    ]
    for r in results:
        lines.append(
            f"| {r.agent_a} | {r.agent_b} | {r.games} | {r.wins_a} | {r.wins_b} | "
            f"{r.win_rate_a:.3f} | [{r.ci_low:.3f}, {r.ci_high:.3f}] | "
            f"{r.mean_point_diff_a:+.2f} | {r.mean_hands:.1f} |"
        )
    return "\n".join(lines) + "\n"


def write_report(
    config: TournamentConfig,
    results: Sequence[MatchupResult],
    elapsed: float,
    config_path: str | None = None,
) -> Path:
    out = Path(config.output_dir)
    out.mkdir(parents=True, exist_ok=True)
    (out / "tournament.md").write_text(render_markdown(config, results), encoding="utf-8")
    payload = {
        "name": config.name,
        "config_path": config_path,
        "commit": git_commit(),
        "contract_version": CONTRACT_VERSION,
        "date": datetime.now(UTC).isoformat(timespec="seconds"),
        "seed": config.seed,
        "pairs": config.pairs,
        "rules": asdict(config.rules),
        "agents": [{"id": a.id, "type": a.type, "params": dict(a.params)} for a in config.agents],
        "platform": platform.platform(),
        "python": platform.python_version(),
        "elapsed_seconds": round(elapsed, 2),
        "results": [asdict(r) for r in results],
    }
    (out / "results.json").write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return out


def run_and_report(config: TournamentConfig, config_path: str | None = None) -> Path:
    start = time.perf_counter()
    results = run_tournament(config)
    return write_report(config, results, time.perf_counter() - start, config_path)
