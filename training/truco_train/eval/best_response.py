"""Explotabilidad exacta para juegos chicos (Kuhn).

La mejor respuesta se calcula enumerando todas las estrategias puras del jugador que responde, lo
que solo es viable en juegos diminutos: Kuhn tiene 6 information sets de 2 acciones por jugador
(64 estrategias puras). En truco la explotabilidad es aproximada (fase 8).
"""

from __future__ import annotations

from collections.abc import Callable
from itertools import product

from truco_train.cfr.tabular_policy import TabularPolicy
from truco_train.games.game_api import CHANCE, Game

StrategyFn = Callable[[int, str, list[int]], dict[int, float]]


def policy_strategy(policy: TabularPolicy) -> StrategyFn:
    def strategy(player: int, key: str, legal: list[int]) -> dict[int, float]:
        probs = policy.get(key)
        if probs is None:
            return {a: 1.0 / len(legal) for a in legal}
        return {a: float(probs[a]) for a in legal}

    return strategy


def expected_returns[S](game: Game[S], strategy: StrategyFn) -> tuple[float, float]:
    def value(state: S) -> float:
        if game.is_terminal(state):
            return game.returns(state)[0]
        player = game.current_player(state)
        if player == CHANCE:
            return sum(p * value(game.apply(state, a)) for a, p in game.chance_outcomes(state))
        legal = game.legal_actions(state)
        probs = strategy(player, game.info_key(state, player), legal)
        return sum(p * value(game.apply(state, a)) for a, p in probs.items() if p > 0.0)

    v0 = value(game.initial_state())
    return (v0, -v0)


def information_sets[S](game: Game[S], player: int) -> dict[str, list[int]]:
    found: dict[str, list[int]] = {}

    def walk(state: S) -> None:
        if game.is_terminal(state):
            return
        p = game.current_player(state)
        if p == CHANCE:
            for a, _ in game.chance_outcomes(state):
                walk(game.apply(state, a))
            return
        legal = game.legal_actions(state)
        if p == player:
            found.setdefault(game.info_key(state, player), legal)
        for a in legal:
            walk(game.apply(state, a))

    walk(game.initial_state())
    return found


def best_response_value[S](game: Game[S], policy: TabularPolicy, br_player: int) -> float:
    base = policy_strategy(policy)
    infos = information_sets(game, br_player)
    keys = sorted(infos)
    best = float("-inf")
    for choice in product(*(infos[k] for k in keys)):
        pure = dict(zip(keys, choice, strict=True))

        def strategy(
            player: int, key: str, legal: list[int], pure: dict[str, int] = pure
        ) -> dict[int, float]:
            if player == br_player:
                return {pure[key]: 1.0}
            return base(player, key, legal)

        best = max(best, expected_returns(game, strategy)[br_player])
    return best


def exploitability[S](game: Game[S], policy: TabularPolicy) -> float:
    """(BR0 + BR1) / 2: cero en un equilibrio de Nash de un juego de suma cero."""
    return (best_response_value(game, policy, 0) + best_response_value(game, policy, 1)) / 2.0
