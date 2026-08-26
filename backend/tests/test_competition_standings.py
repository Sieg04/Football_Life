import ast
from datetime import date
import json
import os
import subprocess
import sys
import time

import pytest

from app.competition.domain import (
    CompetitionParticipant,
    CompetitionSeason,
    CompetitionStage,
    CompetitionStageType,
)
from app.competition.standings import (
    PointsRule,
    StandingEntry,
    StandingsTable,
    apply_match_result,
    get_club_rank,
    initialize_standings,
    rank_standings,
)
from app.match.domain import MatchResult


def make_test_season(participant_ids: list[int], season_id: str = "cs1") -> CompetitionSeason:
    participants = tuple(
        CompetitionParticipant(
            competition_season_id=season_id,
            club_id=cid,
            seed=f"seed_{cid}",
        )
        for cid in participant_ids
    )
    stage = CompetitionStage(
        id="st1",
        competition_season_id=season_id,
        stage_type=CompetitionStageType.REGULAR_SEASON,
        stage_number=1,
        participant_club_ids=tuple(participant_ids),
    )
    return CompetitionSeason(
        id=season_id,
        competition_id="c1",
        season_label="2025/2026",
        start_date=date(2025, 8, 1),
        end_date=date(2026, 5, 31),
        participants=participants,
        stages=(stage,),
        seed="master_seed",
    )


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
        home_possession=55.0,
        away_possession=45.0,
        home_shots=10,
        away_shots=8,
        player_performances=[],
        events=[],
    )


# --- 1. PointsRule Tests ---

def test_points_rule_defaults():
    rule = PointsRule()
    assert rule.win_points == 3
    assert rule.draw_points == 1
    assert rule.loss_points == 0


def test_points_rule_custom_and_immutability():
    rule = PointsRule(win_points=2, draw_points=1, loss_points=0)
    assert rule.win_points == 2
    with pytest.raises(Exception):
        rule.win_points = 3  # type: ignore


@pytest.mark.parametrize(
    "win,draw,loss",
    [
        (-1, 1, 0),
        (3, -1, 0),
        (3, 1, -1),
    ],
)
def test_points_rule_invalid(win, draw, loss):
    with pytest.raises(ValueError):
        PointsRule(win_points=win, draw_points=draw, loss_points=loss)


# --- 2. StandingEntry Tests ---

def test_standing_entry_valid():
    entry = StandingEntry(
        club_id=1,
        played=5,
        wins=3,
        draws=1,
        losses=1,
        goals_for=8,
        goals_against=4,
        goal_difference=4,
        points=10,
    )
    assert entry.club_id == 1
    assert entry.played == 5
    assert entry.goal_difference == 4


@pytest.mark.parametrize(
    "kwargs,exc",
    [
        ({"club_id": 0, "played": 0, "wins": 0, "draws": 0, "losses": 0, "goals_for": 0, "goals_against": 0, "goal_difference": 0, "points": 0}, ValueError),
        ({"club_id": 1, "played": 5, "wins": 2, "draws": 1, "losses": 1, "goals_for": 8, "goals_against": 4, "goal_difference": 4, "points": 10}, ValueError), # played != 4
        ({"club_id": 1, "played": 5, "wins": 3, "draws": 1, "losses": 1, "goals_for": 8, "goals_against": 4, "goal_difference": 5, "points": 10}, ValueError), # GD mismatch
        ({"club_id": 1, "played": -1, "wins": 0, "draws": 0, "losses": 0, "goals_for": 0, "goals_against": 0, "goal_difference": 0, "points": 0}, ValueError),
        ({"club_id": 1, "played": 0, "wins": 0, "draws": 0, "losses": 0, "goals_for": -1, "goals_against": 0, "goal_difference": -1, "points": 0}, ValueError),
    ],
)
def test_standing_entry_invalid(kwargs, exc):
    with pytest.raises(exc):
        StandingEntry(**kwargs)


# --- 3. StandingsTable Tests ---

def test_standings_table_valid():
    entry1 = StandingEntry(1, 0, 0, 0, 0, 0, 0, 0, 0)
    entry2 = StandingEntry(2, 0, 0, 0, 0, 0, 0, 0, 0)
    table = StandingsTable(competition_season_id="cs1", entries=(entry1, entry2))
    assert table.competition_season_id == "cs1"
    assert len(table.entries) == 2


