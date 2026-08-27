import json
import subprocess
import sys
from datetime import date
import pytest

from app.competition.domain import (
    CompetitionParticipant,
    CompetitionSeason,
    CompetitionStage,
    CompetitionStageType,
)
from app.competition.form import (
    FormRecord,
    calculate_form_points,
    calculate_form_rate,
    calculate_goal_difference,
)
from app.competition.season_state import (
    CompetitionSeasonState,
    apply_match_result_to_season_state,
    apply_match_results_to_season_state,
    get_club_form,
    get_ranked_standings,
    get_season_club_rank,
    initialize_competition_season_state,
)
from app.competition.standings import (
    PointsRule,
    StandingEntry,
    StandingsTable,
    initialize_standings,
    rank_standings,
)
from app.match.domain import MatchResult, PlayerMatchPerformance


def _make_match_result(
    match_id: str,
    home_club_id: int,
    away_club_id: int,
    home_score: int,
    away_score: int,
) -> MatchResult:
    return MatchResult(
        match_id=match_id,
        home_club_id=home_club_id,
        away_club_id=away_club_id,
        home_score=home_score,
        away_score=away_score,
        home_xg=1.5,
        away_xg=1.0,
        home_possession=55.0,
        away_possession=45.0,
        home_shots=10,
        away_shots=8,
        player_performances=[],
        events=[],
    )


def _make_season(season_id: str = "season_1", club_ids: tuple[int, ...] = (1, 2, 3, 4)) -> CompetitionSeason:
    participants = tuple(
        CompetitionParticipant(
            competition_season_id=season_id,
            club_id=cid,
            seed=f"seed_{cid}",
        )
        for cid in club_ids
    )
    stage = CompetitionStage(
        id=f"{season_id}_stage_1",
        competition_season_id=season_id,
        stage_type=CompetitionStageType.REGULAR_SEASON,
        stage_number=1,
        participant_club_ids=club_ids,
    )
    return CompetitionSeason(
        id=season_id,
        competition_id="comp_1",
        season_label="2024/2025",
        start_date=date(2024, 8, 1),
        end_date=date(2025, 5, 31),
        participants=participants,
        stages=(stage,),
        seed="season_seed",
    )


# -----------------------------------------------------------------------------
# State Validation & Construction Tests
# -----------------------------------------------------------------------------


def test_competition_season_state_valid() -> None:
    season = _make_season()
    state = initialize_competition_season_state(season)
    assert state.competition_season_id == "season_1"
    assert len(state.standings.entries) == 4
    assert len(state.form_table) == 4
    assert state.processed_match_ids == ()


def test_competition_season_state_invalid_season_id() -> None:
    season = _make_season()
    standings = initialize_standings(season)
    form_table = {cid: FormRecord(club_id=cid) for cid in (1, 2, 3, 4)}
    with pytest.raises(ValueError, match="competition_season_id must be a non-empty string"):
        CompetitionSeasonState(
            competition_season_id="",
            standings=standings,
            form_table=form_table,
        )


def test_competition_season_state_standings_mismatch() -> None:
    season_a = _make_season("season_A")
    standings_a = initialize_standings(season_a)
    form_table = {cid: FormRecord(club_id=cid) for cid in (1, 2, 3, 4)}
    with pytest.raises(ValueError, match="does not match competition_season_id"):
        CompetitionSeasonState(
            competition_season_id="season_B",
            standings=standings_a,
            form_table=form_table,
        )


def test_competition_season_state_form_table_club_id_mismatch() -> None:
    season = _make_season()
    standings = initialize_standings(season)
    # Missing club 4, extra club 5
    form_table = {1: FormRecord(1), 2: FormRecord(2), 3: FormRecord(3), 5: FormRecord(5)}
    with pytest.raises(ValueError, match="Form table club IDs"):
        CompetitionSeasonState(
            competition_season_id="season_1",
            standings=standings,
            form_table=form_table,
        )


