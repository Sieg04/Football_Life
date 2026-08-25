import ast
import random
import pytest

from app.match.aggregation import (
    SeasonPerformance,
    aggregate_season_performance,
    calculate_performance_factor,
    calculate_playing_time_factor,
)
from app.match.domain import MatchResult, PlayerMatchPerformance


def _create_mock_perf(
    match_id: str = "M-101",
    player_id: str = "P-001",
    starter: bool = True,
    minutes: int = 90,
    rating: float = 7.0,
    goals: int = 0,
    assists: int = 0,
    shots: int = 1,
    sot: int = 1,
    key_passes: int = 0,
    tackles: int = 1,
    interceptions: int = 1,
    clearances: int = 1,
    saves: int = 0,
) -> PlayerMatchPerformance:
    actual_shots = max(shots, goals)
    actual_sot = max(sot, goals)
    return PlayerMatchPerformance(
        player_id=player_id,
        match_id=match_id,
        starter=starter,
        minutes=minutes,
        rating=rating,
        goals=goals,
        assists=assists,
        shots=actual_shots,
        shots_on_target=actual_sot,
        key_passes=key_passes,
        tackles=tackles,
        interceptions=interceptions,
        clearances=clearances,
        saves=saves,
        role="ST",
        position="ST",
        latent_influence=70.0,
    )


def test_1_single_match_aggregation() -> None:
    p = _create_mock_perf(minutes=90, rating=7.5, goals=1, assists=1)
    sp = aggregate_season_performance("P-001", 1, [p])

    assert sp.player_id == "P-001"
    assert sp.season_number == 1
    assert sp.appearances == 1
    assert sp.starts == 1
    assert sp.minutes_played == 90
    assert sp.goals == 1
    assert sp.assists == 1
    assert sp.average_rating == 7.5


def test_2_multi_match_aggregation() -> None:
    p1 = _create_mock_perf(match_id="M-1", minutes=90, goals=1, assists=0)
    p2 = _create_mock_perf(match_id="M-2", minutes=90, goals=2, assists=1)
    sp = aggregate_season_performance("P-001", 1, [p1, p2])

    assert sp.appearances == 2
    assert sp.goals == 3
    assert sp.assists == 1
    assert sp.minutes_played == 180


def test_3_appearances() -> None:
    p1 = _create_mock_perf(match_id="M-1", minutes=90)
    p2 = _create_mock_perf(match_id="M-2", minutes=0)  # unused sub
    sp = aggregate_season_performance("P-001", 1, [p1, p2])

    assert sp.appearances == 1


def test_4_starts() -> None:
    p1 = _create_mock_perf(match_id="M-1", starter=True, minutes=90)
    p2 = _create_mock_perf(match_id="M-2", starter=False, minutes=30)
    sp = aggregate_season_performance("P-001", 1, [p1, p2])

    assert sp.starts == 1


def test_5_substitute_appearances() -> None:
    p1 = _create_mock_perf(match_id="M-1", starter=True, minutes=90)
    p2 = _create_mock_perf(match_id="M-2", starter=False, minutes=30)
    sp = aggregate_season_performance("P-001", 1, [p1, p2])

    assert sp.substitute_appearances == 1


def test_6_total_minutes() -> None:
    p1 = _create_mock_perf(match_id="M-1", minutes=90)
    p2 = _create_mock_perf(match_id="M-2", minutes=45)
    sp = aggregate_season_performance("P-001", 1, [p1, p2])

    assert sp.minutes_played == 135


def test_7_goals_aggregation() -> None:
    p1 = _create_mock_perf(match_id="M-1", goals=2)
    p2 = _create_mock_perf(match_id="M-2", goals=1)
    sp = aggregate_season_performance("P-001", 1, [p1, p2])

    assert sp.goals == 3


def test_8_assists_aggregation() -> None:
    p1 = _create_mock_perf(match_id="M-1", assists=1)
    p2 = _create_mock_perf(match_id="M-2", assists=2)
    sp = aggregate_season_performance("P-001", 1, [p1, p2])

    assert sp.assists == 3


