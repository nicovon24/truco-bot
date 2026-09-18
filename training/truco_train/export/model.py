"""Exporta una corrida a un artefacto servible y escribe `models/<nombre>/metadata.json`.

El binario queda en `artifacts/<nombre>/<versión>/` (fuera de Git) y se copia a la caché local de
la API (`.model_cache/`), así `agent_registry` lo encuentra sin descargarlo. La URL pública sale de
`artifact_base_url`; publicar el binario ahí (GitHub Releases o S3) es un paso manual.
"""

from __future__ import annotations

import hashlib
import json
import shutil
from collections.abc import Mapping
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from truco_engine import CONTRACT_VERSION, ENCODE_SIZE, NUM_ACTIONS
from truco_engine.tabular import TabularPolicy
from truco_train.provenance import git_commit

DEFAULT_BASE_URL = "https://github.com/nicovon24/truco-bot/releases/download/models"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _build_artifact(
    kind: str, run_dir: Path, target: Path, run: Mapping[str, Any]
) -> dict[str, Any]:
    if kind == "tabular":
        src = run_dir / "policy.msgpack"
        policy, meta = TabularPolicy.load(src)
        if policy.num_actions != NUM_ACTIONS:
            raise ValueError("la política tabular no usa el espacio de 13 acciones")
        shutil.copyfile(src, target)
        return {"infosets": len(policy), "variant": (meta.get("game") or {}).get("variant")}
    if kind == "neural" and (run_dir / "policy.onnx").exists():
        # PPO: el ONNX ya se exportó y validó (paridad) al terminar la corrida.
        shutil.copyfile(run_dir / "policy.onnx", target)
        return {"onnx_parity_max_abs_error": run.get("onnx_parity_max_abs_error")}
    if kind == "neural":
        import torch

        from truco_train.deep_cfr.networks import MLP
        from truco_train.export.to_onnx import export_with_parity

        hidden = int(run.get("hidden", 256))
        model = MLP(ENCODE_SIZE, NUM_ACTIONS, hidden)
        state = torch.load(run_dir / "strategy.pt", map_location="cpu", weights_only=True)
        model.load_state_dict(state)
        err = export_with_parity(model, ENCODE_SIZE, target)
        return {"onnx_parity_max_abs_error": err, "hidden": hidden}
    raise ValueError(f"tipo de modelo desconocido: {kind}")


def export_model(config: Mapping[str, Any], config_path: str | None = None) -> Path:
    spec = config["export"]
    name = str(spec["name"])
    version = str(spec["version"])
    kind = str(spec["type"])
    run_dir = Path(spec.get("run_dir") or config.get("output_dir") or f"runs/{config['name']}")
    run: dict[str, Any] = json.loads((run_dir / "metrics.json").read_text(encoding="utf-8"))
    filename = "policy.msgpack" if kind == "tabular" else "strategy.onnx"

    artifact_dir = Path("artifacts") / name / version
    artifact_dir.mkdir(parents=True, exist_ok=True)
    artifact = artifact_dir / filename
    details = _build_artifact(kind, run_dir, artifact, run)
    checksum = sha256(artifact)

    cache = Path(spec.get("model_cache_dir", ".model_cache")) / name / version / filename
    cache.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(artifact, cache)

    base = str(spec.get("artifact_base_url", DEFAULT_BASE_URL)).rstrip("/")
    evaluation = {
        k: v
        for k, v in run.items()
        if k.startswith("final_") or k in ("iterations", "infosets", "exported_infosets")
    }
    if run.get("metrics"):
        evaluation["last_metrics"] = run["metrics"][-1]
    evaluation.update(spec.get("evaluation") or {})

    metadata = {
        "name": name,
        "type": kind,
        "version": version,
        "description": str(spec.get("description", "")),
        "created_at": datetime.now(UTC).isoformat(timespec="seconds"),
        "commit": git_commit(),
        "seed": int(run.get("config", {}).get("seed", config.get("seed", 0))),
        "config": {"train": run.get("config", {}), "export_config_path": config_path, **details},
        "contract": {
            "version": CONTRACT_VERSION,
            "num_actions": NUM_ACTIONS,
            "encode_size": ENCODE_SIZE,
        },
        "artifact": {
            "url": f"{base}/{name}-{version}-{filename}",
            "sha256": checksum,
            "filename": filename,
        },
        "evaluation": evaluation,
    }
    out = Path("models") / name / "metadata.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(metadata, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return out
