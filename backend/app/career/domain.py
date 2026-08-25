from dataclasses import dataclass, field
from datetime import date
from enum import StrEnum

from app.player.domain import Player


class CareerPhase(StrEnum):
    YOUTH = "YOUTH"
    EARLY_PRO = "EARLY_PRO"
    DEVELOPMENT = "DEVELOPMENT"
    PRIME = "PRIME"
    LATE_PRIME = "LATE_PRIME"
    DECLINE = "DECLINE"
    VETERAN = "VETERAN"


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
    club_id: int
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


@dataclass
class Season:
    season_number: int
    season_label: str
    start_date: date
    end_date: date
    player_id: str
    club_id: int
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


@dataclass
class Career:
    id: str
    player: Player
    start_date: date
    end_date: date | None
    current_season_number: int
    current_season_label: str
    current_club_id: int
    career_phase: CareerPhase
    peak_ability: float
    peak_ovr: float
    peak_age: int
    peak_position: str
    peak_club_id: int
    seasons: list[Season] = field(default_factory=list)
    snapshots: list[SeasonSnapshot] = field(default_factory=list)
    seed: str = "FL-0000-0000"
