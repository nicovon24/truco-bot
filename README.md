# Truco AI

Truco argentino 1 vs 1 para jugar en el navegador contra bots de dificultad creciente: random, heurístico, CFR tabular, Deep CFR y PPO. El proyecto prioriza un motor correcto y testeado, un piloto jugable y experimentos reproducibles.

## Demo

Próximamente.

## Stack

- Python 3.12, `uv`, FastAPI, Pydantic v2, NumPy y ONNX Runtime.
- Next.js App Router, TypeScript, Tailwind, Zustand y `pnpm`.
- PyTorch, Gymnasium, `sb3-contrib`, Typer, PyYAML y TensorBoard para entrenamiento.
- Pytest, Hypothesis, mypy strict, Ruff y GitHub Actions.
- Docker Compose para desarrollo; Vercel y Railway para producción.

## Desarrollo local

```bash
# Todo con Docker: API en http://localhost:8000 y web en http://localhost:3000
docker compose up --build

# Sin Docker
uv sync --all-groups && pnpm install
uv run uvicorn app.main:app --app-dir api --reload   # API
pnpm dev                                             # web

# Validaciones
uv run pytest && uv run ruff check . && uv run mypy engine api training
pnpm lint && pnpm typecheck && pnpm test

# Regenerar el contrato OpenAPI y los tipos del front
uv run python -m app.export_openapi api/openapi.json && pnpm gen:api
```

## Estructura

```text
engine/    motor de reglas y agentes servibles
api/       API de partidas e inferencia
web/       cliente jugable
training/  algoritmos, evaluación y exportación
models/    metadata de modelos, sin binarios
docs/      reglas, arquitectura y registro de decisiones
```

## Documentación

- [Especificación](SPEC.md)
- [Arquitectura](docs/architecture.md)
- [Reglas](docs/rules.md)
- [Contrato de acciones y observaciones](docs/action-space.md)
- [Entrenamiento](docs/training.md)
- [Evaluación](docs/evaluation.md)
- [Deploy](docs/deploy.md)
- [Roadmap](docs/roadmap.md)
- [Glosario](docs/glossary.md)
- [Decisiones](docs/decisions/)
- [Experimentos](docs/experiments/)

