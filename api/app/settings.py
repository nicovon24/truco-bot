"""Configuración por variables de entorno."""

from __future__ import annotations

from pathlib import Path
from typing import Annotated

from pydantic import field_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Lista separada por comas. Vacía = sin CORS.
    cors_origins: Annotated[list[str], NoDecode] = ["http://localhost:3000"]
    models_dir: Path = Path("models")
    model_cache_dir: Path = Path(".model_cache")
    log_level: str = "INFO"

    @field_validator("cors_origins", mode="before")
    @classmethod
    def _split_origins(cls, value: object) -> object:
        if isinstance(value, str):
            return [o.strip() for o in value.split(",") if o.strip()]
        return value
