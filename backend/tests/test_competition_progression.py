from datetime import date
import subprocess
import sys
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
    generate_round_robin_fixtures,
    generate_single_elimination_fixtures,
    generate_two_leg_elimination_fixtures,
)
from app.competition.progression import (
    ProgressionResult,
    TieBreakResult,
    build_next_stage_participants,
    calculate_aggregate_score,
    evaluate_knockout_stage_progression,
    evaluate_round_robin_completion,
    resolve_two_leg_tie,
)
from app.match.domain import MatchResult


def create_dummy_match_result(
    fixture: Fixture, home_score: int, away_score: int
) -> MatchResult:
    return MatchResult(
        match_id=fixture.id,
        home_club_id=fixture.home_club_id,
        away_club_id=fixture.away_club_id,
        home_score=home_score,
        away_score=away_score,
        home_xg=1.5,
        away_xg=1.2,
        home_possession=55.0,
        away_possession=45.0,
        home_shots=10,
        away_shots=8,
        player_performances=[],
        events=[],
    )


# --- Section 27: ProgressionResult Dataclass Tests ---

def test_progression_result_valid():
    res = ProgressionResult(
        competition_season_id="season_1",
        stage_completed=True,
        current_stage_index=0,
        advanced_club_ids=(1, 2),
        eliminated_club_ids=(3, 4),
        winner_club_id=1,
        next_stage_id="stage_2",
    )
    assert res.competition_season_id == "season_1"
    assert res.stage_completed is True
    assert res.current_stage_index == 0
    assert res.advanced_club_ids == (1, 2)
    assert res.eliminated_club_ids == (3, 4)
    assert res.winner_club_id == 1
    assert res.next_stage_id == "stage_2"


def test_progression_result_empty_season_id():
    with pytest.raises(ValueError, match="competition_season_id"):
        ProgressionResult(
            competition_season_id="",
            stage_completed=True,
            current_stage_index=0,
            advanced_club_ids=(1,),
            eliminated_club_ids=(2,),
        )


def test_progression_result_negative_stage_index():
    with pytest.raises(ValueError, match="current_stage_index"):
        ProgressionResult(
            competition_season_id="season_1",
            stage_completed=True,
            current_stage_index=-1,
            advanced_club_ids=(1,),
            eliminated_club_ids=(2,),
        )


def test_progression_result_invalid_club_id():
    with pytest.raises(ValueError, match="all advanced club IDs must be positive"):
        ProgressionResult(
            competition_season_id="season_1",
            stage_completed=True,
            current_stage_index=0,
            advanced_club_ids=(0,),
            eliminated_club_ids=(2,),
        )


def test_progression_result_duplicate_advanced_ids():
    with pytest.raises(ValueError, match="advanced_club_ids contains duplicate"):
        ProgressionResult(
            competition_season_id="season_1",
            stage_completed=True,
            current_stage_index=0,
            advanced_club_ids=(1, 1),
            eliminated_club_ids=(2,),
        )


def test_progression_result_duplicate_eliminated_ids():
    with pytest.raises(ValueError, match="eliminated_club_ids contains duplicate"):
        ProgressionResult(
            competition_season_id="season_1",
            stage_completed=True,
            current_stage_index=0,
            advanced_club_ids=(1,),
            eliminated_club_ids=(2, 2),
        )


def test_progression_result_overlap_clubs():
    with pytest.raises(ValueError, match="appear in both advanced and eliminated"):
        ProgressionResult(
            competition_season_id="season_1",
            stage_completed=True,
            current_stage_index=0,
            advanced_club_ids=(1, 2),
            eliminated_club_ids=(2, 3),
        )


def test_progression_result_invalid_winner():
    with pytest.raises(ValueError, match="winner_club_id"):
        ProgressionResult(
            competition_season_id="season_1",
            stage_completed=True,
            current_stage_index=0,
            advanced_club_ids=(1,),
            eliminated_club_ids=(2,),
            winner_club_id=-5,
        )


def test_progression_result_invalid_next_stage_id():
    with pytest.raises(ValueError, match="next_stage_id"):
        ProgressionResult(
            competition_season_id="season_1",
            stage_completed=True,
            current_stage_index=0,
            advanced_club_ids=(1,),
            eliminated_club_ids=(2,),
            next_stage_id="   ",
        )


