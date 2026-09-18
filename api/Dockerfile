# Contexto de build: raíz del repositorio.
FROM python:3.12-slim

COPY --from=ghcr.io/astral-sh/uv:0.8 /uv /bin/uv

WORKDIR /app
ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PROJECT_ENVIRONMENT=/app/.venv \
    PYTHONUNBUFFERED=1

COPY pyproject.toml uv.lock README.md ./
COPY engine engine
COPY api api
COPY training training
RUN uv sync --frozen --no-dev --package truco-api

COPY models models

ENV PORT=8000 \
    MODELS_DIR=/app/models \
    MODEL_CACHE_DIR=/app/.model_cache
EXPOSE 8000
WORKDIR /app/api
CMD ["sh", "-c", "/app/.venv/bin/uvicorn app.main:app --host 0.0.0.0 --port ${PORT}"]
