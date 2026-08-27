from datetime import date
import json
import subprocess
import sys
import pytest

from app.competition.domain import (
    CompetitionFormat,
    CompetitionParticipant,
    CompetitionSeason,
    CompetitionSeasonStatus,
    CompetitionStage,
    CompetitionStageType,
)
from app.competition.fixtures import (
    Fixture,
    FixtureStatus,
    generate_round_robin_fixtures,
    generate_single_elimination_fixtures,
    generate_two_leg_elimination_fixtures,
)
from app.competition.progression import (
    ProgressionResult,
    TieBreakResult,
    build_next_stage_participants,
)
from app.competition.progression_state import (
    CompetitionProgressionState,
    advance_current_stage,
    advance_knockout_stage,
    advance_round_robin_stage,
    initialize_competition_progression_state,
)
from app.competition.season_state import (
    apply_match_results_to_season_state,
    initialize_competition_season_state,
)
from app.match.domain import MatchResult


def create_dummy_match_result(
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
        away_xg=1.2,
        home_possession=55.0,
        away_possession=45.0,
        home_shots=10,
        away_shots=8,
        player_performances=[],
        events=[],
    )


def create_sample_season(
    season_id: str = "season_2025_1",
    stage_types: list[CompetitionStageType] | None = None,
    club_ids: list[int] | None = None,
) -> CompetitionSeason:
    if club_ids is None:
        club_ids = [1, 2, 3, 4]
    if stage_types is None:
        stage_types = [CompetitionStageType.REGULAR_SEASON]

    participants = tuple(
        CompetitionParticipant(
            competition_season_id=season_id,
            club_id=cid,
            seed=str(i + 1),
        )
        for i, cid in enumerate(club_ids)
    )

    stages = tuple(
        CompetitionStage(
            id=f"{season_id}_stage_{i+1}",
            competition_season_id=season_id,
            stage_type=st,
            stage_number=i + 1,
            participant_club_ids=tuple(club_ids),
        )
        for i, st in enumerate(stage_types)
    )

    return CompetitionSeason(
        id=season_id,
        competition_id="comp_1",
        season_label="2025/2026",
        start_date=date(2025, 8, 1),
        end_date=date(2026, 5, 30),
        participants=participants,
        stages=stages,
        seed="season_seed_123",
        status=CompetitionSeasonStatus.ACTIVE,
        current_stage_index=0,
    )


def test_progression_state_valid():
    state = CompetitionProgressionState(
        competition_season_id="s1",
        current_stage_id="s1_stage_1",
        current_stage_index=0,
        completed=False,
        winner_club_id=None,
        advanced_club_ids=(1, 2),
        eliminated_club_ids=(3, 4),
        next_stage_id="s1_stage_2",
    )
    assert state.competition_season_id == "s1"
    assert state.current_stage_id == "s1_stage_1"
    assert state.current_stage_index == 0
    assert not state.completed
    assert state.winner_club_id is None
    assert state.advanced_club_ids == (1, 2)
    assert state.eliminated_club_ids == (3, 4)
    assert state.next_stage_id == "s1_stage_2"


def test_progression_state_invalid_season_id():
    with pytest.raises(ValueError, match="competition_season_id must be a non-empty string"):
        CompetitionProgressionState(
            competition_season_id="",
            current_stage_id="st1",
            current_stage_index=0,
            completed=False,
            winner_club_id=None,
            advanced_club_ids=(),
            eliminated_club_ids=(),
            next_stage_id=None,
        )


def test_progression_state_invalid_stage_id():
    with pytest.raises(ValueError, match="current_stage_id must be a non-empty string"):
        CompetitionProgressionState(
            competition_season_id="s1",
            current_stage_id="  ",
            current_stage_index=0,
            completed=False,
            winner_club_id=None,
            advanced_club_ids=(),
            eliminated_club_ids=(),
            next_stage_id=None,
        )


def test_progression_state_invalid_stage_index():
    with pytest.raises(ValueError, match="current_stage_index must be >= 0"):
        CompetitionProgressionState(
            competition_season_id="s1",
            current_stage_id="st1",
            current_stage_index=-1,
            completed=False,
            winner_club_id=None,
            advanced_club_ids=(),
            eliminated_club_ids=(),
            next_stage_id=None,
        )


