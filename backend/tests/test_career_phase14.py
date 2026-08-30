import pytest
from fastapi.testclient import TestClient

from app.career.domain import CareerSessionStatus
from app.career.service import CareerSessionService
from app.main import app

client = TestClient(app)


@pytest.fixture(autouse=True)
def clear_sessions():
    CareerSessionService.clear_all_sessions()
    yield
    CareerSessionService.clear_all_sessions()


def test_create_career_session():
    response = client.post(
        "/career",
        json={
            "player_name": "Carlos Vela",
            "position": "ST",
            "starting_club_id": "club_101",
            "nationality": "Mexico",
            "seed": "SEED-TEST-001",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert "career_id" in data
    assert data["status"] == CareerSessionStatus.ACTIVE.value
    assert data["player_id"].startswith("p_")
    assert data["current_season"] == "2026/27"


def test_get_career_session():
    create_res = client.post(
        "/career",
        json={"player_name": "Mateo Kovacic", "position": "CM", "nationality": "Croatia"},
    )
    career_id = create_res.json()["career_id"]

    get_res = client.get(f"/career/{career_id}")
    assert get_res.status_code == 200
    data = get_res.json()
    assert data["career_id"] == career_id


def test_get_nonexistent_career():
    res = client.get("/career/nonexistent_id")
    assert res.status_code == 404


def test_advance_career_session():
    create_res = client.post(
        "/career",
        json={"player_name": "Nico Williams", "position": "LW"},
    )
    career_id = create_res.json()["career_id"]

    advance_res = client.post(f"/career/{career_id}/advance")
    assert advance_res.status_code == 200
    adv_data = advance_res.json()
    assert adv_data["previous_season"] == "2026/27"
    assert adv_data["current_season"] == "2027/28"
    assert adv_data["success"] is True


def test_decision_required_flow():
    create_res = client.post(
        "/career",
        json={"player_name": "Lamine Yamal", "position": "RW"},
    )
    career_id = create_res.json()["career_id"]

    # Advance Season 1 -> Season 2
    client.post(f"/career/{career_id}/advance")
    # Advance Season 2 -> Season 3 (triggers decision)
    adv2 = client.post(f"/career/{career_id}/advance")
    assert adv2.status_code == 200
    adv2_data = adv2.json()
    assert adv2_data["status"] == CareerSessionStatus.DECISION_PENDING.value
    assert adv2_data["pending_decision"] is not None

    # Advancing while decision is pending should fail
    adv3 = client.post(f"/career/{career_id}/advance")
    assert adv3.status_code == 409

    # Resolve decision
    dec_id = adv2_data["pending_decision"]["id"]
    opt_id = adv2_data["pending_decision"]["options"][0]["id"]

    res_dec = client.post(
        f"/career/{career_id}/decision",
        json={"decision_id": dec_id, "option_id": opt_id},
    )
    assert res_dec.status_code == 200
    dec_data = res_dec.json()
    assert dec_data["status"] == CareerSessionStatus.ACTIVE.value
    assert dec_data["pending_decision"] is None

    # Now advancement succeeds again
    adv4 = client.post(f"/career/{career_id}/advance")
    assert adv4.status_code == 200


def test_pause_session():
    create_res = client.post(
        "/career",
        json={"player_name": "Pedri Gonzalez", "position": "CM"},
    )
    career_id = create_res.json()["career_id"]

    pause_res = client.post(f"/career/{career_id}/pause")
    assert pause_res.status_code == 200
    assert pause_res.json()["status"] == CareerSessionStatus.PAUSED.value


def test_get_events_and_presentation():
    create_res = client.post(
        "/career",
        json={"player_name": "Gavi Paez", "position": "CM"},
    )
    career_id = create_res.json()["career_id"]

    events_res = client.get(f"/career/{career_id}/events")
    assert events_res.status_code == 200
    assert "events" in events_res.json()

    pres_res = client.get(f"/career/{career_id}/presentation")
    assert pres_res.status_code == 200
    assert "player" in pres_res.json()
