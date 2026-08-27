import ast
from dataclasses import FrozenInstanceError
from datetime import date
import subprocess
import sys
from typing import Any
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
from app.competition.fixtures import Fixture, FixtureStatus
from app.competition.orchestrator import (
    FixtureExecutionResult,
    FixtureExecutor,
    OrchestrationContext,
    SeasonSimulationConfig,
    SeasonSimulationResult,
    simulate_competition_season,
)


def create_sample_competition(
    comp_id: str = "comp_1",
    name: str = "Premier League",
    competition_type: CompetitionType = CompetitionType.LEAGUE,
    importance: float = 80.0,
    level: int = 1,
    format: CompetitionFormat = CompetitionFormat.ROUND_ROBIN,
    participant_count: int = 4,
) -> Competition:
    return Competition(
        id=comp_id,
        name=name,
        competition_type=competition_type,
        country_id=1,
        importance=importance,
        level=level,
        format=format,
        participant_count=participant_count,
    )


def create_sample_season(
    season_id: str = "season_2025",
    comp_id: str = "comp_1",
    start_date: date = date(2025, 8, 1),
    end_date: date = date(2026, 5, 30),
    club_ids: tuple[int, ...] = (101, 102, 103, 104),
    seed: str = "season_seed_123",
) -> CompetitionSeason:
    participants = tuple(
        CompetitionParticipant(
            competition_season_id=season_id,
            club_id=cid,
            seed=f"{seed}_part_{cid}",
        )
        for cid in club_ids
    )
    stage = CompetitionStage(
        id="stage_regular",
        competition_season_id=season_id,
        stage_type=CompetitionStageType.REGULAR_SEASON,
        stage_number=1,
        participant_club_ids=club_ids,
        completed=False,
    )
    return CompetitionSeason(
        id=season_id,
        competition_id=comp_id,
        season_label="2025/2026",
        start_date=start_date,
        end_date=end_date,
        participants=participants,
        stages=(stage,),
        seed=seed,
        status=CompetitionSeasonStatus.ACTIVE,
    )


def create_sample_fixture(
    fixture_id: str = "fix_1",
    season_id: str = "season_2025",
    stage_id: str = "stage_regular",
    round_number: int = 1,
    scheduled_date: date = date(2025, 8, 10),
    home_club_id: int = 101,
    away_club_id: int = 102,
    importance: float = 50.0,
    seed: str = "fix_seed_1",
) -> Fixture:
    return Fixture(
        id=fixture_id,
        competition_season_id=season_id,
        stage_id=stage_id,
        round_number=round_number,
        scheduled_date=scheduled_date,
        home_club_id=home_club_id,
        away_club_id=away_club_id,
        importance=importance,
        rivalry_factor=1.0,
        seed=seed,
        status=FixtureStatus.SCHEDULED,
    )


# --- 1. SeasonSimulationConfig Tests ---

def test_config_valid_creation():
    config = SeasonSimulationConfig(
        start_date=date(2025, 8, 1),
        end_date=date(2026, 5, 30),
        seed="sim_seed_123",
    )
    assert config.start_date == date(2025, 8, 1)
    assert config.end_date == date(2026, 5, 30)
    assert config.seed == "sim_seed_123"


def test_config_invalid_date_range():
    with pytest.raises(ValueError, match="start_date must be <= end_date"):
        SeasonSimulationConfig(
            start_date=date(2026, 6, 1),
            end_date=date(2025, 8, 1),
            seed="sim_seed",
        )


def test_config_empty_seed():
    with pytest.raises(ValueError, match="seed must be a non-empty string"):
        SeasonSimulationConfig(
            start_date=date(2025, 8, 1),
            end_date=date(2026, 5, 30),
            seed="   ",
        )


def test_config_immutability():
    config = SeasonSimulationConfig(
        start_date=date(2025, 8, 1),
        end_date=date(2026, 5, 30),
        seed="sim_seed",
    )
    with pytest.raises(FrozenInstanceError):
        config.seed = "new_seed"  # type: ignore


# --- 2. FixtureExecutionResult Tests ---

def test_fixture_execution_result_valid():
    res = FixtureExecutionResult(fixture_id="fix_100", completed=True)
    assert res.fixture_id == "fix_100"
    assert res.completed is True


def test_fixture_execution_result_empty_id():
    with pytest.raises(ValueError, match="fixture_id must be a non-empty string"):
        FixtureExecutionResult(fixture_id="", completed=True)


