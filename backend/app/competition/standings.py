from dataclasses import dataclass
from typing import Sequence

from app.competition.domain import CompetitionSeason
from app.match.domain import MatchResult


@dataclass(frozen=True)
class PointsRule:
    win_points: int = 3
    draw_points: int = 1
    loss_points: int = 0

    def __post_init__(self) -> None:
        if self.win_points < 0:
            raise ValueError("win_points must be >= 0")
        if self.draw_points < 0:
            raise ValueError("draw_points must be >= 0")
        if self.loss_points < 0:
            raise ValueError("loss_points must be >= 0")


@dataclass(frozen=True)
class StandingEntry:
    club_id: int
    played: int
    wins: int
    draws: int
    losses: int
    goals_for: int
    goals_against: int
    goal_difference: int
    points: int

    def __post_init__(self) -> None:
        if self.club_id <= 0:
            raise ValueError("club_id must be a positive integer")
        if self.played < 0:
            raise ValueError("played must be >= 0")
        if self.wins < 0:
            raise ValueError("wins must be >= 0")
        if self.draws < 0:
            raise ValueError("draws must be >= 0")
        if self.losses < 0:
            raise ValueError("losses must be >= 0")
        if self.goals_for < 0:
            raise ValueError("goals_for must be >= 0")
        if self.goals_against < 0:
            raise ValueError("goals_against must be >= 0")
        if self.points < 0:
            raise ValueError("points must be >= 0")

        if self.played != self.wins + self.draws + self.losses:
            raise ValueError(
                f"played ({self.played}) must equal wins + draws + losses "
                f"({self.wins} + {self.draws} + {self.losses})"
            )

        expected_gd = self.goals_for - self.goals_against
        if self.goal_difference != expected_gd:
            raise ValueError(
                f"goal_difference ({self.goal_difference}) must equal goals_for - goals_against "
                f"({self.goals_for} - {self.goals_against} = {expected_gd})"
            )


@dataclass(frozen=True)
class StandingsTable:
    competition_season_id: str
    entries: tuple[StandingEntry, ...]
    points_rule: PointsRule = PointsRule()

    def __post_init__(self) -> None:
        if not self.competition_season_id or not self.competition_season_id.strip():
            raise ValueError("competition_season_id must be a non-empty string")

        if not isinstance(self.entries, tuple):
            object.__setattr__(self, "entries", tuple(self.entries))

        if len(self.entries) < 2:
            raise ValueError("entries must contain at least 2 clubs")

        seen_clubs = set()
        for entry in self.entries:
            if entry.club_id in seen_clubs:
                raise ValueError(f"Duplicate club_id '{entry.club_id}' in standings table entries")
            seen_clubs.add(entry.club_id)


def initialize_standings(
    competition_season: CompetitionSeason,
    points_rule: PointsRule | None = None,
) -> StandingsTable:
    if points_rule is None:
        points_rule = PointsRule()

    participant_club_ids = sorted(p.club_id for p in competition_season.participants)

    entries = tuple(
        StandingEntry(
            club_id=cid,
            played=0,
            wins=0,
            draws=0,
            losses=0,
            goals_for=0,
            goals_against=0,
            goal_difference=0,
            points=0,
        )
        for cid in participant_club_ids
    )

    return StandingsTable(
        competition_season_id=competition_season.id,
        entries=entries,
        points_rule=points_rule,
    )


def apply_match_result(
    standings: StandingsTable,
    result: MatchResult,
) -> StandingsTable:
    if result.home_club_id == result.away_club_id:
        raise ValueError("home_club_id and away_club_id must be different")

    entry_map = {e.club_id: e for e in standings.entries}

    if result.home_club_id not in entry_map:
        raise ValueError(f"Home club_id '{result.home_club_id}' not found in standings table")
    if result.away_club_id not in entry_map:
        raise ValueError(f"Away club_id '{result.away_club_id}' not found in standings table")

    home_entry = entry_map[result.home_club_id]
    away_entry = entry_map[result.away_club_id]

    rule = standings.points_rule

    if result.home_score > result.away_score:
        h_w, h_d, h_l = 1, 0, 0
        a_w, a_d, a_l = 0, 0, 1
        h_pts_delta = rule.win_points
        a_pts_delta = rule.loss_points
    elif result.home_score < result.away_score:
        h_w, h_d, h_l = 0, 0, 1
        a_w, a_d, a_l = 1, 0, 0
        h_pts_delta = rule.loss_points
        a_pts_delta = rule.win_points
    else:
        h_w, h_d, h_l = 0, 1, 0
        a_w, a_d, a_l = 0, 1, 0
        h_pts_delta = rule.draw_points
        a_pts_delta = rule.draw_points

    new_home_gf = home_entry.goals_for + result.home_score
    new_home_ga = home_entry.goals_against + result.away_score
    new_home_entry = StandingEntry(
        club_id=home_entry.club_id,
        played=home_entry.played + 1,
        wins=home_entry.wins + h_w,
        draws=home_entry.draws + h_d,
        losses=home_entry.losses + h_l,
        goals_for=new_home_gf,
        goals_against=new_home_ga,
        goal_difference=new_home_gf - new_home_ga,
        points=home_entry.points + h_pts_delta,
    )

    new_away_gf = away_entry.goals_for + result.away_score
    new_away_ga = away_entry.goals_against + result.home_score
    new_away_entry = StandingEntry(
        club_id=away_entry.club_id,
        played=away_entry.played + 1,
        wins=away_entry.wins + a_w,
        draws=away_entry.draws + a_d,
        losses=away_entry.losses + a_l,
        goals_for=new_away_gf,
        goals_against=new_away_ga,
        goal_difference=new_away_gf - new_away_ga,
        points=away_entry.points + a_pts_delta,
    )

    new_entries = tuple(
        new_home_entry
        if e.club_id == result.home_club_id
        else (new_away_entry if e.club_id == result.away_club_id else e)
        for e in standings.entries
    )

    return StandingsTable(
        competition_season_id=standings.competition_season_id,
        entries=new_entries,
        points_rule=standings.points_rule,
    )


def rank_standings(
    standings: StandingsTable,
) -> tuple[StandingEntry, ...]:
    return tuple(
        sorted(
            standings.entries,
            key=lambda e: (-e.points, -e.goal_difference, -e.goals_for, e.club_id),
        )
    )


def get_club_rank(
    standings: StandingsTable,
    club_id: int,
) -> int:
    ranked = rank_standings(standings)
    for idx, entry in enumerate(ranked):
        if entry.club_id == club_id:
            return idx + 1
    raise ValueError(f"club_id '{club_id}' not found in standings table")