def test_progression_state_duplicate_advanced():
    with pytest.raises(ValueError, match="advanced_club_ids contains duplicate club IDs"):
        CompetitionProgressionState(
            competition_season_id="s1",
            current_stage_id="st1",
            current_stage_index=0,
            completed=False,
            winner_club_id=None,
            advanced_club_ids=(1, 1),
            eliminated_club_ids=(2,),
            next_stage_id=None,
        )


def test_progression_state_duplicate_eliminated():
    with pytest.raises(ValueError, match="eliminated_club_ids contains duplicate club IDs"):
        CompetitionProgressionState(
            competition_season_id="s1",
            current_stage_id="st1",
            current_stage_index=0,
            completed=False,
            winner_club_id=None,
            advanced_club_ids=(1,),
            eliminated_club_ids=(2, 2),
            next_stage_id=None,
        )


def test_progression_state_overlap_advanced_eliminated():
    with pytest.raises(ValueError, match="clubs appear in both advanced and eliminated lists"):
        CompetitionProgressionState(
            competition_season_id="s1",
            current_stage_id="st1",
            current_stage_index=0,
            completed=False,
            winner_club_id=None,
            advanced_club_ids=(1, 2),
            eliminated_club_ids=(2, 3),
            next_stage_id=None,
        )


def test_progression_state_invalid_winner():
    with pytest.raises(ValueError, match="winner_club_id must be a positive integer"):
        CompetitionProgressionState(
            competition_season_id="s1",
            current_stage_id="st1",
            current_stage_index=0,
            completed=True,
            winner_club_id=-5,
            advanced_club_ids=(1,),
            eliminated_club_ids=(),
            next_stage_id=None,
        )


def test_progression_state_invalid_next_stage_id():
    with pytest.raises(ValueError, match="next_stage_id must be a non-empty string"):
        CompetitionProgressionState(
            competition_season_id="s1",
            current_stage_id="st1",
            current_stage_index=0,
            completed=False,
            winner_club_id=None,
            advanced_club_ids=(),
            eliminated_club_ids=(),
            next_stage_id="  ",
        )


def test_progression_state_immutability():
    state = CompetitionProgressionState(
        competition_season_id="s1",
        current_stage_id="st1",
        current_stage_index=0,
        completed=False,
        winner_club_id=None,
        advanced_club_ids=(1,),
        eliminated_club_ids=(2,),
        next_stage_id=None,
    )
    with pytest.raises(AttributeError):
        state.completed = True  # type: ignore


def test_initialize_progression_state_valid():
    season = create_sample_season()
    state = initialize_competition_progression_state(season)

    assert state.competition_season_id == season.id
    assert state.current_stage_id == season.stages[0].id
    assert state.current_stage_index == 0
    assert not state.completed
    assert state.winner_club_id is None
    assert state.advanced_club_ids == ()
    assert state.eliminated_club_ids == ()
    assert state.next_stage_id is None


def test_initialize_progression_state_empty_stages():
    season = create_sample_season()
    object.__setattr__(season, "stages", ())
    with pytest.raises(ValueError, match="must contain at least one stage"):
        initialize_competition_progression_state(season)


def test_initialize_progression_state_out_of_bounds_stage_index():
    season = create_sample_season()
    object.__setattr__(season, "current_stage_index", 5)
    with pytest.raises(ValueError, match="current_stage_index .* is out of bounds"):
        initialize_competition_progression_state(season)


def test_round_robin_progression_single_stage_final():
    season = create_sample_season(stage_types=[CompetitionStageType.REGULAR_SEASON])
    stage = season.stages[0]

    fixtures = generate_round_robin_fixtures(
        competition_season=season,
        stage=stage,
        start_date=date(2025, 8, 1),
    )

    results = []
    for f in fixtures:
        h_score = 3 if f.home_club_id == 1 else 0
        a_score = 3 if f.away_club_id == 1 else 0
        results.append(
            create_dummy_match_result(
                match_id=f.id,
                home_club_id=f.home_club_id,
                away_club_id=f.away_club_id,
                home_score=h_score,
                away_score=a_score,
            )
        )

    prog_state = advance_round_robin_stage(
        competition_season=season,
        stage=stage,
        fixtures=fixtures,
        match_results=results,
    )

    assert prog_state.completed
    assert prog_state.winner_club_id == 1
    assert prog_state.advanced_club_ids == (1,)
    assert set(prog_state.eliminated_club_ids) == {2, 3, 4}
    assert prog_state.next_stage_id is None


