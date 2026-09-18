from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from app.routers.deps import get_service
from app.schemas.games import ActionIn, ActionResultOut, CreateGameIn, GameOut
from app.schemas.mappers import event_out, game_out
from app.services.game_service import (
    GameNotFoundError,
    GameService,
    InvalidMoveError,
    UnknownAgentError,
)

router = APIRouter(prefix="/games", tags=["games"])

Service = Annotated[GameService, Depends(get_service)]


@router.post("", status_code=status.HTTP_201_CREATED)
def create_game(body: CreateGameIn, service: Service) -> GameOut:
    try:
        record = service.create(body.agent_id, body.seed, body.target_score)
    except UnknownAgentError as exc:
        raise HTTPException(
            status.HTTP_422_UNPROCESSABLE_CONTENT, f"agente desconocido: {exc}"
        ) from exc
    return game_out(record)


@router.get("/{game_id}")
def get_game(game_id: str, service: Service) -> GameOut:
    try:
        return game_out(service.get(game_id))
    except GameNotFoundError as exc:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "partida inexistente") from exc


@router.post("/{game_id}/actions")
def play_action(game_id: str, body: ActionIn, service: Service) -> ActionResultOut:
    try:
        record, events = service.play(game_id, body.action)
    except GameNotFoundError as exc:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "partida inexistente") from exc
    except InvalidMoveError as exc:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_CONTENT, str(exc)) from exc
    return ActionResultOut(game=game_out(record), new_events=[event_out(e) for e in events])


@router.post("/{game_id}/next-hand")
def deal_next_hand(game_id: str, service: Service) -> ActionResultOut:
    try:
        record, events = service.next_hand(game_id)
    except GameNotFoundError as exc:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "partida inexistente") from exc
    except InvalidMoveError as exc:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_CONTENT, str(exc)) from exc
    return ActionResultOut(game=game_out(record), new_events=[event_out(e) for e in events])
