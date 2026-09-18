# Instrucciones para agentes de código

Este repositorio se implementa por fases. Leé `SPEC.md` y los documentos relacionados antes de modificar una parte del sistema. No agregues funciones fuera del alcance definido.

## Comandos

Estos son los contratos de comandos que debe ofrecer el scaffolding desde la fase 1. Si todavía no existen, no improvises un comando alternativo: implementalos en la fase correspondiente y actualizá este archivo si cambia el contrato.

```bash
# Instalar dependencias Python y Node
uv sync --all-groups
pnpm install

# Ejecutar tests
uv run pytest
pnpm test

# Validar formato, lint y tipos
uv run ruff format --check .
uv run ruff check .
uv run mypy engine api training
pnpm lint
pnpm typecheck

# Levantar API y web
docker compose up --build

# Torneo básico (fase 3)
uv run truco-train eval tournament --config training/configs/tournament_basic.yaml

# Benchmark del motor
uv run python engine/benchmarks/random_vs_random.py --games 2000 --seed 0

# Entrenar, evaluar y exportar; los subcomandos y configs se agregan en sus fases
uv run truco-train train --config training/configs/<config>.yaml
uv run truco-train eval tournament --config training/configs/<config>.yaml
uv run truco-train export --config training/configs/<config>.yaml
```

> ⚠️ A CONFIRMAR: nombres y argumentos finales de los subcomandos `train` y `export` cuando se diseñe la CLI de entrenamiento.

## Convenciones

- Usá Python 3.12 y tipado estricto. El código nuevo debe pasar mypy en modo strict y Ruff.
- Usá TypeScript estricto en la web. Los tipos de la API se generan con `openapi-typescript`.
- Mantené `engine/` libre de dependencias web y de ML.
- Modelá los estados del motor con dataclasses inmutables. `legal_actions` y `apply` deben ser funciones puras.
- Toda aleatoriedad debe entrar por un `random.Random` con semilla. No uses generadores globales ni fuentes implícitas de azar.
- Escribí y ejecutá los tests definidos para cada fase antes de declararla terminada.
- Registrá decisiones de diseño no triviales con un ADR en `docs/decisions/`.
- Registrá cada experimento reproducible en `docs/experiments/`.

## Reglas duras

- El front no implementa ni deduce reglas de Truco: renderiza solamente la observación y las acciones legales que devuelve la API.
- Los índices del espacio de acciones y el layout de `encode()` son un contrato versionado. Un cambio requiere una nueva versión y validación de compatibilidad.
- Los bots que aprenden muestrean desde `policy()`; nunca eligen por `argmax` durante el juego normal.
- Toda partida, evaluación y corrida de entrenamiento usa semillas registradas.
- Los binarios de modelos quedan fuera de Git. `models/` contiene solamente `metadata.json` por modelo.
- La API usa NumPy y ONNX Runtime para inferencia; nunca depende de PyTorch.
- Ante una ambigüedad reglamentaria, frená esa parte, documentala y preguntá. No inventes una regla.

## Flujo por fases

Trabajá solamente sobre la fase autorizada. Al cerrarla:

1. ejecutá las validaciones aplicables;
2. resumí los cambios y la evidencia;
3. enumerá decisiones y pendientes;
4. frená y esperá aprobación explícita antes de avanzar.

