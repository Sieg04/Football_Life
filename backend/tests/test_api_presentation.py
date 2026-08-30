from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_get_sample_presentation():
    response = client.get("/presentation/sample")
    assert response.status_code == 200
    data = response.json()
    assert "player" in data
    assert "overview" in data
    assert "timeline" in data
    assert data["player"]["name"] == "Adrian Martínez"
    assert data["player"]["overall_rating"] == 87


def test_get_player_presentation():
    response = client.get("/presentation/player_123")
    assert response.status_code == 200
    data = response.json()
    assert data["player"]["player_id"] == "player_123"
    assert data["metadata"]["player_id"] == "player_123"
