# Roadmap

Cada fase se cierra con validaciones, resumen y aprobación antes de avanzar.

## Estado al 2026-09-18

Autorizadas las fases 1 a 4. Validaciones actuales: `uv run pytest` (128 tests), `ruff format --check`, `ruff check` y `mypy` strict en verde.

- **Fase 1 — hecha, falta aprobación.** Workspaces `uv` y `pnpm`, Ruff, mypy strict, ESLint, TypeScript strict, Vitest, tipos con `openapi-typescript`, Dockerfiles + `docker-compose.yml` (verificado: API healthy y web 200) y CI de GitHub Actions.
- **Fase 2 — hecha, falta aprobación.** Motor completo con reglas confirmadas (ADR 0010), contrato v1 (ADR 0012), tests unitarios, no filtración, shape de `encode`, 5.000 partidas con Hypothesis y benchmark (3.646 manos/s).
- **Fase 3 — hecha, falta aprobación.** RandomAgent y HeuristicAgent con policies explícitas; torneo espejado con `truco-train eval tournament` (el heurístico gana el 95,2%).
- **Fase 4 — hecha, falta aprobación.** FastAPI: `/health`, `/agents`, `/games`, `/games/{id}`, `/games/{id}/actions`, `/games/{id}/next-hand` (ADR 0011); 422 ante acción ilegal, CORS por `CORS_ORIGINS`, repositorio en memoria, `agent_registry` con validación de contrato, descarga y checksum.
- Skills de front instaladas para Claude y Codex: `impeccable` y `ui-ux-pro-max`.

- [x] **Fase 0 — Documentación inicial.** Terminada cuando existen todos los documentos requeridos, `SPEC.md` reproduce la especificación sin cambios y las ambigüedades están marcadas para confirmación.
- [x] **Fase 1 — Scaffolding y tooling.** (pendiente de aprobación) Terminada cuando `uv` y `pnpm` instalan el monorepo desde cero; Ruff, mypy strict, ESLint, tipos y tests vacíos pasan; Docker Compose levanta API y web; CI ejecuta lint y tests.
- [x] **Fase 2 — Motor completo.** (pendiente de aprobación) Terminada cuando las reglas confirmadas están implementadas con estados inmutables y funciones puras; pasan unitarios, pruebas de no filtración, shape de `encode()` y 5.000 partidas de Hypothesis; el benchmark random vs random está reportado.
- [x] **Fase 3 — Bots base y torneo básico.** (pendiente de aprobación) Terminada cuando RandomAgent y HeuristicAgent exponen policies explícitas, juegan partidas reproducibles y un torneo básico compara ambos con semillas fijas.
- [x] **Fase 4 — API.** (pendiente de aprobación) Terminada cuando funcionan `/health`, `/agents` y el ciclo de `/games`; una acción ilegal devuelve 422; los tests cubren turnos humano-bot, policies en eventos, CORS y repositorio en memoria.
- [ ] **Fase 5 — Front y deploy. HITO PILOTO.** Terminada cuando una persona puede elegir un bot y completar una partida desde móvil y escritorio; la botonera refleja solo acciones de la API; web y API están desplegadas en Vercel y Railway y el flujo se verifica de punta a punta.
- [ ] **Fase 6 — Game API, Kuhn y MCCFR.** Terminada cuando el protocolo genérico está probado y MCCFR converge de manera reproducible en Kuhn hacia `−1/18`, con explotabilidad descendente hacia cero.
- [ ] **Fase 7 — Truco tabular.** Terminada cuando `truco_hand` funciona primero en `sin_envido` y después en `completo`; MCCFR guarda checkpoints y exporta la estrategia promedio a msgpack; TabularAgent juega en la aplicación y registra fallbacks.
- [ ] **Fase 8 — Evaluación completa.** Terminada cuando el CLI genera torneo todos contra todos, repartos espejados, intervalos de confianza, curvas contra el heurístico y explotabilidad aproximada, con tablas y gráficos reproducibles en `reports/`.
- [ ] **Fase 9 — Deep CFR.** Terminada cuando los reservoirs y entrenadores producen una política evaluada; la red se exporta a ONNX con prueba de paridad; NeuralAgent la carga y juega desde la API.
- [ ] **Fase 10 — MaskablePPO.** Terminada cuando entrena con máscaras y pool de rivales, registra posible ciclado estratégico y se compara bajo el mismo protocolo de torneo.
- [ ] **Fase 11 — Análisis y cierre.** Terminada cuando el front muestra las probabilidades usadas por el bot en cada decisión y el README final enlaza resultados, gráficos, reproducción de experimentos y decisiones de diseño.

## Después

Estas funciones están fuera del alcance de las fases 0–11:

- Flor implementada.
- Truco 2 vs 2.
- Partidas online entre personas.
- Ranking y cuentas de usuario.
- Marcador completo dentro del juego de entrenamiento, en lugar de una sola mano.