def test_progression_result_immutability():
    res = ProgressionResult(
        competition_season_id="season_1",
        stage_completed=True,
        current_stage_index=0,
        advanced_club_ids=(1,),
        eliminated_club_ids=(2,),
    )
    with pytest.raises(AttributeError):
        res.competition_season_id = "other"  # type: ignore


# --- Section 28: TieBreakResult Dataclass Tests ---

def test_tiebreak_result_valid():
    tb = TieBreakResult(winner_club_id=1, method="PENALTIES")
    assert tb.winner_club_id == 1
    assert tb.method == "PENALTIES"

    tb_et = TieBreakResult(winner_club_id=2, method="EXTRA_TIME")
    assert tb_et.winner_club_id == 2
    assert tb_et.method == "EXTRA_TIME"


def test_tiebreak_result_unresolved():
    tb = TieBreakResult(winner_club_id=None, method="PENALTIES")
    assert tb.winner_club_id is None
    assert tb.method == "PENALTIES"


def test_tiebreak_result_invalid_method():
    with pytest.raises(ValueError, match="Invalid tiebreak method"):
        TieBreakResult(winner_club_id=1, method="COIN_TOSS")


def test_tiebreak_result_empty_method():
    with pytest.raises(ValueError, match="method must be a non-empty string"):
        TieBreakResult(winner_club_id=1, method="")


def test_tiebreak_result_invalid_winner():
    with pytest.raises(ValueError, match="winner_club_id"):
        TieBreakResult(winner_club_id=0, method="PENALTIES")


def test_tiebreak_result_immutability():
    tb = TieBreakResult(winner_club_id=1, method="PENALTIES")
    with pytest.raises(AttributeError):
        tb.method = "EXTRA_TIME"  # type: ignore


# --- Section 29: Round-Robin Progression Tests ---

def test_round_robin_progression_complete():
    participants = (
        CompetitionParticipant("season_1", 1, "seed1"),
        CompetitionParticipant("season_1", 2, "seed2"),
        CompetitionParticipant("season_1", 3, "seed3"),
        CompetitionParticipant("season_1", 4, "seed4"),
    )
    stage = CompetitionStage(
        id="stage_rr",
        competition_season_id="season_1",
        stage_type=CompetitionStageType.REGULAR_SEASON,
        stage_number=1,
        participant_club_ids=(1, 2, 3, 4),
    )
    season = CompetitionSeason(
        id="season_1",
        competition_id="comp_1",
        season_label="2025/2026",
        start_date=date(2025, 9, 1),
        end_date=date(2026, 5, 30),
        participants=participants,
        stages=(stage,),
        seed="season_seed",
    )

    fixtures = generate_round_robin_fixtures(season, stage, start_date=date(2025, 9, 1))

    # Make club 1 win all matches
    match_results = []
    for f in fixtures:
        if f.home_club_id == 1:
            match_results.append(create_dummy_match_result(f, 3, 0))
        elif f.away_club_id == 1:
            match_results.append(create_dummy_match_result(f, 0, 3))
        else:
            match_results.append(create_dummy_match_result(f, 1, 1))

    progression = evaluate_round_robin_completion(season, stage, fixtures, match_results)

    assert progression.stage_completed is True
    assert progression.winner_club_id == 1
    assert progression.advanced_club_ids == (1,)
    assert set(progression.eliminated_club_ids) == {2, 3, 4}
    # Invariant: advanced ∩ eliminated = empty
    assert set(progression.advanced_club_ids).isdisjoint(set(progression.eliminated_club_ids))


