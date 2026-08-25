import ast
from datetime import date
import random
import pytest

from app.match.domain import CompetitionType, MatchContext, PlayerMatchPerformance, SimulationMode
from app.match.lineup import FORMATION_PRESETS, Lineup, LineupSlot, select_lineup
from app.match.performance import (
    allocate_player_shots,
    attribute_assists,
    calculate_contextual_match_rating,
    calculate_latent_influence,
    calculate_minutes_and_substitutions,
    distribute_chance_shares,
    generate_defensive_contributions,
    get_sha256_player_rng,
    resolve_goal_conversions,
    simulate_player_performances,
)
from app.match.resolution import MatchResolutionState
from app.player.domain import DevelopmentProfile, Player, PlayerAttributes, PlayerState


def _create_mock_player(
    player_id: str,
    pos: str,
    ca: float = 70.0,
    pot: float = 80.0,
    form: float = 70.0,
    fitness: float = 100.0,
    traits: tuple[str, ...] = (),
    finishing: float = 70.0,
    vision: float = 70.0,
) -> Player:
    attrs = PlayerAttributes(
        acceleration=70.0,
        sprint_speed=70.0,
        finishing=finishing,
        shot_power=70.0,
        long_shots=70.0,
        volleys=70.0,
        penalties=70.0,
        vision=vision,
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
        current_ability=ca,
        potential=pot,
        development_rate=70.0,
        development_profile=DevelopmentProfile.BALANCED,
        traits=traits,
        role_familiarity={
            "POACHER": 85.0,
            "PLAYMAKER": 85.0,
            "CENTRE_BACK": 85.0,
            "TRADITIONAL_KEEPER": 85.0,
            "WINGER": 85.0,
            "FULL_BACK": 85.0,
            "WING_BACK": 85.0,
            "BALL_WINNER": 85.0,
        },
        state=PlayerState(form=form, fitness=fitness),
    )


def _create_full_squad(prefix: str = "H") -> list[Player]:
    squad = [
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
        _create_mock_player(f"{prefix}_CM3", "CM"),
    ]
    return squad


def _create_mock_context(seed: str = "SEED-PERF", match_id: str = "M-PERF-1", mode: SimulationMode = SimulationMode.DETAILED) -> MatchContext:
    return MatchContext(
        match_id=match_id,
        home_club_id=1,
        away_club_id=2,
        competition_type=CompetitionType.LEAGUE,
        competition_importance=50.0,
        match_importance=50.0,
        seed=seed,
        simulation_mode=mode,
    )


def _create_mock_resolution() -> MatchResolutionState:
    return MatchResolutionState(
        home_effective_strength=75.0,
        away_effective_strength=70.0,
        home_raw_xg=1.8,
        away_raw_xg=1.1,
        home_xg=1.8,
        away_xg=1.1,
        home_score=2,
        away_score=1,
        home_possession=55.0,
        away_possession=45.0,
        home_shots=12,
        away_shots=8,
        home_shots_on_target=6,
        away_shots_on_target=3,
        derived_home_win_probability=0.55,
        derived_draw_probability=0.25,
        derived_away_win_probability=0.20,
    )


def test_1_deterministic_latent_influence() -> None:
    p = _create_mock_player("P1", "ST")
    rng1 = get_sha256_player_rng("SEED-100", "M-1", "P1", "influence")
    rng2 = get_sha256_player_rng("SEED-100", "M-1", "P1", "influence")

    inf1 = calculate_latent_influence(p, "ST", 80.0, 50.0, rng1)
    inf2 = calculate_latent_influence(p, "ST", 80.0, 50.0, rng2)

    assert inf1 == inf2
    assert 0.0 <= inf1 <= 100.0


def test_2_deterministic_player_performance() -> None:
    ctx1 = _create_mock_context(seed="DET-PERF-SEED")
    ctx2 = _create_mock_context(seed="DET-PERF-SEED")
    res = _create_mock_resolution()

    h_lineup = select_lineup(_create_full_squad("H"), club_id=1)
    a_lineup = select_lineup(_create_full_squad("A"), club_id=2)

    perfs1, events1 = simulate_player_performances(ctx1, res, h_lineup, a_lineup)
    perfs2, events2 = simulate_player_performances(ctx2, res, h_lineup, a_lineup)

    assert perfs1 == perfs2
    assert events1 == events2


