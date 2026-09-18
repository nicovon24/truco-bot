# Reglamento implementado por el motor

Este documento es la referencia humana del reglamento. Solo afirma comportamientos definidos en `SPEC.md`. Cada punto pendiente está señalado y debe resolverse antes de implementar la parte afectada del motor.

## Partida, mano y turnos

La partida es de dos jugadores y se juega a 15 puntos por defecto. `RulesConfig` permitirá parametrizar el puntaje objetivo a 15 o 30. Cada mano reparte tres cartas por jugador y tiene hasta tres bazas. El rol de **mano** alterna al comenzar cada mano.

El ganador de una baza abre la siguiente. Si la baza termina parda, abre el mano.

> ⚠️ A CONFIRMAR: si “abre el mano” siempre significa el mano original de esa mano o el jugador que abrió la baza que terminó parda.

La flor queda representada por un flag de configuración y una acción reservada, pero no se implementa: la acción siempre es ilegal.

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

## Bazas y pardas

Una carta gana una baza cuando pertenece a un escalón más alto que la carta rival. Si ambas cartas están en el mismo escalón, la baza es parda.

Casos definidos:

| Baza 1 | Baza 2 | Baza 3 | Resultado |
|---|---|---|---|
| Parda | A gana | No se juega | A gana la mano |
| Parda | Parda | A gana | A gana la mano |
| Parda | Parda | Parda | Gana el mano |
| A gana | Parda | No se juega | A gana la mano |
| A gana | A gana | No se juega | A gana la mano |

Ejemplo de primera parda: el mano juega un 5 de copa y el rival un 5 de oro. En la segunda baza el rival juega un 6 y el mano un 4. El rival gana la segunda baza y, con ella, la mano.

Ejemplo de segunda parda: el mano gana la primera baza con un 2 contra un 12. En la segunda ambos juegan un 6. La segunda es parda y la mano queda para quien ganó la primera.

Ejemplo de tres pardas: las tres parejas de cartas pertenecen al mismo escalón. La mano queda para el jugador que era mano al comenzar.

> ⚠️ A CONFIRMAR: si cada jugador gana una de las primeras dos bazas y la tercera es parda, falta definir expresamente quién gana la mano.

## Truco

El canto puede subir en tres niveles. Solo puede subirlo el jugador que no hizo el último canto. Ante un canto pendiente se puede querer, no querer o realizar una subida legal.

| Estado aceptado | Valor de la mano | Si se rechaza ese canto |
|---|---:|---:|
| Sin Truco | 1 | — |
| Truco | 2 | 1 para quien cantó Truco |
| Retruco | 3 | 2 para quien cantó Retruco |
| Vale cuatro | 4 | 3 para quien cantó Vale cuatro |

Ejemplo: A canta Truco y B quiere. Más tarde B canta Retruco y A dice No quiero. B recibe 2 puntos, el nivel anterior aceptado.

> ⚠️ A CONFIRMAR: qué valor se considera “Truco en juego” al irse al mazo mientras hay una subida pendiente todavía no aceptada.

## Envido

El envido solo puede cantarse durante la primera baza y antes de que el jugador que canta haya tirado su primera carta. Existen Envido, Real Envido y Falta Envido; se permiten Envido-Envido y combinaciones entre cantos.

> ⚠️ A CONFIRMAR: enumerar las cadenas legales completas, incluidos el máximo de Envidos consecutivos y desde qué cantos se puede subir a Real Envido o Falta Envido.

### Cálculo del valor

Para calcular el envido:

1. si hay al menos dos cartas del mismo palo, se toman dos de ese palo y se suman 20 más sus valores de envido;
2. 10, 11 y 12 valen 0; las demás cartas valen su número;
3. si no hay dos cartas del mismo palo, se usa el valor de envido más alto de una carta;
4. si ambos jugadores tienen el mismo valor, gana el mano.

Ejemplos:

- 7 y 6 del mismo palo valen 33.
- 12 y 5 del mismo palo valen 25.
- 7 de oro, 6 de copa y 4 de basto valen 7.
- Si ambos anuncian 29, gana el mano.

Cuando el envido es querido, los dos valores pasan a ser públicos en la observación.

### Puntaje

| Resolución | Puntaje |
|---|---|
| No quiero | Puntos acumulados antes del último canto, con mínimo de 1 |
| Envido querido | ⚠️ A CONFIRMAR |
| Envido-Envido querido | ⚠️ A CONFIRMAR |
| Real Envido querido, solo o combinado | ⚠️ A CONFIRMAR |
| Falta Envido querida | Lo que le falta al jugador que va ganando para alcanzar el puntaje objetivo |

> ⚠️ A CONFIRMAR: definir los valores sumados por Envido y Real Envido, y publicar una tabla exhaustiva de aceptación y rechazo para cada cadena legal.

> ⚠️ A CONFIRMAR: definir Falta Envido cuando el marcador está empatado y confirmar la fórmula para partidas a 15 y a 30.

En el adaptador de entrenamiento de una sola mano, Falta Envido usa un valor fijo configurable porque no existe un marcador de partida.

## Prioridad del envido

“El envido está primero”: si un jugador canta Truco en la primera baza, el rival puede responder con Envido antes de contestar el Truco.

> ⚠️ A CONFIRMAR: flujo exacto para reanudar el Truco después de resolver el Envido y acciones permitidas mientras ambos cantos están pendientes.

> ⚠️ A CONFIRMAR: confirmar que el segundo jugador puede cantar Envido después de que el primero haya tirado una carta, siempre que todavía no haya tirado la propia.

## Irse al mazo

Irse al mazo está disponible en cada turno propio. La mano termina y el rival recibe los puntos del Truco en juego. `RulesConfig` controla si corresponde agregar 1 punto de envido.

> ⚠️ A CONFIRMAR: estados exactos en los que se agrega ese punto de envido y valor predeterminado de la opción.

> ⚠️ A CONFIRMAR: puntaje cuando alguien se va al mazo con un canto de Truco, Envido o ambos pendiente de respuesta.

