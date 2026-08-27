import ast
from datetime import date
import json
from pathlib import Path
import subprocess
import sys
import pytest

from app.competition.domain import (
    Competition,
    CompetitionFormat,
    CompetitionParticipant,
    CompetitionSeason,
    CompetitionSeasonStatus,
    CompetitionStage,
    CompetitionStageType,
)
from app.competition.fixtures import Fixture, FixtureStatus
from app.competition.match_executor import (
    MatchFixtureExecutionResult,
    MatchSimulationParticipants,
    build_match_context,
    build_match_engine_executor,
    execute_fixture_with_match_engine,
)
from app.competition.orchestrator import (
    OrchestrationContext,
    SeasonSimulationConfig,
    simulate_competition_season,
)
from app.match.domain import CompetitionType, MatchContext, MatchResult, SimulationMode
from app.player.domain import DevelopmentProfile, Player, PlayerAttributes, PlayerState
from app.world.entities import Club, Manager


def _create_mock_manager(name: str = "Manager") -> Manager:
    return Manager(
        name=name,
        tactical_quality=80.0,
        player_development=80.0,
        game_management=80.0,
        rotation=50.0,
        adaptability=80.0,
        tactical_style="balanced",
        youth_preference=50.0,
        discipline=80.0,
    )


def _create_mock_player(player_id: str, pos: str) -> Player:
    attrs = PlayerAttributes(
        acceleration=70.0,
        sprint_speed=70.0,
        finishing=70.0,
        shot_power=70.0,
        long_shots=70.0,
        volleys=70.0,
        penalties=70.0,
        vision=70.0,
        short_passing=70.0,
        long_passing=70.0,
        crossing=70.0,
        curve=70.0,
        agility=70.0,
        balance=70.0,
        ball_control=70.0,
        dribbling=70.0,
        reactions=70.0,
        defensive_awareness=70.0,
        standing_tackle=70.0,
        interceptions=70.0,
        heading=70.0,
        strength=70.0,
        stamina=70.0,
        jumping=70.0,
        aggression=70.0,
        decision_making=70.0,
        composure=70.0,
        creativity=70.0,
        positioning=70.0,
        concentration=70.0,
        work_rate=70.0,
        leadership=70.0,
        diving=70.0 if pos == "GK" else 10.0,
        handling=70.0 if pos == "GK" else 10.0,
        kicking=70.0 if pos == "GK" else 10.0,
        reflexes=70.0 if pos == "GK" else 10.0,
        speed=70.0 if pos == "GK" else 10.0,
        goalkeeper_positioning=70.0 if pos == "GK" else 10.0,
    )
    return Player(
        id=player_id,
        name="Name",
        surname=player_id,
        nationality="ARG",
        birth_date=date(2000, 1, 1),
        height=180.0,
        weight=75.0,
        preferred_foot="RIGHT",
        primary_position=pos,
        secondary_positions=(),
        attributes=attrs,
        current_ability=70.0,
        potential=80.0,
        development_rate=70.0,
        development_profile=DevelopmentProfile.BALANCED,
        traits=(),
        role_familiarity={},
        state=PlayerState(form=70.0, fitness=100.0),
    )


def _create_full_squad(prefix: str) -> tuple[Player, ...]:
    return (
        _create_mock_player(f"{prefix}_GK1", "GK"),
        _create_mock_player(f"{prefix}_GK2", "GK"),
        _create_mock_player(f"{prefix}_CB1", "CB"),
        _create_mock_player(f"{prefix}_CB2", "CB"),
        _create_mock_player(f"{prefix}_CB3", "CB"),
        _create_mock_player(f"{prefix}_LB1", "LB"),
        _create_mock_player(f"{prefix}_RB1", "RB"),
        _create_mock_player(f"{prefix}_CM1", "CM"),
        _create_mock_player(f"{prefix}_CM2", "CM"),
        _create_mock_player(f"{prefix}_CAM1", "CAM"),
        _create_mock_player(f"{prefix}_LW1", "LW"),
        _create_mock_player(f"{prefix}_RW1", "RW"),
        _create_mock_player(f"{prefix}_ST1", "ST"),
        _create_mock_player(f"{prefix}_ST2", "ST"),

    )


