from dataclasses import dataclass, field
from datetime import date
from enum import StrEnum
from typing import Any

from app.event.career_domain import CareerEvent, CareerRecord
from app.event.decisions import Decision
from app.event.presentation_domain import CareerPresentation
from app.player.domain import Player


class CareerPhase(StrEnum):
    YOUTH = "YOUTH"
    EARLY_PRO = "EARLY_PRO"
    DEVELOPMENT = "DEVELOPMENT"
    PRIME = "PRIME"
    LATE_PRIME = "LATE_PRIME"
    DECLINE = "DECLINE"
    VETERAN = "VETERAN"


class CareerSessionStatus(StrEnum):
    SETUP = "SETUP"
    ACTIVE = "ACTIVE"
    EVENT_PENDING = "EVENT_PENDING"
    DECISION_PENDING = "DECISION_PENDING"
    PAUSED = "PAUSED"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


@dataclass
class SeasonalPlayingTimeInput:
    minutes_played: int = 2000
    playing_time_factor: float | None = None


@dataclass
class SeasonalPerformanceInput:
    average_rating: float = 6.8
    performance_factor: float | None = None


@dataclass
class SeasonalEnvironmentInput:
    facilities: float = 50.0
    manager_player_development: float = 50.0


@dataclass
class MatchDrivenSeasonInput:
    season_performance: object
    environment_input: SeasonalEnvironmentInput = field(default_factory=SeasonalEnvironmentInput)

    @property
    def playing_time_factor(self) -> float:
        return float(getattr(self.season_performance, "playing_time_factor", 1.0))

    @property
    def performance_factor(self) -> float:
        return float(getattr(self.season_performance, "performance_factor", 1.0))


@dataclass
class SeasonSnapshot:
    season_number: int
    season_label: str
    starting_age: int
    ending_age: int
    club_id: Any
    starting_position: str
    ending_position: str
    starting_ability: float
    ending_ability: float
    starting_ovr: float
    ending_ovr: float
    career_phase_at_start: CareerPhase
    career_phase_at_end: CareerPhase
    playing_time_input: SeasonalPlayingTimeInput
    performance_input: SeasonalPerformanceInput
    environment_input: SeasonalEnvironmentInput
    development_budget: float
    development_summary: dict[str, float]
    attribute_changes: dict[str, float]
    season_seed: str
    season_summary: Any = None


@dataclass
class Season:
    season_number: int
    season_label: str
    start_date: date
    end_date: date
    player_id: str
    club_id: Any
    starting_age: int
    ending_age: int
    starting_position: str
    ending_position: str
    starting_ability: float
    ending_ability: float
    starting_ovr: float
    ending_ovr: float
    career_phase_at_start: CareerPhase
    career_phase_at_end: CareerPhase
    playing_time_input: SeasonalPlayingTimeInput
    performance_input: SeasonalPerformanceInput
    environment_input: SeasonalEnvironmentInput
    development_budget: float
    development_summary: dict[str, float]
    attribute_changes: dict[str, float]
    season_seed: str
    is_completed: bool = False
    season_summary: Any = None


@dataclass
class Career:
    id: str
    player: Player
    start_date: date
    end_date: date | None
    current_season_number: int
    current_season_label: str
    current_club_id: Any
    career_phase: CareerPhase
    peak_ability: float
    peak_ovr: float
    peak_age: int
    peak_position: str
    peak_club_id: Any
    seasons: list[Season] = field(default_factory=list)
    snapshots: list[SeasonSnapshot] = field(default_factory=list)
    seed: str = "FL-0000-0000"


@dataclass(frozen=True)
class CareerSetupRequest:
    player_name: str
    position: str = "ST"
    starting_club_id: str = "club_1"
    nationality: str = "Spain"
    seed: str = "FL-CAREER-0001"


@dataclass(frozen=True)
class CareerSessionNotification:
    id: str
    title: str
    message: str
    type: str = "INFO"
    created_at_season: str = "2026/27"


@dataclass(frozen=True)
class CareerSession:
    career_id: str
    player_id: str
    current_season: str
    simulation_position: int
    status: CareerSessionStatus
    career: Career
    career_record: CareerRecord
    presentation: CareerPresentation
    pending_decision: Decision | None = None
    pending_events: tuple[CareerEvent, ...] = field(default_factory=tuple)
    notifications: tuple[CareerSessionNotification, ...] = field(default_factory=tuple)
    last_processed_event_id: str | None = None
    seed: str = "FL-CAREER-0001"


@dataclass(frozen=True)
class CareerAdvanceResult:
    career_id: str
    previous_season: str
    current_season: str
    status: CareerSessionStatus
    processed_events: tuple[CareerEvent, ...]
    new_notifications: tuple[CareerSessionNotification, ...]
    pending_decision: Decision | None = None
    presentation: CareerPresentation | None = None
    updated_career: Career | None = None
    updated_record: CareerRecord | None = None
    success: bool = True
