from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from datetime import date, timedelta
from types import MappingProxyType
from typing import Any

from app.competition.domain import (
    Competition,
    CompetitionFormat,
    CompetitionSeason,
    CompetitionSeasonStatus,
    CompetitionStage,
    CompetitionStageType,
)
from app.competition.fixtures import (
    Fixture,
    generate_round_robin_fixtures,
    generate_single_elimination_fixtures,
    generate_two_leg_elimination_fixtures,
)
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.competition.match_executor import ParticipantResolver
    MatchResult = Any
    SimulationMode = Any
else:
    ParticipantResolver = Any
    MatchResult = Any
    SimulationMode = Any
from app.competition.progression import (
    ProgressionResult,
    TieBreakResult,
    build_next_stage_participants,
)
from app.competition.progression_state import (
    CompetitionProgressionState,
    advance_current_stage,
    initialize_competition_progression_state,
)
from app.competition.season_state import (
    CompetitionSeasonState,
    apply_match_result_to_season_state,
    initialize_competition_season_state,
)
import importlib

from app.competition.form import FormRecord
from app.competition.standings import StandingsTable


@dataclass(frozen=True)
class SeasonSimulationConfig:
    start_date: date
    end_date: date
    seed: str

    def __post_init__(self) -> None:
        if self.start_date > self.end_date:
            raise ValueError("start_date must be <= end_date")
        if not self.seed or not self.seed.strip():
            raise ValueError("seed must be a non-empty string")


@dataclass(frozen=True)
class FixtureExecutionResult:
    fixture_id: str
    completed: bool

    def __post_init__(self) -> None:
        if not self.fixture_id or not self.fixture_id.strip():
            raise ValueError("fixture_id must be a non-empty string")


@dataclass(frozen=True)
class OrchestrationContext:
    competition_season: CompetitionSeason
    competition: Competition
    config: SeasonSimulationConfig


@dataclass(frozen=True)
class SeasonSimulationResult:
    competition_season_id: str
    completed: bool
    fixtures_processed: int
    fixtures_completed: int
    final_date: date | None
    execution_results: tuple[FixtureExecutionResult, ...]

    def __post_init__(self) -> None:
        if not self.competition_season_id or not self.competition_season_id.strip():
            raise ValueError("competition_season_id must be a non-empty string")
        if self.fixtures_processed < 0:
            raise ValueError("fixtures_processed must be >= 0")
        if self.fixtures_completed < 0:
            raise ValueError("fixtures_completed must be >= 0")
        if self.fixtures_completed > self.fixtures_processed:
            raise ValueError("fixtures_completed cannot exceed fixtures_processed")

        if not isinstance(self.execution_results, tuple):
            object.__setattr__(self, "execution_results", tuple(self.execution_results))

        if len(self.execution_results) != self.fixtures_processed:
            raise ValueError("len(execution_results) must equal fixtures_processed")


FixtureExecutor = Callable[
    [Fixture, OrchestrationContext],
    FixtureExecutionResult,
]