def _create_mock_club(club_id: int, name: str, squad_prefix: str) -> Club:
    mgr = _create_mock_manager(f"Manager {name}")
    c = Club(
        name=name,
        country_code="ENG",
        league_code="EPL",
        manager=mgr,
        prestige=75.0,
        financial_power=75.0,
        academy_quality=75.0,
        facilities=75.0,
        fan_pressure=75.0,
        squad_depth=75.0,
        uefa_coefficient_raw=10.0,
        uefa_coefficient_normalized=10.0,
        domestic_reputation=75.0,
        international_reputation=75.0,
        squad=_create_full_squad(squad_prefix),
    )
    object.__setattr__(c, "id", club_id)
    return c


def _create_mock_environment(season_id: str = "SEASON1", comp_id: str = "COMP1"):
    comp = Competition(
        id=comp_id,
        name="Test Premier League",
        competition_type=CompetitionType.LEAGUE,
        country_id=1,
        importance=80.0,
        level=1,
        format=CompetitionFormat.ROUND_ROBIN,
        participant_count=4,
    )

    participants = (
        CompetitionParticipant(season_id, 1, "SEED1"),
        CompetitionParticipant(season_id, 2, "SEED2"),
        CompetitionParticipant(season_id, 3, "SEED3"),
        CompetitionParticipant(season_id, 4, "SEED4"),
    )

    stage = CompetitionStage(
        id="STAGE1",
        competition_season_id=season_id,
        stage_type=CompetitionStageType.REGULAR_SEASON,
        stage_number=1,
        participant_club_ids=(1, 2, 3, 4),
    )

    season = CompetitionSeason(
        id=season_id,
        competition_id=comp_id,
        season_label="2026/27",
        start_date=date(2026, 8, 1),
        end_date=date(2027, 5, 30),
        participants=participants,
        stages=(stage,),
        seed="SEASON_SEED_100",
        status=CompetitionSeasonStatus.ACTIVE,
    )

    config = SeasonSimulationConfig(
        start_date=date(2026, 8, 1),
        end_date=date(2027, 5, 30),
        seed="SIM_CONFIG_SEED",
    )

    return comp, season, config, stage


def _mock_participant_resolver(fixture: Fixture, context: OrchestrationContext) -> MatchSimulationParticipants:
    home_c = _create_mock_club(fixture.home_club_id, f"Club {fixture.home_club_id}", f"C{fixture.home_club_id}")
    away_c = _create_mock_club(fixture.away_club_id, f"Club {fixture.away_club_id}", f"C{fixture.away_club_id}")

    return MatchSimulationParticipants(
        home_club=home_c,
        away_club=away_c,
        home_manager=home_c.manager,
        away_manager=away_c.manager,
    )


# --- 1. Domain Adapter Tests (build_match_context) ---

def test_build_match_context_valid_mapping():
    comp, season, config, _ = _create_mock_environment()
    fixture = Fixture(
        id="FIX1",
        competition_season_id=season.id,
        stage_id="STAGE1",
        round_number=1,
        scheduled_date=date(2026, 8, 15),
        home_club_id=1,
        away_club_id=2,
        importance=85.0,
        rivalry_factor=1.2,
        seed="FIX_SEED_123",
    )

    match_ctx = build_match_context(fixture, comp, season, config, SimulationMode.FAST)

    assert match_ctx.match_id == "FIX1"
    assert match_ctx.home_club_id == 1
    assert match_ctx.away_club_id == 2
    assert match_ctx.competition_type == CompetitionType.LEAGUE
    assert match_ctx.competition_importance == 80.0
    assert match_ctx.match_importance == 85.0
    assert match_ctx.seed == "FIX_SEED_123"
    assert match_ctx.rivalry_factor == 1.2
    assert match_ctx.simulation_mode == SimulationMode.FAST


def test_build_match_context_season_mismatch():
    comp, season, config, _ = _create_mock_environment()
    fixture = Fixture(
        id="FIX1",
        competition_season_id="OTHER_SEASON",
        stage_id="STAGE1",
        round_number=1,
        scheduled_date=date(2026, 8, 15),
        home_club_id=1,
        away_club_id=2,
        importance=85.0,
        rivalry_factor=1.0,
        seed="FIX_SEED_123",
    )

    with pytest.raises(ValueError, match="does not match competition_season.id"):
        build_match_context(fixture, comp, season, config)


