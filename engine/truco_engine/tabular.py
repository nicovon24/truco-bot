"""Política tabular: dict[info_key] -> probabilidades, serializada en msgpack.

La escribe el entrenamiento (MCCFR) y la lee `TabularAgent`."""

from __future__ import annotations

from collections.abc import Iterator, Mapping
from pathlib import Path
from typing import Any

import msgpack
import numpy as np
import numpy.typing as npt

FORMAT_VERSION = 1


class TabularPolicy:
    """Probabilidades por information set sobre el espacio fijo de acciones del juego."""

    def __init__(
        self, num_actions: int, table: Mapping[str, npt.NDArray[np.float64]] | None = None
    ) -> None:
        self.num_actions = num_actions
        self._table: dict[str, npt.NDArray[np.float64]] = dict(table or {})

    def __len__(self) -> int:
        return len(self._table)

    def __contains__(self, key: object) -> bool:
        return key in self._table

    def __iter__(self) -> Iterator[str]:
        return iter(self._table)

    def get(self, key: str) -> npt.NDArray[np.float64] | None:
        return self._table.get(key)

    def set(self, key: str, probs: npt.NDArray[np.float64]) -> None:
        if probs.shape != (self.num_actions,):
            raise ValueError(f"shape inválido {probs.shape}")
        self._table[key] = probs

    def to_bytes(self, metadata: Mapping[str, Any] | None = None) -> bytes:
        payload = {
            "format_version": FORMAT_VERSION,
            "num_actions": self.num_actions,
            "metadata": dict(metadata or {}),
            "table": {k: [float(p) for p in v] for k, v in sorted(self._table.items())},
        }
        data: bytes = msgpack.packb(payload, use_bin_type=True)
        return data

    @classmethod
    def from_bytes(cls, data: bytes) -> tuple[TabularPolicy, dict[str, Any]]:
        payload = msgpack.unpackb(data, raw=False)
        if payload.get("format_version") != FORMAT_VERSION:
            raise ValueError("versión de formato de política tabular incompatible")
        policy = cls(int(payload["num_actions"]))
        for key, probs in payload["table"].items():
            policy.set(key, np.asarray(probs, dtype=np.float64))
        return policy, dict(payload.get("metadata") or {})

    def save(self, path: Path, metadata: Mapping[str, Any] | None = None) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(self.to_bytes(metadata))

    @classmethod
    def load(cls, path: Path) -> tuple[TabularPolicy, dict[str, Any]]:
        return cls.from_bytes(path.read_bytes())
