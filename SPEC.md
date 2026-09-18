# SPEC

## Visión
Truco argentino 1 vs 1 jugable en el navegador contra bots de dificultad creciente: random, heurístico,
CFR tabular, Deep CFR y PPO. Los bots que aprenden se entrenan por self-play y se sirven desde la API.
Prioridades: (1) motor correcto y testeado, (2) piloto jugable rápido, (3) aprendizaje medible y reproducible.

## Stack
- Monorepo. Python 3.12 con uv; Node con pnpm.
- `engine/`: Python puro, sin dependencias web ni de ML. mypy strict, ruff, pytest + hypothesis.
  Si el benchmark lo justifica: Numba en las funciones calientes (Rust + PyO3 solo como último recurso).
- `api/`: FastAPI + Pydantic v2. Inferencia con onnxruntime + numpy (NUNCA torch en la API).
- `web/`: Next.js (App Router) + TypeScript + Tailwind + Zustand. Tipos generados con openapi-typescript.
- `training/`: PyTorch, numpy, sb3-contrib (MaskablePPO), Gymnasium, typer (CLI), PyYAML (configs),
  TensorBoard para métricas. OpenSpiel como referencia opcional para comparar resultados.
- Docker Compose para desarrollo local (api + web).
- Deploy: web en Vercel; API + modelos en Railway (alternativas: Render, Fly.io).

## Estructura
```
truco-ai/
├── SPEC.md  README.md  CLAUDE.md
├── docs/
├── engine/truco_engine/
│   ├── cards.py            # mazo de 40, jerarquía de truco (14 escalones), valor de envido
│   ├── state.py            # GameState / HandState inmutables (dataclasses frozen)
│   ├── actions.py          # espacio de acciones FIJO (ver abajo)
│   ├── rules.py            # legal_actions(state), apply(state, action) -> state
│   ├── scoring.py
│   ├── observation.py      # vista parcial por jugador, info_key() y encode()
│   ├── config.py           # RulesConfig: puntos (15/30), flor (off), mazo-con-envido, etc.
│   └── agents/
│       ├── base.py         # Protocol Agent
│       ├── random_agent.py
│       ├── heuristic_agent.py
│       ├── tabular_agent.py   # carga política tabular (msgpack)
│       └── neural_agent.py    # carga .onnx (extra opcional [neural])
├── engine/tests/
├── api/app/                # main.py, routers/, schemas/, services/, repositories/, agent_registry.py
├── web/src/                # app/, components/, lib/api.ts, store/
├── training/truco_train/
│   ├── games/
│   │   ├── game_api.py     # Protocol Game genérico (estilo OpenSpiel)
│   │   ├── kuhn.py         # Kuhn poker para validar algoritmos
│   │   └── truco_hand.py   # adaptador: UNA mano de truco como juego de suma cero
│   ├── cfr/                # regret_matching.py, mccfr.py, tabular_policy.py
│   ├── deep_cfr/           # networks.py, reservoir.py, trainer.py
│   ├── ppo/                # env.py (Gymnasium), opponent_pool.py, train.py (MaskablePPO)
│   ├── eval/               # tournament.py, best_response.py, plots.py
│   ├── export/             # to_onnx.py, to_msgpack.py
│   └── cli.py
├── training/configs/*.yaml
├── models/                 # SOLO metadata.json por modelo; los binarios van a S3 o GitHub Releases
└── docker-compose.yml
```

## Reglas (parametrizables en RulesConfig; si algo es ambiguo, PREGUNTAR, no inventar)
- Mazo español de 40 cartas (sin 8 ni 9).
- Jerarquía de truco de mayor a menor: 1♠, 1♣, 7♠, 7 de oro, 3s, 2s, 1 de oro y 1 de copa, 12, 11, 10,
  7 de copa y 7♣, 6, 5, 4. Cartas del mismo escalón empatan (parda).
- 3 bazas por mano. El ganador de una baza abre la siguiente; si fue parda, abre el mano.
- Pardas: si la primera es parda, gana quien gane la siguiente no parda; si alguien ganó la primera y la
  segunda es parda, gana quien ganó la primera; si todas son pardas, gana el mano.
- La mano alterna cada mano.
- Truco (2), retruco (3), vale cuatro (4). "No quiero" otorga los puntos del nivel anterior.
  Solo puede subir quien no hizo el último canto.
