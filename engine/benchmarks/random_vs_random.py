"""Benchmark: manos por segundo en partidas completas random vs random.

Uso: uv run python engine/benchmarks/random_vs_random.py --games 2000 --seed 0
"""

from __future__ import annotations

import argparse
import platform
import sys
import time
from random import Random

from truco_engine.agents import RandomAgent
from truco_engine.config import RulesConfig
from truco_engine.game import play_game


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--games", type=int, default=2_000)
    parser.add_argument("--seed", type=int, default=0)
    args = parser.parse_args()

    agents = [RandomAgent(), RandomAgent()]
    config = RulesConfig()
    hands = decisions = 0
    start = time.perf_counter()
    for i in range(args.games):
        seed = args.seed + i
        result = play_game(agents, config, Random(seed), Random(f"agents:{seed}"))
        hands += result.hands
        decisions += result.decisions
    elapsed = time.perf_counter() - start

    print(f"python: {sys.version.split()[0]} ({platform.platform()})")
    print(f"partidas: {args.games}  semillas: {args.seed}..{args.seed + args.games - 1}")
    print(f"manos: {hands}  decisiones: {decisions}  tiempo: {elapsed:.2f}s")
    print(f"manos/s: {hands / elapsed:,.0f}  decisiones/s: {decisions / elapsed:,.0f}")


if __name__ == "__main__":
    main()
