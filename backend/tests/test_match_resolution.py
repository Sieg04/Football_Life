import ast
import random
from pathlib import Path
import pytest

from app.match.domain import CompetitionType, MatchContext
from app.match.lineup import EffectiveTeamStrength
from app.match.resolution import (
    MatchResolutionState,
    calculate_possession,
    calculate_xg,
    derive_match_probabilities,
    get_sha256_match_rng,
    poisson_sample,
    resolve_match_resolution,
)


def _create_mock_context(seed: str = "SEED-001", match_id: str = "M-101", importance: float = 50.0) -> MatchContext:
    return MatchContext(
        match_id=match_id,
        home_club_id=1,
        away_club_id=2,
        competition_type=CompetitionType.LEAGUE,
        competition_importance=importance,
        match_importance=importance,
        seed=seed,
    )


def _create_mock_strength(club_id: int, eff_strength: float, tac_fit: float = 80.0) -> EffectiveTeamStrength:
    return EffectiveTeamStrength(
        club_id=club_id,
        xi_quality=eff_strength,
        tactical_fit=tac_fit,
        form_factor=70.0,
        fitness_factor=100.0,
        manager_quality=70.0,
        effective_strength=eff_strength,
    )


def test_1_equal_strength_balanced_xg() -> None:
    rng = random.Random(123)
    _, _, h_xg, a_xg = calculate_xg(75.0, 75.0, rng=rng)
    assert abs(h_xg - a_xg) < 1.0


def test_2_stronger_team_higher_xg() -> None:
    rng = random.Random(456)
    _, _, h_xg, a_xg = calculate_xg(85.0, 60.0, rng=rng)
    assert h_xg > a_xg


def test_3_xg_lower_bound() -> None:
    rng = random.Random(789)
    _, _, h_xg, a_xg = calculate_xg(1.0, 100.0, rng=rng)
    assert h_xg >= 0.15
    assert a_xg >= 0.15


def test_4_xg_upper_bound() -> None:
    rng = random.Random(101)
    _, _, h_xg, a_xg = calculate_xg(100.0, 1.0, rng=rng)
    assert h_xg <= 4.50
    assert a_xg <= 4.50


def test_5_same_seed_identical_result() -> None:
    ctx1 = _create_mock_context(seed="SAME-SEED-123", match_id="M-200")
    ctx2 = _create_mock_context(seed="SAME-SEED-123", match_id="M-200")
    str1 = _create_mock_strength(1, 78.0)
    str2 = _create_mock_strength(2, 72.0)

    res1 = resolve_match_resolution(ctx1, str1, str2)
    res2 = resolve_match_resolution(ctx2, str1, str2)

    assert res1.home_score == res2.home_score
    assert res1.away_score == res2.away_score
    assert res1.home_xg == res2.home_xg
    assert res1.away_xg == res2.away_xg
    assert res1.home_possession == res2.home_possession


def test_6_different_seed_can_produce_different_result() -> None:
    ctx1 = _create_mock_context(seed="SEED-AAA", match_id="M-201")
    ctx2 = _create_mock_context(seed="SEED-BBB", match_id="M-201")
    str1 = _create_mock_strength(1, 75.0)
    str2 = _create_mock_strength(2, 75.0)

    res1 = resolve_match_resolution(ctx1, str1, str2)
    res2 = resolve_match_resolution(ctx2, str1, str2)

    # Different seeds produce different random draws or xG
    assert res1.home_raw_xg != res2.home_raw_xg or res1.home_score != res2.home_score or res1.away_score != res2.away_score


def test_7_poisson_sample_integer_non_negative() -> None:
    rng = random.Random(999)
    for lam in (0.15, 1.0, 2.0, 4.5):
        sample = poisson_sample(lam, rng)
        assert isinstance(sample, int)
        assert sample >= 0


def test_8_high_lambda_higher_mean_goals() -> None:
    rng = random.Random(42)
    trials = 5000
    samples_low = [poisson_sample(0.5, rng) for _ in range(trials)]
    samples_high = [poisson_sample(3.5, rng) for _ in range(trials)]

    mean_low = sum(samples_low) / trials
    mean_high = sum(samples_high) / trials

    assert abs(mean_low - 0.5) < 0.1
    assert abs(mean_high - 3.5) < 0.1
    assert mean_high > mean_low