def test_9_shots_aggregation() -> None:
    p1 = _create_mock_perf(match_id="M-1", shots=4)
    p2 = _create_mock_perf(match_id="M-2", shots=3)
    sp = aggregate_season_performance("P-001", 1, [p1, p2])

    assert sp.total_shots == 7


def test_10_sot_aggregation() -> None:
    p1 = _create_mock_perf(match_id="M-1", shots=4, sot=2)
    p2 = _create_mock_perf(match_id="M-2", shots=3, sot=2)
    sp = aggregate_season_performance("P-001", 1, [p1, p2])

    assert sp.shots_on_target == 4


def test_11_key_passes_aggregation() -> None:
    p1 = _create_mock_perf(match_id="M-1", key_passes=3)
    p2 = _create_mock_perf(match_id="M-2", key_passes=1)
    sp = aggregate_season_performance("P-001", 1, [p1, p2])

    assert sp.key_passes == 4


def test_12_defensive_stats_aggregation() -> None:
    p1 = _create_mock_perf(match_id="M-1", tackles=2, interceptions=3, clearances=4)
    p2 = _create_mock_perf(match_id="M-2", tackles=1, interceptions=2, clearances=1)
    sp = aggregate_season_performance("P-001", 1, [p1, p2])

    assert sp.tackles == 3
    assert sp.interceptions == 5
    assert sp.clearances == 5


def test_13_weighted_average_rating() -> None:
    # 90 mins @ 8.0 = 720
    # 30 mins @ 6.0 = 180
    # Weighted avg = (720 + 180) / 120 = 900 / 120 = 7.50
    p1 = _create_mock_perf(match_id="M-1", minutes=90, rating=8.0)
    p2 = _create_mock_perf(match_id="M-2", minutes=30, rating=6.0)
    sp = aggregate_season_performance("P-001", 1, [p1, p2])

    assert sp.average_rating == 7.50


def test_14_performance_factor_baseline_6_8() -> None:
    factor = calculate_performance_factor(6.8)
    assert factor == 1.00


def test_15_performance_factor_above_baseline() -> None:
    factor = calculate_performance_factor(7.8)
    assert factor == 1.10


def test_16_performance_factor_below_baseline() -> None:
    factor = calculate_performance_factor(5.8)
    assert factor == 0.90


def test_17_performance_factor_lower_clamp() -> None:
    factor = calculate_performance_factor(4.0)
    assert factor == 0.80


def test_18_performance_factor_upper_clamp() -> None:
    factor = calculate_performance_factor(9.5)
    assert factor == 1.20


def test_19_playing_time_boundary_values() -> None:
    assert calculate_playing_time_factor(0) == 0.30
    assert calculate_playing_time_factor(300) == 0.30
    assert calculate_playing_time_factor(301) == 0.55
    assert calculate_playing_time_factor(750) == 0.55
    assert calculate_playing_time_factor(751) == 0.80
    assert calculate_playing_time_factor(1400) == 0.80
    assert calculate_playing_time_factor(1401) == 1.00
    assert calculate_playing_time_factor(2200) == 1.00
    assert calculate_playing_time_factor(2201) == 1.05
    assert calculate_playing_time_factor(3000) == 1.05
    assert calculate_playing_time_factor(3001) == 1.00


def test_20_clean_sheet_counting() -> None:
    p1 = _create_mock_perf(match_id="M-1", minutes=90)
    p2 = _create_mock_perf(match_id="M-2", minutes=90)

    res1 = MatchResult("M-1", 1, 2, 1, 0, 1.2, 0.4, 55.0, 45.0, 10, 5, [p1], [])  # Clean sheet
    res2 = MatchResult("M-2", 1, 2, 2, 1, 1.8, 0.9, 50.0, 50.0, 12, 6, [p2], [])  # Conceded 1 goal

    match_map = {"M-1": res1, "M-2": res2}
    sp = aggregate_season_performance("P-001", 1, [p1, p2], match_map)

    assert sp.clean_sheets == 1


