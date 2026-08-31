from dataclasses import dataclass
from enum import StrEnum


class InjuryCategory(StrEnum):
    MINOR = "MINOR"
    MODERATE = "MODERATE"
    MAJOR = "MAJOR"
    SEASON_ENDING = "SEASON_ENDING"


@dataclass(frozen=True)
class Injury:
    id: str
    player_id: str
    category: InjuryCategory
    name: str
    duration_weeks: int
    matches_missed: int
    start_season: int
    start_matchday: int

    def __post_init__(self) -> None:
        if not self.id or not self.player_id:
            raise ValueError("id and player_id cannot be empty")
        if self.duration_weeks <= 0 or self.matches_missed < 0:
            raise ValueError("invalid duration or matches_missed")