def test_build_match_context_competition_mismatch():
    comp, season, config, _ = _create_mock_environment(season_id="S1", comp_id="C1")
    other_comp = Competition(
        id="C2",
        name="Other Cup",
        competition_type=CompetitionType.DOMESTIC_CUP,
        country_id=1,
        importance=50.0,
        level=1,
        format=CompetitionFormat.SINGLE_ELIMINATION,
        participant_count=2,
    )

    fixture = Fixture(
        id="FIX1",
        competition_season_id="S1",
        stage_id="STAGE1",
        round_number=1,
        scheduled_date=date(2026, 8, 15),
        home_club_id=1,
        away_club_id=2,
        importance=50.0,
        rivalry_factor=1.0,
        seed="FIX_SEED",
    )

    with pytest.raises(ValueError, match="does not match competition.id"):
        build_match_context(fixture, other_comp, season, config)


def test_build_match_context_input_immutability():
    comp, season, config, _ = _create_mock_environment()
    fixture = Fixture(
        id="FIX1",
        competition_season_id=season.id,
        stage_id="STAGE1",
        round_number=1,
        scheduled_date=date(2026, 8, 15),
        home_club_id=1,
        away_club_id=2,
        importance=85.0,
        rivalry_factor=1.0,
        seed="SEED1",
    )

    orig_fixture_seed = fixture.seed
    orig_season_seed = season.seed

    match_ctx = build_match_context(fixture, comp, season, config)

    assert fixture.seed == orig_fixture_seed
    assert season.seed == orig_season_seed
    assert match_ctx is not None


# --- 2. Executor & Match Execution Tests ---

def test_execute_fixture_with_match_engine_success():
    comp, season, config, _ = _create_mock_environment()
    fixture = Fixture(
        id="FIX_EXEC_1",
        competition_season_id=season.id,
        stage_id="STAGE1",
        round_number=1,
        scheduled_date=date(2026, 8, 15),
        home_club_id=1,
        away_club_id=2,
        importance=70.0,
        rivalry_factor=1.0,
        seed="EXEC_SEED_1",
    )

    orch_ctx = OrchestrationContext(competition_season=season, competition=comp, config=config)

    res = execute_fixture_with_match_engine(
        fixture=fixture,
        context=orch_ctx,
        participant_resolver=_mock_participant_resolver,
        simulation_mode=SimulationMode.FAST,
    )

    assert isinstance(res, MatchFixtureExecutionResult)
    assert res.fixture_id == "FIX_EXEC_1"
    assert res.completed is True
    assert isinstance(res.match_result, MatchResult)
    assert res.match_result.match_id == "FIX_EXEC_1"
    assert res.match_result.home_club_id == 1
    assert res.match_result.away_club_id == 2
    assert res.match_result.home_score >= 0
    assert res.match_result.away_score >= 0


def test_executor_invalid_resolver_raises():
    comp, season, config, _ = _create_mock_environment()
    fixture = Fixture(
        id="FIX1",
        competition_season_id=season.id,
        stage_id="STAGE1",
        round_number=1,
        scheduled_date=date(2026, 8, 15),
        home_club_id=1,
        away_club_id=2,
        importance=70.0,
        rivalry_factor=1.0,
        seed="SEED1",
    )
    orch_ctx = OrchestrationContext(competition_season=season, competition=comp, config=config)

    with pytest.raises(ValueError, match="participant_resolver must be callable"):
        execute_fixture_with_match_engine(fixture, orch_ctx, None)


def test_executor_resolver_returning_bad_type_raises():
    comp, season, config, _ = _create_mock_environment()
    fixture = Fixture(
        id="FIX1",
        competition_season_id=season.id,
        stage_id="STAGE1",
        round_number=1,
        scheduled_date=date(2026, 8, 15),
        home_club_id=1,
        away_club_id=2,
        importance=70.0,
        rivalry_factor=1.0,
        seed="SEED1",
    )
    orch_ctx = OrchestrationContext(competition_season=season, competition=comp, config=config)

    def bad_resolver(f, c):
        return "invalid_participants_object"

    with pytest.raises(TypeError, match="expected MatchSimulationParticipants"):
        execute_fixture_with_match_engine(fixture, orch_ctx, bad_resolver)


def test_executor_resolver_club_id_mismatch_raises():
    comp, season, config, _ = _create_mock_environment()
    fixture = Fixture(
        id="FIX1",
        competition_season_id=season.id,
        stage_id="STAGE1",
        round_number=1,
        scheduled_date=date(2026, 8, 15),
        home_club_id=1,
        away_club_id=2,
        importance=70.0,
        rivalry_factor=1.0,
        seed="SEED1",
    )
    orch_ctx = OrchestrationContext(competition_season=season, competition=comp, config=config)

    def mismatch_resolver(f, c):
        # Swap club IDs
        home_c = _create_mock_club(2, "Club 2", "C2")
        away_c = _create_mock_club(1, "Club 1", "C1")
        return MatchSimulationParticipants(
            home_club=home_c, away_club=away_c, home_manager=home_c.manager, away_manager=away_c.manager
        )

    with pytest.raises(ValueError, match="Resolved home_club.id '2' does not match fixture home_club_id '1'"):
        execute_fixture_with_match_engine(fixture, orch_ctx, mismatch_resolver)


