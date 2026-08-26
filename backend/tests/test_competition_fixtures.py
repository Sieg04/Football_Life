import ast
from datetime import date, timedelta
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
from app.competition.fixtures import (
    Fixture,
    FixtureStatus,
    calculate_match_importance,
    generate_fixture_seed,
    generate_round_robin_fixtures,
    generate_single_elimination_fixtures,
    generate_two_leg_elimination_fixtures,
)


def make_season_and_stage(
    participant_ids: list[int],
    start_date: date = date(2025, 8, 1),
    end_date: date = date(2026, 5, 31),
    stage_type: CompetitionStageType = CompetitionStageType.REGULAR_SEASON,
    season_id: str = "cs1",
    stage_id: str = "st1",
    season_seed: str = "seed123",
) -> tuple[CompetitionSeason, CompetitionStage]:
    participants = tuple(
        CompetitionParticipant(
            competition_season_id=season_id,
            club_id=cid,
            seed=f"pseed_{cid}",
        )
        for cid in participant_ids
    )
    stage = CompetitionStage(
        id=stage_id,
        competition_season_id=season_id,
        stage_type=stage_type,
        stage_number=1,
        participant_club_ids=tuple(participant_ids),
        completed=False,
    )
    season = CompetitionSeason(
        id=season_id,
        competition_id="c1",
        season_label="2025/2026",
        start_date=start_date,
        end_date=end_date,
        participants=participants,
        stages=(stage,),
        seed=season_seed,
    )
    return season, stage


# --- 1. Fixture Domain Primitive Tests ---

def test_fixture_valid():
    fix = Fixture(
        id="cs1:st1:1:1:2",
        competition_season_id="cs1",
        stage_id="st1",
        round_number=1,
        scheduled_date=date(2025, 8, 10),
        home_club_id=1,
        away_club_id=2,
        importance=50.0,
        rivalry_factor=1.0,
        seed="fixture_seed_123",
        status=FixtureStatus.SCHEDULED,
    )
    assert fix.id == "cs1:st1:1:1:2"
    assert fix.home_club_id == 1
    assert fix.away_club_id == 2
    assert fix.status == FixtureStatus.SCHEDULED


def test_fixture_frozen_immutability():
    fix = Fixture(
        id="cs1:st1:1:1:2",
        competition_season_id="cs1",
        stage_id="st1",
        round_number=1,
        scheduled_date=date(2025, 8, 10),
        home_club_id=1,
        away_club_id=2,
        importance=50.0,
        rivalry_factor=1.0,
        seed="fixture_seed_123",
    )
    with pytest.raises(Exception):
        fix.round_number = 2  # type: ignore


@pytest.mark.parametrize(
    "field,value,exc",
    [
        ("id", "", ValueError),
        ("id", "  ", ValueError),
        ("competition_season_id", "", ValueError),
        ("stage_id", "", ValueError),
        ("round_number", 0, ValueError),
        ("home_club_id", 0, ValueError),
        ("away_club_id", -1, ValueError),
        ("home_club_id", 2, ValueError),  # home == away when away is also 2
        ("importance", -0.1, ValueError),
        ("importance", 100.1, ValueError),
        ("rivalry_factor", -1.0, ValueError),
        ("seed", "", ValueError),
    ],
)
def test_fixture_invalid_fields(field, value, exc):
    kwargs = {
        "id": "cs1:st1:1:1:2",
        "competition_season_id": "cs1",
        "stage_id": "st1",
        "round_number": 1,
        "scheduled_date": date(2025, 8, 10),
        "home_club_id": 1,
        "away_club_id": 2,
        "importance": 50.0,
        "rivalry_factor": 1.0,
        "seed": "fixture_seed_123",
    }
    if field == "home_club_id" and value == 2:
        kwargs["home_club_id"] = 2
        kwargs["away_club_id"] = 2
    else:
        kwargs[field] = value

    with pytest.raises(exc):
        Fixture(**kwargs)


