import ast
from datetime import date
from dataclasses import FrozenInstanceError
import pytest

from app.competition.domain import (
    Competition,
    CompetitionFormat,
    CompetitionParticipant,
    CompetitionSeason,
    CompetitionSeasonStatus,
    CompetitionStage,
    CompetitionStageType,
    CompetitionType,
)


def test_enum_string_values() -> None:
    assert CompetitionType.LEAGUE == "LEAGUE"
    assert CompetitionType.DOMESTIC_CUP == "DOMESTIC_CUP"
    assert CompetitionType.EUROPEAN == "EUROPEAN"
    assert CompetitionType.INTERNATIONAL == "INTERNATIONAL"

    assert CompetitionFormat.ROUND_ROBIN == "ROUND_ROBIN"
    assert CompetitionFormat.SINGLE_ELIMINATION == "SINGLE_ELIMINATION"
    assert CompetitionFormat.TWO_LEG_ELIMINATION == "TWO_LEG_ELIMINATION"
    assert CompetitionFormat.LEAGUE_PHASE == "LEAGUE_PHASE"

    assert CompetitionStageType.REGULAR_SEASON == "REGULAR_SEASON"
    assert CompetitionStageType.GROUP_STAGE == "GROUP_STAGE"
    assert CompetitionStageType.LEAGUE_PHASE == "LEAGUE_PHASE"
    assert CompetitionStageType.ROUND_OF_32 == "ROUND_OF_32"
    assert CompetitionStageType.ROUND_OF_16 == "ROUND_OF_16"
    assert CompetitionStageType.QUARTER_FINAL == "QUARTER_FINAL"
    assert CompetitionStageType.SEMI_FINAL == "SEMI_FINAL"
    assert CompetitionStageType.FINAL == "FINAL"

    assert CompetitionSeasonStatus.NOT_STARTED == "NOT_STARTED"
    assert CompetitionSeasonStatus.ACTIVE == "ACTIVE"
    assert CompetitionSeasonStatus.COMPLETED == "COMPLETED"


def test_competition_valid_creation() -> None:
    comp = Competition(
        id="comp_1",
        name="Premier League",
        competition_type=CompetitionType.LEAGUE,
        country_id=1,
        importance=95.0,
        level=1,
        format=CompetitionFormat.ROUND_ROBIN,
        participant_count=20,
        rules={"subs": 5},
    )
    assert comp.id == "comp_1"
    assert comp.name == "Premier League"
    assert comp.competition_type == CompetitionType.LEAGUE
    assert comp.country_id == 1
    assert comp.importance == 95.0
    assert comp.level == 1
    assert comp.format == CompetitionFormat.ROUND_ROBIN
    assert comp.participant_count == 20
    assert comp.rules["subs"] == 5


def test_competition_invalid_id() -> None:
    with pytest.raises(ValueError, match="id must be a non-empty string"):
        Competition(
            id="   ",
            name="League",
            competition_type=CompetitionType.LEAGUE,
            country_id=1,
            importance=50.0,
            level=1,
            format=CompetitionFormat.ROUND_ROBIN,
            participant_count=10,
        )


def test_competition_invalid_name() -> None:
    with pytest.raises(ValueError, match="name must be a non-empty string"):
        Competition(
            id="comp_1",
            name="",
            competition_type=CompetitionType.LEAGUE,
            country_id=1,
            importance=50.0,
            level=1,
            format=CompetitionFormat.ROUND_ROBIN,
            participant_count=10,
        )


def test_competition_invalid_importance() -> None:
    with pytest.raises(ValueError, match="importance must be between"):
        Competition(
            id="comp_1",
            name="League",
            competition_type=CompetitionType.LEAGUE,
            country_id=1,
            importance=-1.0,
            level=1,
            format=CompetitionFormat.ROUND_ROBIN,
            participant_count=10,
        )

    with pytest.raises(ValueError, match="importance must be between"):
        Competition(
            id="comp_1",
            name="League",
            competition_type=CompetitionType.LEAGUE,
            country_id=1,
            importance=105.0,
            level=1,
            format=CompetitionFormat.ROUND_ROBIN,
            participant_count=10,
        )


def test_competition_invalid_level() -> None:
    with pytest.raises(ValueError, match="level must be greater than 0"):
        Competition(
            id="comp_1",
            name="League",
            competition_type=CompetitionType.LEAGUE,
            country_id=1,
            importance=50.0,
            level=0,
            format=CompetitionFormat.ROUND_ROBIN,
            participant_count=10,
        )


