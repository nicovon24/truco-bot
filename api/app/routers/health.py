from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends

from app.agent_registry import AgentRegistry
from app.routers.deps import get_registry
from app.schemas.games import HealthOut
from truco_engine import CONTRACT_VERSION

router = APIRouter(tags=["health"])


@router.get("/health")
def health(registry: Annotated[AgentRegistry, Depends(get_registry)]) -> HealthOut:
    return HealthOut(status="ok", contract_version=CONTRACT_VERSION, agents=len(registry.list()))
