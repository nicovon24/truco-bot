"""Vista parcial por jugador, info_key() y encode().

La observación nunca contiene las cartas no jugadas del rival. El layout de `encode()` es parte del
contrato versionado (`CONTRACT_VERSION`) y está documentado en docs/action-space.md.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import numpy.typing as npt

from truco_engine.actions import PLAY_ACTIONS, Action
from truco_engine.cards import NUM_CARDS, TRUCO_RANK, Card
from truco_engine.state import NO_CARD, PARDA, GameState, PublicEvent


@dataclass(frozen=True, slots=True)
class Observation:
    player: int
    mano: int
    current_player: int | None
    hand_number: int
    baza: int
    # Cartas propias por slot; NO_CARD si ya se jugó.
    my_slots: tuple[Card, Card, Card]
    my_envido: int
    # played[baza] = (asiento 0, asiento 1) con NO_CARD si falta.
    played: tuple[tuple[Card, Card], ...]
    results: tuple[int, ...]
    truco_level: int
    truco_pending: bool
    truco_last_caller: int | None
    envido_calls: tuple[Action, ...]
    envido_caller: int | None
    envido_pending: bool
    envido_resolved: bool
    envido_accepted: bool
    # Valores (asiento 0, asiento 1), solo si el envido fue querido.
    envido_values: tuple[int, int] | None
    envido_winner: int | None
    envido_points: int
    scores: tuple[int, int]
    target_score: int
    hand_finished: bool
    hand_winner: int | None
    hand_points: tuple[int, int]
    folded_by: int | None
    history: tuple[PublicEvent, ...]

    @property
    def rival(self) -> int:
        return 1 - self.player

    @property
    def my_remaining(self) -> tuple[Card, ...]:
        return tuple(c for c in self.my_slots if c != NO_CARD)


def observe(state: GameState, player: int) -> Observation:
    hand = state.hand
    own = hand.hands[player]
    slots = tuple(NO_CARD if hand.slot_used(player, i) else own[i] for i in range(3))
    env = hand.envido
    return Observation(
        player=player,
        mano=hand.mano,
        current_player=state.current_player,
        hand_number=state.hand_number,
        baza=hand.baza,
        my_slots=(slots[0], slots[1], slots[2]),
        my_envido=hand.envido_values[player],
        played=hand.played,
        results=hand.results,
        truco_level=hand.truco.level,
        truco_pending=hand.truco.pending,
        truco_last_caller=hand.truco.last_caller,
        envido_calls=env.calls,
        envido_caller=env.caller,
        envido_pending=env.pending,
        envido_resolved=env.resolved,
        envido_accepted=env.accepted,
        envido_values=env.values,
        envido_winner=env.winner,
        envido_points=env.points,
        scores=state.scores,
        target_score=state.config.target_score,
        hand_finished=hand.finished,
        hand_winner=hand.winner,
        hand_points=hand.points,
        folded_by=hand.folded_by,
        history=hand.history,
    )


# ---------------------------------------------------------------------------
# info_key
# ---------------------------------------------------------------------------

_ACTION_CODES: dict[Action, str] = {
    Action.ENVIDO: "E",
    Action.REAL_ENVIDO: "R",
    Action.FALTA_ENVIDO: "F",
    Action.TRUCO: "T",
    Action.RETRUCO: "RT",
    Action.VALE_CUATRO: "V",
    Action.QUIERO: "Q",
    Action.NO_QUIERO: "N",
    Action.FOLD: "M",
}


def info_key(obs: Observation) -> str:
    """Clave canónica del information set (contrato v1, ver docs/action-space.md).

    Formato: `c=<escalones propios>|e=<envido o ->|m=<0/1>|s=<mío>-<rival>|v=<envidos o ->|h=<...>`
    Los eventos del historial usan `a` para el observador y `b` para el rival; las cartas jugadas
    se representan por su escalón de truco.
    """
    ranks = ".".join(str(r) for r in sorted(TRUCO_RANK[c] for c in obs.my_remaining))
    envido = "-" if obs.envido_resolved else str(obs.my_envido)
    mano = "1" if obs.mano == obs.player else "0"
    scores = f"{obs.scores[obs.player]}-{obs.scores[obs.rival]}"
    if obs.envido_values is None:
        revealed = "-"
    else:
        revealed = f"{obs.envido_values[obs.player]}-{obs.envido_values[obs.rival]}"
    tokens: list[str] = []
    for ev in obs.history:
        who = "a" if ev.player == obs.player else "b"
        if ev.action in PLAY_ACTIONS:
            tokens.append(f"{who}{TRUCO_RANK[ev.card]}")
        else:
            tokens.append(f"{who}{_ACTION_CODES[ev.action]}")
    return f"c={ranks}|e={envido}|m={mano}|s={scores}|v={revealed}|h={','.join(tokens)}"


# ---------------------------------------------------------------------------
# encode
# ---------------------------------------------------------------------------

# Offsets del layout v1. Todas las posiciones son desde la perspectiva del observador
# ("yo" = observador, "rival" = el otro asiento).
OFF_MY_CARDS = 0  # 40: multi-hot de mis cartas restantes
OFF_PLAYED = OFF_MY_CARDS + NUM_CARDS  # 240: 3 bazas x (yo, rival) x one-hot 40
OFF_BAZA_RESULTS = OFF_PLAYED + 3 * 2 * NUM_CARDS  # 9: 3 bazas x (gané, perdí, parda)
OFF_TRUCO = OFF_BAZA_RESULTS + 9  # 7: nivel aceptado one-hot 4, pendiente, cantó yo, cantó rival
OFF_ENVIDO = OFF_TRUCO + 7  # 10: ver _encode_envido
OFF_ENVIDO_VALUES = OFF_ENVIDO + 10  # 3: revelado, mi valor/33, valor rival/33
OFF_BAZA = OFF_ENVIDO_VALUES + 3  # 3: baza actual one-hot
OFF_MANO = OFF_BAZA + 3  # 1: soy mano
OFF_MY_TURN = OFF_MANO + 1  # 1: me toca actuar
OFF_SCORES = OFF_MY_TURN + 1  # 2: mi puntaje/objetivo, rival/objetivo
OFF_MY_ENVIDO = OFF_SCORES + 2  # 1: mi envido privado/33, 0 si ya se resolvió
ENCODE_SIZE = OFF_MY_ENVIDO + 1

MAX_ENVIDO = 33.0


def encode(obs: Observation) -> npt.NDArray[np.float32]:
    """Vector float32 de tamaño fijo `ENCODE_SIZE` (contrato v1)."""
    x = np.zeros(ENCODE_SIZE, dtype=np.float32)
    me, rival = obs.player, obs.rival

    for c in obs.my_remaining:
        x[OFF_MY_CARDS + c] = 1.0

    for b, pair in enumerate(obs.played[:3]):
        for rel, seat in enumerate((me, rival)):
            card = pair[seat]
            if card != NO_CARD:
                x[OFF_PLAYED + (b * 2 + rel) * NUM_CARDS + card] = 1.0

    for b, result in enumerate(obs.results[:3]):
        idx = 2 if result == PARDA else (0 if result == me else 1)
        x[OFF_BAZA_RESULTS + b * 3 + idx] = 1.0

    x[OFF_TRUCO + obs.truco_level - 1] = 1.0
    x[OFF_TRUCO + 4] = float(obs.truco_pending)
    if obs.truco_last_caller is not None:
        x[OFF_TRUCO + (5 if obs.truco_last_caller == me else 6)] = 1.0

    _encode_envido(x, obs)

    if obs.envido_values is not None:
        x[OFF_ENVIDO_VALUES] = 1.0
        x[OFF_ENVIDO_VALUES + 1] = obs.envido_values[me] / MAX_ENVIDO
        x[OFF_ENVIDO_VALUES + 2] = obs.envido_values[rival] / MAX_ENVIDO

    x[OFF_BAZA + min(obs.baza, 2)] = 1.0
    x[OFF_MANO] = float(obs.mano == me)
    x[OFF_MY_TURN] = float(obs.current_player == me)
    x[OFF_SCORES] = min(obs.scores[me] / obs.target_score, 1.0)
    x[OFF_SCORES + 1] = min(obs.scores[rival] / obs.target_score, 1.0)
    if not obs.envido_resolved:
        x[OFF_MY_ENVIDO] = obs.my_envido / MAX_ENVIDO
    return x


def _encode_envido(x: npt.NDArray[np.float32], obs: Observation) -> None:
    """10 posiciones: cantidad de envidos (0/1/2 one-hot), real, falta, pendiente, cantó yo,
    cantó rival, resuelto, querido."""
    n_envido = sum(1 for c in obs.envido_calls if c is Action.ENVIDO)
    x[OFF_ENVIDO + n_envido] = 1.0
    x[OFF_ENVIDO + 3] = float(Action.REAL_ENVIDO in obs.envido_calls)
    x[OFF_ENVIDO + 4] = float(Action.FALTA_ENVIDO in obs.envido_calls)
    x[OFF_ENVIDO + 5] = float(obs.envido_pending)
    if obs.envido_caller is not None:
        x[OFF_ENVIDO + (6 if obs.envido_caller == obs.player else 7)] = 1.0
    x[OFF_ENVIDO + 8] = float(obs.envido_resolved)
    x[OFF_ENVIDO + 9] = float(obs.envido_accepted)
