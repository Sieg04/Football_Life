from dataclasses import dataclass, field
from enum import StrEnum
import math


class SimulationMode(StrEnum):
    FAST = "FAST"
    DETAILED = "DETAILED"


class CompetitionType(StrEnum):
    LEAGUE = "LEAGUE"
    DOMESTIC_CUP = "DOMESTIC_CUP"
    EUROPEAN = "EUROPEAN"
    INTERNATIONAL = "INTERNATIONAL"


class MatchEventType(StrEnum):
    GOAL = "GOAL"
    ASSIST = "ASSIST"
    KEY_PASS = "KEY_PASS"
    BIG_SAVE = "BIG_SAVE"
    YELLOW_CARD = "YELLOW_CARD"
    RED_CARD = "RED_CARD"
    SUBSTITUTION = "SUBSTITUTION"
    MISSED_CHANCE = "MISSED_CHANCE"


@dataclass
class MatchContext:
    match_id: str
    home_club_id: int
    away_club_id: int
    competition_type: CompetitionType
    competition_importance: float
    match_importance: float
    seed: str
    home_advantage_points: float = 3.0
    rivalry_factor: float = 1.0
    simulation_mode: SimulationMode = SimulationMode.DETAILED

    def __post_init__(self) -> None:
        if self.home_club_id == self.away_club_id:
            raise ValueError("home_club_id and away_club_id must be different")
        if not (0.0 <= self.competition_importance <= 100.0):
            raise ValueError("competition_importance must be between 0 and 100")
        if not (0.0 <= self.match_importance <= 100.0):
            raise ValueError("match_importance must be between 0 and 100")
        if self.rivalry_factor < 0.0:
            raise ValueError("rivalry_factor must be non-negative")
        if not math.isfinite(self.home_advantage_points):
            raise ValueError("home_advantage_points must be a finite number")
        if not self.seed or not self.seed.strip():
            raise ValueError("seed must be a non-empty string")


@dataclass
class PlayerMatchPerformance:
    player_id: str
    match_id: str
    starter: bool
    minutes: int
    rating: float
    goals: int
    assists: int
    shots: int
    shots_on_target: int
    key_passes: int
    tackles: int
    interceptions: int
    clearances: int
    saves: int
    role: str
    position: str
    latent_influence: float

    def __post_init__(self) -> None:
        if not (0 <= self.minutes <= 120):
            raise ValueError("minutes must be between 0 and 120")
        if not (1.0 <= self.rating <= 10.0):
            raise ValueError("rating must be between 1.0 and 10.0")

        counting_stats = (
            ("goals", self.goals),
            ("assists", self.assists),
            ("shots", self.shots),
            ("shots_on_target", self.shots_on_target),
            ("key_passes", self.key_passes),
            ("tackles", self.tackles),
            ("interceptions", self.interceptions),
            ("clearances", self.clearances),
            ("saves", self.saves),
        )
        for name, val in counting_stats:
            if val < 0:
                raise ValueError(f"{name} must be non-negative")

        if self.shots_on_target > self.shots:
            raise ValueError("shots_on_target cannot exceed total shots")
        if self.goals > self.shots_on_target:
            raise ValueError("goals cannot exceed shots_on_target")


@dataclass
class MatchEvent:
    minute: int
    event_type: MatchEventType
    primary_player_id: str
    secondary_player_id: str | None = None
    metadata: dict = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not (0 <= self.minute <= 120):
            raise ValueError("minute must be between 0 and 120")


@dataclass
class MatchResult:
    match_id: str
    home_club_id: int
    away_club_id: int
    home_score: int
    away_score: int
    home_xg: float
    away_xg: float
    home_possession: float
    away_possession: float
    home_shots: int
    away_shots: int
    player_performances: list[PlayerMatchPerformance]
    events: list[MatchEvent]

    def __post_init__(self) -> None:
        if self.home_club_id == self.away_club_id:
            raise ValueError("home_club_id and away_club_id must be different")
        if self.home_score < 0 or self.away_score < 0:
            raise ValueError("scores must be non-negative")
        if self.home_xg < 0.0 or self.away_xg < 0.0:
            raise ValueError("xG must be non-negative")
        if not (0.0 <= self.home_possession <= 100.0) or not (0.0 <= self.away_possession <= 100.0):
            raise ValueError("possession values must be between 0 and 100")
        if abs((self.home_possession + self.away_possession) - 100.0) > 1.0:
            raise ValueError("home_possession and away_possession must sum to approximately 100%")
        if self.home_shots < 0 or self.away_shots < 0:
            raise ValueError("shots must be non-negative")
        if self.home_score > self.home_shots:
            raise ValueError("home_score cannot exceed home_shots")
        if self.away_score > self.away_shots:
            raise ValueError("away_score cannot exceed away_shots")

        seen_player_ids = set()
        for perf in self.player_performances:
            if perf.match_id != self.match_id:
                raise ValueError(f"PlayerMatchPerformance match_id '{perf.match_id}' does not match MatchResult match_id '{self.match_id}'")
            if perf.player_id in seen_player_ids:
                raise ValueError(f"Duplicate player performance record for player_id '{perf.player_id}'")
            seen_player_ids.add(perf.player_id)

        for event in self.events:
            if not (0 <= event.minute <= 120):
                raise ValueError(f"MatchEvent minute '{event.minute}' is outside valid 0..120 range")
