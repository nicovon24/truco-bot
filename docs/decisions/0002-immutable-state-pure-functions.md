# ADR 0002 — Estado inmutable y funciones puras en el motor

- Estado: Aceptada
- Fecha: 2026-09-18

## Contexto

El motor necesita reproducibilidad, exploración de árboles de juego y tests capaces de comparar transiciones sin estado oculto.

## Decisión

Representar `GameState` y `HandState` con dataclasses frozen. `legal_actions(state)` no modifica datos y `apply(state, action)` devuelve un estado nuevo.

## Alternativas consideradas

- Estado mutable orientado a objetos: reduce algunas asignaciones, pero hace más frágiles el backtracking, los tests y los recorridos de CFR.
- Copias manuales de objetos mutables: mantienen riesgos de aliasing y agregan disciplina implícita.

## Consecuencias

- Las transiciones son fáciles de testear, reproducir y compartir entre algoritmos.
- Puede haber costo de asignación; solo se optimizará con evidencia del profiler.
- La aleatoriedad debe permanecer fuera del estado global y entrar de forma explícita.

