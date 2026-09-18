"""Protocol Game genérico (estilo OpenSpiel). Los algoritmos solo hablan con esta interfaz."""

from __future__ import annotations

from random import Random
from typing import Protocol

import numpy as np
import numpy.typing as npt

CHANCE = -1


class Game[S](Protocol):
    """Juego de dos jugadores y suma cero con nodos de azar explícitos."""

    name: str
    num_actions: int

    def initial_state(self) -> S: ...

    def current_player(self, state: S) -> int:
        """0, 1 o CHANCE."""
        ...

    def legal_actions(self, state: S) -> list[int]: ...

    def apply(self, state: S, action: int) -> S: ...

    def is_terminal(self, state: S) -> bool: ...

    def returns(self, state: S) -> tuple[float, float]:
        """Pagos finales; suman cero."""
        ...

    def info_key(self, state: S, player: int) -> str: ...

    def info_tensor(self, state: S, player: int) -> npt.NDArray[np.float32]: ...

    def chance_outcomes(self, state: S) -> list[tuple[int, float]]:
        """Resultados de azar posibles y sus probabilidades (para evaluación exacta)."""
        ...

    def sample_chance(self, state: S, rng: Random) -> S:
        """Aplica un resultado de azar muestreado con `rng`."""
        ...