# --- 2. Fixture Seed Tests ---

def test_generate_fixture_seed_determinism():
    s1 = generate_fixture_seed("seedA", "cs1", "st1", 1, 10, 20)
    s2 = generate_fixture_seed("seedA", "cs1", "st1", 1, 10, 20)
    assert s1 == s2
    assert len(s1) == 64  # SHA-256 hex length


def test_generate_fixture_seed_different_inputs():
    s1 = generate_fixture_seed("seedA", "cs1", "st1", 1, 10, 20)
    s2 = generate_fixture_seed("seedB", "cs1", "st1", 1, 10, 20)
    s3 = generate_fixture_seed("seedA", "cs1", "st1", 2, 10, 20)
    assert s1 != s2
    assert s1 != s3


test_generate_fixture_seed_swapped_home_away = lambda: None  # placeholder function name for lint


def test_generate_fixture_seed_swapped_home_away_diff():
    s_home_away = generate_fixture_seed("seedA", "cs1", "st1", 1, 10, 20)
    s_away_home = generate_fixture_seed("seedA", "cs1", "st1", 1, 20, 10)
    assert s_home_away != s_away_home


@pytest.mark.parametrize(
    "kwargs",
    [
        {"season_seed": "", "competition_season_id": "cs1", "stage_id": "st1", "round_number": 1, "home_club_id": 1, "away_club_id": 2},
        {"season_seed": "s", "competition_season_id": "", "stage_id": "st1", "round_number": 1, "home_club_id": 1, "away_club_id": 2},
        {"season_seed": "s", "competition_season_id": "cs1", "stage_id": "", "round_number": 1, "home_club_id": 1, "away_club_id": 2},
        {"season_seed": "s", "competition_season_id": "cs1", "stage_id": "st1", "round_number": 0, "home_club_id": 1, "away_club_id": 2},
        {"season_seed": "s", "competition_season_id": "cs1", "stage_id": "st1", "round_number": 1, "home_club_id": 0, "away_club_id": 2},
    ],
)
def test_generate_fixture_seed_invalid(kwargs):
    with pytest.raises(ValueError):
        generate_fixture_seed(**kwargs)


# --- 3. Match Importance Tests ---

@pytest.mark.parametrize(
    "stage_type,expected",
    [
        (CompetitionStageType.FINAL, 95.0),
        (CompetitionStageType.SEMI_FINAL, 85.0),
        (CompetitionStageType.QUARTER_FINAL, 75.0),
        (CompetitionStageType.ROUND_OF_16, 65.0),
        (CompetitionStageType.ROUND_OF_32, 60.0),
    ],
)
def test_calculate_match_importance_stages(stage_type, expected):
    assert calculate_match_importance(50.0, stage_type, 1) == expected


def test_calculate_match_importance_regular_stage_preserves_base():
    assert calculate_match_importance(45.0, CompetitionStageType.REGULAR_SEASON, 1) == 45.0
    assert calculate_match_importance(80.0, CompetitionStageType.GROUP_STAGE, 3) == 80.0


def test_calculate_match_importance_clamping():
    assert calculate_match_importance(-10.0, CompetitionStageType.REGULAR_SEASON, 1) == 0.0
    assert calculate_match_importance(150.0, CompetitionStageType.REGULAR_SEASON, 1) == 100.0


# --- 4. Round-Robin Generation Tests ---

