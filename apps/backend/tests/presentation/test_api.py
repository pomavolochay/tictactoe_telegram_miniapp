import re

from fastapi.testclient import TestClient

from tictactoe.presentation.api.app import create_app

app = create_app()
client = TestClient(app)


def test_move_endpoint_win() -> None:
    payload = {
        "board": ["X", "X", "", "O", "O", "", "", "", ""],
        "playerSymbol": "X",
        "moveIndex": 2,
    }
    response = client.post("/api/v1/game/move", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "win"
    assert re.fullmatch(r"[A-Z0-9]{5}", data["promoCode"])
    assert data["next"] == "none"


def test_reset_endpoint() -> None:
    response = client.post("/api/v1/game/reset")
    assert response.status_code == 200
    data = response.json()
    assert data["board"] == ["" for _ in range(9)]
    assert data["status"] == "in_progress"


def test_invalid_move_returns_400() -> None:
    payload = {
        "board": ["X", "", "", "", "", "", "", "", ""],
        "playerSymbol": "X",
        "moveIndex": 0,
    }
    response = client.post("/api/v1/game/move", json=payload)
    assert response.status_code == 400


def test_metrics_endpoint() -> None:
    response = client.get("/metrics")
    assert response.status_code == 200
    assert "http_requests_total" in response.text
