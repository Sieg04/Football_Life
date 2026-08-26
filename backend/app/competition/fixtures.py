from dataclasses import dataclass
from datetime import date, timedelta
from enum import StrEnum
import hashlib

from app.competition.domain import (
    CompetitionSeason,
    CompetitionStage,
    CompetitionStageType,
)


class FixtureStatus(StrEnum):
    SCHEDULED = "SCHEDULED"
    PLAYED = "PLAYED"
    POSTPONED = "POSTPONED"
    CANCELLED = "CANCELLED"


@dataclass(frozen=True)
class Fixture:
    id: str
    competition_season_id: str
    stage_id: str
    round_number: int
    scheduled_date: date
    home_club_id: int
    away_club_id: int
    importance: float
    rivalry_factor: float
    seed: str
    status: FixtureStatus = FixtureStatus.SCHEDULED

    def __post_init__(self) -> None:
        if not self.id or not self.id.strip():
            raise ValueError("id must be a non-empty string")
        if not self.competition_season_id or not self.competition_season_id.strip():
            raise ValueError("competition_season_id must be a non-empty string")
        if not self.stage_id or not self.stage_id.strip():
            raise ValueError("stage_id must be a non-empty string")
        if self.round_number < 1:
            raise ValueError("round_number must be >= 1")
        if self.home_club_id <= 0:
            raise ValueError("home_club_id must be a positive integer")
        if self.away_club_id <= 0:
            raise ValueError("away_club_id must be a positive integer")
        if self.home_club_id == self.away_club_id:
            raise ValueError("home_club_id and away_club_id must be different")
        if not (0.0 <= self.importance <= 100.0):
            raise ValueError("importance must be between 0.0 and 100.0")
        if self.rivalry_factor < 0:
            raise ValueError("rivalry_factor must be >= 0")
        if not self.seed or not self.seed.strip():
            raise ValueError("seed must be a non-empty string")


def generate_fixture_seed(
    season_seed: str,
    competition_season_id: str,
    stage_id: str,
    round_number: int,
    home_club_id: int,
    away_club_id: int,
) -> str:
    if not season_seed or not season_seed.strip():
        raise ValueError("season_seed must be a non-empty string")
    if not competition_season_id or not competition_season_id.strip():
        raise ValueError("competition_season_id must be a non-empty string")
    if not stage_id or not stage_id.strip():
        raise ValueError("stage_id must be a non-empty string")
    if round_number < 1:
        raise ValueError("round_number must be >= 1")
    if home_club_id <= 0 or away_club_id <= 0:
        raise ValueError("club IDs must be positive integers")

    raw_str = f"{season_seed}:{competition_season_id}:{stage_id}:{round_number}:{home_club_id}:{away_club_id}"
    return hashlib.sha256(raw_str.encode("utf-8")).hexdigest()


def calculate_match_importance(
    competition_importance: float,
    stage_type: CompetitionStageType,
    round_number: int,
) -> float:
    stage_overrides = {
        CompetitionStageType.FINAL: 95.0,
        CompetitionStageType.SEMI_FINAL: 85.0,
        CompetitionStageType.QUARTER_FINAL: 75.0,
        CompetitionStageType.ROUND_OF_16: 65.0,
        CompetitionStageType.ROUND_OF_32: 60.0,
    }

    val = stage_overrides.get(stage_type, competition_importance)
    return max(0.0, min(100.0, float(val)))


def _validate_stage_and_season(
    competition_season: CompetitionSeason, stage: CompetitionStage
) -> tuple[int, ...]:
    if stage.competition_season_id != competition_season.id:
        raise ValueError(
            f"Stage competition_season_id '{stage.competition_season_id}' "
            f"does not match season id '{competition_season.id}'"
        )
    if len(stage.participant_club_ids) < 2:
        raise ValueError("Stage must have at least 2 participants")
    if len(stage.participant_club_ids) != len(set(stage.participant_club_ids)):
        raise ValueError("Duplicate club IDs in stage participants")
    if any(cid <= 0 for cid in stage.participant_club_ids):
        raise ValueError("All participant club IDs must be positive integers")
    season_club_ids = {p.club_id for p in competition_season.participants}
    if any(cid not in season_club_ids for cid in stage.participant_club_ids):
        raise ValueError("Stage participant club IDs must belong to season participants")

    return tuple(sorted(stage.participant_club_ids))