def test_9_derived_probabilities_sum_to_one() -> None:
    p_home, p_draw, p_away = derive_match_probabilities(1.8, 1.2)
    assert abs((p_home + p_draw + p_away) - 1.0) < 1e-5


def test_10_derived_probabilities_change_logically() -> None:
    p_home_eq, p_draw_eq, p_away_eq = derive_match_probabilities(1.5, 1.5)
    p_home_fav, p_draw_fav, p_away_fav = derive_match_probabilities(3.0, 0.5)

    assert abs(p_home_eq - p_away_eq) < 1e-4
    assert p_home_fav > p_home_eq
    assert p_away_fav < p_away_eq


def test_11_scores_generated_only_from_poisson() -> None:
    ctx = _create_mock_context()
    str1 = _create_mock_strength(1, 80.0)
    str2 = _create_mock_strength(2, 70.0)
    res = resolve_match_resolution(ctx, str1, str2)

    assert isinstance(res.home_score, int)
    assert isinstance(res.away_score, int)


def test_12_goals_less_or_equal_shots() -> None:
    ctx = _create_mock_context()
    str1 = _create_mock_strength(1, 80.0)
    str2 = _create_mock_strength(2, 70.0)
    res = resolve_match_resolution(ctx, str1, str2)

    assert res.home_score <= res.home_shots
    assert res.away_score <= res.away_shots


def test_13_goals_less_or_equal_shots_on_target() -> None:
    ctx = _create_mock_context()
    str1 = _create_mock_strength(1, 80.0)
    str2 = _create_mock_strength(2, 70.0)
    res = resolve_match_resolution(ctx, str1, str2)

    assert res.home_score <= res.home_shots_on_target
    assert res.away_score <= res.away_shots_on_target
    assert res.home_shots_on_target <= res.home_shots
    assert res.away_shots_on_target <= res.away_shots


def test_14_possession_remains_valid() -> None:
    ctx = _create_mock_context()
    str1 = _create_mock_strength(1, 80.0)
    str2 = _create_mock_strength(2, 70.0)
    res = resolve_match_resolution(ctx, str1, str2)

    assert 0.0 <= res.home_possession <= 100.0
    assert 0.0 <= res.away_possession <= 100.0
    assert abs((res.home_possession + res.away_possession) - 100.0) < 0.2


def test_15_home_advantage_influences_expected_strength() -> None:
    ctx = _create_mock_context()
    # Home effective strength includes home advantage in 5B calculation
    str_home = _create_mock_strength(1, 78.0)
    str_away = _create_mock_strength(2, 75.0)

    res = resolve_match_resolution(ctx, str_home, str_away)
    assert res.home_xg > res.away_xg


def test_16_match_importance_does_not_directly_multiply_xg() -> None:
    ctx_normal = _create_mock_context(seed="TEST-SEED", match_id="M-1", importance=20.0)
    ctx_crucial = _create_mock_context(seed="TEST-SEED", match_id="M-1", importance=100.0)

    str1 = _create_mock_strength(1, 75.0)
    str2 = _create_mock_strength(2, 75.0)

    res1 = resolve_match_resolution(ctx_normal, str1, str2)
    res2 = resolve_match_resolution(ctx_crucial, str1, str2)

    # Match importance does not multiply raw xG or clamped xG directly
    assert res1.home_raw_xg == res2.home_raw_xg
    assert res1.home_xg == res2.home_xg


def test_17_xg_range_respected_across_extremes() -> None:
    for h_str in (5.0, 50.0, 95.0, 150.0):
        for a_str in (5.0, 50.0, 95.0, 150.0):
            _, _, h_xg, a_xg = calculate_xg(h_str, a_str)
            assert 0.15 <= h_xg <= 4.50
            assert 0.15 <= a_xg <= 4.50


def test_18_no_player_performance_generation() -> None:
    ctx = _create_mock_context()
    str1 = _create_mock_strength(1, 75.0)
    str2 = _create_mock_strength(2, 75.0)
    res = resolve_match_resolution(ctx, str1, str2)

    assert not hasattr(res, "player_performances")
    assert not hasattr(res, "events")