def test_3_chance_shares_sum_to_one() -> None:
    squad = _create_full_squad("H")
    lineup = select_lineup(squad, club_id=1)
    latents = {s.player.id: 70.0 for s in lineup.starters}
    rng = random.Random(42)

    shares = distribute_chance_shares(lineup.starters, latents, rng)
    assert abs(sum(shares.values()) - 1.0) < 1e-5


def test_4_shots_sum_to_team_shots() -> None:
    squad = _create_full_squad("H")
    lineup = select_lineup(squad, club_id=1)
    latents = {s.player.id: 70.0 for s in lineup.starters}
    rng = random.Random(42)

    shares = distribute_chance_shares(lineup.starters, latents, rng)
    alloc = allocate_player_shots(lineup.starters, 12, 6, shares, rng)

    tot_shots = sum(s for s, sot in alloc.values())
    assert tot_shots == 12


def test_5_shots_on_target_less_or_equal_shots() -> None:
    squad = _create_full_squad("H")
    lineup = select_lineup(squad, club_id=1)
    latents = {s.player.id: 70.0 for s in lineup.starters}
    rng = random.Random(42)

    shares = distribute_chance_shares(lineup.starters, latents, rng)
    alloc = allocate_player_shots(lineup.starters, 12, 6, shares, rng)

    for pid, (s, sot) in alloc.items():
        assert sot <= s


def test_6_goals_assigned_equal_team_score() -> None:
    squad = _create_full_squad("H")
    lineup = select_lineup(squad, club_id=1)
    latents = {s.player.id: 70.0 for s in lineup.starters}
    rng = random.Random(42)

    shares = distribute_chance_shares(lineup.starters, latents, rng)
    alloc = allocate_player_shots(lineup.starters, 12, 6, shares, rng)
    goals = resolve_goal_conversions(lineup.starters, 3, alloc, None, 50.0, rng)

    assert sum(goals.values()) == 3


def test_7_goals_less_or_equal_shots_on_target() -> None:
    squad = _create_full_squad("H")
    lineup = select_lineup(squad, club_id=1)
    latents = {s.player.id: 70.0 for s in lineup.starters}
    rng = random.Random(42)

    shares = distribute_chance_shares(lineup.starters, latents, rng)
    alloc = allocate_player_shots(lineup.starters, 12, 6, shares, rng)
    goals = resolve_goal_conversions(lineup.starters, 2, alloc, None, 50.0, rng)

    for pid, g in goals.items():
        s, sot = alloc.get(pid, (0, 0))
        assert g <= max(1, sot)


def test_8_assists_less_or_equal_goals() -> None:
    squad = _create_full_squad("H")
    lineup = select_lineup(squad, club_id=1)
    latents = {s.player.id: 70.0 for s in lineup.starters}
    rng = random.Random(42)

    player_goals = {lineup.starters[0].player.id: 2}
    assists = attribute_assists(lineup.starters, 2, player_goals, latents, rng)

    assert sum(assists.values()) <= 2


def test_9_no_self_assists() -> None:
    squad = _create_full_squad("H")
    lineup = select_lineup(squad, club_id=1)
    st_id = next(s.player.id for s in lineup.starters if s.slot_position == "ST")

    player_goals = {st_id: 1}
    latents = {s.player.id: 70.0 for s in lineup.starters}

    for i in range(50):
        rng = random.Random(i)
        assists = attribute_assists(lineup.starters, 1, player_goals, latents, rng)
        assert assists.get(st_id, 0) == 0


def test_10_one_goal_match_stochastic_scorers_across_seeds() -> None:
    squad = _create_full_squad("H")
    lineup = select_lineup(squad, club_id=1)
    alloc = {s.player.id: (2, 1) for s in lineup.starters}

    unique_scorers = set()
    for i in range(100):
        goals = resolve_goal_conversions(lineup.starters, 1, alloc, None, 50.0, random.Random(i))
        for pid, g in goals.items():
            if g > 0:
                unique_scorers.add(pid)

    # Across 100 seeds in a 1-goal match, multiple different players score (not locked to single player)
    assert len(unique_scorers) > 1


def test_11_two_goal_match_multiple_scorers() -> None:
    squad = _create_full_squad("H")
    lineup = select_lineup(squad, club_id=1)
    alloc = {s.player.id: (3, 2) for s in lineup.starters}

    multi_scorer_matches = 0
    for i in range(100):
        goals = resolve_goal_conversions(lineup.starters, 2, alloc, None, 50.0, random.Random(i))
        scorers = [pid for pid, g in goals.items() if g > 0]
        if len(scorers) > 1:
            multi_scorer_matches += 1

    assert multi_scorer_matches > 30


