from collections.abc import Mapping
from dataclasses import dataclass, field
from datetime import date
from enum import StrEnum
from types import MappingProxyType
from typing import Any

from app.match.domain import CompetitionType


class CompetitionFormat(StrEnum):
    ROUND_ROBIN = "ROUND_ROBIN"
    SINGLE_ELIMINATION = "SINGLE_ELIMINATION"
    TWO_LEG_ELIMINATION = "TWO_LEG_ELIMINATION"
    LEAGUE_PHASE = "LEAGUE_PHASE"


class CompetitionStageType(StrEnum):
    REGULAR_SEASON = "REGULAR_SEASON"
    GROUP_STAGE = "GROUP_STAGE"
    LEAGUE_PHASE = "LEAGUE_PHASE"
    ROUND_OF_32 = "ROUND_OF_32"
    ROUND_OF_16 = "ROUND_OF_16"
    QUARTER_FINAL = "QUARTER_FINAL"
    SEMI_FINAL = "SEMI_FINAL"
    FINAL = "FINAL"


class CompetitionSeasonStatus(StrEnum):
    NOT_STARTED = "NOT_STARTED"
    ACTIVE = "ACTIVE"
    COMPLETED = "COMPLETED"


@dataclass(frozen=True)
class Competition:
    id: str
    name: str
    competition_type: CompetitionType
    country_id: int | None
    importance: float
    level: int
    format: CompetitionFormat
    participant_count: int
    rules: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.id or not self.id.strip():
            raise ValueError("id must be a non-empty string")
        if not self.name or not self.name.strip():
            raise ValueError("name must be a non-empty string")
        if not (0.0 <= self.importance <= 100.0):
            raise ValueError("importance must be between 0.0 and 100.0")
        if self.level <= 0:
            raise ValueError("level must be greater than 0")
        if self.participant_count < 2:
            raise ValueError("participant_count must be at least 2")

        if not isinstance(self.rules, MappingProxyType):
            object.__setattr__(self, "rules", MappingProxyType(dict(self.rules)))


@dataclass(frozen=True)
class CompetitionParticipant:
    competition_season_id: str
    club_id: int
    seed: str

    def __post_init__(self) -> None:
        if not self.competition_season_id or not self.competition_season_id.strip():
            raise ValueError("competition_season_id must be a non-empty string")
        if self.club_id <= 0:
            raise ValueError("club_id must be a positive integer")
        if not self.seed or not self.seed.strip():
            raise ValueError("seed must be a non-empty string")


@dataclass
class CompetitionStage:
    id: str
    competition_season_id: str
    stage_type: CompetitionStageType
    stage_number: int
    participant_club_ids: tuple[int, ...]
    completed: bool = False

    def __post_init__(self) -> None:
        if not self.id or not self.id.strip():
            raise ValueError("id must be a non-empty string")
        if not self.competition_season_id or not self.competition_season_id.strip():
            raise ValueError("competition_season_id must be a non-empty string")
        if self.stage_number < 1:
            raise ValueError("stage_number must be >= 1")

        if not isinstance(self.participant_club_ids, tuple):
            self.participant_club_ids = tuple(self.participant_club_ids)

        if len(self.participant_club_ids) < 2:
            raise ValueError("participant_club_ids must contain at least 2 clubs")

        if any(cid <= 0 for cid in self.participant_club_ids):
            raise ValueError("all club_ids must be positive integers")

        if len(self.participant_club_ids) != len(set(self.participant_club_ids)):
            raise ValueError("duplicate club IDs are not allowed in stage participants")


@dataclass
class CompetitionSeason:
    id: str
    competition_id: str
    season_label: str
    start_date: date
    end_date: date
    participants: tuple[CompetitionParticipant, ...]
    stages: tuple[CompetitionStage, ...]
    seed: str
    status: CompetitionSeasonStatus = CompetitionSeasonStatus.NOT_STARTED
    current_stage_index: int = 0
    winner_id: int | None = None

    def __post_init__(self) -> None:
        if not self.id or not self.id.strip():
            raise ValueError("id must be a non-empty string")
        if not self.competition_id or not self.competition_id.strip():
            raise ValueError("competition_id must be a non-empty string")
        if not self.season_label or not self.season_label.strip():
            raise ValueError("season_label must be a non-empty string")
        if not self.seed or not self.seed.strip():
            raise ValueError("seed must be a non-empty string")
        if self.start_date > self.end_date:
            raise ValueError("start_date must be <= end_date")

        if not isinstance(self.participants, tuple):
            self.participants = tuple(self.participants)
        if len(self.participants) < 2:
            raise ValueError("participants must contain at least 2 participants")

        if not isinstance(self.stages, tuple):
            self.stages = tuple(self.stages)

        if self.current_stage_index < 0:
            raise ValueError("current_stage_index must be >= 0")
        if self.stages and self.current_stage_index >= len(self.stages):
            raise ValueError("current_stage_index out of bounds")

        seen_clubs = set()
        for participant in self.participants:
            if participant.competition_season_id != self.id:
                raise ValueError(
                    f"Participant competition_season_id '{participant.competition_season_id}' "
                    f"does not match season id '{self.id}'"
                )
            if participant.club_id in seen_clubs:
                raise ValueError(f"Duplicate participant club_id '{participant.club_id}'")
            seen_clubs.add(participant.club_id)

        seen_stage_ids = set()
        for stage in self.stages:
            if stage.competition_season_id != self.id:
                raise ValueError(
                    f"Stage competition_season_id '{stage.competition_season_id}' "
                    f"does not match season id '{self.id}'"
                )
            if stage.id in seen_stage_ids:
                raise ValueError(f"Duplicate stage id '{stage.id}'")
            seen_stage_ids.add(stage.id)

        if self.status == CompetitionSeasonStatus.COMPLETED:
            if self.winner_id is None:
                raise ValueError("Completed competition season must have a winner_id")
            if self.winner_id not in seen_clubs:
                raise ValueError(
                    f"Winner club_id '{self.winner_id}' must belong to season participants"
                )

    @property
    def winner_club_id(self) -> int | None:
        return self.winner_id
