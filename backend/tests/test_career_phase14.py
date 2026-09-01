import pytest
from fastapi.testclient import TestClient

from app.career.context import build_club_context
from app.career.domain import CareerSessionStatus
from app.career.engine import CareerSessionEngine
from app.career.service import CareerSessionService
from app.main import app

client = TestClient(app)


def test_phase18_club_context_fields_are_available():
    ctx = build_club_context("Real Madrid")
    assert ctx.country_id == "ES"
    assert ctx.league_id == "ESP1"
    assert ctx.club_prestige >= 90
    assert ctx.domestic_competition_level > 0
    assert ctx.expected_player_quality > 0
    assert ctx.international_competition_level > 0
    assert ctx.country_code == ctx.country_id
    assert ctx.league_code == ctx.league_id


def test_phase18_career_uses_context_calibrated_starting_ovr():
    req = __import__("app.career.domain", fromlist=["CareerSetupRequest"]).CareerSetupRequest(
        player_name="Context Player",
        position="ST",
        starting_club_id="Real Madrid",
        nationality="Spain",
        seed="PHASE18-OVR",
    )
    session = CareerSessionEngine.create_session(req)
    assert session.career.current_club_id == "Real Madrid"
    assert session.career.snapshots[0].starting_ovr > 75
    assert session.career.peak_ovr >= session.career.snapshots[0].starting_ovr


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


def test_deterministic_careers_follow_elite_mid_lower_club_context():
    elite = CareerSessionEngine.create_session(
        __import__("app.career.domain", fromlist=["CareerSetupRequest"]).CareerSetupRequest(
            player_name="Elite Player",
            position="ST",
            starting_club_id="Real Madrid",
            nationality="Spain",
            seed="ELITE-CAREER",
        )
    )
    mid = CareerSessionEngine.create_session(
        __import__("app.career.domain", fromlist=["CareerSetupRequest"]).CareerSetupRequest(
            player_name="Mid Player",
            position="ST",
            starting_club_id="Arsenal",
            nationality="England",
            seed="MID-CAREER",
        )
    )
    lower = CareerSessionEngine.create_session(
        __import__("app.career.domain", fromlist=["CareerSetupRequest"]).CareerSetupRequest(
            player_name="Lower Player",
            position="ST",
            starting_club_id="Lyon",
            nationality="France",
            seed="LOWER-CAREER",
        )
    )

    assert elite.career.peak_ovr >= mid.career.peak_ovr >= lower.career.peak_ovr
    assert elite.career.snapshots[0].starting_ovr >= mid.career.snapshots[0].starting_ovr >= lower.career.snapshots[0].starting_ovr


def test_advance_career_result_exposes_season_summary():
    create_res = client.post(
        "/career",
        json={"player_name": "Season Summary Test", "position": "RW", "starting_club_id": "Real Madrid", "nationality": "Spain"},
    )
    career_id = create_res.json()["career_id"]

    advance_res = CareerSessionService.advance_career(career_id)
    assert advance_res.season_summary is not None
    assert advance_res.season_summary.season_label == "2027/28"
    assert advance_res.season_summary.statistics.appearances >= 0
    assert advance_res.season_summary.statistics.average_rating >= 0


def test_advance_career_persists_season_summary_on_session():
    session = CareerSessionService.create_career(
        __import__("app.career.domain", fromlist=["CareerSetupRequest"]).CareerSetupRequest(
            player_name="Persisted Summary",
            position="RW",
            starting_club_id="Real Madrid",
            nationality="Spain",
            seed="SUMMARY-PERSIST-01",
        )
    )

    advance_res = CareerSessionService.advance_career(session.career_id)
    stored_session = CareerSessionService.get_session(session.career_id)

    assert advance_res.season_summary is not None
    assert stored_session.season_summary is not None
    assert stored_session.season_summary.season_label == "2027/28"
    assert stored_session.current_season == "2027/28"