def test_19_no_career_engine_calls() -> None:
    res_path = Path(__file__).resolve().parents[1] / "app" / "match" / "resolution.py"
    tree = ast.parse(res_path.read_text(encoding="utf-8"))

    forbidden_terms = {"career", "simulate_season", "development_budget", "soft_caps"}
    found_terms = set()

    for node in ast.walk(tree):
        if isinstance(node, ast.Name) and node.id.lower() in forbidden_terms:
            found_terms.add(node.id)
        elif isinstance(node, ast.FunctionDef) and node.name.lower() in forbidden_terms:
            found_terms.add(node.name)

    assert not found_terms, f"Found Career Engine references in resolution.py: {found_terms}"


def test_20_no_infrastructure_imports() -> None:
    res_path = Path(__file__).resolve().parents[1] / "app" / "match" / "resolution.py"
    tree = ast.parse(res_path.read_text(encoding="utf-8"))

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
    assert not forbidden_found, f"Found infrastructure imports in match resolution: {forbidden_found}"


def test_21_monte_carlo_10k_matches_audit() -> None:
    """Run a 10,000 match Monte Carlo audit reporting core statistical distributions."""
    num_matches = 10000
    home_wins = 0
    draws = 0
    away_wins = 0
    total_goals = 0
    goal_counts = []
    clean_sheets = 0
    zero_zero_draws = 0
    four_plus_team_goals = 0
    upsets = 0  # Weaker away team (60 strength vs 75 home strength) wins/draws

    str_fav = _create_mock_strength(1, 75.0)
    str_und = _create_mock_strength(2, 60.0)

    for i in range(num_matches):
        ctx = MatchContext(
            match_id=f"MC-{i}",
            home_club_id=1,
            away_club_id=2,
            competition_type=CompetitionType.LEAGUE,
            competition_importance=50.0,
            match_importance=50.0,
            seed=f"MC-SEED-{i}",
        )
        res = resolve_match_resolution(ctx, str_fav, str_und)

        match_goals = res.home_score + res.away_score
        total_goals += match_goals
        goal_counts.append(match_goals)

        if res.home_score > res.away_score:
            home_wins += 1
        elif res.home_score == res.away_score:
            draws += 1
            if res.home_score == 0:
                zero_zero_draws += 1
                upsets += 1  # Draw against favorite
        else:
            away_wins += 1
            upsets += 1  # Away win against favorite

        if res.home_score == 0 or res.away_score == 0:
            clean_sheets += 1

        if res.home_score >= 4 or res.away_score >= 4:
            four_plus_team_goals += 1

    goal_counts.sort()
    mean_goals = total_goals / num_matches
    median_goals = goal_counts[num_matches // 2]
    p90_goals = goal_counts[int(num_matches * 0.90)]

    home_win_pct = (home_wins / num_matches) * 100.0
    draw_pct = (draws / num_matches) * 100.0
    away_win_pct = (away_wins / num_matches) * 100.0
    clean_sheet_pct = (clean_sheets / num_matches) * 100.0
    zero_zero_pct = (zero_zero_draws / num_matches) * 100.0
    four_plus_pct = (four_plus_team_goals / num_matches) * 100.0
    upset_pct = (upsets / num_matches) * 100.0

    print("\n=================== MONTE CARLO 10k AUDIT RESULTS ===================")
    print(f"Total Matches Simulated: {num_matches}")
    print(f"Mean Goals / Match: {mean_goals:.2f}")
    print(f"Median Goals: {median_goals}")
    print(f"P90 Goals: {p90_goals}")
    print(f"Home Wins: {home_wins} ({home_win_pct:.1f}%)")
    print(f"Draws: {draws} ({draw_pct:.1f}%)")
    print(f"Away Wins: {away_wins} ({away_win_pct:.1f}%)")
    print(f"Clean Sheets (either team): {clean_sheets} ({clean_sheet_pct:.1f}%)")
    print(f"0-0 Scorelines: {zero_zero_draws} ({zero_zero_pct:.1f}%)")
    print(f"4+ Team Goals Matches: {four_plus_team_goals} ({four_plus_pct:.1f}%)")
    print(f"Upset Frequency (Draw/Away Win vs +15 Strength Fav): {upsets} ({upset_pct:.1f}%)")
    print("=====================================================================")

    # Sanity distribution assertions
    assert 1.5 <= mean_goals <= 4.0
    assert home_win_pct > away_win_pct  # Favorite at home wins more often
    assert upset_pct > 5.0  # Upsets are non-zero and plausible
