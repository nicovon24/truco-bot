# Contrato de acciones y observaciones

El espacio de acciones, `info_key()` y `encode()` forman el contrato entre motor, entrenamiento, modelos y API. Un artefacto solo puede cargarse si su metadata declara una versión compatible (`contract.version`, `num_actions`, `encode_size`; lo valida `api/app/agent_registry.py`).

**Versión vigente: `1`** (`truco_engine.actions.CONTRACT_VERSION`). Ver [ADR 0012](decisions/0012-contrato-v1.md).

## Orden canónico de cartas

Índice `palo * 10 + posición del número`, con palos `espada=0, basto=1, oro=2, copa=3` y números `1, 2, 3, 4, 5, 6, 7, 10, 11, 12`. Ejemplos: 1 de espada = 0, 12 de espada = 9, 1 de basto = 10, 12 de copa = 39.

## Espacio fijo de acciones

| Índice | Identificador | Significado |
|---:|---|---|
| 0 | `PLAY_CARD_0` | Tirar la carta del slot 0 (menor jerarquía) |
| 1 | `PLAY_CARD_1` | Tirar la carta del slot 1 |
| 2 | `PLAY_CARD_2` | Tirar la carta del slot 2 (mayor jerarquía) |
| 3 | `ENVIDO` | Cantar Envido |
| 4 | `REAL_ENVIDO` | Cantar Real Envido |
| 5 | `FALTA_ENVIDO` | Cantar Falta Envido |
| 6 | `TRUCO` | Cantar Truco |
| 7 | `RETRUCO` | Cantar Retruco |
| 8 | `VALE_CUATRO` | Cantar Vale Cuatro |
| 9 | `QUIERO` | Aceptar el canto pendiente (el envido tiene prioridad) |
| 10 | `NO_QUIERO` | Rechazar el canto pendiente |
| 11 | `FOLD` | Irse al mazo |
| 12 | `FLOR_RESERVED` | Reservada para Flor; siempre ilegal |

Slots: se asignan una vez al repartir, ordenando de menor a mayor escalón de truco; los empates de escalón se desempatan por índice canónico (menor primero). Los slots son **estables** durante toda la mano: jugar una carta no renumera las demás y un slot usado es ilegal.

## `info_key(obs)`

Formato (un string, campos separados por `|`):

```
c=<escalones propios restantes, ascendentes, separados por .>
|e=<mi envido privado, o - si el envido ya se resolvió>
|m=<1 si soy mano, 0 si no>
|s=<mis puntos>-<puntos rival>
|v=<envido mío>-<envido rival si fue querido, o ->
|h=<historial público separado por comas>
```

Cada evento del historial es `a` (observador) o `b` (rival) seguido del escalón de truco de la carta tirada, o de un código de canto: `E`, `R`, `F`, `T`, `RT`, `V`, `Q`, `N`, `M` (mazo).

Ejemplo: `c=7.10.14|e=-|m=0|s=0-2|v=3-33|h=bE,aQ,b11`.

Las cartas jugadas se abstraen a su escalón: el palo solo importa para el envido, que ya viaja como valor.

## `encode(obs)`

`np.ndarray` float32 de tamaño fijo **317**, desde la perspectiva del observador ("yo" / "rival"). Todas las posiciones están en `[0, 1]`.

| Offset | Largo | Bloque | Codificación |
|---:|---:|---|---|
| 0 | 40 | Mis cartas restantes | Multi-hot por índice canónico |
| 40 | 240 | Cartas jugadas | 3 bazas × (yo, rival) × one-hot 40; ceros si falta |
| 280 | 9 | Resultado de bazas | 3 bazas × (gané, perdí, parda); ceros si no terminó |
| 289 | 7 | Truco | Nivel aceptado one-hot 4 (1..4), pendiente, último canto mío, último canto rival |
| 296 | 10 | Envido | Cantidad de envidos one-hot 3 (0/1/2), hay real, hay falta, pendiente, cantó yo, cantó rival, resuelto, querido |
| 306 | 3 | Envidos revelados | Revelado, mi valor/33, valor rival/33; ceros si no fue querido |
| 309 | 3 | Baza actual | One-hot 0/1/2 |
| 312 | 1 | Soy mano | 0/1 |
| 313 | 1 | Me toca | 0/1 |
| 314 | 2 | Marcador | Mis puntos/objetivo, rival/objetivo (tope 1) |
| 316 | 1 | Mi envido privado | Valor/33; 0 si ya se resolvió |

## Invariantes (con tests)

- El vector siempre conserva el mismo `shape`, sin importar la fase de la mano.
- Ni `encode` ni `info_key` cambian si se reemplazan las cartas no jugadas del rival (`engine/tests/test_observation.py`).
- La perspectiva siempre corresponde al jugador que recibe la observación.
- Las máscaras legales tienen 13 posiciones y usan los mismos índices de la tabla de acciones.
- Cambiar índices, offsets, tamaño o semántica exige una nueva versión del contrato.
