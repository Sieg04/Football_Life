import ast
from datetime import date
import json
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
    CompetitionType,
)
from app.competition.fixtures import Fixture, FixtureStatus
from app.competition.match_executor import MatchSimulationParticipants
from app.competition.orchestrator import (
    CompetitionSeasonBinding,
    FullCompetitionSeasonResult,
    MultiCompetitionSeasonResult,
    SeasonSimulationConfig,
    simulate_full_competition_season,
    simulate_multi_competition_season,
)
from app.competition.progression import TieBreakResult
from app.competition.standings import rank_standings
from app.match.domain import SimulationMode
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


def _deterministic_tiebreak_provider(fixtures, match_results):
    tiebreaks = {}
    result_map = {m.match_id: m for m in match_results}
    for f in fixtures:
        m = result_map.get(f.id)
        if m and m.home_score == m.away_score:
            winner_id = f.home_club_id if (f.home_club_id + f.away_club_id) % 2 == 0 else f.away_club_id
            tiebreaks[f.id] = TieBreakResult(winner_club_id=winner_id, method="PENALTIES")
        pair_key = f"{min(f.home_club_id, f.away_club_id)}:{max(f.home_club_id, f.away_club_id)}"
        winner_id = min(f.home_club_id, f.away_club_id)
        tiebreaks[pair_key] = TieBreakResult(winner_club_id=winner_id, method="PENALTIES")
    return tiebreaks


def _mock_participant_resolver(fixture: Fixture, context) -> MatchSimulationParticipants:
    home_c = _create_mock_club(fixture.home_club_id, f"Club {fixture.home_club_id}", f"C{fixture.home_club_id}")
    away_c = _create_mock_club(fixture.away_club_id, f"Club {fixture.away_club_id}", f"C{fixture.away_club_id}")
    return MatchSimulationParticipants(
        home_club=home_c,
        away_club=away_c,
        home_manager=home_c.manager,
        away_manager=away_c.manager,
    )


def _build_league_environment(num_teams: int = 4, season_id: str = "LEAGUE_S2025", comp_id: str = "LEAGUE_1"):
    club_ids = tuple(range(1, num_teams + 1))
    comp = Competition(
        id=comp_id,
        name="Test Premier League",
        competition_type=CompetitionType.LEAGUE,
        country_id=1,
        importance=80.0,
        level=1,
        format=CompetitionFormat.ROUND_ROBIN,
        participant_count=num_teams,
    )

    participants = tuple(
        CompetitionParticipant(competition_season_id=season_id, club_id=cid, seed=f"seed_p_{cid}")
        for cid in club_ids
    )

    stage = CompetitionStage(
        id=f"{season_id}_stage_rr",
        competition_season_id=season_id,
        stage_type=CompetitionStageType.REGULAR_SEASON,
        stage_number=1,
        participant_club_ids=club_ids,
        completed=False,
    )

    season = CompetitionSeason(
        id=season_id,
        competition_id=comp_id,
        season_label="2025/2026",
        start_date=date(2025, 8, 1),
        end_date=date(2026, 5, 30),
        participants=participants,
        stages=(stage,),
        seed=f"seed_{season_id}",
        status=CompetitionSeasonStatus.ACTIVE,
    )

    config = SeasonSimulationConfig(
        start_date=date(2025, 8, 1),
        end_date=date(2026, 5, 30),
        seed="sim_config_seed_100",
    )

    return comp, season, config


