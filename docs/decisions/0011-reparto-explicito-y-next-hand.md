# ADR 0011 — Reparto explícito entre manos y endpoint `next-hand`

- Estado: Aceptada
- Fecha: 2026-09-18

## Contexto

`apply(state, action)` debe ser pura, pero repartir la mano siguiente necesita azar. Además, el SPEC pide que la API haga jugar al bot "hasta que vuelva a tocar al humano o termine la mano", lo que deja al humano frente a una mano terminada.

## Decisión

- Una mano terminada deja el estado en `Phase.HAND_OVER` (sin acciones legales). La siguiente se reparte con `next_hand(state, rng)`, que recibe el `random.Random` explícito. Es el equivalente a un nodo de azar.
- La API expone `POST /games/{id}/next-hand` para que el cliente decida cuándo repartir (y mostrar el resultado de la mano antes).
- Cada partida de la API deriva de su semilla dos generadores: `"{seed}:deal"` para repartos y `"{seed}:bot"` para el bot. El torneo usa el mismo principio para que los repartos espejados sean idénticos.

## Alternativas consideradas

- Repartir automáticamente dentro de `apply`: rompe la pureza o mete un RNG en el estado.
- Repartir en la misma respuesta de la API: el humano no ve el cierre de la mano.

## Consecuencias

- La API tiene un endpoint más que los listados en el SPEC.
- `truco_hand` (fase 7) puede usar `HAND_OVER` como estado terminal sin cambios en el motor.
