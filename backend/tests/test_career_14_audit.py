import pytest
from app.career.domain import CareerSessionStatus, CareerSetupRequest
from app.career.engine import CareerSessionEngine
from app.career.service import CareerSessionService


@pytest.fixture(autouse=True)
def clear_sessions():
    CareerSessionService.clear_all_sessions()
    yield
    CareerSessionService.clear_all_sessions()


def test_determinism_audit():
    req1 = CareerSetupRequest(player_name="Determined Player", seed="SEED-AUDIT-100")
    req2 = CareerSetupRequest(player_name="Determined Player", seed="SEED-AUDIT-100")

    s1 = CareerSessionEngine.create_session(req1)
    s2 = CareerSessionEngine.create_session(req2)

    assert s1.career_id == s2.career_id
    assert s1.player_id == s2.player_id
    assert s1.presentation.player.name == s2.presentation.player.name

    adv1 = CareerSessionEngine.advance_season(s1)
    adv2 = CareerSessionEngine.advance_season(s2)

    assert adv1.current_season == adv2.current_season
    assert adv1.processed_events[0].event_id == adv2.processed_events[0].event_id


def test_immutability_audit():
    req = CareerSetupRequest(player_name="Immutable Test", seed="SEED-IMMUTABLE")
    s = CareerSessionEngine.create_session(req)

    with pytest.raises(Exception):
        s.status = CareerSessionStatus.PAUSED

    with pytest.raises(Exception):
        s.career_id = "NEW_ID"

    with pytest.raises(Exception):
        s.current_season = "2099/00"


def test_100x_career_simulation_audit():
    for i in range(100):
        req = CareerSetupRequest(
            player_name=f"Audit Player {i}",
            position="ST",
            seed=f"AUDIT-SEED-{i}",
        )
        session = CareerSessionEngine.create_session(req)
        assert session.status == CareerSessionStatus.ACTIVE
        assert session.player_id.startswith("p_")

        adv_res = CareerSessionEngine.advance_season(session)
        assert adv_res.success is True
        assert adv_res.current_season == "2027/28"