def test_12_three_goal_match_braces_and_hattricks() -> None:
    squad = _create_full_squad("H")
    lineup = select_lineup(squad, club_id=1)
    alloc = {s.player.id: (4, 3) for s in lineup.starters}

    braces = 0
    hattricks = 0
    for i in range(500):
        goals = resolve_goal_conversions(lineup.starters, 3, alloc, None, 50.0, random.Random(i))
        max_g = max(goals.values()) if goals else 0
        if max_g == 2:
            braces += 1
        elif max_g == 3:
            hattricks += 1

    assert braces > 0
    assert hattricks > 0


def test_13_equal_sot_nonzero_probability() -> None:
    slots = [
        LineupSlot("ST", _create_mock_player("P_ST", "ST"), "POACHER", 85, 80, 80),
        LineupSlot("CAM", _create_mock_player("P_CAM", "CAM"), "PLAYMAKER", 85, 80, 80),
        LineupSlot("RW", _create_mock_player("P_RW", "RW"), "WINGER", 85, 80, 80),
        LineupSlot("CM", _create_mock_player("P_CM", "CM"), "PLAYMAKER", 85, 80, 80),
    ]
    alloc = {s.player.id: (2, 1) for s in slots}

    goal_counts = {s.player.id: 0 for s in slots}
    for i in range(1000):
        goals = resolve_goal_conversions(slots, 1, alloc, None, 50.0, random.Random(i))
        for pid, g in goals.items():
            goal_counts[pid] += g

    # EVERY position has a non-zero probability of scoring when they have SOT
    for pid in goal_counts:
        assert goal_counts[pid] > 0, f"Player {pid} had 0 goals across 1,000 matches!"


def test_14_st_more_likely_than_cam() -> None:
    slots = [
        LineupSlot("ST", _create_mock_player("P_ST", "ST"), "POACHER", 85, 80, 80),
        LineupSlot("CAM", _create_mock_player("P_CAM", "CAM"), "PLAYMAKER", 85, 80, 80),
    ]
    alloc = {"P_ST": (2, 1), "P_CAM": (2, 1)}

    st_goals = 0
    cam_goals = 0
    for i in range(1000):
        goals = resolve_goal_conversions(slots, 1, alloc, None, 50.0, random.Random(i))
        st_goals += goals.get("P_ST", 0)
        cam_goals += goals.get("P_CAM", 0)

    assert st_goals > cam_goals


def test_15_no_alphabetical_tiebreak_bias() -> None:
    p_z = _create_mock_player("Z_STRIKER", "ST")
    p_a = _create_mock_player("A_MIDFIELD", "CM")

    slot_st = LineupSlot("ST", p_z, "POACHER", 85.0, 80.0, 80.0)
    slot_cm = LineupSlot("CM", p_a, "PLAYMAKER", 85.0, 80.0, 80.0)

    alloc = {"Z_STRIKER": (2, 1), "A_MIDFIELD": (2, 1)}

    st_goals = 0
    cm_goals = 0
    for i in range(1000):
        goals = resolve_goal_conversions([slot_st, slot_cm], 1, alloc, None, 50.0, random.Random(i))
        st_goals += goals.get("Z_STRIKER", 0)
        cm_goals += goals.get("A_MIDFIELD", 0)

    assert st_goals > cm_goals


def test_16_substitution_limits() -> None:
    lineup = select_lineup(_create_full_squad("H"), club_id=1)
    rng = random.Random(42)

    minutes_map, sub_events = calculate_minutes_and_substitutions(lineup, 2, 0, 50.0, rng)
    assert len(sub_events) <= 5


def test_17_minutes_valid() -> None:
    lineup = select_lineup(_create_full_squad("H"), club_id=1)
    rng = random.Random(42)

    minutes_map, _ = calculate_minutes_and_substitutions(lineup, 1, 1, 50.0, rng)
    for mins in minutes_map.values():
        assert 0 <= mins <= 120


def test_18_ratings_bounded() -> None:
    p = _create_mock_player("P1", "ST")
    stats_great = {"goals": 3, "assists": 1, "shots": 5, "shots_on_target": 4, "key_passes": 2}
    stats_poor = {"goals": 0, "assists": 0, "shots": 4, "shots_on_target": 0, "key_passes": 0}

    r_great = calculate_contextual_match_rating(p, "ST", "POACHER", 90, stats_great, team_won=True, team_draw=False)
    r_poor = calculate_contextual_match_rating(p, "ST", "POACHER", 90, stats_poor, team_won=False, team_draw=False)

    assert 1.0 <= r_great <= 10.0
    assert 1.0 <= r_poor <= 10.0
    assert r_great > r_poor


