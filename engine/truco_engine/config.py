"""RulesConfig: puntos (15/30), flor (off), punto de envido al irse al mazo, etc."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class RulesConfig:
    target_score: int = 15
    # Flag presente para el contrato; la flor no está implementada.
    flor: bool = False
    # Si quien se va al mazo en la primera baza, sin envido cantado y sin truco querido, le da
    # 1 punto de envido extra al rival.
    fold_envido_bonus: bool = True
    # Valor fijo de la falta envido. Lo usa el adaptador de entrenamiento de una sola mano, donde no
    # existe marcador. None = calcularlo con el marcador real.
    falta_envido_fixed: int | None = None

    def __post_init__(self) -> None:
        if self.target_score not in (15, 30):
            raise ValueError("target_score debe ser 15 o 30")
        if self.flor:
            raise NotImplementedError("la flor no está implementada")
        if self.falta_envido_fixed is not None and self.falta_envido_fixed < 1:
            raise ValueError("falta_envido_fixed debe ser >= 1")
