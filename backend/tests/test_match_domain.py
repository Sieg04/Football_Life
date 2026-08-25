import ast
import math
import sys
import pytest

from app.match.domain import (
    CompetitionType,
    MatchContext,
    MatchEvent,
    MatchEventType,
    MatchResult,
    PlayerMatchPerformance,
    SimulationMode,
)


def test_1_valid_match_context() -> None:
    context = MatchContext(
        match_id="M-101",
        home_club_id=1,
        away_club_id=2,
        competition_type=CompetitionType.LEAGUE,
        competition_importance=75.0,
        match_importance=80.0,
        seed="FL-SEED-101",
    )
    assert context.match_id == "M-101"
    assert context.home_club_id == 1
    assert context.away_club_id == 2
    assert context.home_advantage_points == 3.0
    assert context.rivalry_factor == 1.0
    assert context.simulation_mode == SimulationMode.DETAILED


def test_2_invalid_club_ids() -> None:
    with pytest.raises(ValueError, match="home_club_id and away_club_id must be different"):
        MatchContext(
            match_id="M-102",
            home_club_id=5,
            away_club_id=5,
            competition_type=CompetitionType.LEAGUE,
            competition_importance=50.0,
            match_importance=50.0,
            seed="FL-SEED-102",
        )


def test_3_invalid_importance() -> None:
    with pytest.raises(ValueError, match="competition_importance must be between 0 and 100"):
        MatchContext(
            match_id="M-103",
            home_club_id=1,
            away_club_id=2,
            competition_type=CompetitionType.LEAGUE,
            competition_importance=150.0,
            match_importance=50.0,
            seed="FL-SEED-103",
        )

    with pytest.raises(ValueError, match="match_importance must be between 0 and 100"):
        MatchContext(
            match_id="M-103",
            home_club_id=1,
            away_club_id=2,
            competition_type=CompetitionType.LEAGUE,
            competition_importance=50.0,
            match_importance=-10.0,
            seed="FL-SEED-103",
        )


def test_4_invalid_rivalry_factor() -> None:
    with pytest.raises(ValueError, match="rivalry_factor must be non-negative"):
        MatchContext(
            match_id="M-104",
            home_club_id=1,
            away_club_id=2,
            competition_type=CompetitionType.LEAGUE,
            competition_importance=50.0,
            match_importance=50.0,
            rivalry_factor=-0.5,
            seed="FL-SEED-104",
        )


def test_5_invalid_home_advantage() -> None:
    with pytest.raises(ValueError, match="home_advantage_points must be a finite number"):
        MatchContext(
            match_id="M-105",
            home_club_id=1,
            away_club_id=2,
            competition_type=CompetitionType.LEAGUE,
            competition_importance=50.0,
            match_importance=50.0,
            home_advantage_points=float("nan"),
            seed="FL-SEED-105",
        )


def test_6_invalid_seed() -> None:
    with pytest.raises(ValueError, match="seed must be a non-empty string"):
        MatchContext(
            match_id="M-106",
            home_club_id=1,
            away_club_id=2,
            competition_type=CompetitionType.LEAGUE,
            competition_importance=50.0,
            match_importance=50.0,
            seed="   ",
        )


def test_7_fast_mode() -> None:
    context = MatchContext(
        match_id="M-107",
        home_club_id=1,
        away_club_id=2,
        competition_type=CompetitionType.DOMESTIC_CUP,
        competition_importance=60.0,
        match_importance=60.0,
        seed="FL-SEED-107",
        simulation_mode=SimulationMode.FAST,
    )
    assert context.simulation_mode == SimulationMode.FAST


def test_8_detailed_mode() -> None:
    context = MatchContext(
        match_id="M-108",
        home_club_id=1,
        away_club_id=2,
        competition_type=CompetitionType.EUROPEAN,
        competition_importance=90.0,
        match_importance=95.0,
        seed="FL-SEED-108",
        simulation_mode=SimulationMode.DETAILED,
    )
    assert context.simulation_mode == SimulationMode.DETAILED


def test_9_valid_player_match_performance() -> None:
    perf = PlayerMatchPerformance(
        player_id="P-001",
        match_id="M-101",
        starter=True,
        minutes=90,
        rating=8.2,
        goals=2,
        assists=1,
        shots=4,
        shots_on_target=3,
        key_passes=2,
        tackles=1,
        interceptions=0,
        clearances=0,
        saves=0,
        role="POACHER",
        position="ST",
        latent_influence=0.85,
    )
    assert perf.player_id == "P-001"
    assert perf.rating == 8.2
    assert perf.goals == 2


def test_10_invalid_minutes() -> None:
    with pytest.raises(ValueError, match="minutes must be between 0 and 120"):
        PlayerMatchPerformance(
            player_id="P-001",
            match_id="M-101",
            starter=True,
            minutes=130,
            rating=6.5,
            goals=0,
            assists=0,
            shots=0,
            shots_on_target=0,
            key_passes=0,
            tackles=0,
            interceptions=0,
            clearances=0,
            saves=0,
            role="ST",
            position="ST",
            latent_influence=0.5,
        )