def test_21_unused_substitute_not_counted_in_clean_sheet() -> None:
    p_unused = _create_mock_perf(match_id="M-1", minutes=0, starter=False)
    res1 = MatchResult("M-1", 1, 2, 1, 0, 1.2, 0.4, 55.0, 45.0, 10, 5, [p_unused], [])

    sp = aggregate_season_performance("P-001", 1, [p_unused], {"M-1": res1})
    assert sp.clean_sheets == 0


def test_22_duplicate_match_rejection() -> None:
    p1 = _create_mock_perf(match_id="M-1")
    p2 = _create_mock_perf(match_id="M-1")  # Duplicate match_id for same player

    with pytest.raises(ValueError, match="Duplicate match record for match_id 'M-1'"):
        aggregate_season_performance("P-001", 1, [p1, p2])


def test_23_mixed_player_rejection() -> None:
    p1 = _create_mock_perf(match_id="M-1", player_id="P-001")
    p2 = _create_mock_perf(match_id="M-2", player_id="P-002")  # Different player_id

    with pytest.raises(ValueError, match="Mixed player IDs in season aggregation: expected 'P-001', got 'P-002'"):
        aggregate_season_performance("P-001", 1, [p1, p2])


def test_24_empty_season_behavior() -> None:
    sp = aggregate_season_performance("P-001", 1, [])

    assert sp.player_id == "P-001"
    assert sp.season_number == 1
    assert sp.appearances == 0
    assert sp.minutes_played == 0
    assert sp.average_rating == 6.8
    assert sp.performance_factor == 1.00
    assert sp.playing_time_factor == 0.30


def test_25_deterministic_aggregation() -> None:
    p1 = _create_mock_perf(match_id="M-1", minutes=90, goals=1, rating=7.5)
    p2 = _create_mock_perf(match_id="M-2", minutes=60, goals=0, rating=6.8)

    sp1 = aggregate_season_performance("P-001", 1, [p1, p2])
    sp2 = aggregate_season_performance("P-001", 1, [p1, p2])

    assert sp1 == sp2


def test_26_input_order_independence() -> None:
    p1 = _create_mock_perf(match_id="M-1", minutes=90, goals=1, rating=7.5)
    p2 = _create_mock_perf(match_id="M-2", minutes=60, goals=0, rating=6.8)
    p3 = _create_mock_perf(match_id="M-3", minutes=45, goals=2, rating=8.2)

    list1 = [p1, p2, p3]
    list2 = [p3, p1, p2]

    sp1 = aggregate_season_performance("P-001", 1, list1)
    sp2 = aggregate_season_performance("P-001", 1, list2)

    assert sp1 == sp2


def test_27_no_rng_usage() -> None:
    from pathlib import Path
    agg_path = Path(__file__).resolve().parents[1] / "app" / "match" / "aggregation.py"
    tree = ast.parse(agg_path.read_text(encoding="utf-8"))

    forbidden_terms = {"random", "rng", "randint", "choices", "seed", "hashlib"}
    found_terms = set()

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name in forbidden_terms:
                    found_terms.add(alias.name)
        elif isinstance(node, ast.ImportFrom):
            if node.module and node.module in forbidden_terms:
                found_terms.add(node.module)

    assert not found_terms, f"Found RNG references in aggregation.py: {found_terms}"


def test_28_no_infrastructure_imports() -> None:
    from pathlib import Path
    agg_path = Path(__file__).resolve().parents[1] / "app" / "match" / "aggregation.py"
    tree = ast.parse(agg_path.read_text(encoding="utf-8"))

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
    assert not forbidden_found, f"Found infrastructure imports in match aggregation: {forbidden_found}"


