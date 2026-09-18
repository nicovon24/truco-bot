"""CLI truco-train (typer)."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Annotated, Any

import typer
import yaml

from truco_train.eval.tournament import TournamentConfig, run_and_report


def _load(config: Path) -> dict[str, Any]:
    data: dict[str, Any] = yaml.safe_load(config.read_text(encoding="utf-8"))
    return data


app = typer.Typer(help="Entrenamiento, evaluación y exportación de bots de Truco.")
eval_app = typer.Typer(help="Evaluación de agentes.")
app.add_typer(eval_app, name="eval")


@app.command("train")
def train(
    config: Annotated[Path, typer.Option("--config", help="YAML de entrenamiento.", exists=True)],
) -> None:
    """Entrena según `algorithm` de la config (mccfr, deep_cfr, ppo)."""
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")
    data = _load(config)
    algorithm = data.get("algorithm")
    if algorithm == "mccfr":
        from truco_train.cfr.train import run_mccfr

        out = run_mccfr(data, config_path=config.as_posix())
    else:
        raise typer.BadParameter(f"algoritmo desconocido: {algorithm}")
    typer.echo(f"Corrida escrita en {out}")


@eval_app.command("tournament")
def tournament(
    config: Annotated[Path, typer.Option("--config", help="YAML del torneo.", exists=True)],
) -> None:
    """Torneo todos contra todos con repartos espejados; escribe tabla y JSON en reports/."""
    cfg = TournamentConfig.from_dict(_load(config))
    out = run_and_report(cfg, config_path=config.as_posix())
    typer.echo((out / "tournament.md").read_text(encoding="utf-8"))
    typer.echo(f"Reporte escrito en {out}")


if __name__ == "__main__":
    app()
