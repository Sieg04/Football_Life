from dataclasses import dataclass
from enum import StrEnum


class InternationalStatus(StrEnum):
    NOT_SELECTED = "NOT_SELECTED"
    PRESELECTED = "PRESELECTED"
    CALLED_UP = "CALLED_UP"
    BENCH = "BENCH"
    STARTER = "STARTER"


@dataclass(frozen=True)
class InternationalCallUp:
    id: str
    player_id: str
    country_code: str
    season_number: int
    status: InternationalStatus
    caps: int
    goals: int
    assists: int

    def __post_init__(self) -> None:
        if not self.id or not self.player_id or not self.country_code:
            raise ValueError("id, player_id, and country_code cannot be empty")
        if self.caps < 0 or self.goals < 0 or self.assists < 0:
            raise ValueError("caps, goals, assists must be non-negative")
