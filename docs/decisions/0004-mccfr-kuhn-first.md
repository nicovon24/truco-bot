# ADR 0004 — Validar MCCFR tabular en Kuhn antes de usar redes

- Estado: Aceptada
- Fecha: 2026-09-18

## Contexto

Los errores en juegos de información imperfecta pueden confundirse con problemas de escala, representación o redes neuronales. Kuhn Poker tiene un valor conocido y explotabilidad calculable.

## Decisión

Implementar MCCFR tabular con external sampling y validarlo en Kuhn. No avanzar a Truco ni a métodos neuronales hasta reproducir convergencia hacia `−1/18` para el primer jugador y explotabilidad hacia cero.

## Alternativas consideradas

- Empezar directamente con Truco: dificulta separar errores algorítmicos de errores del motor.
- Empezar con Deep CFR o PPO: agrega aproximación funcional y más hiperparámetros antes de validar la base.

## Consecuencias

- Existe una prueba controlada del algoritmo.
- Se agrega una implementación de juego que no forma parte del producto final.
- La fase de Truco queda bloqueada si la validación no converge.