def test_generate_round_robin_4_teams():
    season, stage = make_season_and_stage([1, 2, 3, 4])
    fixtures = generate_round_robin_fixtures(season, stage, start_date=date(2025, 8, 1))

    # 4 teams -> (4-1)*2 = 6 rounds. Each round has 4//2 = 2 matches -> 12 fixtures
    assert len(fixtures) == 12

    rounds = set(f.round_number for f in fixtures)
    assert rounds == {1, 2, 3, 4, 5, 6}

    # Verify each unordered pair meets twice
    pair_counts = {}
    for f in fixtures:
        pair = tuple(sorted([f.home_club_id, f.away_club_id]))
        pair_counts[pair] = pair_counts.get(pair, 0) + 1
    assert all(count == 2 for count in pair_counts.values())

    # Verify home/away balance per club
    for cid in [1, 2, 3, 4]:
        home_matches = [f for f in fixtures if f.home_club_id == cid]
        away_matches = [f for f in fixtures if f.away_club_id == cid]
        assert len(home_matches) == 3
        assert len(away_matches) == 3


def test_generate_round_robin_odd_teams_5():
    season, stage = make_season_and_stage([1, 2, 3, 4, 5])
    fixtures = generate_round_robin_fixtures(season, stage, start_date=date(2025, 8, 1))

    # 5 teams -> 6 virtual teams -> 5 rounds in single, 10 rounds in double.
    # Each round has 2 matches (since 1 team has a bye) -> 20 fixtures total.
    assert len(fixtures) == 20

    # No BYE fixture exists
    for f in fixtures:
        assert f.home_club_id in [1, 2, 3, 4, 5]
        assert f.away_club_id in [1, 2, 3, 4, 5]

    # Each team plays 8 matches
    for cid in [1, 2, 3, 4, 5]:
        team_fixtures = [f for f in fixtures if f.home_club_id == cid or f.away_club_id == cid]
        assert len(team_fixtures) == 8


def test_generate_round_robin_no_duplicate_matches_in_round():
    season, stage = make_season_and_stage([1, 2, 3, 4, 5, 6])
    fixtures = generate_round_robin_fixtures(season, stage, start_date=date(2025, 8, 1))

    # Group fixtures by round
    by_round = {}
    for f in fixtures:
        by_round.setdefault(f.round_number, []).append(f)

    for r, r_fixtures in by_round.items():
        teams_in_round = set()
        for f in r_fixtures:
            assert f.home_club_id not in teams_in_round
            assert f.away_club_id not in teams_in_round
            teams_in_round.add(f.home_club_id)
            teams_in_round.add(f.away_club_id)


def test_generate_round_robin_outside_season_window_raises():
    season, stage = make_season_and_stage(
        [1, 2, 3, 4], start_date=date(2025, 8, 1), end_date=date(2025, 8, 15)
    )
    # 6 rounds with 7 days interval requires 35 days -> exceeds Aug 15!
    with pytest.raises(ValueError, match="outside competition season window"):
        generate_round_robin_fixtures(season, stage, start_date=date(2025, 8, 1), interval_days=7)


def test_generate_round_robin_invalid_interval():
    season, stage = make_season_and_stage([1, 2, 3, 4])
    with pytest.raises(ValueError, match="interval_days must be > 0"):
        generate_round_robin_fixtures(season, stage, start_date=date(2025, 8, 1), interval_days=0)


def test_generate_round_robin_mismatched_season_id():
    season, _ = make_season_and_stage([1, 2, 3, 4], season_id="cs1")
    stage_bad = CompetitionStage(
        id="st1",
        competition_season_id="cs_other",
        stage_type=CompetitionStageType.REGULAR_SEASON,
        stage_number=1,
        participant_club_ids=(1, 2, 3, 4),
    )
    with pytest.raises(ValueError, match="does not match season id"):
        generate_round_robin_fixtures(season, stage_bad, start_date=date(2025, 8, 1))


def test_generate_round_robin_participant_not_in_season():
    participants = (
        CompetitionParticipant(competition_season_id="cs1", club_id=1, seed="s1"),
        CompetitionParticipant(competition_season_id="cs1", club_id=2, seed="s2"),
    )
    stage = CompetitionStage(
        id="st1",
        competition_season_id="cs1",
        stage_type=CompetitionStageType.REGULAR_SEASON,
        stage_number=1,
        participant_club_ids=(1, 3),  # 3 is not in season participants
    )
    season = CompetitionSeason(
        id="cs1",
        competition_id="c1",
        season_label="2025",
        start_date=date(2025, 8, 1),
        end_date=date(2026, 5, 31),
        participants=participants,
        stages=(stage,),
        seed="s123",
    )
    with pytest.raises(ValueError, match="must belong to season participants"):
        generate_round_robin_fixtures(season, stage, start_date=date(2025, 8, 1))


