# Experimento: MCCFR en Kuhn poker (validación, fase 6)

## Identidad

- Fecha: 2026-09-18
- Commit: `e2251f5` (registrado en `runs/mccfr_kuhn/metrics.json`)
- Autor: nicovon24 (con Claude Code)
- Objetivo: validar MCCFR external sampling antes de usarlo en truco.

## Configuración

- Config: `training/configs/mccfr_kuhn.yaml`
- Comando: `uv run truco-train train --config training/configs/mccfr_kuhn.yaml`
- Algoritmo: MCCFR external sampling, regret matching+ y promediado lineal
- Semilla: 20260918; 100.000 iteraciones; evaluación exacta cada 10.000

## Entorno

- AMD Ryzen 5 5600, Windows 11, Python 3.12.2. Duración: 5 s.

## Resultados

| Iteración | Valor para el jugador 1 | Explotabilidad exacta |
|---:|---:|---:|
| 10.000 | −0,05591 | 0,0120 |
| 30.000 | −0,05605 | 0,0061 |
| 60.000 | −0,05604 | 0,0031 |
| 100.000 | −0,05594 | 0,0039 |

Valor teórico: −1/18 ≈ −0,05556. Error final: 3,8·10⁻⁴. Gráfico: `reports/curves/mccfr.png`.

La explotabilidad exacta se calcula con la mejor respuesta de estrategia pura (64 estrategias por jugador), en `truco_train/eval/best_response.py`. El test `test_known_equilibrium_value_and_zero_exploitability` valida esa medición contra el equilibrio conocido (explotabilidad 0).

## Observaciones

- La corrida es determinista: repetirla con la misma semilla dio las mismas cifras en dos implementaciones de las tablas (objetos por nodo y matrices compactas).
- Después de 60.000 iteraciones la explotabilidad deja de bajar de forma monótona. Es el ruido del muestreo de MCCFR, alrededor de 0,003 a 0,005.

## Próximos pasos

Criterio de la fase 6 cumplido: convergencia a −1/18 y explotabilidad cercana a 0. Se habilita el uso en truco.