def test_competition_season_state_duplicate_processed_match_ids() -> None:
    season = _make_season()
    standings = initialize_standings(season)
    form_table = {cid: FormRecord(club_id=cid) for cid in (1, 2, 3, 4)}
    with pytest.raises(ValueError, match="duplicate match IDs found"):
        CompetitionSeasonState(
            competition_season_id="season_1",
            standings=standings,
            form_table=form_table,
            processed_match_ids=("m1", "m1"),
        )


def test_competition_season_state_invalid_form_record_type() -> None:
    season = _make_season()
    standings = initialize_standings(season)
    form_table = {1: FormRecord(1), 2: FormRecord(2), 3: FormRecord(3), 4: "not_a_form_record"}
    with pytest.raises(TypeError, match="is not a FormRecord"):
        CompetitionSeasonState(
            competition_season_id="season_1",
            standings=standings,
            form_table=form_table,
        )


def test_competition_season_state_form_record_key_mismatch() -> None:
    season = _make_season()
    standings = initialize_standings(season)
    form_table = {1: FormRecord(1), 2: FormRecord(2), 3: FormRecord(3), 4: FormRecord(5)}
    with pytest.raises(ValueError, match="does not match form_table key"):
        CompetitionSeasonState(
            competition_season_id="season_1",
            standings=standings,
            form_table=form_table,
        )


# -----------------------------------------------------------------------------
# Initialization Tests
# -----------------------------------------------------------------------------


def test_initialize_competition_season_state_defaults() -> None:
    season = _make_season()
    state = initialize_competition_season_state(season)
    for cid in (1, 2, 3, 4):
        rec = state.form_table[cid]
        assert rec.club_id == cid
        assert rec.window_size == 5
        assert rec.results == ()
        assert rec.goals_for == ()
        assert rec.goals_against == ()


def test_initialize_competition_season_state_custom_points_rule_and_window() -> None:
    season = _make_season()
    rule = PointsRule(win_points=2, draw_points=1, loss_points=0)
    state = initialize_competition_season_state(season, points_rule=rule, form_window_size=3)
    assert state.standings.points_rule == rule
    for cid in (1, 2, 3, 4):
        assert state.form_table[cid].window_size == 3


def test_initialize_competition_season_state_invalid_window() -> None:
    season = _make_season()
    with pytest.raises(ValueError, match="form_window_size must be >= 1"):
        initialize_competition_season_state(season, form_window_size=0)


def test_initialize_competition_season_state_does_not_mutate_season() -> None:
    season = _make_season()
    stage_count_before = len(season.stages)
    initialize_competition_season_state(season)
    assert len(season.stages) == stage_count_before


# -----------------------------------------------------------------------------
# Single Result & Form Update Tests
# -----------------------------------------------------------------------------


def test_apply_single_match_result_home_win() -> None:
    season = _make_season()
    state = initialize_competition_season_state(season)

    match = _make_match_result("m1", home_club_id=1, away_club_id=2, home_score=2, away_score=0)
    new_state = apply_match_result_to_season_state(state, match)

    assert new_state is not state
    assert new_state.processed_match_ids == ("m1",)
    assert state.processed_match_ids == ()

    # Home form & standings
    home_entry = next(e for e in new_state.standings.entries if e.club_id == 1)
    assert home_entry.played == 1
    assert home_entry.wins == 1
    assert home_entry.points == 3
    assert home_entry.goals_for == 2
    assert home_entry.goals_against == 0

    home_form = new_state.form_table[1]
    assert home_form.results == ("W",)
    assert home_form.goals_for == (2,)
    assert home_form.goals_against == (0,)

    # Away form & standings
    away_entry = next(e for e in new_state.standings.entries if e.club_id == 2)
    assert away_entry.played == 1
    assert away_entry.losses == 1
    assert away_entry.points == 0
    assert away_entry.goals_for == 0
    assert away_entry.goals_against == 2

    away_form = new_state.form_table[2]
    assert away_form.results == ("L",)
    assert away_form.goals_for == (0,)
    assert away_form.goals_against == (2,)