def test_19_role_specific_rating_behavior() -> None:
    p_st = _create_mock_player("P_ST", "ST")
    p_gk = _create_mock_player("P_GK", "GK")

    stats_st = {"goals": 2, "assists": 0, "shots": 3, "shots_on_target": 2}
    stats_gk = {"saves": 6}

    r_st = calculate_contextual_match_rating(p_st, "ST", "POACHER", 90, stats_st, team_won=True, team_draw=False)
    r_gk = calculate_contextual_match_rating(p_gk, "GK", "TRADITIONAL_KEEPER", 90, stats_gk, team_won=True, team_draw=False)

    assert r_st >= 7.5
    assert r_gk >= 7.5


def test_20_no_infrastructure_imports() -> None:
    from pathlib import Path
    perf_path = Path(__file__).resolve().parents[1] / "app" / "match" / "performance.py"
    tree = ast.parse(perf_path.read_text(encoding="utf-8"))

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
    assert not forbidden_found, f"Found infrastructure imports in match performance: {forbidden_found}"


def test_21_no_career_engine_calls() -> None:
    from pathlib import Path
    perf_path = Path(__file__).resolve().parents[1] / "app" / "match" / "performance.py"
    tree = ast.parse(perf_path.read_text(encoding="utf-8"))

    forbidden_terms = {"career", "simulate_season", "development_budget", "soft_caps"}
    found_terms = set()

    for node in ast.walk(tree):
        if isinstance(node, ast.Name) and node.id.lower() in forbidden_terms:
            found_terms.add(node.id)
        elif isinstance(node, ast.FunctionDef) and node.name.lower() in forbidden_terms:
            found_terms.add(node.name)

    assert not found_terms, f"Found Career Engine references in performance.py: {found_terms}"


def test_22_no_season_aggregation_calls() -> None:
    from pathlib import Path
    perf_path = Path(__file__).resolve().parents[1] / "app" / "match" / "performance.py"
    tree = ast.parse(perf_path.read_text(encoding="utf-8"))

    forbidden_terms = {"aggregate_season", "performance_factor", "playing_time_factor"}
    found_terms = set()

    for node in ast.walk(tree):
        if isinstance(node, ast.Name) and node.id.lower() in forbidden_terms:
            found_terms.add(node.id)

    assert not found_terms, f"Found Season Aggregation references in performance.py: {found_terms}"


def test_23_fast_mode_vs_detailed_mode_consistency() -> None:
    ctx_fast = _create_mock_context(seed="MODE-SEED", mode=SimulationMode.FAST)
    ctx_det = _create_mock_context(seed="MODE-SEED", mode=SimulationMode.DETAILED)
    res = _create_mock_resolution()

    h_lineup = select_lineup(_create_full_squad("H"), club_id=1)
    a_lineup = select_lineup(_create_full_squad("A"), club_id=2)

    perfs_fast, _ = simulate_player_performances(ctx_fast, res, h_lineup, a_lineup)
    perfs_det, events_det = simulate_player_performances(ctx_det, res, h_lineup, a_lineup)

    assert len(perfs_fast) == len(perfs_det)
    assert len(events_det) > 0


def test_24_deterministic_repeated_execution() -> None:
    ctx = _create_mock_context(seed="REPEAT-SEED")
    res = _create_mock_resolution()

    h_lineup = select_lineup(_create_full_squad("H"), club_id=1)
    a_lineup = select_lineup(_create_full_squad("A"), club_id=2)

    for _ in range(5):
        perfs, events = simulate_player_performances(ctx, res, h_lineup, a_lineup)
        assert len(perfs) > 0


