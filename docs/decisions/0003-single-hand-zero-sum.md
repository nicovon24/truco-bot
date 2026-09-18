# ADR 0003 — Entrenamiento sobre una mano de suma cero sin marcador

- Estado: Aceptada
- Fecha: 2026-09-18

## Contexto

Una partida completa a 15 agrega un marcador de largo horizonte y aumenta el espacio de estados. La primera meta es validar algoritmos y aprender políticas de una mano.

## Decisión

El adaptador `truco_hand` modelará una sola mano. El retorno será `puntos ganados - puntos perdidos`, con retornos opuestos para ambos jugadores. Ignorará el marcador, salvo un valor fijo configurable para Falta Envido.

## Alternativas consideradas

- Entrenar partidas completas desde el inicio: representa mejor la estrategia dependiente del marcador, pero amplía mucho el problema antes de validar el método.
- Recompensa solo por ganar la mano: pierde la magnitud de los cantos.

## Consecuencias

- El juego de entrenamiento es más pequeño y claramente de suma cero.
- La política no aprende adaptaciones estratégicas al marcador.
- La evaluación principal sigue usando partidas completas a 15.
- Incorporar el marcador al entrenamiento queda en el roadmap posterior.

