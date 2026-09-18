# Experimento: MCCFR tabular en una mano de truco (fase 7)

## Identidad

- Fecha: 2026-09-18
- Commits: `sin_envido` en `1c193ac` y `completo` en `e2251f5` (ver `runs/*/metrics.json`)
- Autor: nicovon24 (con Claude Code)
- Objetivo: entrenar la política tabular de `truco_hand`, primero `sin_envido` y después `completo`, y servirla con `TabularAgent`.

## Configuración

- Configs: `training/configs/mccfr_truco_sin_envido.yaml` y `mccfr_truco_completo.yaml`
- Algoritmo: MCCFR external sampling, RM+ y promediado lineal. Tablas compactas (ADR 0013).
- Semilla: 20260918. Falta envido fija en 6.
- Presupuesto: 60.000 iteraciones (`sin_envido`) y 15.000 (`completo`), acotado por memoria.
- Export: information sets con al menos 20 visitas (`export_min_visits`).
- Evaluación: payoff medio por mano contra el heurístico, 300 repartos espejados (semilla 777).

## Entorno

- AMD Ryzen 5 5600, 16 GB, Windows 11, Python 3.12.2.

## Resultados

`sin_envido` (1.118 s, 4.245.107 information sets vistos, 22.085 exportados):

| Iteración | Payoff por mano vs heurístico | Fallback al heurístico |
|---:|---:|---:|
| 15.000 | −0,082 | 72% |
| 30.000 | −0,193 | 58% |
| 45.000 | −0,198 | 49% |
| 60.000 | −0,148 | 43% |

`completo`: ver `runs/mccfr_truco_completo/metrics.json`. Con 5.000 iteraciones la tasa de fallback ya era del 99,8%: casi ningún information set llega a 20 visitas.

## Observaciones

- **Primer intento fallido:** un objeto por nodo llevó la memoria a 1,5 y 2,3 GB en 7 minutos y dejó 0,5 GB libres. Las corridas se cortaron y se rehízo el almacenamiento (ADR 0013).
- El árbol de una mano es enorme para una tabla: incluso con 60.000 iteraciones, el 43% de las decisiones evaluadas cae en information sets sin datos confiables.
- La estrategia promedio tabular pierde contra el heurístico. El heurístico no es un equilibrio, sino un rival explotable con reglas fijas, y MCCFR con poco muestreo converge hacia un equilibrio que no explota esas reglas.
- Resultado esperado para el SPEC: el tabular sirve de base y motiva Deep CFR, que generaliza entre information sets.

## Próximos pasos

- Deep CFR (fase 9) sobre la variante `completo`.
- Si se quiere mejorar el tabular: más iteraciones en una máquina con más RAM, o abstracción de cartas (requiere versionar `info_key`).