# --- 3. Determinism & Seeding Tests ---

def test_controlled_match_execution_determinism():
    comp, season, config, _ = _create_mock_environment()
    fixture = Fixture(
        id="FIX_DET_1",
        competition_season_id=season.id,
        stage_id="STAGE1",
        round_number=1,
        scheduled_date=date(2026, 8, 15),
        home_club_id=1,
        away_club_id=2,
        importance=70.0,
        rivalry_factor=1.0,
        seed="SAME_SEEDED_MATCH_123",
    )
    orch_ctx = OrchestrationContext(competition_season=season, competition=comp, config=config)

    res1 = execute_fixture_with_match_engine(fixture, orch_ctx, _mock_participant_resolver)
    res2 = execute_fixture_with_match_engine(fixture, orch_ctx, _mock_participant_resolver)

    m1 = res1.match_result
    m2 = res2.match_result

    assert m1.home_score == m2.home_score
    assert m1.away_score == m2.away_score
    assert m1.home_xg == m2.home_xg
    assert m1.away_xg == m2.away_xg
    assert m1.home_possession == m2.home_possession
    assert m1.away_possession == m2.away_possession
    assert len(m1.player_performances) == len(m2.player_performances)

    for p1, p2 in zip(m1.player_performances, m2.player_performances):
        assert p1.player_id == p2.player_id
        assert p1.rating == p2.rating
        assert p1.goals == p2.goals
        assert p1.assists == p2.assists


def test_cross_process_determinism():
    cmd = [
        sys.executable,
        "-c",
        """
import json, sys
from datetime import date
from app.competition.domain import Competition, CompetitionFormat, CompetitionParticipant, CompetitionSeason, CompetitionSeasonStatus, CompetitionStage, CompetitionStageType
from app.competition.fixtures import Fixture
from app.competition.orchestrator import OrchestrationContext, SeasonSimulationConfig
from app.competition.match_executor import execute_fixture_with_match_engine, MatchSimulationParticipants
from app.match.domain import CompetitionType, SimulationMode
from app.player.domain import Player, PlayerAttributes, PlayerState, DevelopmentProfile
from app.world.entities import Club, Manager

def make_player(pid, pos):
    attrs = PlayerAttributes(
        acceleration=70, sprint_speed=70, finishing=70, shot_power=70, long_shots=70, volleys=70, penalties=70,
        vision=70, short_passing=70, long_passing=70, crossing=70, curve=70, agility=70, balance=70, ball_control=70,
        dribbling=70, reactions=70, defensive_awareness=70, standing_tackle=70, interceptions=70, heading=70,
        strength=70, stamina=70, jumping=70, aggression=70, decision_making=70, composure=70, creativity=70,
        positioning=70, concentration=70, work_rate=70, leadership=70,
        diving=70 if pos=='GK' else 10, handling=70 if pos=='GK' else 10, kicking=70 if pos=='GK' else 10,
        reflexes=70 if pos=='GK' else 10, speed=70 if pos=='GK' else 10, goalkeeper_positioning=70 if pos=='GK' else 10
    )
    return Player(
        id=pid, name='N', surname=pid, nationality='ARG', birth_date=date(2000, 1, 1), height=180.0, weight=75.0,
        preferred_foot='RIGHT', primary_position=pos, secondary_positions=(), attributes=attrs, current_ability=70.0,
        potential=80.0, development_rate=70.0, development_profile=DevelopmentProfile.BALANCED, traits=(),
        role_familiarity={}, state=PlayerState(form=70.0, fitness=100.0)
    )

def make_club(cid, name, pref):
    squad = tuple([make_player(f'{pref}_GK1', 'GK'), make_player(f'{pref}_GK2', 'GK')] + [make_player(f'{pref}_P{i}', pos) for i, pos in enumerate(['CB','CB','CB','LB','RB','CM','CM','CAM','LW','RW','ST','ST'])])
    mgr = Manager(name='M', tactical_quality=80, player_development=80, game_management=80, rotation=50, adaptability=80, tactical_style='balanced', youth_preference=50, discipline=80)
    c = Club(name=name, country_code='ENG', league_code='EPL', manager=mgr, prestige=75, financial_power=75, academy_quality=75, facilities=75, fan_pressure=75, squad_depth=75, uefa_coefficient_raw=10, uefa_coefficient_normalized=10, domestic_reputation=75, international_reputation=75, squad=squad)
    object.__setattr__(c, 'id', cid)
    return c

comp = Competition('C1', 'League', CompetitionType.LEAGUE, 1, 80.0, 1, CompetitionFormat.ROUND_ROBIN, 2)
season = CompetitionSeason('S1', 'C1', '2026/27', date(2026,8,1), date(2027,5,30), (CompetitionParticipant('S1', 1, 'SEED1'), CompetitionParticipant('S1', 2, 'SEED2')), (), 'S_SEED', CompetitionSeasonStatus.ACTIVE)
config = SeasonSimulationConfig(date(2026,8,1), date(2027,5,30), 'CFG_SEED')
fixture = Fixture('F1', 'S1', 'STAGE1', 1, date(2026,8,15), 1, 2, 80.0, 1.0, 'CROSS_PROCESS_SEED_999')
ctx = OrchestrationContext(season, comp, config)

def resolver(f, c):
    h = make_club(1, 'H', 'H')
    a = make_club(2, 'A', 'A')
    return MatchSimulationParticipants(h, a, h.manager, a.manager)

res = execute_fixture_with_match_engine(fixture, ctx, resolver, SimulationMode.FAST)
m = res.match_result
summary = {
    'match_id': m.match_id,
    'home_score': m.home_score,
    'away_score': m.away_score,
    'home_xg': m.home_xg,
    'away_xg': m.away_xg,
    'perf_len': len(m.player_performances)
}
print(json.dumps(summary, sort_keys=True))
"""
    ]

    out1 = subprocess.check_output(cmd, text=True).strip()
    out2 = subprocess.check_output(cmd, text=True).strip()

    assert out1 == out2