def test_apply_single_match_result_draw() -> None:
    season = _make_season()
    state = initialize_competition_season_state(season)

    match = _make_match_result("m1", home_club_id=1, away_club_id=2, home_score=1, away_score=1)
    new_state = apply_match_result_to_season_state(state, match)

    assert new_state.form_table[1].results == ("D",)
    assert new_state.form_table[2].results == ("D",)
    assert next(e.points for e in new_state.standings.entries if e.club_id == 1) == 1
    assert next(e.points for e in new_state.standings.entries if e.club_id == 2) == 1


def test_apply_single_match_result_away_win() -> None:
    season = _make_season()
    state = initialize_competition_season_state(season)

    match = _make_match_result("m1", home_club_id=1, away_club_id=2, home_score=0, away_score=3)
    new_state = apply_match_result_to_season_state(state, match)

    assert new_state.form_table[1].results == ("L",)
    assert new_state.form_table[2].results == ("W",)
    assert next(e.points for e in new_state.standings.entries if e.club_id == 1) == 0
    assert next(e.points for e in new_state.standings.entries if e.club_id == 2) == 3


# -----------------------------------------------------------------------------
# Apply Result Validation & Duplicate Protection Tests
# -----------------------------------------------------------------------------


def test_apply_match_result_duplicate_match_id_raises() -> None:
    season = _make_season()
    state = initialize_competition_season_state(season)

    m1 = _make_match_result("m1", home_club_id=1, away_club_id=2, home_score=1, away_score=0)
    m2 = _make_match_result("m2", home_club_id=3, away_club_id=4, home_score=0, away_score=0)

    state_after_m1 = apply_match_result_to_season_state(state, m1)
    state_after_m2 = apply_match_result_to_season_state(state_after_m1, m2)

    # Re-apply m1
    with pytest.raises(ValueError, match="has already been processed"):
        apply_match_result_to_season_state(state_after_m2, m1)

    # State remains unchanged
    assert state_after_m2.processed_match_ids == ("m1", "m2")


def test_apply_match_result_unknown_club_raises() -> None:
    season = _make_season()
    state = initialize_competition_season_state(season)

    match = _make_match_result("m1", home_club_id=1, away_club_id=99, home_score=1, away_score=0)
    with pytest.raises(ValueError, match="not found in season state form table"):
        apply_match_result_to_season_state(state, match)


def test_apply_match_result_invalid_result_type() -> None:
    season = _make_season()
    state = initialize_competition_season_state(season)
    with pytest.raises(TypeError, match="must be a MatchResult instance"):
        apply_match_result_to_season_state(state, "not_a_result")  # type: ignore


# -----------------------------------------------------------------------------
# Batch Application & Form Window Tests
# -----------------------------------------------------------------------------


def test_apply_match_results_batch() -> None:
    season = _make_season()
    state = initialize_competition_season_state(season)

    matches = [
        _make_match_result("m1", 1, 2, 2, 0),
        _make_match_result("m2", 3, 4, 1, 1),
    ]
    new_state = apply_match_results_to_season_state(state, matches)
    assert new_state.processed_match_ids == ("m1", "m2")


def test_form_window_truncation() -> None:
    season = _make_season(club_ids=(1, 2))
    state = initialize_competition_season_state(season, form_window_size=5)

    # 7 matches between club 1 and club 2
    matches = [
        _make_match_result(f"m{i}", 1, 2, 1, 0) for i in range(1, 8)
    ]
    final_state = apply_match_results_to_season_state(state, matches)

    form_1 = final_state.form_table[1]
    assert len(form_1.results) == 5
    assert form_1.results == ("W", "W", "W", "W", "W")
    assert form_1.goals_for == (1, 1, 1, 1, 1)
    assert form_1.goals_against == (0, 0, 0, 0, 0)


# -----------------------------------------------------------------------------
# Delegation & Accessor Helpers Tests
# -----------------------------------------------------------------------------


def test_get_ranked_standings_delegation() -> None:
    season = _make_season()
    state = initialize_competition_season_state(season)
    m1 = _make_match_result("m1", 1, 2, 3, 0)
    state = apply_match_result_to_season_state(state, m1)

    ranked = get_ranked_standings(state)
    expected = rank_standings(state.standings)
    assert ranked == expected
    assert ranked[0].club_id == 1


