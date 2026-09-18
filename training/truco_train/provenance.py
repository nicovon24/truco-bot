"""Datos de procedencia comunes a corridas y reportes."""

from __future__ import annotations

import platform
import subprocess
from collections.abc import Mapping
from datetime import UTC, datetime
from typing import Any

from truco_engine import CONTRACT_VERSION


def git_commit() -> str:
    """Commit corto; `-dirty` si hay cambios en archivos trackeados."""
    try:
        out = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"], capture_output=True, text=True, check=True
        )
        dirty = subprocess.run(
            ["git", "status", "--porcelain", "--untracked-files=no"],
            capture_output=True,
            text=True,
            check=True,
        )
    except (OSError, subprocess.CalledProcessError):
        return "unknown"
    return out.stdout.strip() + ("-dirty" if dirty.stdout.strip() else "")


def run_info(config: Mapping[str, Any], config_path: str | None) -> dict[str, Any]:
    return {
        "name": config.get("name"),
        "config_path": config_path,
        "config": dict(config),
        "commit": git_commit(),
        "contract_version": CONTRACT_VERSION,
        "date": datetime.now(UTC).isoformat(timespec="seconds"),
        "platform": platform.platform(),
        "python": platform.python_version(),
    }
