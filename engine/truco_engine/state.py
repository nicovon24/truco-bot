"""GameState y HandState inmutables (dataclasses frozen).

El turno no se guarda: se deriva de los cantos pendientes (ver `HandState.current_player`).
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from truco_engine.actions import Action
from truco_engine.cards import Card
from truco_engine.config import RulesConfig

# Resultado de una baza: 0 o 1 = asiento ganador; PARDA = empate.
PARDA = 2
NO_CARD = -1


class Phase(Enum):
    PLAYING = "playing"
    HAND_OVER = "hand_over"
    GAME_OVER = "game_over"


@dataclass(frozen=True, slots=True)
class PublicEvent:
    """Acción pública de una mano. `card` es la carta tirada o NO_CARD."""

    player: int
    action: Action
    card: Card = NO_CARD


@dataclass(frozen=True, slots=True)
class TrucoState:
    # Valor aceptado de la mano: 1 sin truco, 2 truco, 3 retruco, 4 vale cuatro.
    level: int = 1
    # Si hay un canto sin responder; propone `level + 1`.
    pending: bool = False
    last_caller: int | None = None


@dataclass(frozen=True, slots=True)
class EnvidoState:
    calls: tuple[Action, ...] = ()
    caller: int | None = None
    pending: bool = False
    resolved: bool = False
    accepted: bool = False
    # Valores de envido (asiento 0, asiento 1). Públicos solo si el envido fue querido.
    values: tuple[int, int] | None = None
    winner: int | None = None
    points: int = 0


@dataclass(frozen=True, slots=True)
class HandState:
    mano: int
    # Cartas repartidas por asiento, ordenadas por slot (menor a mayor jerarquía).
    hands: tuple[tuple[Card, Card, Card], tuple[Card, Card, Card]]
    envido_values: tuple[int, int]
    # played[baza] = (carta del asiento 0, carta del asiento 1), NO_CARD si falta.
    played: tuple[tuple[Card, Card], ...] = ((NO_CARD, NO_CARD),)
    results: tuple[int, ...] = ()
    # Quién debe tirar carta cuando no hay cantos pendientes.
    play_turn: int = 0
    truco: TrucoState = TrucoState()
    envido: EnvidoState = EnvidoState()
    history: tuple[PublicEvent, ...] = ()
    finished: bool = False
    winner: int | None = None
    # Puntos ganados en la mano por asiento (truco + envido + bonus de mazo).
    points: tuple[int, int] = (0, 0)
    folded_by: int | None = None

    @property
    def baza(self) -> int:
        return len(self.played) - 1

    @property
    def current_player(self) -> int:
        if self.envido.pending:
            assert self.envido.caller is not None
            return 1 - self.envido.caller
        if self.truco.pending:
            assert self.truco.last_caller is not None
            return 1 - self.truco.last_caller
        return self.play_turn

    def slot_used(self, player: int, slot: int) -> bool:
        card = self.hands[player][slot]
        return any(b[player] == card for b in self.played)

    def has_played_in_baza(self, player: int, baza: int = 0) -> bool:
        return baza < len(self.played) and self.played[baza][player] != NO_CARD


@dataclass(frozen=True, slots=True)
class GameState:
    config: RulesConfig
    scores: tuple[int, int]
    hand_number: int
    hand: HandState

    @property
    def winner(self) -> int | None:
        for p in (0, 1):
            if self.scores[p] >= self.config.target_score:
                return p
        return None

    @property
    def phase(self) -> Phase:
        if self.winner is not None:
            return Phase.GAME_OVER
        if self.hand.finished:
            return Phase.HAND_OVER
        return Phase.PLAYING

    @property
    def is_terminal(self) -> bool:
        return self.winner is not None

    @property
    def current_player(self) -> int | None:
        return self.hand.current_player if self.phase is Phase.PLAYING else None