def simulate_competition_season(
    competition_season: CompetitionSeason,
    competition: Competition,
    fixtures: Sequence[Fixture],
    config: SeasonSimulationConfig,
    fixture_executor: FixtureExecutor,
) -> SeasonSimulationResult:
    if not competition_season.id or not competition_season.id.strip():
        raise ValueError("competition_season.id must be a non-empty string")
    if not competition.id or not competition.id.strip():
        raise ValueError("competition.id must be a non-empty string")

    if competition_season.competition_id != competition.id:
        raise ValueError(
            f"competition_season.competition_id '{competition_season.competition_id}' "
            f"does not match competition.id '{competition.id}'"
        )

    seen_fixture_ids: set[str] = set()
    for fixture in fixtures:
        if not fixture.id or not fixture.id.strip():
            raise ValueError("fixture.id must be a non-empty string")
        if fixture.id in seen_fixture_ids:
            raise ValueError(f"Duplicate fixture id '{fixture.id}'")
        seen_fixture_ids.add(fixture.id)

        if fixture.competition_season_id != competition_season.id:
            raise ValueError(
                f"fixture competition_season_id '{fixture.competition_season_id}' "
                f"does not match season id '{competition_season.id}'"
            )

        if not (config.start_date <= fixture.scheduled_date <= config.end_date):
            raise ValueError(
                f"Fixture scheduled_date {fixture.scheduled_date} outside simulation window "
                f"[{config.start_date}, {config.end_date}]"
            )

        if not fixture.stage_id or not fixture.stage_id.strip():
            raise ValueError("fixture stage_id must be a non-empty string")

        if fixture.home_club_id <= 0 or fixture.away_club_id <= 0:
            raise ValueError("fixture home_club_id and away_club_id must be positive integers")

        if fixture.home_club_id == fixture.away_club_id:
            raise ValueError("fixture home_club_id and away_club_id must be different")

    sorted_fixtures = sorted(
        fixtures,
        key=lambda f: (f.scheduled_date, f.round_number, f.id),
    )

    context = OrchestrationContext(
        competition_season=competition_season,
        competition=competition,
        config=config,
    )

    execution_results: list[FixtureExecutionResult] = []
    fixtures_processed = 0
    fixtures_completed = 0
    final_date: date | None = None

    for fixture in sorted_fixtures:
        res = fixture_executor(fixture, context)

        if not isinstance(res, FixtureExecutionResult):
            raise TypeError(
                f"fixture_executor returned object of type '{type(res).__name__}', "
                f"expected FixtureExecutionResult"
            )

        if res.fixture_id != fixture.id:
            raise ValueError(
                f"fixture_executor returned result with fixture_id '{res.fixture_id}', "
                f"expected '{fixture.id}'"
            )

        execution_results.append(res)
        fixtures_processed += 1
        if res.completed:
            fixtures_completed += 1
        final_date = fixture.scheduled_date

    season_completed = (
        fixtures_processed == len(fixtures)
        and fixtures_completed == fixtures_processed
    )

    return SeasonSimulationResult(
        competition_season_id=competition_season.id,
        completed=season_completed,
        fixtures_processed=fixtures_processed,
        fixtures_completed=fixtures_completed,
        final_date=final_date,
        execution_results=tuple(execution_results),
    )


@dataclass(frozen=True)
class FullCompetitionSeasonResult:
    competition_season_id: str
    completed: bool
    final_stage_index: int
    current_stage_id: str | None
    winner_club_id: int | None
    fixtures_processed: int
    fixtures_completed: int
    match_results: tuple[Any, ...]
    final_standings: StandingsTable | None
    final_form_table: Mapping[int, FormRecord] | None

    def __post_init__(self) -> None:
        if not self.competition_season_id or not self.competition_season_id.strip():
            raise ValueError("competition_season_id must be a non-empty string")
        if self.final_stage_index < 0:
            raise ValueError("final_stage_index must be >= 0")
        if self.fixtures_processed < 0:
            raise ValueError("fixtures_processed must be >= 0")
        if self.fixtures_completed < 0:
            raise ValueError("fixtures_completed must be >= 0")
        if self.fixtures_completed > self.fixtures_processed:
            raise ValueError("fixtures_completed cannot exceed fixtures_processed")

        if not isinstance(self.match_results, tuple):
            object.__setattr__(self, "match_results", tuple(self.match_results))

        if len(self.match_results) != self.fixtures_completed:
            raise ValueError("len(match_results) must equal fixtures_completed")

        if self.winner_club_id is not None and self.winner_club_id <= 0:
            raise ValueError("winner_club_id must be a positive integer when present")

        if self.current_stage_id is not None and not self.current_stage_id.strip():
            raise ValueError("current_stage_id must be a non-empty string when present")

        if self.final_form_table is not None and not isinstance(self.final_form_table, MappingProxyType):
            object.__setattr__(self, "final_form_table", MappingProxyType(dict(self.final_form_table)))