def test_round_robin_progression_qualification_slots_multi_stage():
    season = create_sample_season(
        stage_types=[CompetitionStageType.GROUP_STAGE, CompetitionStageType.SEMI_FINAL]
    )
    stage = season.stages[0]

    fixtures = generate_round_robin_fixtures(
        competition_season=season,
        stage=stage,
        start_date=date(2025, 8, 1),
    )

    results = []
    for f in fixtures:
        if f.home_club_id in (1, 2) and f.away_club_id in (3, 4):
            results.append(create_dummy_match_result(f.id, f.home_club_id, f.away_club_id, 2, 0))
        elif f.away_club_id in (1, 2) and f.home_club_id in (3, 4):
            results.append(create_dummy_match_result(f.id, f.home_club_id, f.away_club_id, 0, 2))
        else:
            results.append(create_dummy_match_result(f.id, f.home_club_id, f.away_club_id, 1, 1))

    prog_state = advance_round_robin_stage(
        competition_season=season,
        stage=stage,
        fixtures=fixtures,
        match_results=results,
        qualification_slots=2,
    )

    assert not prog_state.completed
    assert prog_state.winner_club_id is None
    assert set(prog_state.advanced_club_ids) == {1, 2}
    assert set(prog_state.eliminated_club_ids) == {3, 4}
    assert prog_state.next_stage_id == season.stages[1].id


def test_incomplete_round_robin_raises_error():
    season = create_sample_season(stage_types=[CompetitionStageType.REGULAR_SEASON])
    stage = season.stages[0]

    fixtures = generate_round_robin_fixtures(
        competition_season=season,
        stage=stage,
        start_date=date(2025, 8, 1),
    )

    results = [
        create_dummy_match_result(f.id, f.home_club_id, f.away_club_id, 1, 0) for f in fixtures[:-1]
    ]

    with pytest.raises(ValueError, match="cannot be completed"):
        advance_round_robin_stage(
            competition_season=season,
            stage=stage,
            fixtures=fixtures,
            match_results=results,
        )


def test_round_robin_with_unprocessed_season_state_raises():
    season = create_sample_season()
    stage = season.stages[0]

    fixtures = generate_round_robin_fixtures(
        competition_season=season,
        stage=stage,
        start_date=date(2025, 8, 1),
    )

    results = [
        create_dummy_match_result(f.id, f.home_club_id, f.away_club_id, 1, 0) for f in fixtures
    ]

    season_state = initialize_competition_season_state(season)
    season_state = apply_match_results_to_season_state(season_state, results[:1])

    with pytest.raises(ValueError, match="has not been processed in season_state"):
        advance_round_robin_stage(
            competition_season=season,
            stage=stage,
            fixtures=fixtures,
            match_results=results,
            season_state=season_state,
        )


def test_single_leg_knockout_progression():
    season = create_sample_season(
        club_ids=[1, 2], stage_types=[CompetitionStageType.FINAL]
    )
    stage = season.stages[0]

    fixtures = generate_single_elimination_fixtures(
        competition_season=season,
        stage=stage,
        scheduled_date=date(2025, 8, 1),
    )
    assert len(fixtures) == 1

    results = [create_dummy_match_result(fixtures[0].id, 1, 2, 2, 1)]

    prog_state = advance_knockout_stage(
        competition_season=season,
        stage=stage,
        fixtures=fixtures,
        match_results=results,
    )

    assert prog_state.completed
    assert prog_state.winner_club_id == 1
    assert prog_state.advanced_club_ids == (1,)
    assert prog_state.eliminated_club_ids == (2,)
    assert prog_state.next_stage_id is None


def test_single_leg_knockout_tiebreak():
    season = create_sample_season(
        club_ids=[1, 2], stage_types=[CompetitionStageType.FINAL]
    )
    stage = season.stages[0]

    fixtures = generate_single_elimination_fixtures(
        competition_season=season,
        stage=stage,
        scheduled_date=date(2025, 8, 1),
    )

    results = [create_dummy_match_result(fixtures[0].id, 1, 2, 1, 1)]

    with pytest.raises(ValueError, match="cannot be completed"):
        advance_knockout_stage(
            competition_season=season,
            stage=stage,
            fixtures=fixtures,
            match_results=results,
        )

    tb = {fixtures[0].id: TieBreakResult(winner_club_id=2, method="PENALTIES")}
    prog_state = advance_knockout_stage(
        competition_season=season,
        stage=stage,
        fixtures=fixtures,
        match_results=results,
        tiebreaks=tb,
    )

    assert prog_state.completed
    assert prog_state.winner_club_id == 2
    assert prog_state.advanced_club_ids == (2,)
    assert prog_state.eliminated_club_ids == (1,)


