from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import pytest

from app.agent_registry import (
    AgentRegistry,
    ModelMetadata,
    RegistryError,
    ensure_artifact,
    validate_contract,
)
from app.repositories.games import InMemoryGameRepository
from truco_engine import CONTRACT_VERSION, ENCODE_SIZE, NUM_ACTIONS


def _meta(tmp_path: Path, payload: bytes = b"modelo", **contract: Any) -> ModelMetadata:
    src = tmp_path / "src.bin"
    src.write_bytes(payload)
    return ModelMetadata.model_validate(
        {
            "name": "cfr-test",
            "type": "tabular",
            "version": "0.0.1",
            "created_at": "2026-09-18T00:00:00Z",
            "commit": "abc",
            "seed": 1,
            "contract": {
                "version": CONTRACT_VERSION,
                "num_actions": NUM_ACTIONS,
                "encode_size": ENCODE_SIZE,
            }
            | contract,
            "artifact": {
                "url": src.as_uri(),
                "sha256": hashlib.sha256(b"modelo").hexdigest(),
                "filename": "policy.msgpack",
            },
        }
    )


def test_builtin_registry_without_models(tmp_path: Path) -> None:
    reg = AgentRegistry.load(tmp_path / "models", tmp_path / "cache")
    assert [e.id for e in reg.list()] == ["random", "heuristic"]
    assert reg.get("random") is not None
    assert reg.get("nope") is None


def test_contract_validation(tmp_path: Path) -> None:
    validate_contract(_meta(tmp_path))
    with pytest.raises(RegistryError, match="contrato incompatible"):
        validate_contract(_meta(tmp_path, version="0"))
    with pytest.raises(RegistryError, match="contrato incompatible"):
        validate_contract(_meta(tmp_path, encode_size=ENCODE_SIZE + 1))


def test_artifact_download_and_checksum(tmp_path: Path) -> None:
    meta = _meta(tmp_path)
    path = ensure_artifact(meta, tmp_path / "cache")
    assert path.read_bytes() == b"modelo"
    # La segunda vez usa la caché.
    assert ensure_artifact(meta, tmp_path / "cache") == path


def test_artifact_bad_checksum(tmp_path: Path) -> None:
    meta = _meta(tmp_path, payload=b"otro")
    with pytest.raises(RegistryError, match="checksum"):
        ensure_artifact(meta, tmp_path / "cache")


def test_artifact_download_failure(tmp_path: Path) -> None:
    meta = _meta(tmp_path)
    broken = meta.artifact.model_copy(update={"url": (tmp_path / "missing").as_uri()})
    meta = meta.model_copy(update={"artifact": broken})
    with pytest.raises(RegistryError, match="descargar"):
        ensure_artifact(meta, tmp_path / "cache")


def test_registry_rejects_incompatible_model(tmp_path: Path) -> None:
    models = tmp_path / "models" / "cfr-test"
    models.mkdir(parents=True)
    meta = _meta(tmp_path, version="999")
    (models / "metadata.json").write_text(json.dumps(meta.model_dump()), encoding="utf-8")
    with pytest.raises(RegistryError, match="contrato incompatible"):
        AgentRegistry.load(tmp_path / "models", tmp_path / "cache")


def test_registry_rejects_invalid_metadata(tmp_path: Path) -> None:
    models = tmp_path / "models" / "broken"
    models.mkdir(parents=True)
    (models / "metadata.json").write_text("{}", encoding="utf-8")
    with pytest.raises(RegistryError, match="metadata inválida"):
        AgentRegistry.load(tmp_path / "models", tmp_path / "cache")


def test_registry_rejects_model_types_not_served_yet(tmp_path: Path) -> None:
    models = tmp_path / "models" / "cfr-test"
    models.mkdir(parents=True)
    meta = _meta(tmp_path)
    (models / "metadata.json").write_text(json.dumps(meta.model_dump()), encoding="utf-8")
    with pytest.raises(RegistryError, match="todavía no está soportado"):
        AgentRegistry.load(tmp_path / "models", tmp_path / "cache")


def test_in_memory_repository() -> None:
    repo = InMemoryGameRepository()
    assert repo.get("x") is None
    assert len(repo) == 0
