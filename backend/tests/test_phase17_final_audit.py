import json
import subprocess
import sys
import pytest
from app.career.domain import CareerSetupRequest
from app.career.service import CareerSessionService


def test_single_process_determinism():
    seed = "AUDIT_SEED_SINGLE_PROCESS"

    # Run 1
    req1 = CareerSetupRequest("Adrian Martinez", position="ST", starting_club_id="Real Madrid", nationality="Spain", seed=seed)
    sess1 = CareerSessionService.create_career(req1)
    c_id1 = sess1.career_id
    for _ in range(3):
        cur = CareerSessionService.get_session(c_id1)
        if cur.status == "DECISION_PENDING" and cur.pending_decision:
            CareerSessionService.resolve_decision(c_id1, cur.pending_decision.id, cur.pending_decision.options[0].id)
        CareerSessionService.advance_career(c_id1)
    res1 = CareerSessionService.get_session(c_id1)

    # Run 2
    req2 = CareerSetupRequest("Adrian Martinez", position="ST", starting_club_id="Real Madrid", nationality="Spain", seed=seed)
    sess2 = CareerSessionService.create_career(req2)
    c_id2 = sess2.career_id
    for _ in range(3):
        cur = CareerSessionService.get_session(c_id2)
        if cur.status == "DECISION_PENDING" and cur.pending_decision:
            CareerSessionService.resolve_decision(c_id2, cur.pending_decision.id, cur.pending_decision.options[0].id)
        CareerSessionService.advance_career(c_id2)
    res2 = CareerSessionService.get_session(c_id2)

    assert res1.presentation.overview.matches == res2.presentation.overview.matches
    assert res1.presentation.overview.goals == res2.presentation.overview.goals
    assert res1.presentation.overview.assists == res2.presentation.overview.assists
    assert res1.presentation.overview.trophies == res2.presentation.overview.trophies


def test_10x_repeated_determinism():
    seed = "AUDIT_SEED_10X_REPEAT"
    first_matches = None
    first_goals = None

    for i in range(10):
        req = CareerSetupRequest("Test Player", position="LW", starting_club_id="Barcelona", nationality="Spain", seed=seed)
        sess = CareerSessionService.create_career(req)
        c_id = sess.career_id
        for _ in range(2):
            cur = CareerSessionService.get_session(c_id)
            if cur.status == "DECISION_PENDING" and cur.pending_decision:
                CareerSessionService.resolve_decision(c_id, cur.pending_decision.id, cur.pending_decision.options[0].id)
            CareerSessionService.advance_career(c_id)
        res = CareerSessionService.get_session(c_id)

        if first_matches is None:
            first_matches = res.presentation.overview.matches
            first_goals = res.presentation.overview.goals
        else:
            assert res.presentation.overview.matches == first_matches
            assert res.presentation.overview.goals == first_goals


def test_cross_process_determinism():
    cmd = [
        sys.executable,
        "-c",
        """
import json
from app.career.domain import CareerSetupRequest
from app.career.service import CareerSessionService

req = CareerSetupRequest("Cross Process", position="ST", starting_club_id="Real Madrid", nationality="Spain", seed="CROSS_SEED_17")
sess = CareerSessionService.create_career(req)
CareerSessionService.advance_career(sess.career_id)
res = CareerSessionService.get_session(sess.career_id)

out = {
    "matches": res.presentation.overview.matches,
    "goals": res.presentation.overview.goals,
    "assists": res.presentation.overview.assists,
    "ovr": res.presentation.player.overall_rating
}
print(json.dumps(out))
""",
    ]

    res1 = subprocess.check_output(cmd, text=True, env={"PYTHONPATH": "backend"}).strip()
    res2 = subprocess.check_output(cmd, text=True, env={"PYTHONPATH": "backend"}).strip()

    assert res1 == res2
    data = json.loads(res1)
    assert data["matches"] > 0