def test_two_leg_knockout_progression():
    season = create_sample_season(
        club_ids=[1, 2], stage_types=[CompetitionStageType.SEMI_FINAL, CompetitionStageType.FINAL]
    )
    stage = season.stages[0]

    fixtures = generate_two_leg_elimination_fixtures(
        competition_season=season,
        stage=stage,
        first_leg_date=date(2025, 8, 1),
        second_leg_date=date(2025, 8, 8),
    )
    assert len(fixtures) == 2

    results = [
        create_dummy_match_result(fixtures[0].id, fixtures[0].home_club_id, fixtures[0].away_club_id, 2, 0),
        create_dummy_match_result(fixtures[1].id, fixtures[1].home_club_id, fixtures[1].away_club_id, 1, 1),
    ]

    prog_state = advance_knockout_stage(
        competition_season=season,
        stage=stage,
        fixtures=fixtures,
        match_results=results,
    )

    assert not prog_state.completed
    assert prog_state.winner_club_id is None
    assert prog_state.advanced_club_ids == (1,)
    assert prog_state.eliminated_club_ids == (2,)
    assert prog_state.next_stage_id == season.stages[1].id


def test_two_leg_knockout_aggregate_draw_tiebreak():
    season = create_sample_season(
        club_ids=[1, 2], stage_types=[CompetitionStageType.SEMI_FINAL, CompetitionStageType.FINAL]
    )
    stage = season.stages[0]

    fixtures = generate_two_leg_elimination_fixtures(
        competition_season=season,
        stage=stage,
        first_leg_date=date(2025, 8, 1),
        second_leg_date=date(2025, 8, 8),
    )

    results = [
        create_dummy_match_result(fixtures[0].id, fixtures[0].home_club_id, fixtures[0].away_club_id, 1, 0),
        create_dummy_match_result(fixtures[1].id, fixtures[1].home_club_id, fixtures[1].away_club_id, 1, 0),
    ]

    with pytest.raises(ValueError, match="cannot be completed"):
        advance_knockout_stage(
            competition_season=season,
            stage=stage,
            fixtures=fixtures,
            match_results=results,
        )

    pair_str = f"{min(1, 2)}:{max(1, 2)}"
    tb = {pair_str: TieBreakResult(winner_club_id=2, method="PENALTIES")}
    prog_state = advance_knockout_stage(
        competition_season=season,
        stage=stage,
        fixtures=fixtures,
        match_results=results,
        tiebreaks=tb,
    )

    assert prog_state.advanced_club_ids == (2,)
    assert prog_state.eliminated_club_ids == (1,)


def test_advance_current_stage_dispatcher():
    season = create_sample_season(stage_types=[CompetitionStageType.REGULAR_SEASON])
    stage = season.stages[0]

    fixtures = generate_round_robin_fixtures(
        competition_season=season,
        stage=stage,
        start_date=date(2025, 8, 1),
    )
    results = [create_dummy_match_result(f.id, f.home_club_id, f.away_club_id, 1, 0) for f in fixtures]

    prog_state = advance_current_stage(
        competition_season=season,
        fixtures=fixtures,
        match_results=results,
    )

    assert prog_state.completed
    assert prog_state.winner_club_id is not None


def test_advance_current_stage_already_completed_raises():
    season = create_sample_season()
    prog_state = CompetitionProgressionState(
        competition_season_id=season.id,
        current_stage_id=season.stages[0].id,
        current_stage_index=0,
        completed=True,
        winner_club_id=1,
        advanced_club_ids=(1,),
        eliminated_club_ids=(2, 3, 4),
        next_stage_id=None,
    )

    with pytest.raises(ValueError, match="already completed"):
        advance_current_stage(
            competition_season=season,
            progression_state=prog_state,
        )