def test_fixture_execution_result_immutability():
    res = FixtureExecutionResult(fixture_id="fix_1", completed=True)
    with pytest.raises(FrozenInstanceError):
        res.completed = False  # type: ignore


# --- 3. OrchestrationContext Tests ---

def test_orchestration_context_creation():
    comp = create_sample_competition()
    season = create_sample_season()
    config = SeasonSimulationConfig(date(2025, 8, 1), date(2026, 5, 30), "seed")
    ctx = OrchestrationContext(competition_season=season, competition=comp, config=config)
    assert ctx.competition_season == season
    assert ctx.competition == comp
    assert ctx.config == config


def test_orchestration_context_immutability():
    comp = create_sample_competition()
    season = create_sample_season()
    config = SeasonSimulationConfig(date(2025, 8, 1), date(2026, 5, 30), "seed")
    ctx = OrchestrationContext(competition_season=season, competition=comp, config=config)
    with pytest.raises(FrozenInstanceError):
        ctx.competition = comp  # type: ignore


# --- 4. SeasonSimulationResult Tests ---

def test_season_simulation_result_valid():
    r1 = FixtureExecutionResult("f1", True)
    r2 = FixtureExecutionResult("f2", True)
    res = SeasonSimulationResult(
        competition_season_id="s1",
        completed=True,
        fixtures_processed=2,
        fixtures_completed=2,
        final_date=date(2025, 8, 20),
        execution_results=(r1, r2),
    )
    assert res.competition_season_id == "s1"
    assert res.completed is True
    assert res.fixtures_processed == 2
    assert res.fixtures_completed == 2
    assert res.final_date == date(2025, 8, 20)
    assert len(res.execution_results) == 2


def test_season_simulation_result_invalid_season_id():
    with pytest.raises(ValueError, match="competition_season_id must be a non-empty string"):
        SeasonSimulationResult(
            competition_season_id="",
            completed=False,
            fixtures_processed=0,
            fixtures_completed=0,
            final_date=None,
            execution_results=(),
        )


def test_season_simulation_result_negative_counters():
    with pytest.raises(ValueError, match="fixtures_processed must be >= 0"):
        SeasonSimulationResult(
            competition_season_id="s1",
            completed=False,
            fixtures_processed=-1,
            fixtures_completed=0,
            final_date=None,
            execution_results=(),
        )


def test_season_simulation_result_completed_exceeds_processed():
    with pytest.raises(ValueError, match="fixtures_completed cannot exceed fixtures_processed"):
        SeasonSimulationResult(
            competition_season_id="s1",
            completed=False,
            fixtures_processed=1,
            fixtures_completed=2,
            final_date=None,
            execution_results=(FixtureExecutionResult("f1", True),),
        )


def test_season_simulation_result_length_mismatch():
    with pytest.raises(ValueError, match="len\\(execution_results\\) must equal fixtures_processed"):
        SeasonSimulationResult(
            competition_season_id="s1",
            completed=False,
            fixtures_processed=2,
            fixtures_completed=1,
            final_date=None,
            execution_results=(FixtureExecutionResult("f1", True),),
        )


def test_season_simulation_result_immutability():
    res = SeasonSimulationResult(
        competition_season_id="s1",
        completed=True,
        fixtures_processed=0,
        fixtures_completed=0,
        final_date=None,
        execution_results=(),
    )
    with pytest.raises(FrozenInstanceError):
        res.completed = False  # type: ignore


# --- 5. Main Orchestrator Tests ---

def test_orchestrator_executes_all_fixtures_trace():
    comp = create_sample_competition()
    season = create_sample_season()
    config = SeasonSimulationConfig(date(2025, 8, 1), date(2026, 5, 30), "seed123")

    f1 = create_sample_fixture("f1", scheduled_date=date(2025, 8, 10))
    f2 = create_sample_fixture("f2", scheduled_date=date(2025, 8, 17), home_club_id=103, away_club_id=104)

    executed_ids = []

    def dummy_executor(fixture: Fixture, ctx: OrchestrationContext) -> FixtureExecutionResult:
        executed_ids.append(fixture.id)
        assert ctx.competition == comp
        assert ctx.competition_season == season
        assert ctx.config == config
        return FixtureExecutionResult(fixture_id=fixture.id, completed=True)

    res = simulate_competition_season(
        competition_season=season,
        competition=comp,
        fixtures=[f1, f2],
        config=config,
        fixture_executor=dummy_executor,
    )

    assert executed_ids == ["f1", "f2"]
    assert res.completed is True
    assert res.fixtures_processed == 2
    assert res.fixtures_completed == 2
    assert res.final_date == date(2025, 8, 17)


