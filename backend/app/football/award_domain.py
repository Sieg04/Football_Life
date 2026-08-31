from dataclasses import dataclass
from enum import StrEnum


class AwardType(StrEnum):
    LEAGUE = "LEAGUE"
    GLOBAL = "GLOBAL"


@dataclass(frozen=True)
class Award:
    id: str
    name: str
    award_type: AwardType
    season_number: int
    winner_player_id: str
    winner_player_name: str
    club_name: str
    description: str

    def __post_init__(self) -> None:
        if not self.id or not self.name or not self.winner_player_id:
            raise ValueError("Award id, name, and winner_player_id cannot be empty")


@dataclass(frozen=True)
class Trophy:
    id: str
    competition_id: str
    competition_name: str
    season_number: int
    winner_club_id: str | int
    winner_club_name: str
    player_involvement: str  # "WINNER", "RUNNER_UP", "PARTICIPANT"

    def __post_init__(self) -> None:
        if not self.id or not self.competition_id or not self.competition_name:
            raise ValueError("Trophy id, competition_id, and competition_name cannot be empty")