def test_round_robin_progression_qualification_slots():
    participants = (
        CompetitionParticipant("season_1", 1, "seed1"),
        CompetitionParticipant("season_1", 2, "seed2"),
        CompetitionParticipant("season_1", 3, "seed3"),
        CompetitionParticipant("season_1", 4, "seed4"),
    )
    stage = CompetitionStage(
        id="stage_rr",
        competition_season_id="season_1",
        stage_type=CompetitionStageType.REGULAR_SEASON,
        stage_number=1,
        participant_club_ids=(1, 2, 3, 4),
    )
    season = CompetitionSeason(
        id="season_1",
        competition_id="comp_1",
        season_label="2025/2026",
        start_date=date(2025, 9, 1),
        end_date=date(2026, 5, 30),
        participants=participants,
        stages=(stage,),
        seed="season_seed",
    )

    fixtures = generate_round_robin_fixtures(season, stage, start_date=date(2025, 9, 1))
    match_results = [create_dummy_match_result(f, 1, 0) for f in fixtures]

    progression = evaluate_round_robin_completion(
        season, stage, fixtures, match_results, qualification_slots=2
    )

    assert progression.stage_completed is True
    assert len(progression.advanced_club_ids) == 2
    assert len(progression.eliminated_club_ids) == 2
    assert set(progression.advanced_club_ids).isdisjoint(set(progression.eliminated_club_ids))


def test_round_robin_progression_incomplete():
    participants = (
        CompetitionParticipant("season_1", 1, "seed1"),
        CompetitionParticipant("season_1", 2, "seed2"),
    )
    stage = CompetitionStage(
        id="stage_rr",
        competition_season_id="season_1",
        stage_type=CompetitionStageType.REGULAR_SEASON,
        stage_number=1,
        participant_club_ids=(1, 2),
    )
    season = CompetitionSeason(
        id="season_1",
        competition_id="comp_1",
        season_label="2025/2026",
        start_date=date(2025, 9, 1),
        end_date=date(2026, 5, 30),
        participants=participants,
        stages=(stage,),
        seed="season_seed",
    )

    fixtures = generate_round_robin_fixtures(season, stage, start_date=date(2025, 9, 1))
    # Only supply 1 result out of 2 fixtures
    match_results = [create_dummy_match_result(fixtures[0], 1, 0)]

    progression = evaluate_round_robin_completion(season, stage, fixtures, match_results)
    assert progression.stage_completed is False
    assert progression.advanced_club_ids == ()
    assert progression.eliminated_club_ids == ()


def test_round_robin_progression_rejections():
    participants = (
        CompetitionParticipant("season_1", 1, "seed1"),
        CompetitionParticipant("season_1", 2, "seed2"),
    )
    stage = CompetitionStage(
        id="stage_rr",
        competition_season_id="season_1",
        stage_type=CompetitionStageType.REGULAR_SEASON,
        stage_number=1,
        participant_club_ids=(1, 2),
    )
    season = CompetitionSeason(
        id="season_1",
        competition_id="comp_1",
        season_label="2025/2026",
        start_date=date(2025, 9, 1),
        end_date=date(2026, 5, 30),
        participants=participants,
        stages=(stage,),
        seed="season_seed",
    )
    fixtures = generate_round_robin_fixtures(season, stage, start_date=date(2025, 9, 1))

    # Duplicate match result
    res1 = create_dummy_match_result(fixtures[0], 1, 0)
    with pytest.raises(ValueError, match="Duplicate match result id"):
        evaluate_round_robin_completion(season, stage, fixtures, [res1, res1])


# --- Section 30 & 33: Single-Leg Knockout & Final Tests ---

def test_single_leg_knockout_and_final():
    participants = (
        CompetitionParticipant("season_1", 1, "seed1"),
        CompetitionParticipant("season_1", 2, "seed2"),
        CompetitionParticipant("season_1", 3, "seed3"),
        CompetitionParticipant("season_1", 4, "seed4"),
    )
    stage = CompetitionStage(
        id="stage_sf",
        competition_season_id="season_1",
        stage_type=CompetitionStageType.SEMI_FINAL,
        stage_number=1,
        participant_club_ids=(1, 2, 3, 4),
    )
    season = CompetitionSeason(
        id="season_1",
        competition_id="comp_1",
        season_label="2025/2026",
        start_date=date(2025, 9, 1),
        end_date=date(2026, 5, 30),
        participants=participants,
        stages=(stage,),
        seed="season_seed",
    )

    fixtures = generate_single_elimination_fixtures(season, stage, scheduled_date=date(2025, 10, 1))
    assert len(fixtures) == 2

    # Fixture 1: 1 vs 2 (1 wins), Fixture 2: 3 vs 4 (draw, 4 wins via penalty tiebreak)
    res1 = create_dummy_match_result(fixtures[0], 2, 1)
    res2 = create_dummy_match_result(fixtures[1], 1, 1)

    tb_map = {
        fixtures[1].id: TieBreakResult(winner_club_id=4, method="PENALTIES")
    }

    progression = evaluate_knockout_stage_progression(season, stage, fixtures, [res1, res2], tiebreaks=tb_map)

    assert progression.stage_completed is True
    assert progression.winner_club_id is None  # SEMI_FINAL has no winner
    assert progression.advanced_club_ids == (1, 4)
    assert progression.eliminated_club_ids == (2, 3)
    # Invariant: advanced_count + eliminated_count == participant_count
    assert len(progression.advanced_club_ids) + len(progression.eliminated_club_ids) == 4


