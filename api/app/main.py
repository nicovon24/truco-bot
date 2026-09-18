"""Punto de entrada de la aplicación FastAPI."""

from __future__ import annotations

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.agent_registry import AgentRegistry
from app.repositories.games import GameRepository, InMemoryGameRepository
from app.routers import agents, games, health
from app.services.game_service import GameService
from app.settings import Settings


def create_app(
    settings: Settings | None = None,
    registry: AgentRegistry | None = None,
    repository: GameRepository | None = None,
) -> FastAPI:
    if settings is None:
        settings = Settings()
    logging.basicConfig(level=settings.log_level.upper())
    if registry is None:
        registry = AgentRegistry.load(settings.models_dir, settings.model_cache_dir)
    if repository is None:
        repository = InMemoryGameRepository()

    app = FastAPI(title="Truco API", version="0.1.0")
    app.state.settings = settings
    app.state.registry = registry
    app.state.game_service = GameService(repository, registry)
    if settings.cors_origins:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=settings.cors_origins,
            allow_methods=["GET", "POST"],
            allow_headers=["Content-Type"],
        )
    app.include_router(health.router)
    app.include_router(agents.router)
    app.include_router(games.router)
    return app


app = create_app()
