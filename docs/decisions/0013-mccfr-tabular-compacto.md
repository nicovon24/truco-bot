# ADR 0013 — Tablas compactas y export podado para MCCFR tabular en truco

- Estado: Aceptada
- Fecha: 2026-09-18

## Contexto

La primera corrida de MCCFR sobre `truco_hand` guardaba un objeto con tres arrays NumPy por information set. En 7 minutos llegó a 1,5 GB (`sin_envido`) y 2,3 GB (`completo`) y dejó la máquina con 0,5 GB libres de 16. La clave del information set sigue el SPEC (escalones de las cartas propias, envido, historial público) y no se abstrae más.

## Decisión

- Tablas como índice `dict[str, int]` más matrices `float32` contiguas de regrets y estrategia acumulada, y un contador de visitas `uint32`. Crecen por duplicación. Checkpoints en `npz` comprimido.
- La estrategia promedio exportada omite los information sets con menos de `export_min_visits` visitas (20 en las configs): sus promedios son ruido.
- `TabularAgent` normaliza la clave igual que el entrenamiento (marcador 0-0; en `sin_envido`, sin envido privado) y cae al heurístico cuando la clave falta, registrando la tasa de fallback.
- Presupuestos acotados por memoria: 60 k iteraciones en `sin_envido` y 15 k en `completo`.

## Alternativas consideradas

- Abstraer más las cartas (buckets): cambia el contrato de `info_key` y se aleja del SPEC.
- Claves hasheadas a 64 bits: ahorra memoria, pero pierde la legibilidad de la tabla y no resuelve el tamaño del export.

## Consecuencias

- La política tabular cubre solo la parte frecuente del árbol. El resto lo juega el heurístico, y la tasa de fallback se reporta.
- Es la motivación práctica de Deep CFR (fase 9): una red generaliza a information sets no vistos.