def test_orchestrator_deterministic_sorting():
    comp = create_sample_competition()
    season = create_sample_season()
    config = SeasonSimulationConfig(date(2025, 8, 1), date(2026, 5, 30), "seed123")

    # Fixtures provided out of order
    f3 = create_sample_fixture("f3", round_number=2, scheduled_date=date(2025, 8, 20), home_club_id=101, away_club_id=103)
    f1 = create_sample_fixture("f1", round_number=1, scheduled_date=date(2025, 8, 10), home_club_id=101, away_club_id=102)
    f2 = create_sample_fixture("f2", round_number=1, scheduled_date=date(2025, 8, 10), home_club_id=103, away_club_id=104)

    executed_ids = []

    def dummy_executor(fixture: Fixture, ctx: OrchestrationContext) -> FixtureExecutionResult:
        executed_ids.append(fixture.id)
        return FixtureExecutionResult(fixture_id=fixture.id, completed=True)

    simulate_competition_season(
        competition_season=season,
        competition=comp,
        fixtures=[f3, f1, f2],
        config=config,
        fixture_executor=dummy_executor,
    )

    assert executed_ids == ["f1", "f2", "f3"]


def test_orchestrator_incomplete_fixture():
    comp = create_sample_competition()
    season = create_sample_season()
    config = SeasonSimulationConfig(date(2025, 8, 1), date(2026, 5, 30), "seed123")

    f1 = create_sample_fixture("f1", scheduled_date=date(2025, 8, 10))
    f2 = create_sample_fixture("f2", scheduled_date=date(2025, 8, 17), home_club_id=103, away_club_id=104)

    def dummy_executor(fixture: Fixture, ctx: OrchestrationContext) -> FixtureExecutionResult:
        is_completed = (fixture.id == "f1")
        return FixtureExecutionResult(fixture_id=fixture.id, completed=is_completed)

    res = simulate_competition_season(
        competition_season=season,
        competition=comp,
        fixtures=[f1, f2],
        config=config,
        fixture_executor=dummy_executor,
    )

    assert res.completed is False
    assert res.fixtures_processed == 2
    assert res.fixtures_completed == 1
    assert res.final_date == date(2025, 8, 17)


def test_orchestrator_empty_fixtures():
    comp = create_sample_competition()
    season = create_sample_season()
    config = SeasonSimulationConfig(date(2025, 8, 1), date(2026, 5, 30), "seed123")

    def dummy_executor(fixture: Fixture, ctx: OrchestrationContext) -> FixtureExecutionResult:
        return FixtureExecutionResult(fixture_id=fixture.id, completed=True)

    res = simulate_competition_season(
        competition_season=season,
        competition=comp,
        fixtures=[],
        config=config,
        fixture_executor=dummy_executor,
    )

    assert res.completed is True
    assert res.fixtures_processed == 0
    assert res.fixtures_completed == 0
    assert res.final_date is None
    assert res.execution_results == ()


def test_orchestrator_duplicate_fixture_ids():
    comp = create_sample_competition()
    season = create_sample_season()
    config = SeasonSimulationConfig(date(2025, 8, 1), date(2026, 5, 30), "seed123")

    f1 = create_sample_fixture("f1")
    f1_dup = create_sample_fixture("f1", home_club_id=103, away_club_id=104)

    def dummy_executor(fixture: Fixture, ctx: OrchestrationContext) -> FixtureExecutionResult:
        return FixtureExecutionResult(fixture_id=fixture.id, completed=True)

    with pytest.raises(ValueError, match="Duplicate fixture id 'f1'"):
        simulate_competition_season(
            competition_season=season,
            competition=comp,
            fixtures=[f1, f1_dup],
            config=config,
            fixture_executor=dummy_executor,
        )


def test_orchestrator_wrong_season_fixture():
    comp = create_sample_competition()
    season = create_sample_season()
    config = SeasonSimulationConfig(date(2025, 8, 1), date(2026, 5, 30), "seed123")

    f1 = create_sample_fixture("f1", season_id="wrong_season")

    def dummy_executor(fixture: Fixture, ctx: OrchestrationContext) -> FixtureExecutionResult:
        return FixtureExecutionResult(fixture_id=fixture.id, completed=True)

    with pytest.raises(ValueError, match="fixture competition_season_id 'wrong_season' does not match season id"):
        simulate_competition_season(
            competition_season=season,
            competition=comp,
            fixtures=[f1],
            config=config,
            fixture_executor=dummy_executor,
        )