def test_competition_invalid_participant_count() -> None:
    with pytest.raises(ValueError, match="participant_count must be at least 2"):
        Competition(
            id="comp_1",
            name="League",
            competition_type=CompetitionType.LEAGUE,
            country_id=1,
            importance=50.0,
            level=1,
            format=CompetitionFormat.ROUND_ROBIN,
            participant_count=1,
        )


def test_competition_frozen_and_rules_immutability() -> None:
    initial_rules = {"subs": 3}
    comp = Competition(
        id="comp_1",
        name="League",
        competition_type=CompetitionType.LEAGUE,
        country_id=1,
        importance=50.0,
        level=1,
        format=CompetitionFormat.ROUND_ROBIN,
        participant_count=10,
        rules=initial_rules,
    )
    with pytest.raises(FrozenInstanceError):
        comp.name = "New Name"  # type: ignore[misc]

    initial_rules["subs"] = 99
    assert comp.rules["subs"] == 3

    with pytest.raises(TypeError):
        comp.rules["subs"] = 10  # type: ignore[index]


def test_participant_valid_creation() -> None:
    part = CompetitionParticipant(
        competition_season_id="season_2025",
        club_id=101,
        seed="seed_01",
    )
    assert part.competition_season_id == "season_2025"
    assert part.club_id == 101
    assert part.seed == "seed_01"


def test_participant_invalid_inputs() -> None:
    with pytest.raises(ValueError, match="competition_season_id must be a non-empty string"):
        CompetitionParticipant(competition_season_id="", club_id=1, seed="seed_1")

    with pytest.raises(ValueError, match="club_id must be a positive integer"):
        CompetitionParticipant(competition_season_id="s1", club_id=0, seed="seed_1")

    with pytest.raises(ValueError, match="seed must be a non-empty string"):
        CompetitionParticipant(competition_season_id="s1", club_id=1, seed="   ")


def test_participant_frozen_behavior() -> None:
    part = CompetitionParticipant(competition_season_id="s1", club_id=1, seed="seed_1")
    with pytest.raises(FrozenInstanceError):
        part.club_id = 2  # type: ignore[misc]


def test_stage_valid_creation() -> None:
    stage = CompetitionStage(
        id="stage_1",
        competition_season_id="season_1",
        stage_type=CompetitionStageType.REGULAR_SEASON,
        stage_number=1,
        participant_club_ids=(10, 20, 30),
    )
    assert stage.id == "stage_1"
    assert stage.competition_season_id == "season_1"
    assert stage.stage_type == CompetitionStageType.REGULAR_SEASON
    assert stage.stage_number == 1
    assert stage.participant_club_ids == (10, 20, 30)
    assert not stage.completed


def test_stage_invalid_inputs() -> None:
    with pytest.raises(ValueError, match="id must be a non-empty string"):
        CompetitionStage(
            id="",
            competition_season_id="s1",
            stage_type=CompetitionStageType.REGULAR_SEASON,
            stage_number=1,
            participant_club_ids=(1, 2),
        )

    with pytest.raises(ValueError, match="stage_number must be >= 1"):
        CompetitionStage(
            id="st1",
            competition_season_id="s1",
            stage_type=CompetitionStageType.REGULAR_SEASON,
            stage_number=0,
            participant_club_ids=(1, 2),
        )

    with pytest.raises(ValueError, match="participant_club_ids must contain at least 2 clubs"):
        CompetitionStage(
            id="st1",
            competition_season_id="s1",
            stage_type=CompetitionStageType.REGULAR_SEASON,
            stage_number=1,
            participant_club_ids=(1,),
        )

    with pytest.raises(ValueError, match="all club_ids must be positive integers"):
        CompetitionStage(
            id="st1",
            competition_season_id="s1",
            stage_type=CompetitionStageType.REGULAR_SEASON,
            stage_number=1,
            participant_club_ids=(1, -5),
        )

    with pytest.raises(ValueError, match="duplicate club IDs"):
        CompetitionStage(
            id="st1",
            competition_season_id="s1",
            stage_type=CompetitionStageType.REGULAR_SEASON,
            stage_number=1,
            participant_club_ids=(1, 2, 1),
        )


