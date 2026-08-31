from dataclasses import dataclass


@dataclass(frozen=True)
class CompetitionStatistics:
    competition_id: str
    competition_name: str
    appearances: int
    starts: int
    minutes: int
    goals: int
    assists: int
    yellow_cards: int
    red_cards: int
    average_rating: float

    def __post_init__(self) -> None:
        if self.appearances < 0 or self.starts < 0 or self.minutes < 0 or self.goals < 0 or self.assists < 0:
            raise ValueError("Counting statistics cannot be negative")
        if self.starts > self.appearances:
            raise ValueError("starts cannot exceed appearances")


@dataclass(frozen=True)
class SeasonStatisticsSnapshot:
    season_number: int
    season_label: str
    club_id: str | int
    club_name: str
    appearances: int
    starts: int
    minutes: int
    goals: int
    assists: int
    yellow_cards: int
    red_cards: int
    average_rating: float
    competition_stats: tuple[CompetitionStatistics, ...]

    def __post_init__(self) -> None:
        if self.appearances < 0 or self.starts < 0 or self.minutes < 0 or self.goals < 0 or self.assists < 0:
            raise ValueError("Counting statistics cannot be negative")
        if not isinstance(self.competition_stats, tuple):
            object.__setattr__(self, "competition_stats", tuple(self.competition_stats))


@dataclass(frozen=True)
class CareerStatistics:
    total_appearances: int
    total_starts: int
    total_minutes: int
    total_goals: int
    total_assists: int
    total_yellow_cards: int
    total_red_cards: int
    overall_average_rating: float
    total_trophies: int
    total_awards: int
    international_caps: int
    international_goals: int
    international_assists: int

    def __post_init__(self) -> None:
        if self.total_appearances < 0 or self.total_goals < 0 or self.total_assists < 0:
            raise ValueError("Career statistics cannot be negative")
