# ADR 0014 — Textos de eventos y de la policy del bot generados por la API

- Estado: Aceptada
- Fecha: 2026-09-18

## Contexto

El front no puede deducir reglas y el modo análisis tiene que mostrar la policy del bot. La revisión de diseño pidió nombrar cada acción de la policy con la carta concreta ("12 de basto"). Pero la policy del bot se calcula sobre sus cartas ocultas: nombrarlas antes de que se jueguen revelaría información privada, y el SPEC prohíbe que la observación exponga cartas ocultas del rival.

## Decisión

- `EventOut` trae `label` (texto del canto o "Tira el 7 de oro").
- `EventOut.policy` es una lista `{action, name, label, probability}` ordenada de mayor a menor. Las cartas del bot se nombran por slot: "Carta 1/2/3 del bot". La carta elegida aparece nombrada solo en el evento de la jugada, cuando ya es pública.
- Las acciones legales del humano traen su `label` ("Tirar 1 de espada", "Quiero retruco", "Me voy al mazo").

## Consecuencias

- El front no tiene tablas de textos de acciones: todo lo textual del juego sale de un solo lugar.
- La policy expone el orden de slots (menor a mayor jerarquía), que es un dato del contrato y no una carta concreta.