def _build_knockout_environment(season_id: str = "CUP_S2025", comp_id: str = "CUP_1", two_leg: bool = False):
    club_ids = tuple(range(1, 9))
    comp_format = CompetitionFormat.TWO_LEG_ELIMINATION if two_leg else CompetitionFormat.SINGLE_ELIMINATION
    comp = Competition(
        id=comp_id,
        name="Test FA Cup",
        competition_type=CompetitionType.DOMESTIC_CUP,
        country_id=1,
        importance=70.0,
        level=1,
        format=comp_format,
        participant_count=8,
    )

    participants = tuple(
        CompetitionParticipant(competition_season_id=season_id, club_id=cid, seed=f"seed_p_{cid}")
        for cid in club_ids
    )

    qf_stage = CompetitionStage(
        id=f"{season_id}_qf",
        competition_season_id=season_id,
        stage_type=CompetitionStageType.QUARTER_FINAL,
        stage_number=1,
        participant_club_ids=club_ids,
        completed=False,
    )
    sf_stage = CompetitionStage(
        id=f"{season_id}_sf",
        competition_season_id=season_id,
        stage_type=CompetitionStageType.SEMI_FINAL,
        stage_number=2,
        participant_club_ids=club_ids,
        completed=False,
    )
    final_stage = CompetitionStage(
        id=f"{season_id}_final",
        competition_season_id=season_id,
        stage_type=CompetitionStageType.FINAL,
        stage_number=3,
        participant_club_ids=club_ids,
        completed=False,
    )

    season = CompetitionSeason(
        id=season_id,
        competition_id=comp_id,
        season_label="2025/2026",
        start_date=date(2025, 8, 1),
        end_date=date(2026, 5, 30),
        participants=participants,
        stages=(qf_stage, sf_stage, final_stage),
        seed=f"seed_{season_id}",
        status=CompetitionSeasonStatus.ACTIVE,
    )

    config = SeasonSimulationConfig(
        start_date=date(2025, 8, 1),
        end_date=date(2026, 5, 30),
        seed="sim_config_cup_seed",
    )

    return comp, season, config


# --- 1. Full League Season Tests ---

def test_full_season_4_team_double_round_robin():
    comp, season, config = _build_league_environment(num_teams=4)

    res = simulate_full_competition_season(
        competition_season=season,
        competition=comp,
        config=config,
        participant_resolver=_mock_participant_resolver,
        tiebreak_provider=_deterministic_tiebreak_provider,
    )

    assert res.completed is True
    assert res.competition_season_id == season.id
    assert res.fixtures_processed == 12
    assert res.fixtures_completed == 12
    assert len(res.match_results) == 12
    assert res.winner_club_id is not None
    assert res.winner_club_id in (1, 2, 3, 4)

    ranked = rank_standings(res.final_standings)
    assert len(ranked) == 4
    assert ranked[0].club_id == res.winner_club_id
    total_played = sum(entry.played for entry in ranked)
    assert total_played == 24


def test_full_season_20_team_double_round_robin():
    comp, season, config = _build_league_environment(num_teams=20, season_id="EPL_S2025", comp_id="EPL_1")

    res = simulate_full_competition_season(
        competition_season=season,
        competition=comp,
        config=config,
        participant_resolver=_mock_participant_resolver,
        tiebreak_provider=_deterministic_tiebreak_provider,
    )

    assert res.completed is True
    assert res.fixtures_processed == 380
    assert res.fixtures_completed == 380
    assert len(res.match_results) == 380
    assert res.winner_club_id is not None

    ranked = rank_standings(res.final_standings)
    assert len(ranked) == 20
    assert ranked[0].club_id == res.winner_club_id
    for entry in ranked:
        assert entry.played == 38


# --- 2. Knockout Competition Tests ---

def test_full_season_single_elimination_8_clubs():
    comp, season, config = _build_knockout_environment(two_leg=False)

    res = simulate_full_competition_season(
        competition_season=season,
        competition=comp,
        config=config,
        participant_resolver=_mock_participant_resolver,
        tiebreak_provider=_deterministic_tiebreak_provider,
    )

    assert res.completed is True
    assert res.final_stage_index == 2
    assert res.winner_club_id is not None
    assert res.winner_club_id in range(1, 9)
    # QF (4 matches) + SF (2 matches) + Final (1 match) = 7 matches
    assert res.fixtures_processed == 7
    assert res.fixtures_completed == 7
    assert len(res.match_results) == 7