def _validate_date_bounds(
    fixture_date: date, competition_season: CompetitionSeason
) -> None:
    if not (competition_season.start_date <= fixture_date <= competition_season.end_date):
        raise ValueError(
            f"Fixture date {fixture_date} is outside competition season window "
            f"[{competition_season.start_date}, {competition_season.end_date}]"
        )


def generate_round_robin_fixtures(
    competition_season: CompetitionSeason,
    stage: CompetitionStage,
    start_date: date,
    interval_days: int = 7,
    competition_importance: float = 50.0,
) -> list[Fixture]:
    if interval_days <= 0:
        raise ValueError("interval_days must be > 0")

    sorted_clubs = _validate_stage_and_season(competition_season, stage)
    _validate_date_bounds(start_date, competition_season)

    n = len(sorted_clubs)

    teams: list[int | None] = list(sorted_clubs)
    if n % 2 != 0:
        teams.append(None)
        num_teams = n + 1
    else:
        num_teams = n

    rounds_in_single = num_teams - 1
    half = num_teams // 2

    single_rr_rounds: list[list[tuple[int, int]]] = []

    current_teams = list(teams)
    for r in range(rounds_in_single):
        pairings: list[tuple[int, int]] = []
        for i in range(half):
            t1 = current_teams[i]
            t2 = current_teams[num_teams - 1 - i]
            if t1 is not None and t2 is not None:
                if (r + i) % 2 == 0:
                    pairings.append((t1, t2))
                else:
                    pairings.append((t2, t1))
        single_rr_rounds.append(pairings)
        current_teams = [current_teams[0]] + [current_teams[-1]] + current_teams[1:-1]

    fixtures: list[Fixture] = []
    total_rounds = rounds_in_single * 2

    for r_idx in range(total_rounds):
        round_number = r_idx + 1
        current_date = start_date + timedelta(days=r_idx * interval_days)
        _validate_date_bounds(current_date, competition_season)

        leg = 1 if r_idx < rounds_in_single else 2
        source_r = r_idx % rounds_in_single
        base_pairings = single_rr_rounds[source_r]

        for home_id, away_id in base_pairings:
            if leg == 2:
                h_id, a_id = away_id, home_id
            else:
                h_id, a_id = home_id, away_id

            fixture_id = f"{competition_season.id}:{stage.id}:{round_number}:{h_id}:{a_id}"
            seed = generate_fixture_seed(
                competition_season.seed,
                competition_season.id,
                stage.id,
                round_number,
                h_id,
                a_id,
            )
            importance = calculate_match_importance(
                competition_importance, stage.stage_type, round_number
            )

            fixtures.append(
                Fixture(
                    id=fixture_id,
                    competition_season_id=competition_season.id,
                    stage_id=stage.id,
                    round_number=round_number,
                    scheduled_date=current_date,
                    home_club_id=h_id,
                    away_club_id=a_id,
                    importance=importance,
                    rivalry_factor=1.0,
                    seed=seed,
                    status=FixtureStatus.SCHEDULED,
                )
            )

    return fixtures