@dataclass(frozen=True)
class CompetitionSeasonBinding:
    competition: Competition
    competition_season: CompetitionSeason
    existing_fixtures: tuple[Fixture, ...] = ()

    def __post_init__(self) -> None:
        if self.competition is None:
            raise ValueError("competition must not be None")
        if self.competition_season is None:
            raise ValueError("competition_season must not be None")
        if self.competition_season.competition_id != self.competition.id:
            raise ValueError(
                f"competition_season.competition_id '{self.competition_season.competition_id}' "
                f"does not match competition.id '{self.competition.id}'"
            )

        if not isinstance(self.existing_fixtures, tuple):
            object.__setattr__(self, "existing_fixtures", tuple(self.existing_fixtures))

        for fixture in self.existing_fixtures:
            if not isinstance(fixture, Fixture):
                raise TypeError(f"existing_fixtures element must be Fixture, got '{type(fixture).__name__}'")
            if fixture.competition_season_id != self.competition_season.id:
                raise ValueError(
                    f"fixture competition_season_id '{fixture.competition_season_id}' "
                    f"does not match competition_season.id '{self.competition_season.id}'"
                )


@dataclass(frozen=True)
class MultiCompetitionSeasonResult:
    season_seed: str
    competitions: tuple[FullCompetitionSeasonResult, ...]
    completed: bool
    total_fixtures_processed: int
    total_fixtures_completed: int

    def __post_init__(self) -> None:
        if not self.season_seed or not self.season_seed.strip():
            raise ValueError("season_seed must be a non-empty string")
        if self.total_fixtures_processed < 0:
            raise ValueError("total_fixtures_processed must be >= 0")
        if self.total_fixtures_completed < 0:
            raise ValueError("total_fixtures_completed must be >= 0")
        if self.total_fixtures_completed > self.total_fixtures_processed:
            raise ValueError("total_fixtures_completed cannot exceed total_fixtures_processed")

        if not isinstance(self.competitions, tuple):
            object.__setattr__(self, "competitions", tuple(self.competitions))

        seen_ids: set[str] = set()
        for c in self.competitions:
            if not isinstance(c, FullCompetitionSeasonResult):
                raise TypeError(f"competitions element must be FullCompetitionSeasonResult, got '{type(c).__name__}'")
            if c.competition_season_id in seen_ids:
                raise ValueError(f"Duplicate competition_season_id '{c.competition_season_id}' in multi-competition result")
            seen_ids.add(c.competition_season_id)

        sum_processed = sum(c.fixtures_processed for c in self.competitions)
        sum_completed = sum(c.fixtures_completed for c in self.competitions)
        if self.total_fixtures_processed != sum_processed:
            raise ValueError(f"total_fixtures_processed ({self.total_fixtures_processed}) does not equal sum ({sum_processed})")
        if self.total_fixtures_completed != sum_completed:
            raise ValueError(f"total_fixtures_completed ({self.total_fixtures_completed}) does not equal sum ({sum_completed})")


TieBreakProvider = Callable[
    [Sequence[Fixture], Sequence[MatchResult]],
    Mapping[str, TieBreakResult],
]


def simulate_full_competition_season(
    competition_season: CompetitionSeason,
    competition: Competition,
    config: SeasonSimulationConfig,
    participant_resolver: ParticipantResolver,
    existing_fixtures: Sequence[Fixture] = (),
    tiebreak_provider: TieBreakProvider | None = None,
    simulation_mode: Any = "FAST",
) -> FullCompetitionSeasonResult:
    binding = CompetitionSeasonBinding(
        competition=competition,
        competition_season=competition_season,
        existing_fixtures=tuple(existing_fixtures),
    )
    multi_res = simulate_multi_competition_season(
        competitions=(binding,),
        config=config,
        participant_resolver=participant_resolver,
        tiebreak_provider=tiebreak_provider,
        simulation_mode=simulation_mode,
    )
    return multi_res.competitions[0]


