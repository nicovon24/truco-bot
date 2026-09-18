# Experimento: torneo básico random vs heurístico

## Identidad

- Fecha: 2026-09-18
- Commit: ver `reports/tournament_basic/results.json`
- Autor: nicovon24 (con Claude Code)
- Objetivo: cerrar la fase 3 comparando los bots base con semillas fijas.

## Configuración

- Archivo: `training/configs/tournament_basic.yaml`
- Comando: `uv run truco-train eval tournament --config training/configs/tournament_basic.yaml`
- Semilla: 20260918; 1000 pares espejados (2000 partidas a 15)
- Heurístico con `HeuristicConfig()` por defecto; contrato v1

## Resultados del torneo

- Reporte: `reports/tournament_basic/tournament.md` y `results.json`
- random vs heurístico: el random gana 95 de 2000 (win rate 0,048; IC Wilson 95% [0,039; 0,058]).
- Diferencia media de puntos para el random: −8,68 por partida. 9,3 manos por partida en promedio.

## Observaciones

El IC de Wilson se calcula sobre partidas; los pares espejados no son independientes, así que es aproximado. El método definitivo es tarea de la fase 8.

## Próximos pasos

Usar al heurístico como rival fijo para las curvas de entrenamiento.