def generate_single_elimination_fixtures(
    competition_season: CompetitionSeason,
    stage: CompetitionStage,
    scheduled_date: date,
    competition_importance: float = 50.0,
) -> list[Fixture]:
    sorted_clubs = _validate_stage_and_season(competition_season, stage)
    _validate_date_bounds(scheduled_date, competition_season)

    n = len(sorted_clubs)

    target_size = 1
    while target_size < n:
        target_size *= 2

    num_byes = target_size - n

    byes = set(sorted_clubs[:num_byes])
    playing_teams = sorted_clubs[num_byes:]

    fixtures: list[Fixture] = []
    round_number = 1

    for i in range(0, len(playing_teams), 2):
        home_id = playing_teams[i]
        away_id = playing_teams[i + 1]

        fixture_id = f"{competition_season.id}:{stage.id}:{round_number}:{home_id}:{away_id}"
        seed = generate_fixture_seed(
            competition_season.seed,
            competition_season.id,
            stage.id,
            round_number,
            home_id,
            away_id,
        )
        importance = calculate_match_importance(
            competition_importance, stage.stage_type, round_number
        )

        fixtures.append(
            Fixture(
                id=fixture_id,
                competition_season_id=competition_season.id,
                stage_id=stage.id,
                round_number=round_number,
                scheduled_date=scheduled_date,
                home_club_id=home_id,
                away_club_id=away_id,
                importance=importance,
                rivalry_factor=1.0,
                seed=seed,
                status=FixtureStatus.SCHEDULED,
            )
        )

    return fixtures


def generate_two_leg_elimination_fixtures(
    competition_season: CompetitionSeason,
    stage: CompetitionStage,
    first_leg_date: date,
    second_leg_date: date,
    interval_days: int = 7,
    competition_importance: float = 50.0,
) -> list[Fixture]:
    if interval_days <= 0:
        raise ValueError("interval_days must be > 0")
    if first_leg_date > second_leg_date:
        raise ValueError("first_leg_date must be <= second_leg_date")

    sorted_clubs = _validate_stage_and_season(competition_season, stage)
    _validate_date_bounds(first_leg_date, competition_season)
    _validate_date_bounds(second_leg_date, competition_season)

    if len(sorted_clubs) % 2 != 0:
        raise ValueError("Two-leg elimination requires an even number of participants")

    fixtures: list[Fixture] = []

    pairings: list[tuple[int, int]] = []
    for i in range(0, len(sorted_clubs), 2):
        pairings.append((sorted_clubs[i], sorted_clubs[i + 1]))

    for home_id, away_id in pairings:
        round_number = 1
        fixture_id_1 = f"{competition_season.id}:{stage.id}:{round_number}:{home_id}:{away_id}"
        seed_1 = generate_fixture_seed(
            competition_season.seed,
            competition_season.id,
            stage.id,
            round_number,
            home_id,
            away_id,
        )
        importance_1 = calculate_match_importance(
            competition_importance, stage.stage_type, round_number
        )

        fixtures.append(
            Fixture(
                id=fixture_id_1,
                competition_season_id=competition_season.id,
                stage_id=stage.id,
                round_number=round_number,
                scheduled_date=first_leg_date,
                home_club_id=home_id,
                away_club_id=away_id,
                importance=importance_1,
                rivalry_factor=1.0,
                seed=seed_1,
                status=FixtureStatus.SCHEDULED,
            )
        )

    for home_id, away_id in pairings:
        round_number = 2
        leg2_home, leg2_away = away_id, home_id
        fixture_id_2 = f"{competition_season.id}:{stage.id}:{round_number}:{leg2_home}:{leg2_away}"
        seed_2 = generate_fixture_seed(
            competition_season.seed,
            competition_season.id,
            stage.id,
            round_number,
            leg2_home,
            leg2_away,
        )
        importance_2 = calculate_match_importance(
            competition_importance, stage.stage_type, round_number
        )

        fixtures.append(
            Fixture(
                id=fixture_id_2,
                competition_season_id=competition_season.id,
                stage_id=stage.id,
                round_number=round_number,
                scheduled_date=second_leg_date,
                home_club_id=leg2_home,
                away_club_id=leg2_away,
                importance=importance_2,
                rivalry_factor=1.0,
                seed=seed_2,
                status=FixtureStatus.SCHEDULED,
            )
        )

    return fixtures