def test_full_tournament_sequence():
    club_ids = [1, 2, 3, 4]
    season = create_sample_season(
        club_ids=club_ids,
        stage_types=[CompetitionStageType.SEMI_FINAL, CompetitionStageType.FINAL],
    )

    sf_stage = season.stages[0]
    sf_fixtures = [
        Fixture(
            id="sf_1",
            competition_season_id=season.id,
            stage_id=sf_stage.id,
            round_number=1,
            home_club_id=1,
            away_club_id=2,
            importance=85.0,
            rivalry_factor=1.0,
            seed="seed_1",
            scheduled_date=date(2025, 9, 1),
            status=FixtureStatus.PLAYED,
        ),
        Fixture(
            id="sf_2",
            competition_season_id=season.id,
            stage_id=sf_stage.id,
            round_number=1,
            home_club_id=3,
            away_club_id=4,
            importance=85.0,
            rivalry_factor=1.0,
            seed="seed_2",
            scheduled_date=date(2025, 9, 1),
            status=FixtureStatus.PLAYED,
        ),
    ]

    sf_results = [
        create_dummy_match_result("sf_1", 1, 2, 2, 1),
        create_dummy_match_result("sf_2", 3, 4, 0, 3),
    ]

    sf_prog = advance_current_stage(
        competition_season=season,
        fixtures=sf_fixtures,
        match_results=sf_results,
    )

    assert not sf_prog.completed
    assert sf_prog.next_stage_id == season.stages[1].id
    assert set(sf_prog.advanced_club_ids) == {1, 4}
    assert set(sf_prog.eliminated_club_ids) == {2, 3}

    prog_res = ProgressionResult(
        competition_season_id=sf_prog.competition_season_id,
        stage_completed=True,
        current_stage_index=sf_prog.current_stage_index,
        advanced_club_ids=sf_prog.advanced_club_ids,
        eliminated_club_ids=sf_prog.eliminated_club_ids,
        winner_club_id=sf_prog.winner_club_id,
        next_stage_id=sf_prog.next_stage_id,
    )

    next_stage = build_next_stage_participants(
        stage=sf_stage,
        progression=prog_res,
        next_stage_id=season.stages[1].id,
        next_stage_number=2,
        next_stage_type=CompetitionStageType.FINAL,
    )

    object.__setattr__(season, "current_stage_index", 1)
    new_stages = (sf_stage, next_stage)
    object.__setattr__(season, "stages", new_stages)

    final_fixtures = [
        Fixture(
            id="final_1",
            competition_season_id=season.id,
            stage_id=next_stage.id,
            round_number=1,
            home_club_id=1,
            away_club_id=4,
            importance=95.0,
            rivalry_factor=1.0,
            seed="seed_final",
            scheduled_date=date(2025, 9, 15),
            status=FixtureStatus.PLAYED,
        )
    ]

    final_results = [create_dummy_match_result("final_1", 1, 4, 3, 2)]

    final_prog = advance_current_stage(
        competition_season=season,
        progression_state=sf_prog,
        fixtures=final_fixtures,
        match_results=final_results,
    )

    assert final_prog.completed
    assert final_prog.winner_club_id == 1
    assert final_prog.advanced_club_ids == (1,)
    assert final_prog.eliminated_club_ids == (4,)
    assert final_prog.next_stage_id is None


def test_round_robin_to_knockout_transition():
    season = create_sample_season(
        club_ids=[1, 2, 3, 4],
        stage_types=[CompetitionStageType.GROUP_STAGE, CompetitionStageType.FINAL],
    )

    group_stage = season.stages[0]
    group_fixtures = generate_round_robin_fixtures(
        competition_season=season,
        stage=group_stage,
        start_date=date(2025, 8, 1),
    )

    results = []
    for f in group_fixtures:
        if f.home_club_id in (1, 2) and f.away_club_id in (3, 4):
            results.append(create_dummy_match_result(f.id, f.home_club_id, f.away_club_id, 3, 0))
        elif f.away_club_id in (1, 2) and f.home_club_id in (3, 4):
            results.append(create_dummy_match_result(f.id, f.home_club_id, f.away_club_id, 0, 3))
        else:
            results.append(create_dummy_match_result(f.id, f.home_club_id, f.away_club_id, 1, 1))

    prog_state = advance_round_robin_stage(
        competition_season=season,
        stage=group_stage,
        fixtures=group_fixtures,
        match_results=results,
        qualification_slots=2,
    )

    assert set(prog_state.advanced_club_ids) == {1, 2}
    assert set(prog_state.eliminated_club_ids) == {3, 4}

    prog_res = ProgressionResult(
        competition_season_id=prog_state.competition_season_id,
        stage_completed=True,
        current_stage_index=prog_state.current_stage_index,
        advanced_club_ids=prog_state.advanced_club_ids,
        eliminated_club_ids=prog_state.eliminated_club_ids,
        winner_club_id=prog_state.winner_club_id,
        next_stage_id=prog_state.next_stage_id,
    )

    next_stage = build_next_stage_participants(
        stage=group_stage,
        progression=prog_res,
        next_stage_id=season.stages[1].id,
        next_stage_number=2,
        next_stage_type=CompetitionStageType.FINAL,
    )

    assert set(next_stage.participant_club_ids) == {1, 2}