def test_final_stage_progression():
    participants = (
        CompetitionParticipant("season_1", 1, "seed1"),
        CompetitionParticipant("season_1", 2, "seed2"),
    )
    stage_final = CompetitionStage(
        id="stage_final",
        competition_season_id="season_1",
        stage_type=CompetitionStageType.FINAL,
        stage_number=2,
        participant_club_ids=(1, 2),
    )
    season = CompetitionSeason(
        id="season_1",
        competition_id="comp_1",
        season_label="2025/2026",
        start_date=date(2025, 9, 1),
        end_date=date(2026, 5, 30),
        participants=participants,
        stages=(stage_final,),
        seed="season_seed",
    )

    fixtures = generate_single_elimination_fixtures(season, stage_final, scheduled_date=date(2025, 11, 1))
    res = create_dummy_match_result(fixtures[0], 2, 1)

    progression = evaluate_knockout_stage_progression(season, stage_final, fixtures, [res])

    assert progression.stage_completed is True
    assert progression.winner_club_id == 1
    assert progression.advanced_club_ids == (1,)
    assert progression.eliminated_club_ids == (2,)
    # Final Invariants
    assert len(progression.advanced_club_ids) == 1
    assert len(progression.eliminated_club_ids) == 1
    assert progression.winner_club_id == progression.advanced_club_ids[0]


# --- Section 31: Two-Leg Knockout & Aggregate Tests ---

def test_two_leg_knockout_and_aggregate():
    participants = (
        CompetitionParticipant("season_1", 1, "seed1"),
        CompetitionParticipant("season_1", 2, "seed2"),
    )
    stage = CompetitionStage(
        id="stage_two_leg",
        competition_season_id="season_1",
        stage_type=CompetitionStageType.SEMI_FINAL,
        stage_number=1,
        participant_club_ids=(1, 2),
    )
    season = CompetitionSeason(
        id="season_1",
        competition_id="comp_1",
        season_label="2025/2026",
        start_date=date(2025, 9, 1),
        end_date=date(2026, 5, 30),
        participants=participants,
        stages=(stage,),
        seed="season_seed",
    )

    fixtures = generate_two_leg_elimination_fixtures(
        season, stage, first_leg_date=date(2025, 10, 1), second_leg_date=date(2025, 10, 8)
    )
    assert len(fixtures) == 2

    # Leg 1: 1 (home) 2 - 1 (away) 2
    # Leg 2: 2 (home) 1 - 0 (away) 1
    # Aggregate for 1: 2 + 0 = 2
    # Aggregate for 2: 1 + 1 = 2 (tied 2-2)
    res1 = create_dummy_match_result(fixtures[0], 2, 1)
    res2 = create_dummy_match_result(fixtures[1], 1, 0)

    agg_1 = calculate_aggregate_score(fixtures, [res1, res2], 1)
    agg_2 = calculate_aggregate_score(fixtures, [res1, res2], 2)
    assert agg_1 == 2
    assert agg_2 == 2

    # Without tiebreak -> unresolved (None)
    resolved_no_tb = resolve_two_leg_tie(fixtures, [res1, res2], 1, 2)
    assert resolved_no_tb is None

    # With tiebreak -> winner is 1
    tb = TieBreakResult(winner_club_id=1, method="PENALTIES")
    resolved_tb = resolve_two_leg_tie(fixtures, [res1, res2], 1, 2, tiebreak=tb)
    assert resolved_tb == 1

    progression = evaluate_knockout_stage_progression(
        season, stage, fixtures, [res1, res2], tiebreaks={fixtures[1].id: tb}
    )
    assert progression.stage_completed is True
    assert progression.advanced_club_ids == (1,)
    assert progression.eliminated_club_ids == (2,)