# --- 5. Single Elimination Generation Tests ---

def test_generate_single_elimination_8_teams():
    season, stage = make_season_and_stage([1, 2, 3, 4, 5, 6, 7, 8], stage_type=CompetitionStageType.QUARTER_FINAL)
    fixtures = generate_single_elimination_fixtures(season, stage, scheduled_date=date(2025, 9, 1))

    assert len(fixtures) == 4
    for f in fixtures:
        assert f.round_number == 1
        assert f.scheduled_date == date(2025, 9, 1)
        assert f.importance == 75.0  # QUARTER_FINAL baseline


def test_generate_single_elimination_non_power_of_two_6_teams():
    season, stage = make_season_and_stage([1, 2, 3, 4, 5, 6])
    # Target size is 8. Number of byes is 8 - 6 = 2.
    # Sorted clubs: 1, 2, 3, 4, 5, 6.
    # Byes: 1, 2. Playing: 3, 4, 5, 6.
    # Scheduled fixtures in round 1: (3 vs 4), (5 vs 6) -> 2 fixtures.
    fixtures = generate_single_elimination_fixtures(season, stage, scheduled_date=date(2025, 9, 1))
    assert len(fixtures) == 2
    assert fixtures[0].home_club_id == 3 and fixtures[0].away_club_id == 4
    assert fixtures[1].home_club_id == 5 and fixtures[1].away_club_id == 6


def test_generate_single_elimination_outside_season_window():
    season, stage = make_season_and_stage([1, 2, 3, 4], start_date=date(2025, 8, 1), end_date=date(2025, 8, 31))
    with pytest.raises(ValueError, match="outside competition season window"):
        generate_single_elimination_fixtures(season, stage, scheduled_date=date(2025, 9, 1))


# --- 6. Two-Leg Elimination Generation Tests ---

def test_generate_two_leg_elimination_4_teams():
    season, stage = make_season_and_stage([1, 2, 3, 4], stage_type=CompetitionStageType.SEMI_FINAL)
    fixtures = generate_two_leg_elimination_fixtures(
        season,
        stage,
        first_leg_date=date(2025, 10, 1),
        second_leg_date=date(2025, 10, 8),
    )

    # 4 teams -> 2 pairings -> 2 legs -> 4 fixtures total
    assert len(fixtures) == 4

    leg1 = [f for f in fixtures if f.round_number == 1]
    leg2 = [f for f in fixtures if f.round_number == 2]

    assert len(leg1) == 2
    assert len(leg2) == 2

    # Check reversed home/away
    assert leg1[0].home_club_id == leg2[0].away_club_id
    assert leg1[0].away_club_id == leg2[0].home_club_id
    assert leg1[1].home_club_id == leg2[1].away_club_id
    assert leg1[1].away_club_id == leg2[1].home_club_id

    # Check dates & importance
    for f in leg1:
        assert f.scheduled_date == date(2025, 10, 1)
        assert f.importance == 85.0
    for f in leg2:
        assert f.scheduled_date == date(2025, 10, 8)
        assert f.importance == 85.0


def test_generate_two_leg_elimination_odd_teams_raises():
    season, stage = make_season_and_stage([1, 2, 3])
    with pytest.raises(ValueError, match="requires an even number of participants"):
        generate_two_leg_elimination_fixtures(
            season, stage, first_leg_date=date(2025, 10, 1), second_leg_date=date(2025, 10, 8)
        )


