# Contrato de acciones y observaciones

El espacio de acciones, `info_key()` y `encode()` forman el contrato entre motor, entrenamiento, modelos y API. Un artefacto solo puede cargarse si su metadata declara una versión compatible.

> ⚠️ A CONFIRMAR: identificador de la primera versión del contrato. Hasta resolverlo, no existe una versión publicable.

## Espacio fijo de acciones

| Índice | Identificador propuesto | Significado | Nota |
|---:|---|---|---|
| 0 | `PLAY_CARD_0` | Tirar la carta del slot 0 | Slot de menor jerarquía entre las cartas originales |
| 1 | `PLAY_CARD_1` | Tirar la carta del slot 1 | Slot intermedio entre las cartas originales |
| 2 | `PLAY_CARD_2` | Tirar la carta del slot 2 | Slot de mayor jerarquía entre las cartas originales |
| 3 | `ENVIDO` | Cantar Envido | Solo si las reglas lo permiten |
| 4 | `REAL_ENVIDO` | Cantar Real Envido | Solo si las reglas lo permiten |
| 5 | `FALTA_ENVIDO` | Cantar Falta Envido | Solo si las reglas lo permiten |
| 6 | `TRUCO` | Cantar Truco | Primer nivel |
| 7 | `RETRUCO` | Cantar Retruco | Segundo nivel |
| 8 | `VALE_CUATRO` | Cantar Vale Cuatro | Tercer nivel |
| 9 | `QUIERO` | Aceptar el canto pendiente | Resuelve o acepta según el canto |
| 10 | `NO_QUIERO` | Rechazar el canto pendiente | Otorga el puntaje correspondiente |
| 11 | `FOLD` | Irse al mazo | Termina la mano |
| 12 | `FLOR_RESERVED` | Reservada para Flor | Siempre ilegal mientras Flor no esté implementada |

La interpretación propuesta es asignar los tres slots una vez al repartir, ordenando las cartas de menor a mayor jerarquía de Truco. Jugar una carta no renumeraría los slots y una acción sobre un slot ya usado sería ilegal.

> ⚠️ A CONFIRMAR: confirmar que los slots permanecen estables durante toda la mano, en lugar de compactar las cartas restantes después de cada jugada.

> ⚠️ A CONFIRMAR: criterio de desempate estable para ordenar dos cartas del mismo escalón en slots distintos. Debe basarse en un orden canónico de las 40 cartas.

## `info_key(obs)`

La clave identifica un information set sin incluir cartas ocultas ni el mazo. Sus componentes, en este orden lógico, son:

1. escalones de Truco de las cartas propias restantes, ordenados;
2. valor privado de envido propio mientras el envido no se haya resuelto;
3. historial público compacto: cartas jugadas, cantos, respuestas, quién es mano, turno y marcador aplicable.

> ⚠️ A CONFIRMAR: serialización canónica exacta, separadores, representación de valores ausentes y esquema del historial público. Esto debe cerrarse antes de entrenar una política tabular porque cualquier cambio invalida sus claves.

## `encode(obs)`

El resultado será un `np.ndarray` unidimensional de `float32`, de tamaño fijo. El contenido mínimo exigido es el siguiente:

| Orden | Bloque | Posiciones | Codificación requerida |
|---:|---|---|---|
| 1 | Cartas propias restantes | 40 posiciones | Multi-hot sobre un orden canónico de las 40 cartas |
| 2 | Cartas jugadas | ⚠️ A CONFIRMAR | Carta por baza y jugador, sin exponer cartas futuras |
| 3 | Estado de Truco | ⚠️ A CONFIRMAR | Autor del canto, nivel y condición pendiente |
| 4 | Estado de Envido | ⚠️ A CONFIRMAR | Autor del canto, cadena/nivel y condición pendiente |
| 5 | Valores de envido revelados | ⚠️ A CONFIRMAR | Ambos valores solo después de quedar públicos; ausentes antes |
| 6 | Número de baza | ⚠️ A CONFIRMAR | Codificación fija de la baza actual |
| 7 | Soy mano | ⚠️ A CONFIRMAR | Indicador binario desde la perspectiva del observador |
| 8 | Marcador | ⚠️ A CONFIRMAR | Puntajes normalizados respecto del objetivo |

El índice final y el `shape` no pueden fijarse sin definir la representación de cada bloque.

> ⚠️ A CONFIRMAR: orden canónico de palos y números para las primeras 40 posiciones.

> ⚠️ A CONFIRMAR: elegir la codificación posición por posición de los bloques 2 a 8, incluido el tratamiento de slots vacíos, estados pendientes y valores de envido todavía privados.

## Invariantes

- El vector siempre conserva el mismo `shape`, sin importar la fase de la mano.
- Ninguna posición revela cartas del rival que todavía no se jugaron ni cartas del mazo.
- La perspectiva siempre corresponde al jugador que recibe la observación.
- Las máscaras legales tienen 13 posiciones y usan los mismos índices de la tabla de acciones.
- Cambiar índices, offsets, tamaño o semántica exige una nueva versión del contrato.