def test_different_fixture_seed_passes_through():
    comp, season, config, _ = _create_mock_environment()
    fix1 = Fixture(
        id="FIX_1",
        competition_season_id=season.id,
        stage_id="STAGE1",
        round_number=1,
        scheduled_date=date(2026, 8, 15),
        home_club_id=1,
        away_club_id=2,
        importance=70.0,
        rivalry_factor=1.0,
        seed="SEED_ALPHA",
    )
    fix2 = Fixture(
        id="FIX_2",
        competition_season_id=season.id,
        stage_id="STAGE1",
        round_number=1,
        scheduled_date=date(2026, 8, 15),
        home_club_id=1,
        away_club_id=2,
        importance=70.0,
        rivalry_factor=1.0,
        seed="SEED_BETA",
    )

    ctx1 = build_match_context(fix1, comp, season, config)
    ctx2 = build_match_context(fix2, comp, season, config)

    assert ctx1.seed == "SEED_ALPHA"
    assert ctx2.seed == "SEED_BETA"
    assert ctx1.seed != ctx2.seed


# --- 4. Multi-Fixture Orchestration Tests ---

def test_multi_fixture_orchestration_integration():
    comp, season, config, stage = _create_mock_environment()

    fixtures = [
        Fixture("F1", season.id, stage.id, 1, date(2026, 8, 15), 1, 2, 80.0, 1.0, "SEED_F1"),
        Fixture("F2", season.id, stage.id, 1, date(2026, 8, 15), 3, 4, 80.0, 1.0, "SEED_F2"),
        Fixture("F3", season.id, stage.id, 2, date(2026, 8, 22), 2, 1, 80.0, 1.0, "SEED_F3"),
        Fixture("F4", season.id, stage.id, 2, date(2026, 8, 22), 4, 3, 80.0, 1.0, "SEED_F4"),
    ]

    executor = build_match_engine_executor(_mock_participant_resolver, SimulationMode.FAST)

    season_res = simulate_competition_season(
        competition_season=season,
        competition=comp,
        fixtures=fixtures,
        config=config,
        fixture_executor=executor,
    )

    assert season_res.completed is True
    assert season_res.fixtures_processed == 4
    assert season_res.fixtures_completed == 4
    assert len(season_res.execution_results) == 4

    for exec_res in season_res.execution_results:
        assert isinstance(exec_res, MatchFixtureExecutionResult)
        assert exec_res.completed is True
        assert exec_res.match_result.match_id == exec_res.fixture_id


