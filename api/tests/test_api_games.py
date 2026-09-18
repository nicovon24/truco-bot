from __future__ import annotations

from typing import Any

import pytest
from fastapi.testclient import TestClient

from app.agent_registry import AgentRegistry, builtin_agents
from app.main import create_app
from app.repositories.games import InMemoryGameRepository
from app.settings import Settings


@pytest.fixture
def repo() -> InMemoryGameRepository:
    return InMemoryGameRepository()


@pytest.fixture
def client(repo: InMemoryGameRepository) -> TestClient:
    app = create_app(
        Settings(cors_origins=["https://truco.example"]),
        registry=AgentRegistry(builtin_agents()),
        repository=repo,
    )
    return TestClient(app)


def _create(client: TestClient, agent: str = "random", seed: int | None = 42) -> dict[str, Any]:
    res = client.post("/games", json={"agent_id": agent, "seed": seed})
    assert res.status_code == 201, res.text
    data: dict[str, Any] = res.json()
    return data


def test_health(client: TestClient) -> None:
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json() == {"status": "ok", "contract_version": "1", "agents": 2}


def test_agents(client: TestClient) -> None:
    res = client.get("/agents")
    assert res.status_code == 200
    ids = [a["id"] for a in res.json()]
    assert ids == ["random", "heuristic"]
    assert all(a["model_version"] is None for a in res.json())


def test_create_game_and_get(client: TestClient, repo: InMemoryGameRepository) -> None:
    game = _create(client)
    assert game["seed"] == 42
    assert game["status"] == "playing"
    assert game["observation"]["turn"] == "human"
    assert len(game["legal_actions"]) > 0
    assert len(repo) == 1
    again = client.get(f"/games/{game['id']}").json()
    assert again == game


def test_create_game_without_seed_registers_one(client: TestClient) -> None:
    game = _create(client, seed=None)
    assert isinstance(game["seed"], int)


def test_same_seed_same_game(client: TestClient) -> None:
    a, b = _create(client, "heuristic", 7), _create(client, "heuristic", 7)
    assert a["observation"] == b["observation"]
    assert a["events"] == b["events"]


def test_unknown_agent_is_422(client: TestClient) -> None:
    res = client.post("/games", json={"agent_id": "nope"})
    assert res.status_code == 422


def test_unknown_game_is_404(client: TestClient) -> None:
    assert client.get("/games/nope").status_code == 404
    assert client.post("/games/nope/actions", json={"action": 0}).status_code == 404


def test_illegal_action_is_422(client: TestClient) -> None:
    game = _create(client)
    legal = {a["id"] for a in game["legal_actions"]}
    illegal = next(i for i in range(13) if i not in legal)
    res = client.post(f"/games/{game['id']}/actions", json={"action": illegal})
    assert res.status_code == 422
    res = client.post(f"/games/{game['id']}/actions", json={"action": 99})
    assert res.status_code == 422


def test_bot_events_include_policy(client: TestClient) -> None:
    game = _create(client, "heuristic", 3)
    for _ in range(50):
        if game["status"] != "playing":
            break
        action = game["legal_actions"][0]["id"]
        res = client.post(f"/games/{game['id']}/actions", json={"action": action})
        assert res.status_code == 200, res.text
        body = res.json()
        game = body["game"]
        bot_actions = [
            e for e in body["new_events"] if e["actor"] == "bot" and e["type"] == "action"
        ]
        for ev in bot_actions:
            assert ev["policy"] is not None
            assert sum(ev["policy"].values()) == pytest.approx(1.0)
            assert ev["action_name"] in ev["policy"]
        human = [e for e in body["new_events"] if e["actor"] == "human"]
        assert human[0]["action"] == action
        assert human[0]["policy"] is None
        # Tras la respuesta vuelve a tocar al humano o terminó la mano.
        assert game["observation"]["turn"] in ("human", None)


def test_full_game_until_game_over(client: TestClient) -> None:
    game = _create(client, "heuristic", 11)
    for _ in range(2_000):
        if game["status"] == "game_over":
            break
        if game["status"] == "hand_over":
            res = client.post(f"/games/{game['id']}/next-hand")
        else:
            assert game["legal_actions"], game
            # Estrategia fija del test: la última acción legal que no sea irse al mazo.
            options = [a for a in game["legal_actions"] if a["name"] != "FOLD"]
            action = (options or game["legal_actions"])[-1]["id"]
            res = client.post(f"/games/{game['id']}/actions", json={"action": action})
        assert res.status_code == 200, res.text
        game = res.json()["game"]
    assert game["status"] == "game_over"
    assert game["winner"] in ("human", "bot")
    assert max(game["scores"].values()) >= game["target_score"]
    assert game["legal_actions"] == []
    assert game["events"][-1]["type"] == "game_end"


def test_next_hand_requires_hand_over(client: TestClient) -> None:
    game = _create(client)
    res = client.post(f"/games/{game['id']}/next-hand")
    assert res.status_code == 422


def test_observation_hides_bot_cards(client: TestClient) -> None:
    game = _create(client, "random", 5)
    obs = game["observation"]
    assert obs["bot_cards_in_hand"] == 3 - sum(1 for b in obs["bazas"] if b["bot"])
    assert obs["envido"]["bot_value"] is None
    assert "hands" not in str(game)


def test_cors_allowed_origin(client: TestClient) -> None:
    res = client.options(
        "/agents",
        headers={"Origin": "https://truco.example", "Access-Control-Request-Method": "GET"},
    )
    assert res.headers["access-control-allow-origin"] == "https://truco.example"
    res = client.get("/agents", headers={"Origin": "https://evil.example"})
    assert "access-control-allow-origin" not in res.headers


def test_cors_origins_from_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("CORS_ORIGINS", "https://a.example, https://b.example")
    assert Settings().cors_origins == ["https://a.example", "https://b.example"]
