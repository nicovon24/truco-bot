# ADR 0005 — Espacio fijo de 13 acciones como contrato versionado

- Estado: Aceptada
- Fecha: 2026-09-18

## Contexto

Los modelos tabulares, redes, máscaras, API y cliente deben interpretar cada acción de la misma manera a lo largo del tiempo.

## Decisión

Usar exactamente 13 índices: tres slots de carta, tres cantos de envido, tres cantos de Truco, Quiero, No quiero, Irse al mazo y una posición reservada para Flor. El orden publicado en `docs/action-space.md` es contractual y cada artefacto declara su versión.

## Alternativas consideradas

- Espacio dinámico por estado: reduce acciones en cada decisión, pero rompe salidas fijas y complica máscaras y serving.
- Eliminar la posición de Flor: exigiría ampliar el output de todos los modelos si se implementa después.

## Consecuencias

- Redes y máscaras siempre tienen 13 salidas.
- La acción reservada permanece ilegal por ahora.
- Cambiar un índice o su semántica exige una nueva versión y puede invalidar modelos existentes.

