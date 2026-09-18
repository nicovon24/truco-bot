# ADR 0007 — MaskablePPO de sb3-contrib en lugar de PPO propio

- Estado: Aceptada
- Fecha: 2026-09-18

## Contexto

El espacio fijo contiene muchas acciones ilegales según el estado. PPO se usa como comparación experimental, no como contribución algorítmica propia.

## Decisión

Usar `MaskablePPO` de `sb3-contrib` con un entorno Gymnasium que implemente `action_masks()`. No implementar PPO desde cero.

## Alternativas consideradas

- PPO propio: ofrece control total, pero multiplica riesgos de errores sin aportar al objetivo principal.
- PPO sin máscara y penalización de acciones ilegales: desperdicia muestras y cambia el problema de aprendizaje.

## Consecuencias

- Se reutiliza una implementación mantenida y preparada para máscaras.
- El entorno debe cumplir los contratos de Gymnasium y `sb3-contrib`.
- La reproducibilidad también depende de las versiones fijadas de esas bibliotecas.

