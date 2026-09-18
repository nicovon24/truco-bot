# ADR 0010 — Reglamento confirmado para el motor

- Estado: Aceptada
- Fecha: 2026-09-18

## Contexto

`docs/rules.md` tenía puntos "A CONFIRMAR" (pardas, cadenas y puntaje del envido, falta envido, "el envido está primero", irse al mazo con cantos pendientes). La regla del proyecto prohíbe inventarlos.

## Decisión

Se propuso el reglamento estándar argentino y el dueño del proyecto lo aceptó completo:

- Tras una parda abre el mano original. Una baza cada uno y tercera parda: gana quien ganó la primera.
- "No quiero" o mazo con subida de truco pendiente: el rival cobra el último nivel aceptado.
- Envido: E, E-E, R, E-R, E-E-R y F detrás de cualquiera; querido E=2, EE=4, R=3, ER=5, EER=7, F=falta; no querido = lo querible sin el último canto (mínimo 1).
- Falta = objetivo − puntaje del que va ganando, también con empate.
- El envido está primero: el que responde un truco en primera baza puede cantar envido; resuelto, vuelve a responder el truco. Con truco querido no hay envido.
- Mazo: cantos pendientes cuentan como "no quiero"; +1 de envido (activado por defecto) si se va en primera baza sin envido cantado y sin truco querido.

El detalle vive en `docs/rules.md`.

## Alternativas consideradas

- Variantes regionales (p. ej. falta con "malas y buenas" a 30): más complejas y no pedidas.

## Consecuencias

- El motor y sus tests quedan cerrados sobre estas reglas.
- Cambiar una regla que afecte al historial o a la observación puede requerir una nueva versión del contrato.
