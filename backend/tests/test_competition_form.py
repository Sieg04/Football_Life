import ast
import json
import os
import subprocess
import sys

import pytest

from app.competition.form import (
    FormRecord,
    build_form_table,
    calculate_form_points,
    calculate_form_rate,
    calculate_goal_difference,
    record_form_result,
)
from app.match.domain import MatchResult


def make_synthetic_match_result(
    match_id: str,
    home_club_id: int,
    away_club_id: int,
    home_score: int,
    away_score: int,
) -> MatchResult:
    return MatchResult(
        match_id=match_id,
        home_club_id=home_club_id,
        away_club_id=away_club_id,
        home_score=home_score,
        away_score=away_score,
        home_xg=1.5,
        away_xg=1.0,
        home_possession=50.0,
        away_possession=50.0,
        home_shots=10,
        away_shots=8,
        player_performances=[],
        events=[],
    )


# --- 1. FormRecord Tests ---

def test_form_record_valid():
    rec = FormRecord(
        club_id=1,
        window_size=5,
        results=("W", "D", "L"),
        goals_for=(2, 1, 0),
        goals_against=(0, 1, 3),
    )
    assert rec.club_id == 1
    assert rec.window_size == 5
    assert len(rec.results) == 3


def test_form_record_immutability():
    rec = FormRecord(club_id=1, window_size=5)
    with pytest.raises(Exception):
        rec.window_size = 3  # type: ignore


@pytest.mark.parametrize(
    "kwargs,exc",
    [
        ({"club_id": 0}, ValueError),
        ({"club_id": 1, "window_size": 0}, ValueError),
        ({"club_id": 1, "window_size": 2, "results": ("W", "D", "L"), "goals_for": (1, 1, 1), "goals_against": (0, 0, 0)}, ValueError), # exceeds window
        ({"club_id": 1, "results": ("W", "D"), "goals_for": (1,), "goals_against": (0, 0)}, ValueError), # mismatched gf len
        ({"club_id": 1, "results": ("W", "X"), "goals_for": (1, 0), "goals_against": (0, 0)}, ValueError), # invalid result char
        ({"club_id": 1, "results": ("W",), "goals_for": (-1,), "goals_against": (0,)}, ValueError), # negative gf
    ],
)
def test_form_record_invalid(kwargs, exc):
    with pytest.raises(exc):
        FormRecord(**kwargs)


# --- 2. Record Form Result Tests ---

def test_record_form_result_home_win_and_rolling_window():
    f0 = FormRecord(
        club_id=1,
        window_size=3,
        results=("W", "D", "L"),
        goals_for=(1, 2, 0),
        goals_against=(0, 2, 1),
    )

    m1 = make_synthetic_match_result("m1", 1, 2, 3, 1) # Home win
    f1 = record_form_result(f0, m1)

    # Immutability check
    assert f0.results == ("W", "D", "L")

    # Rolling window: oldest ("W", 1, 0) dropped, newest ("W", 3, 1) added
    assert f1.results == ("D", "L", "W")
    assert f1.goals_for == (2, 0, 3)
    assert f1.goals_against == (2, 1, 1)


def test_record_form_result_away_loss():
    f0 = FormRecord(club_id=2, window_size=5)
    m1 = make_synthetic_match_result("m1", 1, 2, 2, 0) # Away loss for club 2

    f1 = record_form_result(f0, m1)
    assert f1.results == ("L",)
    assert f1.goals_for == (0,)
    assert f1.goals_against == (2,)


def test_record_form_result_uninvolved_club_raises():
    f0 = FormRecord(club_id=99, window_size=5)
    m1 = make_synthetic_match_result("m1", 1, 2, 1, 0)
    with pytest.raises(ValueError, match="not involved in MatchResult"):
        record_form_result(f0, m1)


# --- 3. Form Metrics Tests ---