def test_duplicate_transition_determinism():
    season = create_sample_season(stage_types=[CompetitionStageType.REGULAR_SEASON])
    stage = season.stages[0]

    fixtures = generate_round_robin_fixtures(
        competition_season=season,
        stage=stage,
        start_date=date(2025, 8, 1),
    )
    results = [create_dummy_match_result(f.id, f.home_club_id, f.away_club_id, 1, 0) for f in fixtures]

    res1 = advance_round_robin_stage(season, stage, fixtures, results)
    res2 = advance_round_robin_stage(season, stage, fixtures, results)

    assert res1 == res2


def test_cross_process_determinism():
    code = """
from datetime import date
import json
from app.competition.domain import CompetitionSeason, CompetitionParticipant, CompetitionStage, CompetitionStageType, CompetitionSeasonStatus
from app.competition.fixtures import generate_round_robin_fixtures
from app.competition.progression_state import advance_round_robin_stage
from app.match.domain import MatchResult

participants = tuple(CompetitionParticipant("s1", cid, str(cid)) for cid in [1, 2, 3, 4])
stages = (CompetitionStage("s1_st1", "s1", CompetitionStageType.REGULAR_SEASON, 1, (1, 2, 3, 4)),)
season = CompetitionSeason("s1", "c1", "2025", date(2025,8,1), date(2025,12,31), participants, stages, "seed")
stage = season.stages[0]
fxs = generate_round_robin_fixtures(season, stage, date(2025,8,1))
res = [MatchResult(f.id, f.home_club_id, f.away_club_id, 2 if f.home_club_id==1 else 0, 0, 1.5, 1.2, 55.0, 45.0, 10, 8, [], []) for f in fxs]
st = advance_round_robin_stage(season, stage, fxs, res)
out = {
    "completed": st.completed,
    "winner_club_id": st.winner_club_id,
    "advanced_club_ids": st.advanced_club_ids,
    "eliminated_club_ids": st.eliminated_club_ids,
    "next_stage_id": st.next_stage_id
}
print(json.dumps(out, sort_keys=True))
"""
    cmd = [sys.executable, "-c", code]
    p1 = subprocess.run(cmd, capture_output=True, text=True, check=True, env={"PYTHONPATH": "backend"})
    p2 = subprocess.run(cmd, capture_output=True, text=True, check=True, env={"PYTHONPATH": "backend"})

    assert p1.stdout == p2.stdout
    parsed = json.loads(p1.stdout)
    assert parsed["winner_club_id"] == 1


def test_season_state_immutability_on_progression():
    season = create_sample_season()
    stage = season.stages[0]
    fixtures = generate_round_robin_fixtures(season, stage, date(2025, 8, 1))
    results = [create_dummy_match_result(f.id, f.home_club_id, f.away_club_id, 1, 0) for f in fixtures]

    season_state = initialize_competition_season_state(season)
    season_state = apply_match_results_to_season_state(season_state, results)

    orig_processed = season_state.processed_match_ids
    orig_entries = season_state.standings.entries

    advance_round_robin_stage(
        competition_season=season,
        stage=stage,
        fixtures=fixtures,
        match_results=results,
        season_state=season_state,
    )

    assert season_state.processed_match_ids == orig_processed
    assert season_state.standings.entries == orig_entries


def test_advance_round_robin_stage_wrong_season_id():
    season = create_sample_season(season_id="s1")
    other_season = create_sample_season(season_id="s2")
    stage = season.stages[0]
    fixtures = generate_round_robin_fixtures(season, stage, date(2025, 8, 1))
    results = [create_dummy_match_result(f.id, f.home_club_id, f.away_club_id, 1, 0) for f in fixtures]

    with pytest.raises(ValueError, match="does not match competition_season id"):
        advance_round_robin_stage(
            competition_season=other_season,
            stage=stage,
            fixtures=fixtures,
            match_results=results,
        )