def test_orchestrator_fixture_outside_date_window():
    comp = create_sample_competition()
    season = create_sample_season()
    config = SeasonSimulationConfig(date(2025, 8, 1), date(2026, 5, 30), "seed123")

    f1 = create_sample_fixture("f1", scheduled_date=date(2025, 7, 31))  # before start_date

    def dummy_executor(fixture: Fixture, ctx: OrchestrationContext) -> FixtureExecutionResult:
        return FixtureExecutionResult(fixture_id=fixture.id, completed=True)

    with pytest.raises(ValueError, match="outside simulation window"):
        simulate_competition_season(
            competition_season=season,
            competition=comp,
            fixtures=[f1],
            config=config,
            fixture_executor=dummy_executor,
        )


def test_orchestrator_competition_season_mismatch():
    comp = create_sample_competition(comp_id="comp_1")
    season = create_sample_season(comp_id="comp_2")
    config = SeasonSimulationConfig(date(2025, 8, 1), date(2026, 5, 30), "seed123")

    def dummy_executor(fixture: Fixture, ctx: OrchestrationContext) -> FixtureExecutionResult:
        return FixtureExecutionResult(fixture_id=fixture.id, completed=True)

    with pytest.raises(ValueError, match="does not match competition.id"):
        simulate_competition_season(
            competition_season=season,
            competition=comp,
            fixtures=[],
            config=config,
            fixture_executor=dummy_executor,
        )


def test_orchestrator_executor_failure_propagation():
    comp = create_sample_competition()
    season = create_sample_season()
    config = SeasonSimulationConfig(date(2025, 8, 1), date(2026, 5, 30), "seed123")

    f1 = create_sample_fixture("f1", scheduled_date=date(2025, 8, 10))
    f2 = create_sample_fixture("f2", scheduled_date=date(2025, 8, 17), home_club_id=103, away_club_id=104)

    executed = []

    def failing_executor(fixture: Fixture, ctx: OrchestrationContext) -> FixtureExecutionResult:
        executed.append(fixture.id)
        if fixture.id == "f1":
            raise RuntimeError("Simulation error on f1")
        return FixtureExecutionResult(fixture_id=fixture.id, completed=True)

    with pytest.raises(RuntimeError, match="Simulation error on f1"):
        simulate_competition_season(
            competition_season=season,
            competition=comp,
            fixtures=[f1, f2],
            config=config,
            fixture_executor=failing_executor,
        )

    # Verify processing stopped immediately
    assert executed == ["f1"]


def test_orchestrator_executor_invalid_return_type():
    comp = create_sample_competition()
    season = create_sample_season()
    config = SeasonSimulationConfig(date(2025, 8, 1), date(2026, 5, 30), "seed123")

    f1 = create_sample_fixture("f1")

    def bad_type_executor(fixture: Fixture, ctx: OrchestrationContext) -> Any:
        return {"fixture_id": "f1", "completed": True}  # dict instead of FixtureExecutionResult

    with pytest.raises(TypeError, match="expected FixtureExecutionResult"):
        simulate_competition_season(
            competition_season=season,
            competition=comp,
            fixtures=[f1],
            config=config,
            fixture_executor=bad_type_executor,
        )


def test_orchestrator_executor_mismatched_fixture_id():
    comp = create_sample_competition()
    season = create_sample_season()
    config = SeasonSimulationConfig(date(2025, 8, 1), date(2026, 5, 30), "seed123")

    f1 = create_sample_fixture("f1")

    def mismatched_id_executor(fixture: Fixture, ctx: OrchestrationContext) -> FixtureExecutionResult:
        return FixtureExecutionResult(fixture_id="wrong_id", completed=True)

    with pytest.raises(ValueError, match="returned result with fixture_id 'wrong_id', expected 'f1'"):
        simulate_competition_season(
            competition_season=season,
            competition=comp,
            fixtures=[f1],
            config=config,
            fixture_executor=mismatched_id_executor,
        )