# --- Section 32: Next Stage Construction Tests ---

def test_build_next_stage_participants():
    stage_1 = CompetitionStage(
        id="stage_1",
        competition_season_id="season_1",
        stage_type=CompetitionStageType.ROUND_OF_16,
        stage_number=1,
        participant_club_ids=(1, 2, 3, 4),
    )
    progression = ProgressionResult(
        competition_season_id="season_1",
        stage_completed=True,
        current_stage_index=0,
        advanced_club_ids=(1, 3),
        eliminated_club_ids=(2, 4),
    )

    next_stage = build_next_stage_participants(
        stage=stage_1,
        progression=progression,
        next_stage_id="stage_2",
        next_stage_number=2,
        next_stage_type=CompetitionStageType.QUARTER_FINAL,
    )

    assert next_stage.id == "stage_2"
    assert next_stage.competition_season_id == "season_1"
    assert next_stage.stage_type == CompetitionStageType.QUARTER_FINAL
    assert next_stage.stage_number == 2
    assert next_stage.participant_club_ids == (1, 3)
    assert next_stage.completed is False
    # Verify original stage unchanged
    assert stage_1.participant_club_ids == (1, 2, 3, 4)


def test_build_next_stage_invalid():
    stage_1 = CompetitionStage(
        id="stage_1",
        competition_season_id="season_1",
        stage_type=CompetitionStageType.ROUND_OF_16,
        stage_number=1,
        participant_club_ids=(1, 2),
    )
    incomplete_progression = ProgressionResult(
        competition_season_id="season_1",
        stage_completed=False,
        current_stage_index=0,
        advanced_club_ids=(),
        eliminated_club_ids=(),
    )

    with pytest.raises(ValueError, match="incomplete progression result"):
        build_next_stage_participants(
            stage=stage_1,
            progression=incomplete_progression,
            next_stage_id="stage_2",
            next_stage_number=2,
            next_stage_type=CompetitionStageType.QUARTER_FINAL,
        )

    valid_progression = ProgressionResult(
        competition_season_id="season_1",
        stage_completed=True,
        current_stage_index=0,
        advanced_club_ids=(1,),
        eliminated_club_ids=(2,),
    )
    with pytest.raises(ValueError, match="greater than current stage_number"):
        build_next_stage_participants(
            stage=stage_1,
            progression=valid_progression,
            next_stage_id="stage_2",
            next_stage_number=1,
            next_stage_type=CompetitionStageType.QUARTER_FINAL,
        )


# --- Section 35: Determinism Tests ---

def test_cross_process_determinism():
    code = """
from app.competition.domain import CompetitionParticipant, CompetitionStage, CompetitionStageType, CompetitionSeason
from app.competition.fixtures import generate_single_elimination_fixtures
from app.competition.progression import evaluate_knockout_stage_progression, ProgressionResult
from app.match.domain import MatchResult
from datetime import date

participants = (
    CompetitionParticipant("season_1", 1, "seed1"),
    CompetitionParticipant("season_1", 2, "seed2"),
)
stage = CompetitionStage("stg1", "season_1", CompetitionStageType.FINAL, 1, (1, 2))
season = CompetitionSeason("season_1", "comp1", "2025", date(2025,1,1), date(2025,12,31), participants, (stage,), "seed")
fixtures = generate_single_elimination_fixtures(season, stage, date(2025,5,1))
res = MatchResult(fixtures[0].id, 1, 2, 2, 1, 1.5, 1.0, 50.0, 50.0, 5, 4, [], [])
prog = evaluate_knockout_stage_progression(season, stage, fixtures, [res])
print(repr(prog))
"""
    cmd = [sys.executable, "-c", code]
    out1 = subprocess.check_output(cmd, env={"PYTHONPATH": "backend"}).decode().strip()
    out2 = subprocess.check_output(cmd, env={"PYTHONPATH": "backend"}).decode().strip()

    assert out1 == out2
    assert "winner_club_id=1" in out1
