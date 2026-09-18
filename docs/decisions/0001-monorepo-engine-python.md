# ADR 0001 — Monorepo con motor Python puro separado de la API

- Estado: Aceptada
- Fecha: 2026-09-18

## Contexto

Las reglas deben reutilizarse en partidas servidas, entrenamiento y evaluación sin depender de HTTP ni de frameworks de ML. El proyecto también necesita coordinar contratos entre Python y TypeScript.

## Decisión

Mantener `engine/`, `api/`, `training/` y `web/` en un monorepo. `engine/` será Python puro y no importará FastAPI, PyTorch ni dependencias de la web. `api/` y `training/` dependerán del motor.

## Alternativas consideradas

- Repositorios separados: complican cambios atómicos de contratos y reproducibilidad.
- Reglas dentro de la API: acoplan entrenamiento e inferencia al transporte web.
- Motor en TypeScript: obliga al entrenamiento Python a mantener otro binding o duplicar reglas.

## Consecuencias

- Un mismo motor autoritativo sirve a partidas y entrenamiento.
- CI debe validar varios paquetes y dos ecosistemas.
- Los límites de dependencias deben verificarse para evitar acoplamientos accidentales.