def simulate_multi_competition_season(
    competitions: Sequence[CompetitionSeasonBinding],
    config: SeasonSimulationConfig,
    participant_resolver: ParticipantResolver,
    tiebreak_provider: TieBreakProvider | None = None,
    simulation_mode: Any = "FAST",
) -> MultiCompetitionSeasonResult:
    if config is None:
        raise ValueError("config must not be None")
    if participant_resolver is None or not callable(participant_resolver):
        raise ValueError("participant_resolver must be callable")
    if not competitions:
        raise ValueError("competitions must not be empty")

    seen_comp_ids: set[str] = set()
    for b in competitions:
        if not isinstance(b, CompetitionSeasonBinding):
            raise TypeError(f"competitions element must be CompetitionSeasonBinding, got '{type(b).__name__}'")
        if b.competition_season.id in seen_comp_ids:
            raise ValueError(f"Duplicate competition_season.id '{b.competition_season.id}'")
        seen_comp_ids.add(b.competition_season.id)

    class _CompState:
        def __init__(self, binding: CompetitionSeasonBinding):
            self.competition = binding.competition
            self.current_season = binding.competition_season
            self.existing_fixtures = binding.existing_fixtures
            self.season_state = initialize_competition_season_state(self.current_season)
            self.progression_state = initialize_competition_progression_state(self.current_season)
            self.all_match_results: list[Any] = []
            self.current_stage_executed_fixtures: list[Fixture] = []
            self.current_stage_match_results: list[Any] = []
            self.pending_stage_fixtures: list[Fixture] = []
            self.fixtures_processed = 0
            self.fixtures_completed = 0
            self.completed = False

    from app.competition.match_executor import (
        MatchFixtureExecutionResult,
        build_match_engine_executor,
    )

    comp_states = [_CompState(b) for b in competitions]
    match_executor = build_match_engine_executor(participant_resolver, simulation_mode=simulation_mode)

    def _generate_fixtures_for_current_stage(cs: _CompState, last_fixture_date: date | None) -> list[Fixture]:
        stage = cs.current_season.stages[cs.current_season.current_stage_index]
        existing = [
            f for f in cs.existing_fixtures
            if f.stage_id == stage.id and f.competition_season_id == cs.current_season.id
        ]
        if existing:
            seen_ids: set[str] = set()
            for f in existing:
                if f.id in seen_ids:
                    raise ValueError(f"Duplicate existing fixture id '{f.id}'")
                seen_ids.add(f.id)
                if not (config.start_date <= f.scheduled_date <= config.end_date):
                    raise ValueError(
                        f"Fixture '{f.id}' scheduled_date {f.scheduled_date} outside window [{config.start_date}, {config.end_date}]"
                    )
            return sorted(existing, key=lambda f: (f.scheduled_date, f.round_number, f.id))

        if cs.current_season.current_stage_index == 0:
            stage_start_date = config.start_date
        else:
            ref_date = last_fixture_date if last_fixture_date is not None else config.start_date
            stage_start_date = ref_date + timedelta(days=7)
            if stage_start_date < config.start_date:
                stage_start_date = config.start_date

        stage_type = stage.stage_type
        fmt = cs.competition.format

        if stage_type in (
            CompetitionStageType.REGULAR_SEASON,
            CompetitionStageType.GROUP_STAGE,
            CompetitionStageType.LEAGUE_PHASE,
        ):
            fxs = generate_round_robin_fixtures(
                competition_season=cs.current_season,
                stage=stage,
                start_date=stage_start_date,
                interval_days=7,
                competition_importance=cs.competition.importance,
            )
        elif stage_type in (
            CompetitionStageType.ROUND_OF_32,
            CompetitionStageType.ROUND_OF_16,
            CompetitionStageType.QUARTER_FINAL,
            CompetitionStageType.SEMI_FINAL,
            CompetitionStageType.FINAL,
        ):
            if fmt == CompetitionFormat.TWO_LEG_ELIMINATION:
                if stage_type == CompetitionStageType.FINAL and not cs.competition.rules.get("two_leg_final", False):
                    fxs = generate_single_elimination_fixtures(
                        competition_season=cs.current_season,
                        stage=stage,
                        scheduled_date=stage_start_date,
                        competition_importance=cs.competition.importance,
                    )
                else:
                    fxs = generate_two_leg_elimination_fixtures(
                        competition_season=cs.current_season,
                        stage=stage,
                        first_leg_date=stage_start_date,
                        second_leg_date=stage_start_date + timedelta(days=7),
                        interval_days=7,
                        competition_importance=cs.competition.importance,
                    )
            else:
                fxs = generate_single_elimination_fixtures(
                    competition_season=cs.current_season,
                    stage=stage,
                    scheduled_date=stage_start_date,
                    competition_importance=cs.competition.importance,
                )
        else:
            raise ValueError(f"Unsupported stage type '{stage_type}'")

        for f in fxs:
            if not (config.start_date <= f.scheduled_date <= config.end_date):
                raise ValueError(
                    f"Generated fixture scheduled_date {f.scheduled_date} outside window [{config.start_date}, {config.end_date}]"
                )
        return sorted(fxs, key=lambda f: (f.scheduled_date, f.round_number, f.id))

    global_last_date: date | None = None
    for cs in comp_states:
        cs.pending_stage_fixtures = _generate_fixtures_for_current_stage(cs, global_last_date)

    while not all(cs.completed for cs in comp_states):
        active_fixtures: list[tuple[_CompState, Fixture]] = []
        for cs in comp_states:
            if not cs.completed:
                for f in cs.pending_stage_fixtures:
                    active_fixtures.append((cs, f))

        if not active_fixtures:
            break

        date_club_map: dict[tuple[date, int], tuple[str, str]] = {}
        for cs, f in active_fixtures:
            for cid in (f.home_club_id, f.away_club_id):
                key = (f.scheduled_date, cid)
                if key in date_club_map:
                    prev_comp, prev_fix = date_club_map[key]
                    raise ValueError(
                        f"Calendar conflict detected: club_id {cid} is scheduled to play multiple fixtures on {f.scheduled_date} "
                        f"(fixture '{prev_fix}' in competition '{prev_comp}' and fixture '{f.id}' in competition '{cs.competition.id}')"
                    )
                date_club_map[key] = (cs.competition.id, f.id)

        earliest_date = min(f.scheduled_date for _, f in active_fixtures)
        due_items = [(cs, f) for cs, f in active_fixtures if f.scheduled_date == earliest_date]

        due_items.sort(
            key=lambda item: (
                item[1].scheduled_date,
                -item[0].competition.importance,
                item[0].competition.id,
                item[1].round_number,
                item[1].id,
            )
        )

        for cs, fixture in due_items:
            ctx = OrchestrationContext(
                competition_season=cs.current_season,
                competition=cs.competition,
                config=config,
            )
            exec_res = match_executor(fixture, ctx)
            if not isinstance(exec_res, MatchFixtureExecutionResult):
                raise TypeError(f"Match executor returned invalid result type '{type(exec_res).__name__}'")

            cs.fixtures_processed += 1
            if exec_res.completed:
                cs.fixtures_completed += 1

            m_res = exec_res.match_result
            cs.all_match_results.append(m_res)
            cs.current_stage_match_results.append(m_res)
            cs.current_stage_executed_fixtures.append(fixture)
            cs.season_state = apply_match_result_to_season_state(cs.season_state, m_res)
            cs.pending_stage_fixtures.remove(fixture)
            global_last_date = fixture.scheduled_date

            if not cs.pending_stage_fixtures:
                if tiebreak_provider is not None:
                    tb = tiebreak_provider(cs.current_stage_executed_fixtures, cs.current_stage_match_results)
                else:
                    tb = None

                qualification_slots = cs.competition.rules.get("qualification_slots")
                cs.progression_state = advance_current_stage(
                    competition_season=cs.current_season,
                    season_state=cs.season_state,
                    progression_state=cs.progression_state,
                    fixtures=cs.current_stage_executed_fixtures,
                    match_results=cs.current_stage_match_results,
                    tiebreaks=tb,
                    qualification_slots=qualification_slots,
                )

                if cs.progression_state.completed:
                    cs.completed = True
                    cs.current_season = CompetitionSeason(
                        id=cs.current_season.id,
                        competition_id=cs.current_season.competition_id,
                        season_label=cs.current_season.season_label,
                        start_date=cs.current_season.start_date,
                        end_date=cs.current_season.end_date,
                        participants=cs.current_season.participants,
                        stages=cs.current_season.stages,
                        seed=cs.current_season.seed,
                        status=CompetitionSeasonStatus.COMPLETED,
                        current_stage_index=cs.current_season.current_stage_index,
                        winner_id=cs.progression_state.winner_club_id,
                    )
                else:
                    next_stage_idx = cs.current_season.current_stage_index + 1
                    next_stage_def = cs.current_season.stages[next_stage_idx]
                    current_stage_def = cs.current_season.stages[cs.current_season.current_stage_index]

                    prog_res = ProgressionResult(
                        competition_season_id=cs.current_season.id,
                        stage_completed=True,
                        current_stage_index=cs.current_season.current_stage_index,
                        advanced_club_ids=cs.progression_state.advanced_club_ids,
                        eliminated_club_ids=cs.progression_state.eliminated_club_ids,
                        winner_club_id=cs.progression_state.winner_club_id,
                        next_stage_id=cs.progression_state.next_stage_id,
                    )

                    next_stage_populated = build_next_stage_participants(
                        stage=current_stage_def,
                        progression=prog_res,
                        next_stage_id=next_stage_def.id,
                        next_stage_number=next_stage_def.stage_number,
                        next_stage_type=next_stage_def.stage_type,
                    )

                    new_stages = list(cs.current_season.stages)
                    new_stages[next_stage_idx] = next_stage_populated

                    cs.current_season = CompetitionSeason(
                        id=cs.current_season.id,
                        competition_id=cs.current_season.competition_id,
                        season_label=cs.current_season.season_label,
                        start_date=cs.current_season.start_date,
                        end_date=cs.current_season.end_date,
                        participants=cs.current_season.participants,
                        stages=tuple(new_stages),
                        seed=cs.current_season.seed,
                        status=CompetitionSeasonStatus.ACTIVE,
                        current_stage_index=next_stage_idx,
                        winner_id=None,
                    )
                    cs.current_stage_executed_fixtures = []
                    cs.current_stage_match_results = []
                    cs.pending_stage_fixtures = _generate_fixtures_for_current_stage(cs, global_last_date)

    full_results: list[FullCompetitionSeasonResult] = []
    total_proc = 0
    total_comp = 0
    all_completed = True

    for cs in comp_states:
        total_proc += cs.fixtures_processed
        total_comp += cs.fixtures_completed
        if not cs.completed:
            all_completed = False

        full_results.append(
            FullCompetitionSeasonResult(
                competition_season_id=cs.current_season.id,
                completed=cs.completed,
                final_stage_index=cs.current_season.current_stage_index,
                current_stage_id=cs.progression_state.current_stage_id,
                winner_club_id=cs.progression_state.winner_club_id,
                fixtures_processed=cs.fixtures_processed,
                fixtures_completed=cs.fixtures_completed,
                match_results=tuple(cs.all_match_results),
                final_standings=cs.season_state.standings,
                final_form_table=cs.season_state.form_table,
            )
        )

    return MultiCompetitionSeasonResult(
        season_seed=config.seed,
        competitions=tuple(full_results),
        completed=all_completed,
        total_fixtures_processed=total_proc,
        total_fixtures_completed=total_comp,
    )
