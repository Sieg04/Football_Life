from dataclasses import dataclass
from app.football.award_domain import Award, Trophy
from app.football.injury_domain import Injury
from app.football.international_domain import InternationalCallUp
from app.football.statistics_domain import SeasonStatisticsSnapshot


@dataclass(frozen=True)
class LeagueStandingEntry:
    position: int
    club_id: str | int
    club_name: str
    played: int
    won: int
    drawn: int
    lost: int
    goals_for: int
    goals_against: int
    goal_difference: int
    points: int

    def __post_init__(self) -> None:
        if self.position <= 0 or self.played < 0 or self.points < 0:
            raise ValueError("Standing entry values must be valid")


@dataclass(frozen=True)
class SeasonSummary:
    season_number: int
    season_label: str
    club_id: str | int
    club_name: str
    league_code: str
    league_name: str
    league_position: int
    league_standings: tuple[LeagueStandingEntry, ...]
    cup_progress: str
    continental_progress: str
    statistics: SeasonStatisticsSnapshot
    international_call_up: InternationalCallUp | None
    injuries: tuple[Injury, ...]
    trophies: tuple[Trophy, ...]
    awards: tuple[Award, ...]

    def __post_init__(self) -> None:
        if not isinstance(self.league_standings, tuple):
            object.__setattr__(self, "league_standings", tuple(self.league_standings))
        if not isinstance(self.injuries, tuple):
            object.__setattr__(self, "injuries", tuple(self.injuries))
        if not isinstance(self.trophies, tuple):
            object.__setattr__(self, "trophies", tuple(self.trophies))
        if not isinstance(self.awards, tuple):
            object.__setattr__(self, "awards", tuple(self.awards))
