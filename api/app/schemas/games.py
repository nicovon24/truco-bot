"""Schemas Pydantic v2 de la API. Todo se expresa desde la perspectiva del humano."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field

Seat = Literal["human", "bot"]
Status = Literal["playing", "hand_over", "game_over"]


class AgentOut(BaseModel):
    id: str
    name: str
    type: str
    description: str
    model_version: str | None


class CreateGameIn(BaseModel):
    agent_id: str
    seed: int | None = Field(default=None, ge=0, le=2**63 - 1)


class ActionIn(BaseModel):
    action: int = Field(ge=0, le=12, description="Índice del espacio de acciones (contrato v1).")


SuitName = Literal["espada", "basto", "oro", "copa"]


class CardOut(BaseModel):
    id: int = Field(description="Índice canónico 0..39.")
    number: int
    suit: SuitName
    label: str


class SlotOut(BaseModel):
    slot: int
    card: CardOut | None = Field(description="None si la carta ya se jugó.")


class BazaOut(BaseModel):
    human: CardOut | None
    bot: CardOut | None
    result: Literal["human", "bot", "parda"] | None


class TrucoOut(BaseModel):
    level: int = Field(description="Valor aceptado de la mano: 1 a 4.")
    pending: bool
    last_caller: Seat | None


class EnvidoOut(BaseModel):
    calls: list[str]
    pending: bool
    caller: Seat | None
    resolved: bool
    accepted: bool
    human_value: int
    bot_value: int | None = Field(description="Solo si el envido fue querido.")
    winner: Seat | None
    points: int


class ObservationOut(BaseModel):
    hand_number: int
    mano: Seat
    turn: Seat | None
    baza: int
    my_cards: list[SlotOut]
    bot_cards_in_hand: int
    bazas: list[BazaOut]
    truco: TrucoOut
    envido: EnvidoOut
    hand_finished: bool
    hand_winner: Seat | None
    hand_points: dict[Seat, int]


class LegalActionOut(BaseModel):
    id: int
    name: str
    label: str


class EventOut(BaseModel):
    seq: int
    hand_number: int
    actor: Literal["human", "bot", "system"]
    type: str
    action: int | None = None
    action_name: str | None = None
    card: CardOut | None = None
    policy: dict[str, float] | None = Field(
        default=None, description="Probabilidades por nombre de acción que usó el bot."
    )
    detail: dict[str, Any] = Field(default_factory=dict)


class GameOut(BaseModel):
    id: str
    agent_id: str
    seed: int
    status: Status
    scores: dict[Seat, int]
    target_score: int
    winner: Seat | None
    observation: ObservationOut
    legal_actions: list[LegalActionOut]
    events: list[EventOut]


class ActionResultOut(BaseModel):
    game: GameOut
    new_events: list[EventOut]


class HealthOut(BaseModel):
    status: Literal["ok"]
    contract_version: str
    agents: int