@pytest.mark.parametrize(
    "season_id,entries,exc",
    [
        ("", (StandingEntry(1, 0, 0, 0, 0, 0, 0, 0, 0), StandingEntry(2, 0, 0, 0, 0, 0, 0, 0, 0)), ValueError),
        ("cs1", (StandingEntry(1, 0, 0, 0, 0, 0, 0, 0, 0),), ValueError), # fewer than 2 entries
        ("cs1", (StandingEntry(1, 0, 0, 0, 0, 0, 0, 0, 0), StandingEntry(1, 0, 0, 0, 0, 0, 0, 0, 0)), ValueError), # duplicate club
    ],
)
def test_standings_table_invalid(season_id, entries, exc):
    with pytest.raises(exc):
        StandingsTable(competition_season_id=season_id, entries=entries)


# --- 4. Initialization Tests ---

def test_initialize_standings():
    season = make_test_season([3, 1, 2])
    table = initialize_standings(season)

    assert table.competition_season_id == "cs1"
    assert len(table.entries) == 3
    # Check deterministic ordering (sorted by club_id ASC)
    assert [e.club_id for e in table.entries] == [1, 2, 3]

    for entry in table.entries:
        assert entry.played == 0
        assert entry.wins == 0
        assert entry.draws == 0
        assert entry.losses == 0
        assert entry.goals_for == 0
        assert entry.goals_against == 0
        assert entry.goal_difference == 0
        assert entry.points == 0


# --- 5. Match Application Tests ---

def test_apply_match_result_home_win():
    season = make_test_season([1, 2])
    table = initialize_standings(season)

    res = make_synthetic_match_result("m1", 1, 2, 2, 0)
    new_table = apply_match_result(table, res)

    # Verify original table immutability
    assert table.entries[0].played == 0

    e1 = [e for e in new_table.entries if e.club_id == 1][0]
    e2 = [e for e in new_table.entries if e.club_id == 2][0]

    assert e1.played == 1 and e1.wins == 1 and e1.points == 3 and e1.goals_for == 2 and e1.goals_against == 0 and e1.goal_difference == 2
    assert e2.played == 1 and e2.losses == 1 and e2.points == 0 and e2.goals_for == 0 and e2.goals_against == 2 and e2.goal_difference == -2


def test_apply_match_result_draw():
    season = make_test_season([1, 2])
    table = initialize_standings(season)

    res = make_synthetic_match_result("m1", 1, 2, 1, 1)
    new_table = apply_match_result(table, res)

    e1 = [e for e in new_table.entries if e.club_id == 1][0]
    e2 = [e for e in new_table.entries if e.club_id == 2][0]

    assert e1.played == 1 and e1.draws == 1 and e1.points == 1 and e1.goals_for == 1 and e1.goals_against == 1 and e1.goal_difference == 0
    assert e2.played == 1 and e2.draws == 1 and e2.points == 1 and e2.goals_for == 1 and e2.goals_against == 1 and e2.goal_difference == 0


def test_apply_match_result_away_win():
    season = make_test_season([1, 2])
    table = initialize_standings(season)

    res = make_synthetic_match_result("m1", 1, 2, 0, 3)
    new_table = apply_match_result(table, res)

    e1 = [e for e in new_table.entries if e.club_id == 1][0]
    e2 = [e for e in new_table.entries if e.club_id == 2][0]

    assert e1.played == 1 and e1.losses == 1 and e1.points == 0 and e1.goals_for == 0 and e1.goals_against == 3 and e1.goal_difference == -3
    assert e2.played == 1 and e2.wins == 1 and e2.points == 3 and e2.goals_for == 3 and e2.goals_against == 0 and e2.goal_difference == 3


def test_apply_match_result_unknown_club():
    season = make_test_season([1, 2])
    table = initialize_standings(season)

    res = make_synthetic_match_result("m1", 1, 99, 1, 0)
    with pytest.raises(ValueError, match="not found in standings table"):
        apply_match_result(table, res)


# --- 6. Ranking & Lookup Tests ---

