"""Registro de agentes servibles.

Al arrancar incluye los agentes base (random, heurístico) y lee `models/*/metadata.json`. Cada
modelo se valida contra el contrato del motor; si el binario no está en la caché local se descarga
desde la URL de la metadata y se verifica su checksum. Un modelo inválido hace fallar el arranque
de forma visible.
"""

from __future__ import annotations

import hashlib
import logging
import shutil
import urllib.request
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ValidationError

from truco_engine import CONTRACT_VERSION, ENCODE_SIZE, NUM_ACTIONS
from truco_engine.agents import Agent, HeuristicAgent, RandomAgent
from truco_engine.agents.neural_agent import NeuralAgent
from truco_engine.agents.tabular_agent import TabularAgent
from truco_engine.tabular import TabularPolicy

logger = logging.getLogger(__name__)


class RegistryError(RuntimeError):
    pass


class ContractInfo(BaseModel):
    version: str
    num_actions: int
    encode_size: int


class ArtifactInfo(BaseModel):
    url: str
    sha256: str
    filename: str


class ModelMetadata(BaseModel):
    name: str
    type: Literal["tabular", "neural"]
    version: str
    description: str = ""
    created_at: str
    commit: str
    seed: int
    config: dict[str, object] = {}
    contract: ContractInfo
    artifact: ArtifactInfo
    evaluation: dict[str, object] = {}


@dataclass(frozen=True)
class AgentEntry:
    id: str
    name: str
    type: str
    description: str
    model_version: str | None
    factory: Callable[[], Agent]


def validate_contract(meta: ModelMetadata) -> None:
    c = meta.contract
    if (c.version, c.num_actions, c.encode_size) != (CONTRACT_VERSION, NUM_ACTIONS, ENCODE_SIZE):
        raise RegistryError(
            f"modelo {meta.name}: contrato incompatible {c.model_dump()} "
            f"(motor: version={CONTRACT_VERSION}, num_actions={NUM_ACTIONS}, "
            f"encode_size={ENCODE_SIZE})"
        )


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def ensure_artifact(meta: ModelMetadata, cache_dir: Path) -> Path:
    """Devuelve la ruta local del binario, descargándolo si falta y verificando el checksum."""
    target = cache_dir / meta.name / meta.version / meta.artifact.filename
    if not target.exists():
        target.parent.mkdir(parents=True, exist_ok=True)
        tmp = target.with_suffix(target.suffix + ".part")
        logger.info("descargando %s desde %s", meta.name, meta.artifact.url)
        try:
            with urllib.request.urlopen(meta.artifact.url) as resp, tmp.open("wb") as out:
                shutil.copyfileobj(resp, out)
        except OSError as exc:
            tmp.unlink(missing_ok=True)
            raise RegistryError(f"modelo {meta.name}: no se pudo descargar: {exc}") from exc
        tmp.replace(target)
    digest = sha256_file(target)
    if digest != meta.artifact.sha256.lower():
        raise RegistryError(f"modelo {meta.name}: checksum inválido ({digest})")
    return target


def load_metadata(path: Path) -> ModelMetadata:
    try:
        return ModelMetadata.model_validate_json(path.read_text(encoding="utf-8"))
    except (OSError, ValidationError) as exc:
        raise RegistryError(f"metadata inválida en {path}: {exc}") from exc


def _model_factory(meta: ModelMetadata, artifact: Path) -> Callable[[], Agent]:
    """Valida que el artefacto cargue al arrancar y devuelve una fábrica por partida."""
    try:
        if meta.type == "tabular":
            policy, table_meta = TabularPolicy.load(artifact)
            variant = str((table_meta.get("game") or {}).get("variant", "sin_envido"))

            def tabular() -> Agent:
                return TabularAgent(policy, variant, name=meta.name)

            tabular()
            return tabular
        neural = NeuralAgent.load(artifact, name=meta.name)

        def neural_factory() -> Agent:
            return NeuralAgent(neural.session, name=meta.name)

        return neural_factory
    except (OSError, ValueError, TypeError, KeyError, ImportError) as exc:
        raise RegistryError(f"modelo {meta.name}: no se pudo cargar el artefacto: {exc}") from exc


class AgentRegistry:
    def __init__(self, entries: list[AgentEntry]) -> None:
        self._entries = {e.id: e for e in entries}

    @classmethod
    def load(cls, models_dir: Path, cache_dir: Path) -> AgentRegistry:
        entries = builtin_agents()
        if models_dir.is_dir():
            for meta_path in sorted(models_dir.glob("*/metadata.json")):
                meta = load_metadata(meta_path)
                validate_contract(meta)
                artifact = ensure_artifact(meta, cache_dir)
                entries.append(
                    AgentEntry(
                        id=meta.name,
                        name=_model_display_name(meta),
                        type=meta.type,
                        description=_model_description(meta),
                        model_version=meta.version,
                        factory=_model_factory(meta, artifact),
                    )
                )
        return cls(entries)

    def list(self) -> list[AgentEntry]:
        return list(self._entries.values())

    def get(self, agent_id: str) -> AgentEntry | None:
        return self._entries.get(agent_id)


def builtin_agents() -> list[AgentEntry]:
    return [
        AgentEntry(
            id="random",
            name="Principiante",
            type="random",
            description=(
                "Nivel fácil. Juega al azar entre las opciones válidas: ideal para practicar."
            ),
            model_version=None,
            factory=RandomAgent,
        ),
        AgentEntry(
            id="heuristic",
            name="Desafiante",
            type="heuristic",
            description=(
                "Nivel difícil. Usa una estrategia fija: mide el envido, cuida las cartas fuertes "
                "y a veces farolea."
            ),
            model_version=None,
            factory=HeuristicAgent,
        ),
    ]


def _model_display_name(meta: ModelMetadata) -> str:
    if meta.name == "cfr-sin-envido":
        return "Experimental"
    return meta.name.replace("-", " ").title()


def _model_description(meta: ModelMetadata) -> str:
    if meta.name == "cfr-sin-envido":
        return (
            "En prueba. Aprendió por simulación a jugar las cartas y el truco; "
            "el envido lo resuelve con estrategia fija."
        )
    return meta.description