def test_generate_two_leg_elimination_invalid_dates():
    season, stage = make_season_and_stage([1, 2, 3, 4])
    with pytest.raises(ValueError, match="first_leg_date must be <= second_leg_date"):
        generate_two_leg_elimination_fixtures(
            season, stage, first_leg_date=date(2025, 10, 8), second_leg_date=date(2025, 10, 1)
        )


# --- 7. Purity & Domain Protection Tests ---

def test_purity_season_and_stage_unmodified():
    season, stage = make_season_and_stage([4, 1, 3, 2])
    orig_stage_participants = tuple(stage.participant_club_ids)

    generate_round_robin_fixtures(season, stage, start_date=date(2025, 8, 1))

    assert stage.participant_club_ids == orig_stage_participants


def test_ast_architectural_imports():
    """Verify backend/app/competition/fixtures.py has no prohibited imports or domain leakage."""
    filepath = os.path.join(os.path.dirname(__file__), "..", "app", "competition", "fixtures.py")
    with open(filepath, "r", encoding="utf-8") as f:
        tree = ast.parse(f.read(), filename="fixtures.py")

    prohibited_modules = {
        "fastapi",
        "sqlalchemy",
        "sqlite3",
        "alembic",
        "http",
        "httpx",
        "starlette",
        "angular",
        "app.match",
        "app.career",
        "app.player",
    }

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                for prohibited in prohibited_modules:
                    assert not alias.name.startswith(prohibited), f"Prohibited import: {alias.name}"
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                for prohibited in prohibited_modules:
                    assert not node.module.startswith(prohibited), f"Prohibited import from: {node.module}"


# --- 8. Controlled Audits ---

def test_controlled_audit_a_20_team_double_round_robin():
    teams = list(range(1, 21))
    season, stage = make_season_and_stage(teams)

    t0 = time.perf_counter()
    fixtures = generate_round_robin_fixtures(season, stage, start_date=date(2025, 8, 1), interval_days=7)
    elapsed_ms = (time.perf_counter() - t0) * 1000.0

    # 20 teams DRR Audit Expectations:
    # 380 fixtures total
    # 38 rounds
    # 10 matches per round
    # 38 matches per club
    # 19 home per club
    # 19 away per club
    assert len(fixtures) == 380

    rounds = set(f.round_number for f in fixtures)
    assert len(rounds) == 38

    by_round = {}
    for f in fixtures:
        by_round.setdefault(f.round_number, []).append(f)
    assert all(len(matches) == 10 for matches in by_round.values())

    for cid in teams:
        team_home = [f for f in fixtures if f.home_club_id == cid]
        team_away = [f for f in fixtures if f.away_club_id == cid]
        assert len(team_home) == 19
        assert len(team_away) == 19
        assert len(team_home) + len(team_away) == 38

    # Unique fixture IDs
    fixture_ids = set(f.id for f in fixtures)
    assert len(fixture_ids) == 380

    # All dates inside season
    assert all(season.start_date <= f.scheduled_date <= season.end_date for f in fixtures)

    print(f"\n[Audit A] 20-team DRR: 380 fixtures generated in {elapsed_ms:.2f} ms")


def test_controlled_audit_b_5_team_round_robin():
    teams = list(range(1, 6))
    season, stage = make_season_and_stage(teams)

    t0 = time.perf_counter()
    fixtures = generate_round_robin_fixtures(season, stage, start_date=date(2025, 8, 1))
    elapsed_ms = (time.perf_counter() - t0) * 1000.0

    # 5 teams DRR Audit Expectations:
    # 20 fixtures total
    # 8 matches per club
    # each unordered pair meets twice
    # no BYE fixture exists
    assert len(fixtures) == 20

    for cid in teams:
        club_matches = [f for f in fixtures if f.home_club_id == cid or f.away_club_id == cid]
        assert len(club_matches) == 8

    pair_counts = {}
    for f in fixtures:
        pair = tuple(sorted([f.home_club_id, f.away_club_id]))
        pair_counts[pair] = pair_counts.get(pair, 0) + 1
    assert len(pair_counts) == 10  # 5*4/2 = 10 unique unordered pairs
    assert all(count == 2 for count in pair_counts.values())

    print(f"\n[Audit B] 5-team DRR: 20 fixtures generated in {elapsed_ms:.2f} ms")


