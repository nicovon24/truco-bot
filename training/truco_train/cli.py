"""CLI truco-train (typer). Los subcomandos `train` y `export` se agregan en sus fases."""

from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer
import yaml

from truco_train.eval.tournament import TournamentConfig, run_and_report

app = typer.Typer(help="Entrenamiento, evaluación y exportación de bots de Truco.")
eval_app = typer.Typer(help="Evaluación de agentes.")
app.add_typer(eval_app, name="eval")


@eval_app.command("tournament")
def tournament(
    config: Annotated[Path, typer.Option("--config", help="YAML del torneo.", exists=True)],
) -> None:
    """Torneo todos contra todos con repartos espejados; escribe tabla y JSON en reports/."""
    data = yaml.safe_load(config.read_text(encoding="utf-8"))
    cfg = TournamentConfig.from_dict(data)
    out = run_and_report(cfg, config_path=config.as_posix())
    typer.echo((out / "tournament.md").read_text(encoding="utf-8"))
    typer.echo(f"Reporte escrito en {out}")


if __name__ == "__main__":
    app()