def test_orchestrator_input_immutability():
    comp = create_sample_competition()
    season = create_sample_season()
    config = SeasonSimulationConfig(date(2025, 8, 1), date(2026, 5, 30), "seed123")

    f1 = create_sample_fixture("f1", scheduled_date=date(2025, 8, 10))
    f2 = create_sample_fixture("f2", scheduled_date=date(2025, 8, 17), home_club_id=103, away_club_id=104)

    fixtures = [f1, f2]
    fixtures_copy = list(fixtures)

    def dummy_executor(fixture: Fixture, ctx: OrchestrationContext) -> FixtureExecutionResult:
        return FixtureExecutionResult(fixture_id=fixture.id, completed=True)

    simulate_competition_season(
        competition_season=season,
        competition=comp,
        fixtures=fixtures,
        config=config,
        fixture_executor=dummy_executor,
    )

    assert fixtures == fixtures_copy
    assert f1.scheduled_date == date(2025, 8, 10)


def test_orchestrator_input_order_independence():
    comp = create_sample_competition()
    season = create_sample_season()
    config = SeasonSimulationConfig(date(2025, 8, 1), date(2026, 5, 30), "seed123")

    f1 = create_sample_fixture("f1", scheduled_date=date(2025, 8, 10))
    f2 = create_sample_fixture("f2", scheduled_date=date(2025, 8, 17), home_club_id=103, away_club_id=104)
    f3 = create_sample_fixture("f3", scheduled_date=date(2025, 8, 24), home_club_id=101, away_club_id=104)

    def dummy_executor(fixture: Fixture, ctx: OrchestrationContext) -> FixtureExecutionResult:
        return FixtureExecutionResult(fixture_id=fixture.id, completed=True)

    res1 = simulate_competition_season(season, comp, [f1, f2, f3], config, dummy_executor)
    res2 = simulate_competition_season(season, comp, [f3, f1, f2], config, dummy_executor)
    res3 = simulate_competition_season(season, comp, [f2, f3, f1], config, dummy_executor)

    assert res1 == res2 == res3


def test_orchestrator_cross_process_determinism():
    script = """
from datetime import date
from app.competition.domain import Competition, CompetitionSeason, CompetitionParticipant, CompetitionStage, CompetitionStageType, CompetitionType, CompetitionFormat, CompetitionSeasonStatus
from app.competition.fixtures import Fixture, FixtureStatus
from app.competition.orchestrator import SeasonSimulationConfig, FixtureExecutionResult, OrchestrationContext, simulate_competition_season

comp = Competition(id="comp_1", name="League", competition_type=CompetitionType.LEAGUE, country_id=1, importance=80.0, level=1, format=CompetitionFormat.ROUND_ROBIN, participant_count=2)
parts = (CompetitionParticipant("s1", 1, "seed1"), CompetitionParticipant("s1", 2, "seed2"))
stage = CompetitionStage("st1", "s1", CompetitionStageType.REGULAR_SEASON, 1, (1, 2))
season = CompetitionSeason("s1", "comp_1", "2025", date(2025, 8, 1), date(2026, 5, 30), parts, (stage,), "season_seed", CompetitionSeasonStatus.ACTIVE)

f1 = Fixture("f1", "s1", "st1", 1, date(2025, 8, 10), 1, 2, 50.0, 1.0, "seed_f1", FixtureStatus.SCHEDULED)
config = SeasonSimulationConfig(date(2025, 8, 1), date(2026, 5, 30), "sim_seed")

def exec_cb(fixture, ctx):
    return FixtureExecutionResult(fixture.id, True)

res = simulate_competition_season(season, comp, [f1], config, exec_cb)
print(f"{res.competition_season_id}:{res.completed}:{res.fixtures_processed}:{res.fixtures_completed}:{res.final_date}:{res.execution_results}")
"""

    cmd = [sys.executable, "-c", script]
    out1 = subprocess.check_output(cmd, env={"PYTHONPATH": "backend"}).decode("utf-8").strip()
    out2 = subprocess.check_output(cmd, env={"PYTHONPATH": "backend"}).decode("utf-8").strip()

    assert out1 == out2
    assert "s1:True:1:1:2025-08-10:(FixtureExecutionResult(fixture_id='f1', completed=True),)" in out1


def test_structural_ast_import_audit():
    with open("backend/app/competition/orchestrator.py", "r", encoding="utf-8") as f:
        tree = ast.parse(f.read(), filename="orchestrator.py")

    imported_modules = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imported_modules.add(alias.name)
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                imported_modules.add(node.module)

    forbidden_patterns = [
        "fastapi",
        "starlette",
        "sqlalchemy",
        "sqlite3",
        "alembic",
        "httpx",
        "app.match",
        "app.career",
        "app.player",
        "random",
        "uuid",
    ]

    for imp in imported_modules:
        for forbidden in forbidden_patterns:
            assert not imp.startswith(forbidden), f"Forbidden import '{imp}' found in orchestrator.py"
