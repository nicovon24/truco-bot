"""Dependencias compartidas por los routers."""

from __future__ import annotations

from fastapi import Request

from app.agent_registry import AgentRegistry
from app.services.game_service import GameService


def get_registry(request: Request) -> AgentRegistry:
    registry: AgentRegistry = request.app.state.registry
    return registry


def get_service(request: Request) -> GameService:
    service: GameService = request.app.state.game_service
    return service