- Envido: solo en la primera baza, antes de que ese jugador tire su primera carta. Cadenas: envido,
  envido-envido, real envido, falta envido y combinaciones. Valor: dos cartas del mismo palo = 20 + suma
  (10/11/12 valen 0); si no, la carta más alta (figuras 0). Empate: gana el mano.
  "No quiero": puntos acumulados antes del último canto (mínimo 1). Falta envido: lo que le falta al que va
  ganando para llegar al final (en el adaptador de entrenamiento se aproxima con un valor fijo configurable).
- Si el envido es querido, ambos valores quedan PÚBLICOS en la observación.
- "El envido está primero": ante un truco en la primera baza, el rival puede responder con envido.
- Irse al mazo: siempre disponible en tu turno; da al rival los puntos del truco en juego (+1 de envido si
  corresponde, configurable).
- Partida a 15 por defecto. Sin flor (flag presente, no implementado).

## Espacio de acciones (fijo, 13 acciones; el orden es CONTRATO de los modelos, versionado)
0-2 tirar carta del slot 0/1/2 (slots ordenados por jerarquía de truco, de menor a mayor)
3 envido · 4 real envido · 5 falta envido · 6 truco · 7 retruco · 8 vale cuatro
9 quiero · 10 no quiero · 11 irse al mazo · 12 reservado (flor, siempre ilegal por ahora)

## Contrato de agentes
```python
class Agent(Protocol):
    name: str
    def policy(self, obs: Observation, legal: list[Action]) -> dict[Action, float]: ...
    def act(self, obs: Observation, legal: list[Action], rng: Random) -> Action:
        # por defecto: samplear de policy(). NUNCA argmax en bots que aprenden.
```

## Motor: requisitos
- `legal_actions` y `apply` son puras; el estado es inmutable.
- Toda aleatoriedad pasa por `random.Random` con semilla: partidas 100% reproducibles.
- La observación nunca expone cartas ocultas del rival ni el mazo.
- `info_key(obs) -> str`: clave canónica del information set = (mis cartas restantes como escalones de
  truco ordenados, mi valor de envido si el envido no se resolvió, historial público compacto).
- `encode(obs) -> np.ndarray[float32]` de tamaño fijo y documentado: mis cartas (multi-hot 40),
  cartas jugadas por baza y jugador, estado de canto de truco y envido (quién, nivel, pendiente),
  valores de envido revelados, número de baza, soy mano, marcador normalizado.
- Benchmark: medir y reportar manos/segundo random vs random. Optimizar solo lo que marque el profiler.

## Tests
- Unitarios: jerarquía, envido, cada caso de parda, cadenas de truco y envido con quiero/no quiero, mazo.
- Hypothesis: 5.000 partidas random vs random con semillas aleatorias; nunca crashea, siempre hay acción
  legal hasta el final y la partida termina.
- La observación no filtra información oculta.
- `encode` devuelve siempre el mismo shape.

## Bots base
- RandomAgent: uniforme sobre las acciones legales.
- HeuristicAgent: reglas documentadas con umbrales en config (envido con 27+, truco con fuerza alta,
  farol con probabilidad baja, aceptar según fuerza). `policy()` devuelve probabilidades explícitas.

## API
- `GET /agents` → bots disponibles (nombre, tipo, descripción, versión del modelo).
- `POST /games` → crea partida (agent_id, semilla opcional).
- `GET /games/{id}` → observación del humano, acciones legales, marcador, log de eventos.
- `POST /games/{id}/actions` → aplica la acción humana y hace jugar al bot hasta que vuelva a tocar al
  humano o termine la mano. Devuelve estado + eventos del bot, cada uno con la policy que usó.
- 422 ante acción ilegal. CORS configurable por variable de entorno.
- Store en memoria detrás de una interfaz de repositorio (reemplazable por Redis/Postgres).
- `agent_registry.py`: al arrancar lee `models/*/metadata.json`, descarga el binario si no está local
  (S3 o GitHub Releases, URL en metadata) y rechaza modelos con contrato incompatible.
- `GET /health` para el deploy.

## Front
- Mesa: cartas propias clickeables, bazas jugadas, dorso de las del rival, marcador, log de cantos.
- Botonera con SOLO las acciones legales que devuelve la API (el front no conoce reglas).
- Selector de bot desde `GET /agents`.
- Modo análisis (toggle): muestra las probabilidades que usó el bot en cada decisión.
- Cartas con CSS/SVG propio. Mobile first. URL de la API por variable de entorno.

## Entrenamiento
### Interfaz de juego genérica (games/game_api.py)
current_player (0, 1 o CHANCE), legal_actions, apply, is_terminal, returns (suma cero),
info_key(player), info_tensor(player), sample_chance(rng). Los algoritmos solo hablan con esta interfaz.