def test_input_order_independence():
    comp, season, config, stage = _create_mock_environment()

    f1 = Fixture("F1", season.id, stage.id, 1, date(2026, 8, 15), 1, 2, 80.0, 1.0, "SEED_F1")
    f2 = Fixture("F2", season.id, stage.id, 1, date(2026, 8, 15), 3, 4, 80.0, 1.0, "SEED_F2")
    f3 = Fixture("F3", season.id, stage.id, 2, date(2026, 8, 22), 2, 1, 80.0, 1.0, "SEED_F3")

    executor = build_match_engine_executor(_mock_participant_resolver, SimulationMode.FAST)

    res_ordered = simulate_competition_season(
        competition_season=season,
        competition=comp,
        fixtures=[f1, f2, f3],
        config=config,
        fixture_executor=executor,
    )

    res_shuffled = simulate_competition_season(
        competition_season=season,
        competition=comp,
        fixtures=[f3, f1, f2],
        config=config,
        fixture_executor=executor,
    )

    assert [r.fixture_id for r in res_ordered.execution_results] == [r.fixture_id for r in res_shuffled.execution_results]
    for r1, r2 in zip(res_ordered.execution_results, res_shuffled.execution_results):
        assert r1.match_result.home_score == r2.match_result.home_score
        assert r1.match_result.away_score == r2.match_result.away_score


# --- 5. FAST vs DETAILED Mode Tests ---

def test_fast_vs_detailed_mode_execution():
    comp, season, config, _ = _create_mock_environment()
    fixture = Fixture(
        id="FIX_MODE",
        competition_season_id=season.id,
        stage_id="STAGE1",
        round_number=1,
        scheduled_date=date(2026, 8, 15),
        home_club_id=1,
        away_club_id=2,
        importance=70.0,
        rivalry_factor=1.0,
        seed="MODE_SEED_999",
    )
    orch_ctx = OrchestrationContext(competition_season=season, competition=comp, config=config)

    res_fast = execute_fixture_with_match_engine(
        fixture, orch_ctx, _mock_participant_resolver, SimulationMode.FAST
    )
    res_det = execute_fixture_with_match_engine(
        fixture, orch_ctx, _mock_participant_resolver, SimulationMode.DETAILED
    )

    m_fast = res_fast.match_result
    m_det = res_det.match_result

    assert m_fast.match_id == "FIX_MODE"
    assert m_det.match_id == "FIX_MODE"
    assert m_fast.home_club_id == 1
    assert m_det.home_club_id == 1
    assert m_fast.away_club_id == 2
    assert m_det.away_club_id == 2
    assert len(m_fast.player_performances) > 0
    assert len(m_det.player_performances) > 0
    # Detailed mode produces match events for goals/assists/subs
    assert len(m_det.events) >= len(m_fast.events)


# --- 6. Error Propagation Tests ---

def test_error_propagation_on_resolver_failure():
    comp, season, config, stage = _create_mock_environment()

    f1 = Fixture("F1", season.id, stage.id, 1, date(2026, 8, 15), 1, 2, 80.0, 1.0, "SEED_F1")
    f2 = Fixture("F2", season.id, stage.id, 1, date(2026, 8, 15), 3, 4, 80.0, 1.0, "SEED_F2")

    def failing_resolver(fixture, context):
        if fixture.id == "F2":
            raise RuntimeError("Database connection timeout during participant resolution!")
        return _mock_participant_resolver(fixture, context)

    executor = build_match_engine_executor(failing_resolver)

    with pytest.raises(RuntimeError, match="Database connection timeout"):
        simulate_competition_season(
            competition_season=season,
            competition=comp,
            fixtures=[f1, f2],
            config=config,
            fixture_executor=executor,
        )


# --- 7. Static Audits & Protection Tests ---

def test_no_forbidden_imports_in_match_executor():
    executor_path = Path(__file__).resolve().parents[1] / "app" / "competition" / "match_executor.py"
    tree = ast.parse(executor_path.read_text(encoding="utf-8"))

    forbidden = {"fastapi", "sqlalchemy", "sqlite3", "alembic", "httpx", "starlette", "app.career"}
    imported_modules = set()

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imported_modules.add(alias.name)
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                imported_modules.add(node.module)

    for imp in imported_modules:
        for f in forbidden:
            assert not imp.startswith(f), f"Forbidden import '{imp}' found in match_executor.py"