def test_29_statistical_sanity_audit_1000_player_seasons() -> None:
    """Run a read-only 1,000 player-seasons statistical sanity audit."""
    num_seasons = 1000
    matches_per_season = 38
    rng = random.Random(42)

    sp_list: list[SeasonPerformance] = []

    for s_idx in range(num_seasons):
        pid = f"PLAYER-{s_idx}"
        match_perfs = []
        tot_goals_sim = 0
        tot_ast_sim = 0
        tot_mins_sim = 0

        for m_idx in range(matches_per_season):
            m_id = f"S{s_idx}-M{m_idx}"
            starter = rng.random() < 0.85
            mins = 90 if starter else (int(rng.uniform(15, 30)) if rng.random() < 0.6 else 0)
            rating = max(1.0, min(10.0, round(rng.gauss(6.8, 0.6), 1))) if mins > 0 else 6.0

            g = int(rng.choices([0, 1, 2, 3], weights=[0.80, 0.15, 0.04, 0.01])[0]) if mins > 0 else 0
            a = int(rng.choices([0, 1, 2], weights=[0.85, 0.12, 0.03])[0]) if mins > 0 else 0

            tot_goals_sim += g
            tot_ast_sim += a
            tot_mins_sim += mins

            perf = _create_mock_perf(
                match_id=m_id, player_id=pid, starter=starter, minutes=mins, rating=rating,
                goals=g, assists=a, shots=g + int(rng.uniform(0, 3)), sot=g + int(rng.uniform(0, 1))
            )
            match_perfs.append(perf)

        sp = aggregate_season_performance(pid, 1, match_perfs)
        sp_list.append(sp)

        # Invariant checks
        assert sp.goals == tot_goals_sim
        assert sp.assists == tot_ast_sim
        assert sp.minutes_played == tot_mins_sim

    apps = [sp.appearances for sp in sp_list]
    starts = [sp.starts for sp in sp_list]
    mins = [sp.minutes_played for sp in sp_list]
    goals = [sp.goals for sp in sp_list]
    assists = [sp.assists for sp in sp_list]
    ratings = [sp.average_rating for sp in sp_list]
    perf_factors = [sp.performance_factor for sp in sp_list]
    pt_factors = [sp.playing_time_factor for sp in sp_list]

    mins.sort()
    mean_app = sum(apps) / num_seasons
    mean_starts = sum(starts) / num_seasons
    mean_mins = sum(mins) / num_seasons
    median_mins = mins[num_seasons // 2]
    p10_mins = mins[int(num_seasons * 0.10)]
    p90_mins = mins[int(num_seasons * 0.90)]

    mean_goals = sum(goals) / num_seasons
    mean_assists = sum(assists) / num_seasons
    mean_rating = sum(ratings) / num_seasons
    mean_pf = sum(perf_factors) / num_seasons
    mean_ptf = sum(pt_factors) / num_seasons

    print("\n=================== 1,000 PLAYER-SEASONS STATISTICAL SANITY AUDIT ===================")
    print(f"Total Player Seasons Analyzed: {num_seasons}")
    print(f"Appearances -> Mean: {mean_app:.1f} | Starts -> Mean: {mean_starts:.1f}")
    print(f"Minutes -> Mean: {mean_mins:.1f} | Median: {median_mins} | P10: {p10_mins} | P90: {p90_mins}")
    print(f"Season Goals -> Mean: {mean_goals:.2f} | Max: {max(goals)}")
    print(f"Season Assists -> Mean: {mean_assists:.2f} | Max: {max(assists)}")
    print(f"Season Avg Rating -> Mean: {mean_rating:.2f} | Min: {min(ratings):.2f} | Max: {max(ratings):.2f}")
    print(f"Performance Factor -> Mean: {mean_pf:.3f} | Min: {min(perf_factors):.2f} | Max: {max(perf_factors):.2f}")
    print(f"Playing Time Factor -> Mean: {mean_ptf:.3f} | Min: {min(pt_factors):.2f} | Max: {max(pt_factors):.2f}")
    print("=====================================================================================")

    assert 25.0 <= mean_app <= 38.0
    assert 2000 <= mean_mins <= 3500
    assert 0.80 <= mean_pf <= 1.20
    assert 0.30 <= mean_ptf <= 1.05