def test_11_invalid_rating() -> None:
    with pytest.raises(ValueError, match="rating must be between 1.0 and 10.0"):
        PlayerMatchPerformance(
            player_id="P-001",
            match_id="M-101",
            starter=True,
            minutes=90,
            rating=10.5,
            goals=0,
            assists=0,
            shots=0,
            shots_on_target=0,
            key_passes=0,
            tackles=0,
            interceptions=0,
            clearances=0,
            saves=0,
            role="ST",
            position="ST",
            latent_influence=0.5,
        )


def test_12_negative_statistics() -> None:
    with pytest.raises(ValueError, match="tackles must be non-negative"):
        PlayerMatchPerformance(
            player_id="P-001",
            match_id="M-101",
            starter=True,
            minutes=90,
            rating=6.0,
            goals=0,
            assists=0,
            shots=0,
            shots_on_target=0,
            key_passes=0,
            tackles=-1,
            interceptions=0,
            clearances=0,
            saves=0,
            role="CM",
            position="CM",
            latent_influence=0.5,
        )


def test_13_shots_on_target_exceeds_shots() -> None:
    with pytest.raises(ValueError, match="shots_on_target cannot exceed total shots"):
        PlayerMatchPerformance(
            player_id="P-001",
            match_id="M-101",
            starter=True,
            minutes=90,
            rating=6.0,
            goals=0,
            assists=0,
            shots=2,
            shots_on_target=4,
            key_passes=0,
            tackles=0,
            interceptions=0,
            clearances=0,
            saves=0,
            role="ST",
            position="ST",
            latent_influence=0.5,
        )


def test_14_goals_exceeds_shots_on_target() -> None:
    with pytest.raises(ValueError, match="goals cannot exceed shots_on_target"):
        PlayerMatchPerformance(
            player_id="P-001",
            match_id="M-101",
            starter=True,
            minutes=90,
            rating=8.0,
            goals=3,
            assists=0,
            shots=5,
            shots_on_target=2,
            key_passes=0,
            tackles=0,
            interceptions=0,
            clearances=0,
            saves=0,
            role="ST",
            position="ST",
            latent_influence=0.5,
        )


def test_15_valid_match_event() -> None:
    event = MatchEvent(
        minute=45,
        event_type=MatchEventType.GOAL,
        primary_player_id="P-001",
        secondary_player_id="P-002",
        metadata={"distance": 18},
    )
    assert event.minute == 45
    assert event.event_type == MatchEventType.GOAL
    assert event.secondary_player_id == "P-002"


def test_16_invalid_match_event_minute() -> None:
    with pytest.raises(ValueError, match="minute must be between 0 and 120"):
        MatchEvent(
            minute=125,
            event_type=MatchEventType.YELLOW_CARD,
            primary_player_id="P-001",
        )


def test_17_valid_match_result() -> None:
    perf1 = PlayerMatchPerformance(
        player_id="P-001",
        match_id="M-101",
        starter=True,
        minutes=90,
        rating=8.0,
        goals=2,
        assists=0,
        shots=4,
        shots_on_target=3,
        key_passes=1,
        tackles=0,
        interceptions=0,
        clearances=0,
        saves=0,
        role="ST",
        position="ST",
        latent_influence=0.8,
    )
    event1 = MatchEvent(minute=23, event_type=MatchEventType.GOAL, primary_player_id="P-001")

    result = MatchResult(
        match_id="M-101",
        home_club_id=1,
        away_club_id=2,
        home_score=2,
        away_score=1,
        home_xg=2.1,
        away_xg=0.9,
        home_possession=55.0,
        away_possession=45.0,
        home_shots=12,
        away_shots=8,
        player_performances=[perf1],
        events=[event1],
    )
    assert result.match_id == "M-101"
    assert result.home_score == 2
    assert len(result.player_performances) == 1


def test_18_match_result_invalid_club_ids() -> None:
    with pytest.raises(ValueError, match="home_club_id and away_club_id must be different"):
        MatchResult(
            match_id="M-101",
            home_club_id=1,
            away_club_id=1,
            home_score=0,
            away_score=0,
            home_xg=0.5,
            away_xg=0.5,
            home_possession=50.0,
            away_possession=50.0,
            home_shots=5,
            away_shots=5,
            player_performances=[],
            events=[],
        )


def test_19_match_result_invalid_possession() -> None:
    with pytest.raises(ValueError, match="possession values must be between 0 and 100"):
        MatchResult(
            match_id="M-101",
            home_club_id=1,
            away_club_id=2,
            home_score=0,
            away_score=0,
            home_xg=0.5,
            away_xg=0.5,
            home_possession=105.0,
            away_possession=-5.0,
            home_shots=5,
            away_shots=5,
            player_performances=[],
            events=[],
        )