def test_season_valid_creation() -> None:
    p1 = CompetitionParticipant(competition_season_id="s_2025", club_id=1, seed="seed_1")
    p2 = CompetitionParticipant(competition_season_id="s_2025", club_id=2, seed="seed_2")
    st1 = CompetitionStage(
        id="st_1",
        competition_season_id="s_2025",
        stage_type=CompetitionStageType.REGULAR_SEASON,
        stage_number=1,
        participant_club_ids=(1, 2),
    )
    season = CompetitionSeason(
        id="s_2025",
        competition_id="c_1",
        season_label="2025/2026",
        start_date=date(2025, 8, 1),
        end_date=date(2026, 5, 30),
        participants=(p1, p2),
        stages=(st1,),
        seed="season_seed_123",
        status=CompetitionSeasonStatus.NOT_STARTED,
        current_stage_index=0,
    )
    assert season.id == "s_2025"
    assert season.competition_id == "c_1"
    assert season.season_label == "2025/2026"
    assert season.start_date == date(2025, 8, 1)
    assert season.end_date == date(2026, 5, 30)
    assert season.seed == "season_seed_123"
    assert len(season.participants) == 2
    assert len(season.stages) == 1
    assert season.status == CompetitionSeasonStatus.NOT_STARTED
    assert season.winner_id is None
    assert season.winner_club_id is None


def test_season_invalid_dates() -> None:
    p1 = CompetitionParticipant(competition_season_id="s_1", club_id=1, seed="s1")
    p2 = CompetitionParticipant(competition_season_id="s_1", club_id=2, seed="s2")
    with pytest.raises(ValueError, match="start_date must be <= end_date"):
        CompetitionSeason(
            id="s_1",
            competition_id="c_1",
            season_label="2025",
            start_date=date(2026, 1, 1),
            end_date=date(2025, 1, 1),
            participants=(p1, p2),
            stages=(),
            seed="seed",
        )


def test_season_insufficient_participants() -> None:
    p1 = CompetitionParticipant(competition_season_id="s_1", club_id=1, seed="s1")
    with pytest.raises(ValueError, match="participants must contain at least 2 participants"):
        CompetitionSeason(
            id="s_1",
            competition_id="c_1",
            season_label="2025",
            start_date=date(2025, 1, 1),
            end_date=date(2025, 12, 31),
            participants=(p1,),
            stages=(),
            seed="seed",
        )


def test_season_duplicate_participants() -> None:
    p1 = CompetitionParticipant(competition_season_id="s_1", club_id=1, seed="s1")
    p2 = CompetitionParticipant(competition_season_id="s_1", club_id=1, seed="s2")
    with pytest.raises(ValueError, match="Duplicate participant club_id"):
        CompetitionSeason(
            id="s_1",
            competition_id="c_1",
            season_label="2025",
            start_date=date(2025, 1, 1),
            end_date=date(2025, 12, 31),
            participants=(p1, p2),
            stages=(),
            seed="seed",
        )


def test_season_participant_mismatch() -> None:
    p1 = CompetitionParticipant(competition_season_id="s_OTHER", club_id=1, seed="s1")
    p2 = CompetitionParticipant(competition_season_id="s_1", club_id=2, seed="s2")
    with pytest.raises(ValueError, match="Participant competition_season_id"):
        CompetitionSeason(
            id="s_1",
            competition_id="c_1",
            season_label="2025",
            start_date=date(2025, 1, 1),
            end_date=date(2025, 12, 31),
            participants=(p1, p2),
            stages=(),
            seed="seed",
        )


def test_season_stage_mismatch_and_duplicates() -> None:
    p1 = CompetitionParticipant(competition_season_id="s_1", club_id=1, seed="s1")
    p2 = CompetitionParticipant(competition_season_id="s_1", club_id=2, seed="s2")
    st_wrong = CompetitionStage(
        id="st1",
        competition_season_id="s_WRONG",
        stage_type=CompetitionStageType.REGULAR_SEASON,
        stage_number=1,
        participant_club_ids=(1, 2),
    )
    with pytest.raises(ValueError, match="Stage competition_season_id"):
        CompetitionSeason(
            id="s_1",
            competition_id="c_1",
            season_label="2025",
            start_date=date(2025, 1, 1),
            end_date=date(2025, 12, 31),
            participants=(p1, p2),
            stages=(st_wrong,),
            seed="seed",
        )

    st1 = CompetitionStage(
        id="st1",
        competition_season_id="s_1",
        stage_type=CompetitionStageType.REGULAR_SEASON,
        stage_number=1,
        participant_club_ids=(1, 2),
    )
    st1_dup = CompetitionStage(
        id="st1",
        competition_season_id="s_1",
        stage_type=CompetitionStageType.FINAL,
        stage_number=2,
        participant_club_ids=(1, 2),
    )
    with pytest.raises(ValueError, match="Duplicate stage id"):
        CompetitionSeason(
            id="s_1",
            competition_id="c_1",
            season_label="2025",
            start_date=date(2025, 1, 1),
            end_date=date(2025, 12, 31),
            participants=(p1, p2),
            stages=(st1, st1_dup),
            seed="seed",
        )