def test_get_season_club_rank_delegation() -> None:
    season = _make_season()
    state = initialize_competition_season_state(season)
    m1 = _make_match_result("m1", 1, 2, 3, 0)
    state = apply_match_result_to_season_state(state, m1)

    assert get_season_club_rank(state, 1) == 1
    assert get_season_club_rank(state, 2) == 4


def test_get_club_form_delegation_and_metrics() -> None:
    season = _make_season()
    state = initialize_competition_season_state(season)
    m1 = _make_match_result("m1", 1, 2, 2, 1)
    state = apply_match_result_to_season_state(state, m1)

    form_1 = get_club_form(state, 1)
    assert form_1 == state.form_table[1]
    assert calculate_form_points(form_1) == 3
    assert calculate_form_rate(form_1) == 1.0
    assert calculate_goal_difference(form_1) == 1

    form_2 = get_club_form(state, 2)
    assert calculate_form_points(form_2) == 0
    assert calculate_form_rate(form_2) == 0.0
    assert calculate_goal_difference(form_2) == -1


def test_get_club_form_unknown_club() -> None:
    season = _make_season()
    state = initialize_competition_season_state(season)
    with pytest.raises(ValueError, match="not found in season state form table"):
        get_club_form(state, 99)


# -----------------------------------------------------------------------------
# Controlled Audit A — 4 Team Mini Season
# -----------------------------------------------------------------------------


def test_controlled_audit_a_4_team_mini_season() -> None:
    # A=1, B=2, C=3, D=4
    season = _make_season(club_ids=(1, 2, 3, 4))
    state = initialize_competition_season_state(season)

    mini_season_results = [
        _make_match_result("m1", 1, 2, 2, 0),  # A 2-0 B
        _make_match_result("m2", 3, 4, 1, 1),  # C 1-1 D
        _make_match_result("m3", 1, 3, 1, 1),  # A 1-1 C
        _make_match_result("m4", 2, 4, 0, 2),  # B 0-2 D
        _make_match_result("m5", 1, 4, 0, 1),  # A 0-1 D
        _make_match_result("m6", 2, 3, 1, 1),  # B 1-1 C
    ]

    final_state = apply_match_results_to_season_state(state, mini_season_results)

    assert len(final_state.standings.entries) == 4
    assert len(final_state.processed_match_ids) == 6

    # Verify total played appearances across all teams = 2 * N = 12
    total_played = sum(e.played for e in final_state.standings.entries)
    assert total_played == 12

    # Verify GF == GA across standings table
    total_gf = sum(e.goals_for for e in final_state.standings.entries)
    total_ga = sum(e.goals_against for e in final_state.standings.entries)
    assert total_gf == total_ga == 11

    # Team D (4): 2 wins (vs B, vs A), 1 draw (vs C) -> 7 pts (GF 4, GA 1, GD +3)
    # Team A (1): 1 win (vs B), 1 draw (vs C), 1 loss (vs D) -> 4 pts (GF 3, GA 2, GD +1)
    # Team C (3): 0 wins, 3 draws (vs D, vs A, vs B) -> 3 pts (GF 3, GA 3, GD 0)
    # Team B (2): 0 wins, 1 draw (vs C), 2 losses (vs A, vs D) -> 1 pt (GF 1, GA 5, GD -4)

    ranked = get_ranked_standings(final_state)
    assert tuple(e.club_id for e in ranked) == (4, 1, 3, 2)

    d_entry = next(e for e in final_state.standings.entries if e.club_id == 4)
    assert (d_entry.wins, d_entry.draws, d_entry.losses, d_entry.points) == (2, 1, 0, 7)

    a_entry = next(e for e in final_state.standings.entries if e.club_id == 1)
    assert (a_entry.wins, a_entry.draws, a_entry.losses, a_entry.points) == (1, 1, 1, 4)

    # Form verification
    assert final_state.form_table[4].results == ("D", "W", "W")
    assert final_state.form_table[1].results == ("W", "D", "L")
    assert final_state.form_table[3].results == ("D", "D", "D")
    assert final_state.form_table[2].results == ("L", "L", "D")


# -----------------------------------------------------------------------------
# Controlled Audit B — 20 Team Single Cycle Audit
# -----------------------------------------------------------------------------


