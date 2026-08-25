import ast
import json
import subprocess
import sys
from datetime import date
import pytest

from app.career.domain import (
    CareerPhase,
    MatchDrivenSeasonInput,
    SeasonalEnvironmentInput,
    SeasonalPerformanceInput,
    SeasonalPlayingTimeInput,
)
from app.career.engine import (
    create_career,
    simulate_match_driven_season,
    simulate_season,
)
from app.match.aggregation import SeasonPerformance, aggregate_season_performance
from app.match.domain import CompetitionType, MatchContext, MatchResult, SimulationMode
from app.match.lineup import FORMATION_PRESETS, calculate_effective_team_strength, calculate_xi_quality, select_lineup
from app.match.performance import simulate_player_performances
from app.match.resolution import resolve_match_resolution
from app.player.domain import Player, PlayerAttributes, PlayerState
from app.player.engine import current_ability, position_ovr


def create_sample_player(player_id: str = "P100", age: int = 18, potential: float = 85.0) -> Player:
    birth_year = 2026 - age
    birth_date = date(birth_year, 1, 15)
    attrs = PlayerAttributes(
        acceleration=70, sprint_speed=72, finishing=75, shot_power=75, long_shots=70, volleys=65, penalties=65,
        vision=70, short_passing=70, long_passing=65, crossing=60, curve=60, agility=70, balance=70, ball_control=72,
        dribbling=74, reactions=70, defensive_awareness=35, standing_tackle=35, interceptions=30, heading=60,
        strength=65, stamina=70, jumping=65, aggression=60, decision_making=70, composure=70, creativity=70,
        positioning=75, concentration=65, work_rate=70, leadership=50,
        diving=10, handling=10, kicking=10, reflexes=10, speed=10, goalkeeper_positioning=10
    )
    p = Player(
        id=player_id,
        name="Test",
        surname="Prospect",
        nationality="Testland",
        birth_date=birth_date,
        height=180.0,
        weight=75.0,
        preferred_foot="Right",
        primary_position="ST",
        secondary_positions=("LW",),
        attributes=attrs,
        current_ability=68.0,
        potential=potential,
        development_rate=80.0,
        development_profile="FINISHER",
        personality={"professionalism": 70.0},
        state=PlayerState(fitness=100.0, morale=100.0, confidence=100.0, happiness=100.0),
    )
    p.current_ability = current_ability(p)
    return p


