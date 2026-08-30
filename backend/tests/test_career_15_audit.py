import pytest
from app.career.domain import CareerSessionStatus, CareerSetupRequest
from app.career.engine import CareerSessionEngine
from app.career.service import CareerSessionService


@pytest.fixture(autouse=True)
def clear_sessions():
    CareerSessionService.clear_all_sessions()
    yield
    CareerSessionService.clear_all_sessions()


def test_phase15_determinism_and_immutability_audit():
    req1 = CareerSetupRequest(player_name="Phase15 Determinism", seed="SEED-P15-100")
    req2 = CareerSetupRequest(player_name="Phase15 Determinism", seed="SEED-P15-100")

    s1 = CareerSessionEngine.create_session(req1)
    s2 = CareerSessionEngine.create_session(req2)

    assert s1.career_id == s2.career_id
    assert s1.player_id == s2.player_id
    assert s1.presentation.player.name == s2.presentation.player.name

    # Verify session objects remain strictly frozen
    with pytest.raises(Exception):
        s1.status = CareerSessionStatus.PAUSED

    with pytest.raises(Exception):
        s1.seed = "MODIFIED-SEED"


def test_phase15_career_advance_and_presentation_grounding():
    req = CareerSetupRequest(player_name="Grounding Test", seed="SEED-GROUNDING-15")
    session = CareerSessionEngine.create_session(req)

    assert session.status == CareerSessionStatus.ACTIVE
    assert session.current_season == "2026/27"

    adv_result = CareerSessionEngine.advance_season(session)
    assert adv_result.success is True
    assert adv_result.current_season == "2027/28"
    assert adv_result.presentation is not None
    assert adv_result.presentation.player.name == "Grounding Test"