def test_controlled_audit_b_20_team_cycle() -> None:
    club_ids = tuple(range(1, 21))
    season = _make_season(club_ids=club_ids)
    state = initialize_competition_season_state(season)

    # 10 matches: club 1 vs 2, 3 vs 4, ..., 19 vs 20
    results = [
        _make_match_result(f"m_{i}", i, i + 1, i % 3, (i + 1) % 2)
        for i in range(1, 20, 2)
    ]

    final_state = apply_match_results_to_season_state(state, results)

    assert len(final_state.standings.entries) == 20
    assert len(final_state.processed_match_ids) == 10

    total_played = sum(e.played for e in final_state.standings.entries)
    assert total_played == 20

    total_gf = sum(e.goals_for for e in final_state.standings.entries)
    total_ga = sum(e.goals_against for e in final_state.standings.entries)
    assert total_gf == total_ga


# -----------------------------------------------------------------------------
# Controlled Audit C — Season State Replay
# -----------------------------------------------------------------------------


def test_controlled_audit_c_season_state_replay() -> None:
    season = _make_season()
    initial_state = initialize_competition_season_state(season)

    results = [
        _make_match_result("m1", 1, 2, 2, 1),
        _make_match_result("m2", 3, 4, 0, 0),
        _make_match_result("m3", 1, 3, 1, 2),
    ]

    state_1 = apply_match_results_to_season_state(initial_state, results)
    state_2 = apply_match_results_to_season_state(initial_state, results)

    assert state_1 == state_2
    assert state_1.standings == state_2.standings
    assert state_1.form_table == state_2.form_table
    assert state_1.processed_match_ids == state_2.processed_match_ids


# -----------------------------------------------------------------------------
# Controlled Audit D — Cross Process Determinism
# -----------------------------------------------------------------------------


def test_controlled_audit_d_cross_process_determinism() -> None:
    script = """
import json
from datetime import date
from app.competition.domain import CompetitionParticipant, CompetitionSeason, CompetitionStage, CompetitionStageType
from app.competition.season_state import initialize_competition_season_state, apply_match_results_to_season_state
from app.match.domain import MatchResult

participants = tuple(CompetitionParticipant("s1", cid, f"seed_{cid}") for cid in range(1, 5))
stage = CompetitionStage("s1_st1", "s1", CompetitionStageType.REGULAR_SEASON, 1, (1, 2, 3, 4))
season = CompetitionSeason("s1", "c1", "2024", date(2024,1,1), date(2024,12,31), participants, (stage,), "seed")

state = initialize_competition_season_state(season)
matches = [
    MatchResult("m1", 1, 2, 2, 0, 1.0, 0.5, 50.0, 50.0, 5, 3, [], []),
    MatchResult("m2", 3, 4, 1, 1, 1.0, 1.0, 50.0, 50.0, 4, 4, [], []),
    MatchResult("m3", 1, 3, 0, 1, 0.5, 1.2, 45.0, 55.0, 3, 6, [], []),
]
final_state = apply_match_results_to_season_state(state, matches)

out = {
    "season_id": final_state.competition_season_id,
    "processed": list(final_state.processed_match_ids),
    "standings": [
        {
            "club_id": e.club_id, "played": e.played, "wins": e.wins, "draws": e.draws,
            "losses": e.losses, "gf": e.goals_for, "ga": e.goals_against, "gd": e.goal_difference,
            "pts": e.points
        } for e in final_state.standings.entries
    ],
    "form": {
        str(cid): list(rec.results) for cid, rec in sorted(final_state.form_table.items())
    }
}
print(json.dumps(out, sort_keys=True))
"""

    res1 = subprocess.run(
        [sys.executable, "-c", script],
        capture_output=True,
        text=True,
        check=True,
        env={"PYTHONPATH": "backend"},
    )
    res2 = subprocess.run(
        [sys.executable, "-c", script],
        capture_output=True,
        text=True,
        check=True,
        env={"PYTHONPATH": "backend"},
    )

    assert res1.stdout == res2.stdout
    assert len(res1.stdout.strip()) > 0