def test_20_invalid_possession_sum() -> None:
    with pytest.raises(ValueError, match="home_possession and away_possession must sum to approximately 100%"):
        MatchResult(
            match_id="M-101",
            home_club_id=1,
            away_club_id=2,
            home_score=0,
            away_score=0,
            home_xg=0.5,
            away_xg=0.5,
            home_possession=60.0,
            away_possession=30.0,
            home_shots=5,
            away_shots=5,
            player_performances=[],
            events=[],
        )


def test_21_score_exceeds_shots() -> None:
    with pytest.raises(ValueError, match="home_score cannot exceed home_shots"):
        MatchResult(
            match_id="M-101",
            home_club_id=1,
            away_club_id=2,
            home_score=4,
            away_score=0,
            home_xg=3.5,
            away_xg=0.5,
            home_possession=50.0,
            away_possession=50.0,
            home_shots=2,
            away_shots=5,
            player_performances=[],
            events=[],
        )


def test_22_performance_match_id_mismatch() -> None:
    perf1 = PlayerMatchPerformance(
        player_id="P-001",
        match_id="M-999",
        starter=True,
        minutes=90,
        rating=7.0,
        goals=0,
        assists=0,
        shots=1,
        shots_on_target=1,
        key_passes=0,
        tackles=0,
        interceptions=0,
        clearances=0,
        saves=0,
        role="ST",
        position="ST",
        latent_influence=0.5,
    )
    with pytest.raises(ValueError, match="PlayerMatchPerformance match_id 'M-999' does not match MatchResult match_id 'M-101'"):
        MatchResult(
            match_id="M-101",
            home_club_id=1,
            away_club_id=2,
            home_score=0,
            away_score=0,
            home_xg=0.5,
            away_xg=0.5,
            home_possession=50.0,
            away_possession=50.0,
            home_shots=5,
            away_shots=5,
            player_performances=[perf1],
            events=[],
        )


def test_23_duplicate_player_performance_ids() -> None:
    perf1 = PlayerMatchPerformance(
        player_id="P-001",
        match_id="M-101",
        starter=True,
        minutes=90,
        rating=7.0,
        goals=0,
        assists=0,
        shots=1,
        shots_on_target=1,
        key_passes=0,
        tackles=0,
        interceptions=0,
        clearances=0,
        saves=0,
        role="ST",
        position="ST",
        latent_influence=0.5,
    )
    perf2 = PlayerMatchPerformance(
        player_id="P-001",
        match_id="M-101",
        starter=False,
        minutes=20,
        rating=6.0,
        goals=0,
        assists=0,
        shots=0,
        shots_on_target=0,
        key_passes=0,
        tackles=0,
        interceptions=0,
        clearances=0,
        saves=0,
        role="ST",
        position="ST",
        latent_influence=0.4,
    )
    with pytest.raises(ValueError, match="Duplicate player performance record for player_id 'P-001'"):
        MatchResult(
            match_id="M-101",
            home_club_id=1,
            away_club_id=2,
            home_score=0,
            away_score=0,
            home_xg=0.5,
            away_xg=0.5,
            home_possession=50.0,
            away_possession=50.0,
            home_shots=5,
            away_shots=5,
            player_performances=[perf1, perf2],
            events=[],
        )


def test_24_enum_values() -> None:
    assert SimulationMode.FAST.value == "FAST"
    assert SimulationMode.DETAILED.value == "DETAILED"
    assert CompetitionType.LEAGUE.value == "LEAGUE"
    assert CompetitionType.DOMESTIC_CUP.value == "DOMESTIC_CUP"
    assert CompetitionType.EUROPEAN.value == "EUROPEAN"
    assert CompetitionType.INTERNATIONAL.value == "INTERNATIONAL"
    assert MatchEventType.GOAL.value == "GOAL"
    assert MatchEventType.MISSED_CHANCE.value == "MISSED_CHANCE"


def test_25_dataclass_equality() -> None:
    context1 = MatchContext(
        match_id="M-100",
        home_club_id=10,
        away_club_id=20,
        competition_type=CompetitionType.LEAGUE,
        competition_importance=50.0,
        match_importance=50.0,
        seed="FL-SEED-100",
    )
    context2 = MatchContext(
        match_id="M-100",
        home_club_id=10,
        away_club_id=20,
        competition_type=CompetitionType.LEAGUE,
        competition_importance=50.0,
        match_importance=50.0,
        seed="FL-SEED-100",
    )
    assert context1 == context2


def test_26_zero_infrastructure_imports() -> None:
    from pathlib import Path
    domain_path = Path(__file__).resolve().parents[1] / "app" / "match" / "domain.py"
    tree = ast.parse(domain_path.read_text(encoding="utf-8"))

    forbidden = {"fastapi", "sqlalchemy", "sqlite3", "httpx", "starlette", "requests", "alembic"}
    imported_modules = set()

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imported_modules.add(alias.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                imported_modules.add(node.module.split(".")[0])

    forbidden_found = imported_modules.intersection(forbidden)
    assert not forbidden_found, f"Found infrastructure imports in match domain: {forbidden_found}"