def test_full_season_two_leg_knockout_8_clubs():
    comp, season, config = _build_knockout_environment(two_leg=True)

    res = simulate_full_competition_season(
        competition_season=season,
        competition=comp,
        config=config,
        participant_resolver=_mock_participant_resolver,
        tiebreak_provider=_deterministic_tiebreak_provider,
    )

    assert res.completed is True
    assert res.final_stage_index == 2
    assert res.winner_club_id is not None
    # QF (4 ties x 2 legs = 8) + SF (2 ties x 2 legs = 4) + Final (1 single leg) = 13 matches
    assert res.fixtures_processed == 13
    assert res.fixtures_completed == 13


def test_full_season_round_robin_to_knockout():
    club_ids = tuple(range(1, 9))
    season_id = "HYBRID_S2025"
    comp_id = "HYBRID_1"

    comp = Competition(
        id=comp_id,
        name="Hybrid Champions Cup",
        competition_type=CompetitionType.EUROPEAN,
        country_id=None,
        importance=90.0,
        level=1,
        format=CompetitionFormat.SINGLE_ELIMINATION,
        participant_count=8,
        rules={"qualification_slots": 4},
    )

    participants = tuple(
        CompetitionParticipant(competition_season_id=season_id, club_id=cid, seed=f"seed_p_{cid}")
        for cid in club_ids
    )

    group_stage = CompetitionStage(
        id=f"{season_id}_group",
        competition_season_id=season_id,
        stage_type=CompetitionStageType.GROUP_STAGE,
        stage_number=1,
        participant_club_ids=club_ids,
        completed=False,
    )
    sf_stage = CompetitionStage(
        id=f"{season_id}_sf",
        competition_season_id=season_id,
        stage_type=CompetitionStageType.SEMI_FINAL,
        stage_number=2,
        participant_club_ids=(1, 2, 3, 4),
        completed=False,
    )
    final_stage = CompetitionStage(
        id=f"{season_id}_final",
        competition_season_id=season_id,
        stage_type=CompetitionStageType.FINAL,
        stage_number=3,
        participant_club_ids=(1, 2),
        completed=False,
    )

    season = CompetitionSeason(
        id=season_id,
        competition_id=comp_id,
        season_label="2025/2026",
        start_date=date(2025, 8, 1),
        end_date=date(2026, 5, 30),
        participants=participants,
        stages=(group_stage, sf_stage, final_stage),
        seed="hybrid_season_seed",
        status=CompetitionSeasonStatus.ACTIVE,
    )

    config = SeasonSimulationConfig(
        start_date=date(2025, 8, 1),
        end_date=date(2026, 5, 30),
        seed="sim_config_hybrid_seed",
    )

    res = simulate_full_competition_season(
        competition_season=season,
        competition=comp,
        config=config,
        participant_resolver=_mock_participant_resolver,
    )

    assert res.completed is True
    assert res.winner_club_id is not None
    # Group stage: 8 teams double round-robin = 56 matches
    # SF stage: 4 teams single elimination = 2 matches
    # Final stage: 2 teams single elimination = 1 match
    # Total = 59 matches
    assert res.fixtures_processed == 59
    assert res.fixtures_completed == 59


# --- 3. Multi-Competition & Calendar Conflict Tests ---