def test_advance_round_robin_stage_not_active_stage():
    season = create_sample_season(stage_types=[CompetitionStageType.GROUP_STAGE, CompetitionStageType.FINAL])
    stage2 = season.stages[1]
    fixtures = generate_round_robin_fixtures(season, season.stages[0], date(2025, 8, 1))
    results = [create_dummy_match_result(f.id, f.home_club_id, f.away_club_id, 1, 0) for f in fixtures]

    with pytest.raises(ValueError, match="is not the current active stage"):
        advance_round_robin_stage(
            competition_season=season,
            stage=stage2,
            fixtures=fixtures,
            match_results=results,
        )


def test_advance_knockout_stage_wrong_season_state_id():
    season = create_sample_season(season_id="s1", stage_types=[CompetitionStageType.FINAL], club_ids=[1, 2])
    other_season = create_sample_season(season_id="s2")
    stage = season.stages[0]
    fixtures = generate_single_elimination_fixtures(season, stage, date(2025, 8, 1))
    results = [create_dummy_match_result(fixtures[0].id, 1, 2, 2, 1)]

    wrong_season_state = initialize_competition_season_state(other_season)

    with pytest.raises(ValueError, match="does not match competition_season id"):
        advance_knockout_stage(
            competition_season=season,
            stage=stage,
            fixtures=fixtures,
            match_results=results,
            season_state=wrong_season_state,
        )


def test_advance_current_stage_mismatched_progression_state_season_id():
    season = create_sample_season(season_id="s1")
    prog_state = CompetitionProgressionState(
        competition_season_id="s2",
        current_stage_id="s2_stage_1",
        current_stage_index=0,
        completed=False,
        winner_club_id=None,
        advanced_club_ids=(),
        eliminated_club_ids=(),
        next_stage_id=None,
    )

    with pytest.raises(ValueError, match="does not match competition_season id"):
        advance_current_stage(
            competition_season=season,
            progression_state=prog_state,
        )


def test_advance_current_stage_unsupported_stage_type():
    season = create_sample_season()
    object.__setattr__(season.stages[0], "stage_type", "INVALID_TYPE")

    with pytest.raises(ValueError, match="Unsupported stage_type"):
        advance_current_stage(
            competition_season=season,
        )


def test_knockout_non_final_stage_winner_id_is_none():
    season = create_sample_season(
        club_ids=[1, 2, 3, 4],
        stage_types=[CompetitionStageType.QUARTER_FINAL, CompetitionStageType.SEMI_FINAL],
    )
    stage = season.stages[0]
    fixtures = [
        Fixture("qf1", season.id, stage.id, 1, date(2025, 9, 1), 1, 2, 75.0, 1.0, "s1", FixtureStatus.PLAYED),
        Fixture("qf2", season.id, stage.id, 1, date(2025, 9, 1), 3, 4, 75.0, 1.0, "s2", FixtureStatus.PLAYED),
    ]
    results = [
        create_dummy_match_result("qf1", 1, 2, 2, 0),
        create_dummy_match_result("qf2", 3, 4, 3, 1),
    ]

    prog_state = advance_knockout_stage(
        competition_season=season,
        stage=stage,
        fixtures=fixtures,
        match_results=results,
    )

    assert not prog_state.completed
    assert prog_state.winner_club_id is None
    assert set(prog_state.advanced_club_ids) == {1, 3}
    assert set(prog_state.eliminated_club_ids) == {2, 4}
    assert prog_state.next_stage_id == season.stages[1].id


def test_league_phase_stage_advancement():
    season = create_sample_season(
        stage_types=[CompetitionStageType.LEAGUE_PHASE, CompetitionStageType.ROUND_OF_16]
    )
    stage = season.stages[0]

    fixtures = generate_round_robin_fixtures(
        competition_season=season,
        stage=stage,
        start_date=date(2025, 8, 1),
    )
    results = [create_dummy_match_result(f.id, f.home_club_id, f.away_club_id, 1, 0) for f in fixtures]

    prog_state = advance_current_stage(
        competition_season=season,
        fixtures=fixtures,
        match_results=results,
        qualification_slots=2,
    )

    assert not prog_state.completed
    assert len(prog_state.advanced_club_ids) == 2
    assert prog_state.next_stage_id == season.stages[1].id
