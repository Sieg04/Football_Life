from app.career.context import build_club_context, calculate_playing_time
from app.football.competition_engine import simulate_full_season


def test_club_context_playing_time_ordering_is_realistic() -> None:
    elite = calculate_playing_time(90.0, "ST", build_club_context("Real Madrid"), form=82.0)
    mid = calculate_playing_time(82.0, "ST", build_club_context("Real Betis"), form=76.0)
    lower = calculate_playing_time(72.0, "ST", build_club_context("Lyon"), form=70.0)

    assert elite.expected_role.value == "STARTER"
    assert elite.expected_minutes >= 2500
    assert mid.expected_minutes >= 1800
    assert lower.expected_minutes < mid.expected_minutes
    assert elite.expected_minutes >= mid.expected_minutes >= lower.expected_minutes


def test_season_simulation_uses_contextual_minutes_for_top_players() -> None:
    elite = simulate_full_season(
        season_number=1,
        season_label="2026/27",
        player_id="p_elite_1",
        player_name="Elite Player",
        player_age=22,
        player_nationality="Spain",
        player_position="ST",
        player_ovr=90.0,
        club_name="Real Madrid",
        league_code="ESP1",
        seed="PLAYTIME-ELITE",
    )
    mid = simulate_full_season(
        season_number=1,
        season_label="2026/27",
        player_id="p_mid_1",
        player_name="Mid Player",
        player_age=24,
        player_nationality="Spain",
        player_position="ST",
        player_ovr=82.0,
        club_name="Real Betis",
        league_code="ESP1",
        seed="PLAYTIME-MID",
    )
    lower = simulate_full_season(
        season_number=1,
        season_label="2026/27",
        player_id="p_lower_1",
        player_name="Lower Player",
        player_age=25,
        player_nationality="France",
        player_position="ST",
        player_ovr=72.0,
        club_name="Lyon",
        league_code="FRA1",
        seed="PLAYTIME-LOWER",
    )

    assert elite.statistics.appearances >= 20
    assert elite.statistics.starts >= 12
    assert elite.statistics.minutes >= 1800
    assert mid.statistics.appearances >= 12
    assert lower.statistics.appearances >= 7
    assert elite.statistics.minutes >= mid.statistics.minutes >= lower.statistics.minutes