def test_multi_competition_independent_execution():
    comp1, season1, config = _build_league_environment(num_teams=4, season_id="S1_LEAGUE", comp_id="C1_LEAGUE")
    comp2, season2, _ = _build_knockout_environment(season_id="S2_CUP", comp_id="C2_CUP", two_leg=False)

    # Shift cup dates or use disjoint clubs so there are no club-date conflicts
    b1 = CompetitionSeasonBinding(competition=comp1, competition_season=season1)

    # Re-create season2 with disjoint clubs (101-108) to avoid calendar conflicts
    cup_club_ids = tuple(range(101, 109))
    comp2_disjoint = Competition(
        id="C2_CUP",
        name="Test FA Cup Disjoint",
        competition_type=CompetitionType.DOMESTIC_CUP,
        country_id=1,
        importance=70.0,
        level=1,
        format=CompetitionFormat.SINGLE_ELIMINATION,
        participant_count=8,
    )
    cup_parts = tuple(CompetitionParticipant("S2_CUP", cid, f"seed_{cid}") for cid in cup_club_ids)
    qf = CompetitionStage("S2_CUP_qf", "S2_CUP", CompetitionStageType.QUARTER_FINAL, 1, cup_club_ids)
    sf = CompetitionStage("S2_CUP_sf", "S2_CUP", CompetitionStageType.SEMI_FINAL, 2, (101, 102, 103, 104))
    fn = CompetitionStage("S2_CUP_final", "S2_CUP", CompetitionStageType.FINAL, 3, (101, 102))
    season2_disjoint = CompetitionSeason(
        id="S2_CUP",
        competition_id="C2_CUP",
        season_label="2025/2026",
        start_date=date(2025, 8, 1),
        end_date=date(2026, 5, 30),
        participants=cup_parts,
        stages=(qf, sf, fn),
        seed="seed_cup_disjoint",
        status=CompetitionSeasonStatus.ACTIVE,
    )

    b2 = CompetitionSeasonBinding(competition=comp2_disjoint, competition_season=season2_disjoint)

    multi_res = simulate_multi_competition_season(
        competitions=(b1, b2),
        config=config,
        participant_resolver=_mock_participant_resolver,
        tiebreak_provider=_deterministic_tiebreak_provider,
    )

    assert multi_res.completed is True
    assert len(multi_res.competitions) == 2
    assert multi_res.total_fixtures_processed == 12 + 7
    assert multi_res.total_fixtures_completed == 12 + 7


def test_multi_competition_calendar_conflict_raises():
    comp1, season1, config = _build_league_environment(num_teams=4, season_id="S1_LEAGUE", comp_id="C1_LEAGUE")
    comp2, season2, _ = _build_knockout_environment(season_id="S2_CUP", comp_id="C2_CUP", two_leg=False)

    # Both competitions share club_id 1 and start on 2025-08-01
    b1 = CompetitionSeasonBinding(competition=comp1, competition_season=season1)
    b2 = CompetitionSeasonBinding(competition=comp2, competition_season=season2)

    with pytest.raises(ValueError, match="Calendar conflict detected: club_id 1 is scheduled to play multiple fixtures on 2025-08-01"):
        simulate_multi_competition_season(
            competitions=(b1, b2),
            config=config,
            participant_resolver=_mock_participant_resolver,
        )


def test_cross_competition_independence():
    comp1, season1, config = _build_league_environment(num_teams=4, season_id="S1_LEAGUE", comp_id="C1_LEAGUE")

    res = simulate_full_competition_season(
        competition_season=season1,
        competition=comp1,
        config=config,
        participant_resolver=_mock_participant_resolver,
    )

    # Verify form & standings are isolated per competition
    assert res.final_standings is not None
    assert res.final_form_table is not None
    assert len(res.final_standings.entries) == 4
    assert len(res.final_form_table) == 4


# --- 4. Determinism & Seed Propagation Tests ---

def test_orchestrator_determinism_same_seed():
    comp, season, config = _build_league_environment(num_teams=4)

    res1 = simulate_full_competition_season(season, comp, config, _mock_participant_resolver)
    res2 = simulate_full_competition_season(season, comp, config, _mock_participant_resolver)

    assert res1.winner_club_id == res2.winner_club_id
    assert res1.fixtures_processed == res2.fixtures_processed
    assert [m.home_score for m in res1.match_results] == [m.home_score for m in res2.match_results]
    assert [m.away_score for m in res1.match_results] == [m.away_score for m in res2.match_results]


