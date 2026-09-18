"""Interfaz de repositorio de partidas e implementación en memoria.

La implementación en memoria se pierde al reiniciar la instancia (ver docs/deploy.md). Otra
implementación (Redis/Postgres) debe respetar el mismo Protocol.
"""

from __future__ import annotations

import threading
from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from app.services.game_service import GameRecord


class GameRepository(Protocol):
    def add(self, record: GameRecord) -> None: ...

    def get(self, game_id: str) -> GameRecord | None: ...

    def save(self, record: GameRecord) -> None: ...


class InMemoryGameRepository:
    def __init__(self) -> None:
        self._games: dict[str, GameRecord] = {}
        self._lock = threading.Lock()

    def add(self, record: GameRecord) -> None:
        with self._lock:
            if record.id in self._games:
                raise KeyError(f"partida duplicada: {record.id}")
            self._games[record.id] = record

    def get(self, game_id: str) -> GameRecord | None:
        with self._lock:
            return self._games.get(game_id)

    def save(self, record: GameRecord) -> None:
        with self._lock:
            self._games[record.id] = record

    def __len__(self) -> int:
        with self._lock:
            return len(self._games)