def test_form_metrics():
    rec = FormRecord(
        club_id=1,
        window_size=5,
        results=("W", "W", "D", "L", "W"),
        goals_for=(3, 2, 1, 0, 2),
        goals_against=(1, 0, 1, 2, 1),
    )

    assert calculate_form_points(rec) == 10  # 3 + 3 + 1 + 0 + 3 = 10
    assert calculate_form_rate(rec) == pytest.approx(10 / 15.0)
    assert calculate_goal_difference(rec) == 8 - 5 == 3


def test_form_rate_empty():
    rec = FormRecord(club_id=1, window_size=5)
    assert calculate_form_points(rec) == 0
    assert calculate_form_rate(rec) == 0.0
    assert calculate_goal_difference(rec) == 0


# --- 4. Form Table & Order Independence Tests ---

def test_build_form_table_order_independence():
    m1 = make_synthetic_match_result("m1", 1, 2, 2, 1)
    m2 = make_synthetic_match_result("m2", 1, 3, 0, 0)
    m3 = make_synthetic_match_result("m3", 2, 3, 1, 3)

    # Order 1
    t1 = build_form_table([1, 2, 3], [m1, m2, m3], window_size=5)

    # Order 2 (reversed list)
    t2 = build_form_table([1, 2, 3], [m3, m2, m1], window_size=5)

    assert t1 == t2
    assert t1[1].results == ("W", "D")
    assert t1[2].results == ("L", "L")
    assert t1[3].results == ("D", "W")


def test_build_form_table_duplicate_club_ids():
    with pytest.raises(ValueError, match="duplicate club IDs"):
        build_form_table([1, 1], [])


# --- 5. Audits & Determinism ---

def test_controlled_audit_cross_process_determinism():
    script = """
import json
from app.match.domain import MatchResult
from app.competition.standings import initialize_standings, apply_match_result, rank_standings
from app.competition.form import build_form_table
from app.competition.domain import CompetitionSeason, CompetitionStage, CompetitionStageType, CompetitionParticipant
from datetime import date

participants = tuple(CompetitionParticipant("cs1", cid, f"s_{cid}") for cid in range(1, 5))
stage = CompetitionStage("st1", "cs1", CompetitionStageType.REGULAR_SEASON, 1, (1, 2, 3, 4))
season = CompetitionSeason("cs1", "c1", "2025", date(2025,8,1), date(2026,5,31), participants, (stage,), "seed")

table = initialize_standings(season)
m1 = MatchResult("m1", 1, 2, 2, 1, 1.5, 1.0, 50.0, 50.0, 10, 8, [], [])
m2 = MatchResult("m2", 3, 4, 0, 1, 1.0, 1.2, 45.0, 55.0, 5, 9, [], [])

table = apply_match_result(table, m1)
table = apply_match_result(table, m2)
ranked = rank_standings(table)

form_table = build_form_table([1, 2, 3, 4], [m1, m2])

out = {
    "standings": [{"club_id": e.club_id, "pts": e.points, "gd": e.goal_difference} for e in ranked],
    "form": {cid: list(rec.results) for cid, rec in form_table.items()}
}
print(json.dumps(out))
"""

    env = dict(os.environ)
    env["PYTHONPATH"] = "backend"

    p1 = subprocess.run([sys.executable, "-c", script], capture_output=True, text=True, env=env, check=True)
    p2 = subprocess.run([sys.executable, "-c", script], capture_output=True, text=True, env=env, check=True)

    assert p1.stdout == p2.stdout
    print("\n[Audit Standings/Form] Cross-process determinism: Byte-for-byte identical output verified.")


def test_ast_form_imports():
    filepath = os.path.join(os.path.dirname(__file__), "..", "app", "competition", "form.py")
    with open(filepath, "r", encoding="utf-8") as f:
        tree = ast.parse(f.read(), filename="form.py")

    prohibited = {
        "fastapi", "sqlalchemy", "sqlite3", "alembic", "http", "httpx",
        "starlette", "angular", "app.career", "random", "uuid", "time"
    }

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                for p in prohibited:
                    assert not alias.name.startswith(p), f"Prohibited import: {alias.name}"
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                for p in prohibited:
                    assert not node.module.startswith(p), f"Prohibited import from: {node.module}"
