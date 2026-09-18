"""Cálculo de puntos de truco, envido y ganador de la mano."""

from __future__ import annotations

from collections.abc import Sequence

from truco_engine.actions import Action
from truco_engine.state import PARDA

ENVIDO_CALL_POINTS: dict[Action, int] = {Action.ENVIDO: 2, Action.REAL_ENVIDO: 3}


def falta_envido_value(scores: tuple[int, int], target: int, fixed: int | None) -> int:
    """Lo que le falta al que va ganando para llegar al objetivo (mismo cálculo si hay empate)."""
    if fixed is not None:
        return fixed
    return max(1, target - max(scores))


def envido_accepted_points(calls: Sequence[Action], falta: int) -> int:
    """Puntos de una cadena de envido querida: E=2, R=3 acumulables; con falta, vale la falta."""
    if Action.FALTA_ENVIDO in calls:
        return falta
    return sum(ENVIDO_CALL_POINTS[c] for c in calls)


def envido_rejected_points(calls: Sequence[Action], falta: int) -> int:
    """Puntos por no querer: lo querible antes del último canto, con mínimo 1."""
    if len(calls) <= 1:
        return 1
    return max(1, envido_accepted_points(calls[:-1], falta))


def envido_winner(values: tuple[int, int], mano: int) -> int:
    if values[0] == values[1]:
        return mano
    return 0 if values[0] > values[1] else 1


def hand_winner(results: Sequence[int], mano: int) -> int | None:
    """Ganador de la mano según las bazas resueltas, o None si hay que seguir jugando.

    - Primera parda: gana quien gane la siguiente no parda; tres pardas: gana el mano.
    - Alguien ganó la primera y la segunda es parda: gana quien ganó la primera.
    - Una baza cada uno y tercera parda: gana quien ganó la primera.
    """
    n = len(results)
    if n < 2:
        return None
    r0, r1 = results[0], results[1]
    if n == 2:
        if r0 == PARDA and r1 == PARDA:
            return None
        if r0 == PARDA:
            return r1
        if r1 in (PARDA, r0):
            return r0
        return None
    r2 = results[2]
    if r2 != PARDA:
        return r2
    if r0 == PARDA:
        return mano
    return r0