def test_orchestrator_cross_process_determinism():
    script = """
import json
from datetime import date
from app.competition.domain import Competition, CompetitionSeason, CompetitionParticipant, CompetitionStage, CompetitionStageType, CompetitionType, CompetitionFormat, CompetitionSeasonStatus
from app.competition.orchestrator import SeasonSimulationConfig, simulate_full_competition_season
from app.competition.match_executor import MatchSimulationParticipants
from app.world.entities import Club, Manager
from app.player.domain import Player, PlayerAttributes, PlayerState, DevelopmentProfile

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

def make_club(cid, name):
    squad = tuple([make_player(f'C{cid}_GK1', 'GK'), make_player(f'C{cid}_GK2', 'GK')] + [make_player(f'C{cid}_P{i}', pos) for i, pos in enumerate(['CB','CB','CB','LB','RB','CM','CM','CAM','LW','RW','ST','ST'])])
    mgr = Manager(name='M', tactical_quality=80, player_development=80, game_management=80, rotation=50, adaptability=80, tactical_style='balanced', youth_preference=50, discipline=80)
    c = Club(name=name, country_code='ENG', league_code='EPL', manager=mgr, prestige=75, financial_power=75, academy_quality=75, facilities=75, fan_pressure=75, squad_depth=75, uefa_coefficient_raw=10, uefa_coefficient_normalized=10, domestic_reputation=75, international_reputation=75, squad=squad)
    object.__setattr__(c, 'id', cid)
    return c

def mock_resolver(f, c):
    h = make_club(f.home_club_id, f'H{f.home_club_id}')
    a = make_club(f.away_club_id, f'A{f.away_club_id}')
    return MatchSimulationParticipants(h, a, h.manager, a.manager)

comp = Competition('c1', 'League', CompetitionType.LEAGUE, 1, 80.0, 1, CompetitionFormat.ROUND_ROBIN, 4)
parts = tuple(CompetitionParticipant('s1', cid, f'seed_{cid}') for cid in (1,2,3,4))
stage = CompetitionStage('st1', 's1', CompetitionStageType.REGULAR_SEASON, 1, (1,2,3,4))
season = CompetitionSeason('s1', 'c1', '2025', date(2025, 8, 1), date(2026, 5, 30), parts, (stage,), 'season_seed', CompetitionSeasonStatus.ACTIVE)
config = SeasonSimulationConfig(date(2025, 8, 1), date(2026, 5, 30), 'sim_seed')

res = simulate_full_competition_season(season, comp, config, mock_resolver)
summary = {
    'completed': res.completed,
    'winner': res.winner_club_id,
    'proc': res.fixtures_processed,
    'scores': [(m.home_score, m.away_score) for m in res.match_results]
}
print(json.dumps(summary))
"""
    cmd = [sys.executable, "-c", script]
    out1 = subprocess.check_output(cmd, env={"PYTHONPATH": "backend"}).decode("utf-8").strip()
    out2 = subprocess.check_output(cmd, env={"PYTHONPATH": "backend"}).decode("utf-8").strip()

    assert out1 == out2


# --- 5. Failure Propagation & Invariant Tests ---

def test_failure_propagation_resolver_error():
    comp, season, config = _build_league_environment(num_teams=4)

    def failing_resolver(fixture, context):
        if fixture.home_club_id == 2:
            raise RuntimeError("Failed to resolve squad for club 2")
        return _mock_participant_resolver(fixture, context)

    with pytest.raises(RuntimeError, match="Failed to resolve squad for club 2"):
        simulate_full_competition_season(season, comp, config, failing_resolver)


def test_fixture_execution_count_and_result_accounting():
    comp, season, config = _build_league_environment(num_teams=4)

    res = simulate_full_competition_season(season, comp, config, _mock_participant_resolver)

    assert res.fixtures_processed == len(res.match_results)
    assert res.fixtures_completed == len(res.match_results)

    seen_match_ids = set()
    for m in res.match_results:
        assert m.match_id not in seen_match_ids, f"Duplicate match_id '{m.match_id}' executed!"
        seen_match_ids.add(m.match_id)


# --- 6. AST & Duplication Audits ---

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
        "random",
        "uuid",
    ]

    for imp in imported_modules:
        for forbidden in forbidden_patterns:
            assert not imp.startswith(forbidden), f"Forbidden import '{imp}' found in orchestrator.py"


def test_duplication_audit():
    with open("backend/app/competition/orchestrator.py", "r", encoding="utf-8") as f:
        content = f.read()

    forbidden_definitions = [
        "def calculate_xg",
        "def poisson_sample",
        "def rank_standings",
        "def record_form_result",
        "def calculate_aggregate_score",
    ]

    for stmt in forbidden_definitions:
        assert stmt not in content, f"Duplicated formula definition '{stmt}' found in orchestrator.py!"
