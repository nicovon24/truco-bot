# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Users

Dos audiencias con el mismo peso (confirmado):

- **Jugadores de truco** que quieren jugar partidas completas 1 vs 1 contra bots, desde el celular o la compu, y repetir contra rivales más fuertes.
- **Gente técnica** (devs, reclutadores, curiosos del aprendizaje por refuerzo) que juega una partida corta y abre el modo análisis para ver cómo decide cada bot.

## Product Purpose

Truco argentino 1 vs 1 en el navegador contra bots de dificultad creciente: random, heurístico y, en fases futuras, CFR tabular, Deep CFR y PPO entrenados por self-play. El éxito es que se pueda completar una partida sin fricción y que el modo análisis muestre con honestidad las probabilidades que usó el bot en cada decisión.

## Positioning

El rival no es un script de reglas escondido: cada decisión del bot trae su policy explícita (probabilidades por acción), que la mesa puede mostrar. Las reglas viven solo en el motor. El front no conoce reglas: renderiza la observación y las acciones legales que manda la API.

## Operating Context

- Antes de repartir se elige una partida rápida a 15 puntos o completa a 30, con manos de hasta tres bazas y cantos de truco y envido.
- El humano siempre es el asiento "human". La API responde con la observación, las acciones legales con su texto, el marcador y un log de eventos (acciones, resultado del envido, fin de mano, fin de partida).
- Cuando termina una mano, el jugador ve el resultado y pide la siguiente (`POST /games/{id}/next-hand`).
- Las partidas viven en memoria del servidor: un reinicio las pierde, y el cliente tiene que poder empezar otra.

## Capabilities and Constraints

- Selector de bot desde `GET /agents`.
- Mesa: cartas propias clickeables, bazas jugadas, dorso de las cartas del rival, marcador, log de cantos.
- Botonera con SOLO las acciones legales que devuelve la API. El front no deduce reglas.
- Modo análisis (toggle): probabilidades que usó el bot en cada decisión.
- Cartas dibujadas con CSS/SVG propio (sin imágenes de terceros). Mobile first.
- La URL de la API se configura con `NEXT_PUBLIC_API_URL`.
- Stack fijo: Next.js App Router, TypeScript strict, Tailwind 4, Zustand, tipos generados con openapi-typescript.
- Fuera de alcance: flor, 2 vs 2, online entre personas, cuentas, ranking.

## Brand Commitments

- Nombre visible: **Truco Bot**.
- Voz: rioplatense de mesa. Voseo y los cantos tal como se dicen en la mesa ("Te toca", "Quiero retruco", "Me voy al mazo"). Los textos de las acciones legales llegan desde la API.

## Evidence on Hand

- La interfaz presenta `random` como **Principiante**, `heuristic` como **Desafiante** y `cfr-sin-envido` como **Experimental**. Los nombres técnicos y el alcance de cada estrategia siguen visibles en la explicación. El heurístico le gana al random en el 95,2% de las partidas (ver `reports/tournament_basic`); CFR todavía no se presenta como un nivel superior.
- No hay testimonios, usuarios ni métricas de uso. No inventarlos.

## Product Principles

1. La API es la única autoridad: lo que no está en la respuesta no se muestra ni se infiere.
2. Jugar primero: el camino a la primera carta tirada es corto.
3. Transparencia del bot: la policy se muestra tal cual, sin redondear la verdad.
4. Se lee como una mesa de truco, no como un formulario.

## Accessibility & Inclusion

Uso en celular con una mano: objetivos táctiles amplios, contraste legible en ambientes con luz, y cartas y acciones operables con teclado y lector de pantalla (cada carta anuncia número y palo).
