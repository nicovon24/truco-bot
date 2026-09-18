"""Gráficos de evaluación para reports/: curvas contra el heurístico y matriz de win rates."""

from __future__ import annotations

import json
from collections.abc import Sequence
from pathlib import Path
from typing import Any

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

CURVE_KEYS = ("payoff_vs_heuristic", "payoff_vs_heuristic_actual", "exploitability")
Y_LABELS = {
    "payoff_vs_heuristic": "payoff por mano vs heurístico",
    "payoff_vs_heuristic_actual": "payoff por mano vs heurístico",
    "exploitability": "explotabilidad exacta",
}
X_KEYS = ("iteration", "timesteps")


def curve_points(metrics: Sequence[dict[str, Any]]) -> tuple[str, list[float], list[float]]:
    x_name, _, xs, ys = _curve(metrics)
    return x_name, xs, ys


def _curve(metrics: Sequence[dict[str, Any]]) -> tuple[str, str, list[float], list[float]]:
    xs: list[float] = []
    ys: list[float] = []
    x_name = "iteration"
    y_name = CURVE_KEYS[0]
    for row in metrics:
        y_key = next((k for k in CURVE_KEYS if k in row), None)
        x_key = next((k for k in X_KEYS if k in row), None)
        if y_key is None or x_key is None:
            continue
        x_name, y_name = x_key, y_key
        xs.append(float(row[x_key]))
        ys.append(float(row[y_key]))
    return x_name, y_name, xs, ys


def plot_curves(run_dirs: Sequence[Path], out: Path) -> Path:
    """Una curva por corrida: payoff por mano contra el heurístico durante el entrenamiento."""
    runs = [(d, json.loads((d / "metrics.json").read_text(encoding="utf-8"))) for d in run_dirs]
    fig, axes = plt.subplots(1, len(runs), figsize=(5 * len(runs), 3.6), squeeze=False)
    for ax, (run_dir, data) in zip(axes[0], runs, strict=True):
        x_name, y_name, xs, ys = _curve(data.get("metrics", []))
        ax.plot(xs, ys, marker="o", color="#1e4d3b")
        ax.axhline(0.0, color="#7b1e2c", linewidth=1, linestyle="--")
        ax.set_title(data.get("name") or run_dir.name)
        ax.set_xlabel("iteración" if x_name == "iteration" else "timesteps")
        ax.set_ylabel(Y_LABELS[y_name])
        ax.grid(alpha=0.3)
    fig.tight_layout()
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, dpi=130)
    plt.close(fig)
    return out


def plot_matrix(results_json: Path, out: Path) -> Path:
    """Matriz de win rate (fila contra columna) a partir de results.json del torneo."""
    data = json.loads(results_json.read_text(encoding="utf-8"))
    names = [a["id"] for a in data["agents"]]
    idx = {n: i for i, n in enumerate(names)}
    n = len(names)
    matrix: list[list[float | None]] = [[None] * n for _ in range(n)]
    for r in data["results"]:
        a, b = idx[r["agent_a"]], idx[r["agent_b"]]
        matrix[a][b] = r["win_rate_a"]
        matrix[b][a] = 1.0 - r["win_rate_a"]
    fig, ax = plt.subplots(figsize=(1.2 * n + 2, 1.0 * n + 1.5))
    shown = [[0.5 if v is None else v for v in row] for row in matrix]
    im = ax.imshow(shown, cmap="RdYlGn", vmin=0.0, vmax=1.0)
    ax.set_xticks(range(n), names, rotation=30, ha="right")
    ax.set_yticks(range(n), names)
    for i in range(n):
        for j in range(n):
            v = matrix[i][j]
            ax.text(j, i, "—" if v is None else f"{v:.2f}", ha="center", va="center", fontsize=9)
    ax.set_title("Win rate de la fila contra la columna (partidas a 15)")
    fig.colorbar(im, ax=ax, fraction=0.046)
    fig.tight_layout()
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, dpi=130)
    plt.close(fig)
    return out
