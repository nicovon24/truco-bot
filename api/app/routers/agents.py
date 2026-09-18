from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends

from app.agent_registry import AgentRegistry
from app.routers.deps import get_registry
from app.schemas.games import AgentOut

router = APIRouter(tags=["agents"])


@router.get("/agents")
def list_agents(registry: Annotated[AgentRegistry, Depends(get_registry)]) -> list[AgentOut]:
    return [
        AgentOut(
            id=e.id,
            name=e.name,
            type=e.type,
            description=e.description,
            model_version=e.model_version,
        )
        for e in registry.list()
    ]