def test_controlled_audit_c_8_team_knockout():
    teams = list(range(1, 9))
    season, stage = make_season_and_stage(teams, stage_type=CompetitionStageType.QUARTER_FINAL)

    t0 = time.perf_counter()
    fixtures = generate_single_elimination_fixtures(season, stage, scheduled_date=date(2025, 9, 1))
    elapsed_ms = (time.perf_counter() - t0) * 1000.0

    # 8-team Knockout Audit Expectations:
    # 4 fixtures
    # 8 unique participants
    # no club duplicated
    assert len(fixtures) == 4
    participating_clubs = set()
    for f in fixtures:
        assert f.home_club_id != f.away_club_id
        participating_clubs.add(f.home_club_id)
        participating_clubs.add(f.away_club_id)
    assert participating_clubs == set(teams)

    print(f"\n[Audit C] 8-team Knockout: 4 fixtures generated in {elapsed_ms:.2f} ms")


def test_controlled_audit_d_4_team_two_leg_knockout():
    teams = list(range(1, 5))
    season, stage = make_season_and_stage(teams, stage_type=CompetitionStageType.SEMI_FINAL)

    t0 = time.perf_counter()
    fixtures = generate_two_leg_elimination_fixtures(
        season, stage, first_leg_date=date(2025, 10, 1), second_leg_date=date(2025, 10, 8)
    )
    elapsed_ms = (time.perf_counter() - t0) * 1000.0

    # 4-team Two-Leg Audit Expectations:
    # 4 fixtures total
    # 2 pairings
    # leg 1 home/away, leg 2 reversed
    assert len(fixtures) == 4
    leg1 = fixtures[:2]
    leg2 = fixtures[2:]

    for f1, f2 in zip(leg1, leg2):
        assert f1.home_club_id == f2.away_club_id
        assert f1.away_club_id == f2.home_club_id
        assert f1.scheduled_date == date(2025, 10, 1)
        assert f2.scheduled_date == date(2025, 10, 8)

    print(f"\n[Audit D] 4-team Two-Leg Knockout: 4 fixtures generated in {elapsed_ms:.2f} ms")


def test_controlled_audit_e_cross_process_determinism():
    """Verify determinism across process boundaries using python command subprocess."""
    script = """
import json
from datetime import date
from app.competition.domain import CompetitionSeason, CompetitionStage, CompetitionStageType, CompetitionParticipant
from app.competition.fixtures import generate_round_robin_fixtures

participants = tuple(CompetitionParticipant("cs1", cid, f"seed_{cid}") for cid in range(1, 11))
stage = CompetitionStage("st1", "cs1", CompetitionStageType.REGULAR_SEASON, 1, tuple(range(1, 11)))
season = CompetitionSeason("cs1", "c1", "2025/2026", date(2025, 8, 1), date(2026, 5, 31), participants, (stage,), "master_seed")

fixtures = generate_round_robin_fixtures(season, stage, date(2025, 8, 1))
out = [{"id": f.id, "date": str(f.scheduled_date), "home": f.home_club_id, "away": f.away_club_id, "seed": f.seed} for f in fixtures]
print(json.dumps(out))
"""

    env = dict(os.environ)
    env["PYTHONPATH"] = "backend"

    p1 = subprocess.run([sys.executable, "-c", script], capture_output=True, text=True, env=env, check=True)
    p2 = subprocess.run([sys.executable, "-c", script], capture_output=True, text=True, env=env, check=True)

    assert p1.stdout == p2.stdout
    print("\n[Audit E] Cross-process determinism: Byte-for-byte identical output verified.")
