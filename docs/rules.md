# Reglamento implementado por el motor

Este documento es la referencia humana del reglamento. Los puntos que estaban marcados "A CONFIRMAR" se cerraron el 2026-09-18 con el reglamento estándar propuesto y aceptado (ver [ADR 0010](decisions/0010-reglamento-confirmado.md)). La implementación está en `engine/truco_engine/rules.py` y `scoring.py`, y cada regla tiene tests en `engine/tests/`.

## Partida, mano y turnos

La partida es de dos jugadores y se juega a 15 puntos por defecto. `RulesConfig` permite 15 o 30. Cada mano reparte tres cartas por jugador y tiene hasta tres bazas. El rol de **mano** alterna al comenzar cada mano; el primer mano de la partida se sortea con el `random.Random` de la partida.

El ganador de una baza abre la siguiente. Si la baza termina parda, abre el **mano original de esa mano**.

La partida termina en cuanto un jugador alcanza el objetivo, aunque sea en medio de una mano (por ejemplo, al cobrar un envido).

La flor queda representada por un flag de configuración y una acción reservada, pero no se implementa: la acción siempre es ilegal y `RulesConfig(flor=True)` lanza `NotImplementedError`.

## Mazo y jerarquía de Truco

Se usa el mazo español de 40 cartas, sin 8 ni 9. Las cartas de un mismo escalón tienen la misma fuerza y empatan entre sí.

| Fuerza | Cartas |
|---:|---|
| 1, mayor | 1 de espada |
| 2 | 1 de basto |
| 3 | 7 de espada |
| 4 | 7 de oro |
| 5 | todos los 3 |
| 6 | todos los 2 |
| 7 | 1 de oro, 1 de copa |
| 8 | todos los 12 |
| 9 | todos los 11 |
| 10 | todos los 10 |
| 11 | 7 de copa, 7 de basto |
| 12 | todos los 6 |
| 13 | todos los 5 |
| 14, menor | todos los 4 |

En el código el escalón se guarda invertido (`TRUCO_RANK`: 14 = 1 de espada, 1 = los 4).

## Bazas y pardas

Una carta gana una baza cuando pertenece a un escalón más alto que la carta rival. Si ambas cartas están en el mismo escalón, la baza es parda.

| Baza 1 | Baza 2 | Baza 3 | Resultado |
|---|---|---|---|
| Parda | A gana | No se juega | A gana la mano |
| Parda | Parda | A gana | A gana la mano |
| Parda | Parda | Parda | Gana el mano |
| A gana | Parda | No se juega | A gana la mano |
| A gana | A gana | No se juega | A gana la mano |
| A gana | B gana | B gana | B gana la mano |
| A gana | B gana | Parda | A gana la mano (quien ganó la primera) |

## Truco

El canto puede subir en tres niveles y se puede cantar en cualquier turno propio. Solo puede subirlo el jugador que no hizo el último canto. Ante un canto pendiente se puede querer, no querer, subir (lo que implica querer el canto anterior) o irse al mazo.

| Estado aceptado | Valor de la mano | Si se rechaza ese canto |
|---|---:|---:|
| Sin Truco | 1 | — |
| Truco | 2 | 1 para quien cantó Truco |
| Retruco | 3 | 2 para quien cantó Retruco |
| Vale cuatro | 4 | 3 para quien cantó Vale cuatro |

"No quiero" o irse al mazo con una subida pendiente: el rival cobra el **último nivel aceptado** (1 si no había truco querido).

## Envido

El envido solo puede cantarse durante la primera baza y antes de que **el que canta** haya tirado su carta. El pie puede cantar después de que el mano tiró la suya. No se puede cantar envido si ya hay un truco querido, ni volver a cantar una vez resuelto.

Cadenas legales: `E`, `E-E` (máximo dos envidos), `R`, `E-R`, `E-E-R`, y `F` después de cualquiera de ellas (o sola). Real envido una sola vez. Solo sube quien responde.

### Cálculo del valor

1. Si hay al menos dos cartas del mismo palo, se toman las dos de mayor valor de ese palo y se suman 20.
2. 10, 11 y 12 valen 0; las demás cartas valen su número.
3. Si no hay dos cartas del mismo palo, se usa el valor más alto de una carta.
4. Si ambos jugadores tienen el mismo valor, gana el mano.

Ejemplos: 7 y 6 del mismo palo valen 33; 12 y 5 del mismo palo valen 25; 7 de oro, 6 de copa y 4 de basto valen 7.

Cuando el envido es querido, los dos valores pasan a ser públicos en la observación.

### Puntaje

| Cadena | Querido | No querido |
|---|---:|---:|
| E | 2 | 1 |
| E-E | 4 | 2 |
| R | 3 | 1 |
| E-R | 5 | 2 |
| E-E-R | 7 | 4 |
| F | falta | 1 |
| X-F | falta | lo querible de X (E-F = 2, E-E-F = 4, R-F = 3, E-R-F = 5, E-E-R-F = 7) |

Regla general del "no quiero": lo querible de la cadena sin su último canto, con mínimo 1.

**Falta envido** = objetivo − puntaje del que va ganando (con empate, el mismo cálculo). En el adaptador de entrenamiento de una sola mano se usa `RulesConfig.falta_envido_fixed`.

## Prioridad del envido

"El envido está primero": ante un truco en la primera baza (sin truco querido todavía), quien responde puede cantar envido si todavía no tiró su carta. El truco queda suspendido; mientras el envido está pendiente no se puede cantar truco. Resuelto el envido, el mismo jugador vuelve a responder el truco (quiero, no quiero, retruco o mazo).

## Irse al mazo

Disponible en cada turno propio. La mano termina y el rival recibe:

1. si hay un envido pendiente, los puntos de "no quiero" de esa cadena;
2. si `RulesConfig.fold_envido_bonus` (por defecto activado), 1 punto de envido extra cuando se va en la primera baza, el envido nunca se cantó y no hay truco querido;
3. los puntos del truco al último nivel aceptado (un truco pendiente cuenta como "no quiero").