### Kuhn poker (validación)
MCCFR tiene que converger al valor de juego conocido (−1/18 para el primer jugador) y la explotabilidad
tiene que bajar hacia 0. Si esto no pasa, NO se avanza a truco.

### truco_hand (juego de entrenamiento)
- Una sola mano, suma cero, payoff = puntos ganados − puntos perdidos en esa mano.
- Quién es mano se sortea en el nodo de azar y forma parte del information set.
- Variantes por config: `sin_envido` (solo truco) y `completo`.
- Se ignora el marcador (salvo la aproximación de la falta envido). Documentar esta simplificación.

### MCCFR tabular (cfr/) — implementación propia
- External sampling. En los nodos del jugador que recorre: se exploran todas las acciones legales y se
  actualizan los regrets. En los nodos del rival: se samplea de la estrategia actual y se acumula la
  estrategia promedio. En los nodos de azar: se samplea.
- Regret matching+ y promediado lineal (configurables).
- Tablas: dict[info_key] -> arrays numpy. Checkpoints periódicos. Loguear la cantidad de information sets
  y la memoria usada. Multiprocessing solo si el profiler lo justifica.
- Salida: estrategia PROMEDIO exportada a msgpack → TabularAgent. Para info_keys no vistas,
  fallback al heurístico (loguear cuántas veces pasa).

### Deep CFR (deep_cfr/) — implementación propia en PyTorch
- Una red de ventajas por jugador: MLP (encode → 256 → 256 → 13) que predice regrets.
  La estrategia sale de regret matching sobre las ventajas predichas, con máscara de legales.
- Por iteración: K recorridos con external sampling usando las redes actuales. Guardar
  (tensor, iteración, regrets muestreados) en un reservoir buffer de ventajas y
  (tensor, iteración, estrategia) en un reservoir buffer de estrategia.
- Reentrenar cada red de ventajas desde cero en cada iteración, con MSE ponderado por iteración.
- Al final, entrenar la red de estrategia con los datos acumulados. Esa red es el bot final.

### PPO (ppo/) — experimento comparativo con MaskablePPO de sb3-contrib (NO implementarlo a mano)
- Entorno Gymnasium de una mano con `action_masks()`; el rival sale de un pool: checkpoints propios pasados
  (agregar uno cada N updates), heurístico y random, con pesos configurables.
- Recompensa = payoff normalizado.
- Documentar si aparece el ciclado estratégico y cómo lo mitiga el pool.

### Evaluación (eval/)
- Torneo todos contra todos en partidas COMPLETAS a 15, con semillas fijas y repartos espejados
  (mismo reparto jugado de ambos lados). Win rate con intervalo de confianza.
- Curvas: win rate contra el heurístico por iteración de entrenamiento.
- Explotabilidad: exacta en Kuhn; en truco, aproximada entrenando un MaskablePPO explotador contra la
  política congelada y midiendo cuánto le gana.
- `cli.py eval tournament` genera tabla markdown + gráficos en `reports/`.

### Export y serving
- Redes → ONNX con test de paridad torch vs onnxruntime. Tabular → msgpack.
- `models/<nombre>/metadata.json`: tipo, versión, fecha, commit, config, semilla, versión del contrato
  (acciones + shape de encode), URL del binario, checksum y resultados de evaluación.
- Los binarios NO van a git.

## Reglas de trabajo
- No agregar features fuera de este spec (flor, 2 vs 2, online, ranking → anotar en roadmap como "después").
- Ante ambigüedad, preguntar.
- Toda decisión de diseño no trivial va a `docs/decisions/` como ADR.
- Todo experimento es reproducible y se registra en `docs/experiments/`.
- Frenar al final de cada fase, resumir qué se hizo, qué quedó pendiente y esperar mi OK.

## Fases
0. Documentación inicial (esta tarea).
1. Scaffolding, tooling (uv, ruff, mypy, pnpm, eslint), docker-compose, CI con GitHub Actions (lint + tests).
2. Motor completo + tests + benchmark.
3. Random, heurístico y torneo básico.
4. API + tests de endpoints.
5. Front jugable de punta a punta + deploy (Vercel + Railway). → HITO PILOTO
6. game_api + Kuhn + MCCFR validado en Kuhn.
7. truco_hand (sin_envido) + MCCFR tabular + TabularAgent en la app. Después la variante completo.
8. Harness de evaluación completo (torneo, curvas, explotabilidad aproximada).
9. Deep CFR + export ONNX + NeuralAgent en la app.
10. MaskablePPO con pool de rivales + comparación en el torneo.
11. Modo análisis en el front + README final con resultados, gráficos y decisiones de diseño.
