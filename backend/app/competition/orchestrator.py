from collections.abc import Callable, Sequence
from dataclasses import dataclass
from datetime import date
from typing import Any

from app.competition.domain import Competition, CompetitionSeason
from app.competition.fixtures import Fixture


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