def build_season_perf(player_id: str, minutes: int, avg_rating: float) -> SeasonPerformance:
    perf_factor = round(max(0.80, min(1.20, 1.0 + ((avg_rating - 6.8) / 10.0))), 4)
    if minutes <= 300:
        time_factor = 0.30
    elif minutes <= 750:
        time_factor = 0.55
    elif minutes <= 1400:
        time_factor = 0.80
    elif minutes <= 2200:
        time_factor = 1.00
    elif minutes <= 3000:
        time_factor = 1.05
    else:
        time_factor = 1.00

    return SeasonPerformance(
        player_id=player_id,
        season_number=1,
        appearances=max(1, minutes // 90),
        starts=max(1, minutes // 90),
        substitute_appearances=0,
        minutes_played=minutes,
        goals=10,
        assists=5,
        total_shots=30,
        shots_on_target=15,
        key_passes=10,
        tackles=5,
        interceptions=2,
        clearances=1,
        clean_sheets=0,
        average_rating=avg_rating,
        performance_factor=perf_factor,
        playing_time_factor=time_factor,
    )


def test_neutral_match_driven_season():
    player = create_sample_player(age=18)
    career = create_career("C1", player, club_id=10, start_date=date(2026, 7, 1), seed="SEED1")
    perf = build_season_perf(player.id, minutes=2000, avg_rating=6.8)

    season = simulate_match_driven_season(career, perf)
    assert season.playing_time_input.playing_time_factor == 1.0
    assert season.performance_input.performance_factor == 1.0
    assert season.development_budget > 0.0


def test_high_performance_season():
    player = create_sample_player(age=18)
    career = create_career("C2", player, club_id=10, start_date=date(2026, 7, 1), seed="SEED1")
    perf = build_season_perf(player.id, minutes=2000, avg_rating=7.8)

    season = simulate_match_driven_season(career, perf)
    assert season.performance_input.performance_factor == 1.10


def test_low_performance_season():
    player = create_sample_player(age=18)
    career = create_career("C3", player, club_id=10, start_date=date(2026, 7, 1), seed="SEED1")
    perf = build_season_perf(player.id, minutes=2000, avg_rating=5.8)

    season = simulate_match_driven_season(career, perf)
    assert season.performance_input.performance_factor == 0.90


def test_high_minutes_season():
    player = create_sample_player(age=18)
    career = create_career("C4", player, club_id=10, start_date=date(2026, 7, 1), seed="SEED1")
    perf = build_season_perf(player.id, minutes=2500, avg_rating=6.8)

    season = simulate_match_driven_season(career, perf)
    assert season.playing_time_input.playing_time_factor == 1.05


def test_low_minutes_season():
    player = create_sample_player(age=18)
    career = create_career("C5", player, club_id=10, start_date=date(2026, 7, 1), seed="SEED1")
    perf = build_season_perf(player.id, minutes=200, avg_rating=6.8)

    season = simulate_match_driven_season(career, perf)
    assert season.playing_time_input.playing_time_factor == 0.30


def test_high_perf_high_minutes():
    p1 = create_sample_player("P1", age=18)
    p2 = create_sample_player("P2", age=18)
    c1 = create_career("C6a", p1, club_id=10, start_date=date(2026, 7, 1), seed="SAME_SEED")
    c2 = create_career("C6b", p2, club_id=10, start_date=date(2026, 7, 1), seed="SAME_SEED")

    s1 = simulate_match_driven_season(c1, build_season_perf("P1", 2000, 6.8))
    s2 = simulate_match_driven_season(c2, build_season_perf("P2", 2500, 7.8))

    assert s2.development_budget > s1.development_budget


def test_high_perf_low_minutes():
    p1 = create_sample_player("P1", age=18)
    p2 = create_sample_player("P2", age=18)
    c1 = create_career("C7a", p1, club_id=10, start_date=date(2026, 7, 1), seed="SAME_SEED")
    c2 = create_career("C7b", p2, club_id=10, start_date=date(2026, 7, 1), seed="SAME_SEED")

    s1 = simulate_match_driven_season(c1, build_season_perf("P1", 2000, 6.8))
    s2 = simulate_match_driven_season(c2, build_season_perf("P2", 200, 7.8))

    assert s2.development_budget < s1.development_budget


def test_low_perf_high_minutes():
    p1 = create_sample_player("P1", age=18)
    p2 = create_sample_player("P2", age=18)
    c1 = create_career("C8a", p1, club_id=10, start_date=date(2026, 7, 1), seed="SAME_SEED")
    c2 = create_career("C8b", p2, club_id=10, start_date=date(2026, 7, 1), seed="SAME_SEED")

    s1 = simulate_match_driven_season(c1, build_season_perf("P1", 2000, 6.8))
    s2 = simulate_match_driven_season(c2, build_season_perf("P2", 2500, 5.8))

    assert s2.development_budget < s1.development_budget


def test_neutral_factor_preservation():
    player = create_sample_player(age=18)
    career = create_career("C9", player, club_id=10, start_date=date(2026, 7, 1), seed="SEED")
    perf = build_season_perf(player.id, minutes=2000, avg_rating=6.8)

    season = simulate_match_driven_season(career, perf)
    assert season.playing_time_input.playing_time_factor == 1.0
    assert season.performance_input.performance_factor == 1.0


def test_one_season_ca_progression():
    player = create_sample_player(age=18, potential=90.0)
    initial_ca = current_ability(player)
    career = create_career("C10", player, club_id=10, start_date=date(2026, 7, 1), seed="SEED")
    perf = build_season_perf(player.id, minutes=2200, avg_rating=7.2)

    season = simulate_match_driven_season(career, perf)
    assert season.ending_ability > initial_ca
    assert player.current_ability == season.ending_ability


def test_attribute_changes():
    player = create_sample_player(age=18)
    init_fin = player.attributes.finishing
    career = create_career("C11", player, club_id=10, start_date=date(2026, 7, 1), seed="SEED")
    perf = build_season_perf(player.id, minutes=2000, avg_rating=7.5)

    season = simulate_match_driven_season(career, perf)
    assert len(season.attribute_changes) > 0
    assert player.attributes.finishing > init_fin


def test_potential_constraint():
    player = create_sample_player(age=18, potential=72.0)
    career = create_career("C12", player, club_id=10, start_date=date(2026, 7, 1), seed="SEED")
    perf = build_season_perf(player.id, minutes=2500, avg_rating=9.0)

    for _ in range(5):
        simulate_match_driven_season(career, perf)

    assert player.current_ability <= player.potential + 1e-4
    for attr in vars(player.attributes):
        val = getattr(player.attributes, attr)
        assert 1.0 <= val <= 100.0


def test_age_progression():
    player = create_sample_player(age=18)
    career = create_career("C13", player, club_id=10, start_date=date(2026, 7, 1), seed="SEED")
    perf = build_season_perf(player.id, minutes=2000, avg_rating=6.8)

    season = simulate_match_driven_season(career, perf)
    assert season.starting_age == 18
    assert season.ending_age == 19


def test_season_number_progression():
    player = create_sample_player(age=18)
    career = create_career("C14", player, club_id=10, start_date=date(2026, 7, 1), seed="SEED")
    perf = build_season_perf(player.id, minutes=2000, avg_rating=6.8)

    s1 = simulate_match_driven_season(career, perf)
    assert s1.season_number == 1
    assert career.current_season_number == 2

    s2 = simulate_match_driven_season(career, perf)
    assert s2.season_number == 2
    assert career.current_season_number == 3


def test_season_label_progression():
    player = create_sample_player(age=18)
    career = create_career("C15", player, club_id=10, start_date=date(2026, 7, 1), seed="SEED")
    assert career.current_season_label == "2026/27"

    perf = build_season_perf(player.id, minutes=2000, avg_rating=6.8)
    simulate_match_driven_season(career, perf)
    assert career.current_season_label == "2027/28"


def test_career_phase_progression():
    player = create_sample_player(age=20)
    career = create_career("C16", player, club_id=10, start_date=date(2026, 7, 1), seed="SEED")
    assert career.career_phase == CareerPhase.EARLY_PRO

    perf = build_season_perf(player.id, minutes=2000, avg_rating=6.8)
    season = simulate_match_driven_season(career, perf)
    assert season.career_phase_at_start == CareerPhase.EARLY_PRO
    assert season.career_phase_at_end == CareerPhase.DEVELOPMENT
    assert career.career_phase == CareerPhase.DEVELOPMENT


def test_peak_tracking():
    player = create_sample_player(age=18, potential=90.0)
    career = create_career("C17", player, club_id=10, start_date=date(2026, 7, 1), seed="SEED")
    perf = build_season_perf(player.id, minutes=2000, avg_rating=8.0)

    season = simulate_match_driven_season(career, perf)
    assert career.peak_ability == season.ending_ability
    assert career.peak_ovr == season.ending_ovr
    assert career.peak_age == 19


def test_snapshot_factor_persistence():
    player = create_sample_player(age=18)
    career = create_career("C18", player, club_id=10, start_date=date(2026, 7, 1), seed="SEED")
    perf = build_season_perf(player.id, minutes=2500, avg_rating=7.8)

    simulate_match_driven_season(career, perf)
    snapshot = career.snapshots[-1]
    assert snapshot.playing_time_input.playing_time_factor == 1.05
    assert snapshot.performance_input.performance_factor == 1.10


def test_deterministic_integration():
    p1 = create_sample_player("P_DET", age=18)
    p2 = create_sample_player("P_DET", age=18)

    c1 = create_career("C_DET", p1, club_id=10, start_date=date(2026, 7, 1), seed="SAME_SEED")
    c2 = create_career("C_DET", p2, club_id=10, start_date=date(2026, 7, 1), seed="SAME_SEED")

    perf1 = build_season_perf("P_DET", minutes=2100, avg_rating=7.3)
    perf2 = build_season_perf("P_DET", minutes=2100, avg_rating=7.3)

    s1 = simulate_match_driven_season(c1, perf1)
    s2 = simulate_match_driven_season(c2, perf2)

    assert s1.development_budget == s2.development_budget
    assert s1.ending_ability == s2.ending_ability
    assert s1.attribute_changes == s2.attribute_changes


def test_cross_process_determinism():
    cmd = [
        sys.executable,
        "-c",
        """
import json, sys
from datetime import date
from app.player.domain import Player, PlayerAttributes, PlayerState
from app.player.engine import current_ability
from app.career.engine import create_career, simulate_match_driven_season
from app.match.aggregation import SeasonPerformance

attrs = PlayerAttributes(
    acceleration=70, sprint_speed=72, finishing=75, shot_power=75, long_shots=70, volleys=65, penalties=65,
    vision=70, short_passing=70, long_passing=65, crossing=60, curve=60, agility=70, balance=70, ball_control=72,
    dribbling=74, reactions=70, defensive_awareness=35, standing_tackle=35, interceptions=30, heading=60,
    strength=65, stamina=70, jumping=65, aggression=60, decision_making=70, composure=70, creativity=70,
    positioning=75, concentration=65, work_rate=70, leadership=50,
    diving=10, handling=10, kicking=10, reflexes=10, speed=10, goalkeeper_positioning=10
)
player = Player(
    id='P_CROSS', name='Test', surname='Cross', nationality='Testland', birth_date=date(2008, 1, 15),
    height=180.0, weight=75.0, preferred_foot='Right', primary_position='ST', secondary_positions=(),
    attributes=attrs, current_ability=68.0, potential=85.0, development_rate=80.0, development_profile='FINISHER',
    personality={'professionalism': 70.0}, state=PlayerState(fitness=100.0, morale=100.0, confidence=100.0, happiness=100.0)
)
player.current_ability = current_ability(player)
career = create_career('C_CROSS', player, club_id=10, start_date=date(2026, 7, 1), seed='PROCESS_SEED')
perf = SeasonPerformance(
    player_id='P_CROSS', season_number=1, appearances=25, starts=25, substitute_appearances=0,
    minutes_played=2250, goals=12, assists=4, total_shots=40, shots_on_target=20, key_passes=15,
    tackles=6, interceptions=3, clearances=2, clean_sheets=0, average_rating=7.4, performance_factor=1.06, playing_time_factor=1.05
)
season = simulate_match_driven_season(career, perf)
res = {
    'budget': season.development_budget,
    'ending_ability': season.ending_ability,
    'attribute_changes': season.attribute_changes,
}
print(json.dumps(res, sort_keys=True))
"""
    ]

    res1 = subprocess.check_output(cmd, text=True).strip()
    res2 = subprocess.check_output(cmd, text=True).strip()

    assert res1 == res2


def test_no_duplicate_development_logic():
    match_files = [
        "backend/app/match/domain.py",
        "backend/app/match/lineup.py",
        "backend/app/match/resolution.py",
        "backend/app/match/performance.py",
        "backend/app/match/aggregation.py",
    ]

    forbidden_names = [
        "BASE_RATE",
        "POTENTIAL_GAP_MAX",
        "SOFT_CAPS",
        "DECLINE_RULES",
        "get_age_factor",
        "allocate_two_stage_development",
        "apply_decline_effects",
    ]

    for filepath in match_files:
        with open(filepath, "r", encoding="utf-8") as f:
            tree = ast.parse(f.read(), filename=filepath)

        for node in ast.walk(tree):
            if isinstance(node, ast.Name) and node.id in forbidden_names:
                pytest.fail(f"Forbidden development engine construct '{node.id}' found in '{filepath}'")


def test_existing_phase4_behavior_preserved():
    player = create_sample_player(age=18)
    c1 = create_career("C_P4_a", player, club_id=10, start_date=date(2026, 7, 1), seed="P4_SEED")

    # Standard Phase 4 simulate_season call
    season = simulate_season(c1, SeasonalPlayingTimeInput(minutes_played=2000), SeasonalPerformanceInput(average_rating=6.8))
    assert season.playing_time_input.playing_time_factor is None
    assert season.performance_input.performance_factor is None
    assert season.development_budget > 0.0


def test_end_to_end_synthetic_smoke():
    # Synthetic 1 match -> aggregate -> career simulation
    p_hero = create_sample_player("P_HERO", age=19)
    p_teammates = [create_sample_player(f"P_TEAM_{i}", age=20) for i in range(10)]
    home_players = [p_hero] + p_teammates
    away_players = [create_sample_player(f"P_AWAY_{i}", age=20) for i in range(11)]

    fmt = FORMATION_PRESETS["4-3-3"]
    context = MatchContext(
        match_id="SMOKE_MATCH_1",
        home_club_id=1,
        away_club_id=2,
        competition_type=CompetitionType.LEAGUE,
        competition_importance=50.0,
        match_importance=50.0,
        seed="SMOKE_SEED",
    )

    home_lineup = select_lineup(home_players, club_id=1, formation=fmt)
    away_lineup = select_lineup(away_players, club_id=2, formation=fmt)

    h_xi = calculate_xi_quality(home_lineup.starters, fmt)
    a_xi = calculate_xi_quality(away_lineup.starters, fmt)
    h_eff = calculate_effective_team_strength(h_xi, 75.0, 75.0, home_lineup.tactical_fit, 100.0, 100.0, club_id=1)
    a_eff = calculate_effective_team_strength(a_xi, 75.0, 75.0, away_lineup.tactical_fit, 100.0, 100.0, club_id=2)

    resolution = resolve_match_resolution(context, h_eff, a_eff)
    all_perfs, _ = simulate_player_performances(context, resolution, home_lineup, away_lineup)
    home_perfs = [p for p in all_perfs if p.player_id.startswith("P_HERO") or p.player_id.startswith("P_TEAM")]

    hero_perf = [p for p in home_perfs if p.player_id == "P_HERO"]
    assert len(hero_perf) == 1

    match_res = MatchResult(
        match_id=context.match_id,
        home_club_id=1,
        away_club_id=2,
        home_score=resolution.home_score,
        away_score=resolution.away_score,
        home_xg=resolution.home_xg,
        away_xg=resolution.away_xg,
        home_possession=resolution.home_possession,
        away_possession=resolution.away_possession,
        home_shots=resolution.home_shots,
        away_shots=resolution.away_shots,
        player_performances=all_perfs,
        events=[],
    )

    match_results = {context.match_id: match_res}
    season_perf = aggregate_season_performance(
        player_id="P_HERO",
        season_number=1,
        performances=hero_perf,
        match_results_map=match_results,
        player_club_id=1,
    )

    career = create_career("C_SMOKE", p_hero, club_id=1, start_date=date(2026, 7, 1), seed="SMOKE_SEED")
    init_ca = p_hero.current_ability

    simulated_season = simulate_match_driven_season(career, season_perf)
    assert simulated_season.is_completed is True
    assert p_hero.current_ability == simulated_season.ending_ability
    assert career.current_season_number == 2


def test_statistical_audit_1000_seasons():
    # Statistical audit comparing 1,000 Neutral vs High vs Low integrations
    neutral_budgets, neutral_ca_deltas = [], []
    high_budgets, high_ca_deltas = [], []
    low_budgets, low_ca_deltas = [], []

    for i in range(1000):
        # Deterministic variation across seeds
        seed = f"STAT_SEED_{i}"

        # Neutral
        p_n = create_sample_player(f"PN_{i}", age=18, potential=85.0)
        c_n = create_career(f"CN_{i}", p_n, club_id=10, start_date=date(2026, 7, 1), seed=seed)
        perf_n = build_season_perf(p_n.id, minutes=2000, avg_rating=6.8)
        s_n = simulate_match_driven_season(c_n, perf_n)
        neutral_budgets.append(s_n.development_budget)
        neutral_ca_deltas.append(s_n.ending_ability - s_n.starting_ability)

        # High
        p_h = create_sample_player(f"PH_{i}", age=18, potential=85.0)
        c_h = create_career(f"CH_{i}", p_h, club_id=10, start_date=date(2026, 7, 1), seed=seed)
        perf_h = build_season_perf(p_h.id, minutes=2600, avg_rating=7.7)
        s_h = simulate_match_driven_season(c_h, perf_h)
        high_budgets.append(s_h.development_budget)
        high_ca_deltas.append(s_h.ending_ability - s_h.starting_ability)

        # Low
        p_l = create_sample_player(f"PL_{i}", age=18, potential=85.0)
        c_l = create_career(f"CL_{i}", p_l, club_id=10, start_date=date(2026, 7, 1), seed=seed)
        perf_l = build_season_perf(p_l.id, minutes=500, avg_rating=6.0)
        s_l = simulate_match_driven_season(c_l, perf_l)
        low_budgets.append(s_l.development_budget)
        low_ca_deltas.append(s_l.ending_ability - s_l.starting_ability)

    avg_neutral_budget = sum(neutral_budgets) / 1000.0
    avg_high_budget = sum(high_budgets) / 1000.0
    avg_low_budget = sum(low_budgets) / 1000.0

    avg_neutral_ca_delta = sum(neutral_ca_deltas) / 1000.0
    avg_high_ca_delta = sum(high_ca_deltas) / 1000.0
    avg_low_ca_delta = sum(low_ca_deltas) / 1000.0

    assert avg_high_budget > avg_neutral_budget > avg_low_budget
    assert avg_high_ca_delta > avg_neutral_ca_delta > avg_low_ca_delta