def test_rank_standings_tiebreaks():
    # Construct entries with specific tiebreakers:
    # Club 1: 6 pts, GD +4, GF 6
    # Club 2: 6 pts, GD +4, GF 8  -> beats Club 1 on GF
    # Club 3: 6 pts, GD +5, GF 5  -> beats Club 2 on GD
    # Club 4: 9 pts               -> beats all on points
    # Club 5: 6 pts, GD +4, GF 6  -> same as Club 1, beats on club_id ASC (1 < 5)
    e4 = StandingEntry(4, 3, 3, 0, 0, 9, 0, 9, 9)
    e3 = StandingEntry(3, 3, 2, 0, 1, 6, 1, 5, 6)
    e2 = StandingEntry(2, 3, 2, 0, 1, 8, 4, 4, 6)
    e1 = StandingEntry(1, 3, 2, 0, 1, 6, 2, 4, 6)
    e5 = StandingEntry(5, 3, 2, 0, 1, 6, 2, 4, 6)

    table = StandingsTable("cs1", (e1, e2, e3, e4, e5))
    ranked = rank_standings(table)

    assert [e.club_id for e in ranked] == [4, 3, 2, 1, 5]


def test_get_club_rank():
    e1 = StandingEntry(1, 1, 1, 0, 0, 2, 0, 2, 3)
    e2 = StandingEntry(2, 1, 0, 0, 1, 0, 2, -2, 0)
    table = StandingsTable("cs1", (e1, e2))

    assert get_club_rank(table, 1) == 1
    assert get_club_rank(table, 2) == 2

    with pytest.raises(ValueError, match="not found in standings table"):
        get_club_rank(table, 99)


# --- 7. Invariants & Audits ---

def test_controlled_audit_4_team_standings():
    season = make_test_season([1, 2, 3, 4])
    table = initialize_standings(season)

    # 6 matches for a single round robin
    matches = [
        make_synthetic_match_result("m1", 1, 2, 2, 1), # 1 wins (3), 2 loses (0)
        make_synthetic_match_result("m2", 3, 4, 0, 0), # 3 draws (1), 4 draws (1)
        make_synthetic_match_result("m3", 1, 3, 1, 1), # 1 draws (4), 3 draws (2)
        make_synthetic_match_result("m4", 2, 4, 3, 0), # 2 wins (3), 4 loses (1)
        make_synthetic_match_result("m5", 1, 4, 2, 0), # 1 wins (7), 4 loses (1)
        make_synthetic_match_result("m6", 2, 3, 1, 2), # 3 wins (5), 2 loses (3)
    ]

    for m in matches:
        table = apply_match_result(table, m)

    # Verify table total invariants:
    # Total goals for == total goals against
    tot_gf = sum(e.goals_for for e in table.entries)
    tot_ga = sum(e.goals_against for e in table.entries)
    assert tot_gf == tot_ga == 13

    # Total points = (wins * 3) + (draws * 2) = 4 wins (12) + 2 draws (4) = 16 pts
    tot_pts = sum(e.points for e in table.entries)
    assert tot_pts == 16

    # Verify each entry math invariants
    for e in table.entries:
        assert e.played == e.wins + e.draws + e.losses
        assert e.goal_difference == e.goals_for - e.goals_against

    ranked = rank_standings(table)
    # Ranks: Club 1 (7 pts), Club 3 (5 pts), Club 2 (3 pts), Club 4 (1 pt)
    assert [e.club_id for e in ranked] == [1, 3, 2, 4]


def test_controlled_audit_20_team_standings():
    clubs = list(range(1, 21))
    season = make_test_season(clubs)
    table = initialize_standings(season)

    # Simulate 10 matches (1 full round for 20 teams)
    matches = []
    for i in range(0, 20, 2):
        c1 = clubs[i]
        c2 = clubs[i + 1]
        matches.append(make_synthetic_match_result(f"m_{c1}_{c2}", c1, c2, 1, 0))

    for m in matches:
        table = apply_match_result(table, m)

    assert len(table.entries) == 20
    for e in table.entries:
        assert e.played == 1

    # 10 teams won, 10 lost
    winners = [e for e in table.entries if e.wins == 1]
    losers = [e for e in table.entries if e.losses == 1]
    assert len(winners) == 10
    assert len(losers) == 10


def test_ast_standings_imports():
    filepath = os.path.join(os.path.dirname(__file__), "..", "app", "competition", "standings.py")
    with open(filepath, "r", encoding="utf-8") as f:
        tree = ast.parse(f.read(), filename="standings.py")

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