def test_25_monte_carlo_player_performance_audit() -> None:
    """Run a 100,000 player-match evaluation Monte Carlo re-audit reporting updated per-position metrics."""
    num_matches = 4500  # ~4,500 matches x 22 players = ~100,000 player-match evaluations
    ctx_mode = SimulationMode.FAST

    h_squad = _create_full_squad("H")
    a_squad = _create_full_squad("A")
    h_lineup = select_lineup(h_squad, club_id=1)
    a_lineup = select_lineup(a_squad, club_id=2)

    res = _create_mock_resolution()

    all_ratings = []
    ratings_by_pos = {}
    goals_by_pos = {}
    assists_by_pos = {}
    shots_by_pos = {}
    sot_by_pos = {}
    total_saves = 0
    sub_appearances = 0
    tot_player_matches = 0
    braces_count = 0
    hattricks_count = 0

    for i in range(num_matches):
        ctx = MatchContext(
            match_id=f"MC-P-{i}", home_club_id=1, away_club_id=2,
            competition_type=CompetitionType.LEAGUE, competition_importance=50.0,
            match_importance=50.0, seed=f"MC-PERF-REAUDIT-REDESIGN-{i}", simulation_mode=ctx_mode,
        )
        perfs, _ = simulate_player_performances(ctx, res, h_lineup, a_lineup)

        for p in perfs:
            tot_player_matches += 1
            all_ratings.append(p.rating)
            if not p.starter and p.minutes > 0:
                sub_appearances += 1

            if p.goals == 2:
                braces_count += 1
            elif p.goals >= 3:
                hattricks_count += 1

            pos = p.position
            if pos not in goals_by_pos:
                goals_by_pos[pos] = 0
                assists_by_pos[pos] = 0
                shots_by_pos[pos] = 0
                sot_by_pos[pos] = 0
                ratings_by_pos[pos] = []

            goals_by_pos[pos] += p.goals
            assists_by_pos[pos] += p.assists
            shots_by_pos[pos] += p.shots
            sot_by_pos[pos] += p.shots_on_target
            ratings_by_pos[pos].append(p.rating)

            if p.position == "GK":
                total_saves += p.saves

    all_ratings.sort()
    mean_rating = sum(all_ratings) / len(all_ratings)
    median_rating = all_ratings[len(all_ratings) // 2]
    p10_rating = all_ratings[int(len(all_ratings) * 0.10)]
    p90_rating = all_ratings[int(len(all_ratings) * 0.90)]

    print("\n=================== MONTE CARLO RE-AUDIT (STOCHASTIC ALLOCATION REDESIGN) ===================")
    print(f"Total Player-Match Evaluations: {tot_player_matches}")
    print(f"Overall Mean Rating: {mean_rating:.2f} | Median: {median_rating:.2f} | P10: {p10_rating:.2f} | P90: {p90_rating:.2f}")

    print("\nGoals, Shots & Conversion by Position:")
    for pos, g_cnt in sorted(goals_by_pos.items(), key=lambda x: -x[1]):
        s_cnt = shots_by_pos[pos]
        sot_cnt = sot_by_pos[pos]
        conv_rate = (g_cnt / sot_cnt * 100) if sot_cnt > 0 else 0.0
        print(f"  Pos: {pos:4s} | Goals: {g_cnt:5d} | Shots: {s_cnt:5d} (SOT: {sot_cnt:5d}) | Conversion: {conv_rate:.1f}%")

    print("\nAssists by Position:")
    for pos, a_cnt in sorted(assists_by_pos.items(), key=lambda x: -x[1]):
        print(f"  Pos: {pos:4s} | Assists: {a_cnt:5d}")

    print("\nRatings by Position:")
    for pos, r_list in sorted(ratings_by_pos.items(), key=lambda x: -sum(x[1])/len(x[1])):
        r_list.sort()
        r_mean = sum(r_list) / len(r_list)
        r_med = r_list[len(r_list) // 2]
        r_p10 = r_list[int(len(r_list) * 0.10)]
        r_p90 = r_list[int(len(r_list) * 0.90)]
        print(f"  Pos: {pos:4s} | Mean: {r_mean:.2f} | Med: {r_med:.2f} | P10: {r_p10:.2f} | P90: {r_p90:.2f}")

    print(f"\nBraces Recorded: {braces_count} | Hat-tricks Recorded: {hattricks_count}")
    print(f"Total GK Saves Recorded: {total_saves}")
    print(f"Substitute Appearance Rate: {sub_appearances / tot_player_matches * 100:.1f}%")
    print("=============================================================================================")

    # Qualitative hierarchy assertions
    assert goals_by_pos["ST"] > goals_by_pos["CAM"]
    assert goals_by_pos["CAM"] > goals_by_pos["CM"]
    assert goals_by_pos["LW"] > 0
    assert goals_by_pos["RW"] > 0
    assert (assists_by_pos["CAM"] + assists_by_pos["LW"] + assists_by_pos["RW"]) > assists_by_pos["CB"]
