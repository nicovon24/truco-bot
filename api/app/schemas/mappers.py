"""Conversión de estado del motor a schemas de la API (perspectiva del humano)."""

from __future__ import annotations

from app.schemas.games import (
    BazaOut,
    CardOut,
    EnvidoOut,
    EventOut,
    GameOut,
    LegalActionOut,
    ObservationOut,
    Seat,
    SlotOut,
    Status,
    SuitName,
    TrucoOut,
)
from app.services.game_service import BOT, HUMAN, GameEvent, GameRecord, action_label
from truco_engine import Action, Phase, legal_actions, observe
from truco_engine.cards import Suit, card_number, card_str, card_suit
from truco_engine.state import NO_CARD, PARDA

_STATUS: dict[Phase, Status] = {
    Phase.PLAYING: "playing",
    Phase.HAND_OVER: "hand_over",
    Phase.GAME_OVER: "game_over",
}


_SUITS: dict[Suit, SuitName] = {
    Suit.ESPADA: "espada",
    Suit.BASTO: "basto",
    Suit.ORO: "oro",
    Suit.COPA: "copa",
}


def seat(player: int | None) -> Seat | None:
    if player is None:
        return None
    return "human" if player == HUMAN else "bot"


def card_out(card: int | None) -> CardOut | None:
    if card is None or card == NO_CARD:
        return None
    return CardOut(
        id=card, number=card_number(card), suit=_SUITS[card_suit(card)], label=card_str(card)
    )


def event_out(ev: GameEvent) -> EventOut:
    return EventOut(
        seq=ev.seq,
        hand_number=ev.hand_number,
        actor=ev.actor,
        type=ev.type,
        action=None if ev.action is None else int(ev.action),
        action_name=None if ev.action is None else ev.action.name,
        card=card_out(ev.card),
        policy=None if ev.policy is None else {a.name: p for a, p in sorted(ev.policy.items())},
        detail=ev.detail,
    )


def game_out(record: GameRecord) -> GameOut:
    state = record.state
    obs = observe(state, HUMAN)
    bazas = []
    for i, pair in enumerate(obs.played):
        result = None
        if i < len(obs.results):
            r = obs.results[i]
            result = "parda" if r == PARDA else seat(r)
        bazas.append(BazaOut(human=card_out(pair[HUMAN]), bot=card_out(pair[BOT]), result=result))
    bot_played = sum(1 for pair in obs.played if pair[BOT] != NO_CARD)
    human_legal: list[Action] = (
        legal_actions(state)
        if state.phase is Phase.PLAYING and state.hand.current_player == HUMAN
        else []
    )
    observation = ObservationOut(
        hand_number=obs.hand_number,
        mano=seat(obs.mano) or "human",
        turn=seat(obs.current_player),
        baza=obs.baza,
        my_cards=[SlotOut(slot=i, card=card_out(c)) for i, c in enumerate(obs.my_slots)],
        bot_cards_in_hand=3 - bot_played,
        bazas=bazas,
        truco=TrucoOut(
            level=obs.truco_level,
            pending=obs.truco_pending,
            last_caller=seat(obs.truco_last_caller),
        ),
        envido=EnvidoOut(
            calls=[a.name for a in obs.envido_calls],
            pending=obs.envido_pending,
            caller=seat(obs.envido_caller),
            resolved=obs.envido_resolved,
            accepted=obs.envido_accepted,
            human_value=obs.my_envido,
            bot_value=None if obs.envido_values is None else obs.envido_values[BOT],
            winner=seat(obs.envido_winner),
            points=obs.envido_points,
        ),
        hand_finished=obs.hand_finished,
        hand_winner=seat(obs.hand_winner),
        hand_points={"human": obs.hand_points[HUMAN], "bot": obs.hand_points[BOT]},
    )
    return GameOut(
        id=record.id,
        agent_id=record.agent_id,
        seed=record.seed,
        status=_STATUS[state.phase],
        scores={"human": state.scores[HUMAN], "bot": state.scores[BOT]},
        target_score=state.config.target_score,
        winner=seat(state.winner),
        observation=observation,
        legal_actions=[
            LegalActionOut(id=int(a), name=a.name, label=action_label(a, state, HUMAN))
            for a in human_legal
        ],
        events=[event_out(e) for e in record.events],
    )