def test_season_completed_winner_validation() -> None:
    p1 = CompetitionParticipant(competition_season_id="s_1", club_id=10, seed="s1")
    p2 = CompetitionParticipant(competition_season_id="s_1", club_id=20, seed="s2")

    # Completed without winner
    with pytest.raises(ValueError, match="Completed competition season must have a winner_id"):
        CompetitionSeason(
            id="s_1",
            competition_id="c_1",
            season_label="2025",
            start_date=date(2025, 1, 1),
            end_date=date(2025, 12, 31),
            participants=(p1, p2),
            stages=(),
            seed="seed",
            status=CompetitionSeasonStatus.COMPLETED,
            winner_id=None,
        )

    # Completed with winner not in participants
    with pytest.raises(ValueError, match="Winner club_id '99' must belong to season participants"):
        CompetitionSeason(
            id="s_1",
            competition_id="c_1",
            season_label="2025",
            start_date=date(2025, 1, 1),
            end_date=date(2025, 12, 31),
            participants=(p1, p2),
            stages=(),
            seed="seed",
            status=CompetitionSeasonStatus.COMPLETED,
            winner_id=99,
        )

    # Completed with valid winner
    completed_season = CompetitionSeason(
        id="s_1",
        competition_id="c_1",
        season_label="2025",
        start_date=date(2025, 1, 1),
        end_date=date(2025, 12, 31),
        participants=(p1, p2),
        stages=(),
        seed="seed",
        status=CompetitionSeasonStatus.COMPLETED,
        winner_id=10,
    )
    assert completed_season.winner_id == 10
    assert completed_season.winner_club_id == 10


def test_dataclass_equality_and_determinism() -> None:
    c1 = Competition(
        id="comp_1",
        name="League A",
        competition_type=CompetitionType.LEAGUE,
        country_id=1,
        importance=80.0,
        level=1,
        format=CompetitionFormat.ROUND_ROBIN,
        participant_count=10,
        rules={"points_for_win": 3},
    )
    c2 = Competition(
        id="comp_1",
        name="League A",
        competition_type=CompetitionType.LEAGUE,
        country_id=1,
        importance=80.0,
        level=1,
        format=CompetitionFormat.ROUND_ROBIN,
        participant_count=10,
        rules={"points_for_win": 3},
    )
    assert c1 == c2

    p1 = CompetitionParticipant(competition_season_id="s1", club_id=5, seed="seed_a")
    p2 = CompetitionParticipant(competition_season_id="s1", club_id=5, seed="seed_a")
    assert p1 == p2


def test_zero_infrastructure_imports_ast() -> None:
    with open("backend/app/competition/domain.py", "r", encoding="utf-8") as f:
        tree = ast.parse(f.read(), filename="domain.py")

    forbidden = {"fastapi", "sqlalchemy", "sqlite3", "alembic", "http", "httpx", "starlette", "angular"}

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                root_pkg = alias.name.split(".")[0]
                assert root_pkg not in forbidden, f"Forbidden import found: {alias.name}"
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                root_pkg = node.module.split(".")[0]
                assert root_pkg not in forbidden, f"Forbidden import from found: {node.module}"


def test_phase_boundary_no_future_logic() -> None:
    import app.competition.domain as domain_module

    future_symbols = [
        "generate_round_robin_fixtures",
        "generate_single_elimination_fixtures",
        "generate_two_leg_elimination_fixtures",
        "apply_match_result",
        "rank_standings",
        "record_form_result",
        "evaluate_round_robin_completion",
        "resolve_two_leg_tie",
        "evaluate_knockout_stage_progression",
        "SeasonSimulationConfig",
        "SeasonSimulationResult",
        "simulate_competition_season",
    ]

    for symbol in future_symbols:
        assert not hasattr(domain_module, symbol), f"Phase boundary violation: '{symbol}' found in domain.py"
