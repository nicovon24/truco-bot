"""Ciclo de partidas humano vs bot sobre el motor.

El humano siempre ocupa el asiento 0. Cada partida registra su semilla; de ella salen dos
generadores separados: uno para los repartos y otro para los muestreos del bot.
"""

from __future__ import annotations

import secrets
import threading
import uuid
from dataclasses import dataclass, field
from random import Random
from typing import Literal

from app.agent_registry import AgentRegistry
from app.repositories.games import GameRepository
from truco_engine import (
    Action,
    GameState,
    Phase,
    RulesConfig,
    apply,
    legal_actions,
    new_game,
    next_hand,
    observe,
)
from truco_engine.actions import PLAY_ACTIONS
from truco_engine.agents import Agent
from truco_engine.cards import card_str

HUMAN = 0
BOT = 1
MAX_SEED = 2**63 - 1

Actor = Literal["human", "bot", "system"]


class GameNotFoundError(LookupError):
    pass


class UnknownAgentError(LookupError):
    pass


class InvalidMoveError(ValueError):
    pass


@dataclass
class GameEvent:
    seq: int
    hand_number: int
    actor: Actor
    type: str
    action: Action | None = None
    card: int | None = None
    policy: dict[Action, float] | None = None
    detail: dict[str, object] = field(default_factory=dict)


@dataclass
class GameRecord:
    id: str
    agent_id: str
    seed: int
    state: GameState
    bot: Agent
    deal_rng: Random
    bot_rng: Random
    events: list[GameEvent] = field(default_factory=list)
    lock: threading.Lock = field(default_factory=threading.Lock)

    def actor(self, seat: int) -> Actor:
        return "human" if seat == HUMAN else "bot"


def action_label(action: Action, state: GameState, seat: int) -> str:
    if action in PLAY_ACTIONS:
        return f"Tirar {card_str(state.hand.hands[seat][int(action)])}"
    return CANTO_LABELS[action]


CANTO_LABELS: dict[Action, str] = {
    Action.ENVIDO: "Envido",
    Action.REAL_ENVIDO: "Real envido",
    Action.FALTA_ENVIDO: "Falta envido",
    Action.TRUCO: "Truco",
    Action.RETRUCO: "Quiero retruco",
    Action.VALE_CUATRO: "Quiero vale cuatro",
    Action.QUIERO: "Quiero",
    Action.NO_QUIERO: "No quiero",
    Action.FOLD: "Me voy al mazo",
    Action.FLOR_RESERVED: "Flor",
}


class GameService:
    def __init__(self, repo: GameRepository, registry: AgentRegistry) -> None:
        self.repo = repo
        self.registry = registry

    # -- API pública ---------------------------------------------------------

    def create(self, agent_id: str, seed: int | None = None) -> GameRecord:
        entry = self.registry.get(agent_id)
        if entry is None:
            raise UnknownAgentError(agent_id)
        if seed is None:
            seed = secrets.randbelow(MAX_SEED)
        deal_rng = Random(f"{seed}:deal")
        record = GameRecord(
            id=uuid.uuid4().hex,
            agent_id=agent_id,
            seed=seed,
            state=new_game(RulesConfig(), deal_rng),
            bot=entry.factory(),
            deal_rng=deal_rng,
            bot_rng=Random(f"{seed}:bot"),
        )
        self._emit_deal(record)
        self._run_bot(record)
        self.repo.add(record)
        return record

    def get(self, game_id: str) -> GameRecord:
        record = self.repo.get(game_id)
        if record is None:
            raise GameNotFoundError(game_id)
        return record

    def play(self, game_id: str, action: int) -> tuple[GameRecord, list[GameEvent]]:
        """Aplica la acción humana y hace jugar al bot hasta que vuelva a tocar al humano o
        termine la mano. Devuelve la partida y los eventos nuevos."""
        record = self.get(game_id)
        with record.lock:
            state = record.state
            if state.phase is not Phase.PLAYING or state.hand.current_player != HUMAN:
                raise InvalidMoveError("no es el turno del humano")
            legal = legal_actions(state)
            if action not in legal:
                raise InvalidMoveError(f"acción ilegal: {action}")
            start = len(record.events)
            self._apply(record, HUMAN, Action(action), policy=None)
            self._run_bot(record)
            self.repo.save(record)
            return record, record.events[start:]

    def next_hand(self, game_id: str) -> tuple[GameRecord, list[GameEvent]]:
        record = self.get(game_id)
        with record.lock:
            if record.state.phase is not Phase.HAND_OVER:
                raise InvalidMoveError("la mano no terminó")
            start = len(record.events)
            record.state = next_hand(record.state, record.deal_rng)
            self._emit_deal(record)
            self._run_bot(record)
            self.repo.save(record)
            return record, record.events[start:]

    # -- internos -----------------------------------------------------------

    def _event(
        self,
        record: GameRecord,
        actor: Actor,
        type_: str,
        *,
        action: Action | None = None,
        card: int | None = None,
        policy: dict[Action, float] | None = None,
        detail: dict[str, object] | None = None,
    ) -> None:
        record.events.append(
            GameEvent(
                seq=len(record.events),
                hand_number=record.state.hand_number,
                actor=actor,
                type=type_,
                action=action,
                card=card,
                policy=policy,
                detail=detail or {},
            )
        )

    def _emit_deal(self, record: GameRecord) -> None:
        mano = record.state.hand.mano
        self._event(record, "system", "deal", detail={"mano": record.actor(mano)})

    def _apply(
        self, record: GameRecord, seat: int, action: Action, policy: dict[Action, float] | None
    ) -> None:
        before = record.state
        card = before.hand.hands[seat][int(action)] if action in PLAY_ACTIONS else None
        record.state = apply(before, action)
        self._event(record, record.actor(seat), "action", action=action, card=card, policy=policy)
        self._emit_consequences(record, before)

    def _emit_consequences(self, record: GameRecord, before: GameState) -> None:
        after = record.state
        env = after.hand.envido
        if env.resolved and not before.hand.envido.resolved:
            assert env.winner is not None
            detail: dict[str, object] = {
                "accepted": env.accepted,
                "winner": record.actor(env.winner),
                "points": env.points,
            }
            if env.values is not None:
                detail["values"] = {"human": env.values[HUMAN], "bot": env.values[BOT]}
            self._event(record, "system", "envido_result", detail=detail)
        if after.hand.finished and not before.hand.finished:
            assert after.hand.winner is not None
            self._event(
                record,
                "system",
                "hand_end",
                detail={
                    "winner": record.actor(after.hand.winner),
                    "points": {"human": after.hand.points[HUMAN], "bot": after.hand.points[BOT]},
                    "folded_by": None
                    if after.hand.folded_by is None
                    else record.actor(after.hand.folded_by),
                },
            )
        if after.is_terminal and not before.is_terminal:
            assert after.winner is not None
            self._event(record, "system", "game_end", detail={"winner": record.actor(after.winner)})

    def _run_bot(self, record: GameRecord) -> None:
        while record.state.phase is Phase.PLAYING and record.state.hand.current_player == BOT:
            legal = legal_actions(record.state)
            obs = observe(record.state, BOT)
            policy = record.bot.policy(obs, legal)
            action = record.bot.act(obs, legal, record.bot_rng)
            self._apply(record, BOT, action, policy=policy)
