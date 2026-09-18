"""Exporta el esquema OpenAPI a JSON: uv run python -m app.export_openapi api/openapi.json"""

from __future__ import annotations

import json
import sys
from pathlib import Path

from app.agent_registry import AgentRegistry, builtin_agents
from app.main import create_app
from app.settings import Settings


def main() -> None:
    out = Path(sys.argv[1] if len(sys.argv) > 1 else "api/openapi.json")
    app = create_app(Settings(cors_origins=[]), registry=AgentRegistry(builtin_agents()))
    out.write_text(json.dumps(app.openapi(), indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"OpenAPI escrito en {out}")


if __name__ == "__main__":
    main()
