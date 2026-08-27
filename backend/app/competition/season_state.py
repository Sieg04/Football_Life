from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Any

from app.competition.domain import CompetitionSeason
from app.competition.form import FormRecord, record_form_result
from app.competition.standings import (
    PointsRule,
    StandingEntry,
    StandingsTable,
    apply_match_result,
    get_club_rank,
    initialize_standings,
    rank_standings,
)
from app.match.domain import MatchResult


@dataclass(frozen=True)
class CompetitionSeasonState:
    competition_season_id: str
    standings: StandingsTable
    form_table: Mapping[int, FormRecord]
    processed_match_ids: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.competition_season_id or not self.competition_season_id.strip():
            raise ValueError("competition_season_id must be a non-empty string")

        if self.standings.competition_season_id != self.competition_season_id:
            raise ValueError(
                f"standings competition_season_id '{self.standings.competition_season_id}' "
                f"does not match competition_season_id '{self.competition_season_id}'"
            )

        if not isinstance(self.processed_match_ids, tuple):
            object.__setattr__(self, "processed_match_ids", tuple(self.processed_match_ids))

        for mid in self.processed_match_ids:
            if not mid or not mid.strip():
                raise ValueError("processed_match_ids contains empty or whitespace string")

        if len(self.processed_match_ids) != len(set(self.processed_match_ids)):
            raise ValueError("duplicate match IDs found in processed_match_ids")

        if not isinstance(self.form_table, MappingProxyType):
            object.__setattr__(self, "form_table", MappingProxyType(dict(self.form_table)))

        standing_club_ids = {entry.club_id for entry in self.standings.entries}
        form_club_ids = set(self.form_table.keys())

        if standing_club_ids != form_club_ids:
            raise ValueError(
                f"Form table club IDs ({form_club_ids}) do not match standings club IDs ({standing_club_ids})"
            )

        for club_id, record in self.form_table.items():
            if not isinstance(record, FormRecord):
                raise TypeError(f"Form table value for club_id {club_id} is not a FormRecord")
            if record.club_id != club_id:
                raise ValueError(
                    f"FormRecord club_id '{record.club_id}' does not match form_table key '{club_id}'"
                )


def initialize_competition_season_state(
    competition_season: CompetitionSeason,
    points_rule: PointsRule | None = None,
    form_window_size: int = 5,
) -> CompetitionSeasonState:
    if form_window_size < 1:
        raise ValueError("form_window_size must be >= 1")

    standings = initialize_standings(competition_season, points_rule=points_rule)
    form_table = {
        p.club_id: FormRecord(club_id=p.club_id, window_size=form_window_size)
        for p in competition_season.participants
    }

    return CompetitionSeasonState(
        competition_season_id=competition_season.id,
        standings=standings,
        form_table=form_table,
        processed_match_ids=(),
    )


def apply_match_result_to_season_state(
    state: CompetitionSeasonState,
    result: MatchResult,
) -> CompetitionSeasonState:
    if not isinstance(result, MatchResult):
        raise TypeError("result must be a MatchResult instance")

    if not result.match_id or not result.match_id.strip():
        raise ValueError("result.match_id must be a non-empty string")

    if result.match_id in state.processed_match_ids:
        raise ValueError(f"Match ID '{result.match_id}' has already been processed")

    if result.home_club_id not in state.form_table:
        raise ValueError(f"Home club_id '{result.home_club_id}' not found in season state form table")
    if result.away_club_id not in state.form_table:
        raise ValueError(f"Away club_id '{result.away_club_id}' not found in season state form table")

    new_standings = apply_match_result(state.standings, result)

    home_form = record_form_result(state.form_table[result.home_club_id], result)
    away_form = record_form_result(state.form_table[result.away_club_id], result)

    new_form_table = dict(state.form_table)
    new_form_table[result.home_club_id] = home_form
    new_form_table[result.away_club_id] = away_form

    new_processed_ids = state.processed_match_ids + (result.match_id,)

    return CompetitionSeasonState(
        competition_season_id=state.competition_season_id,
        standings=new_standings,
        form_table=new_form_table,
        processed_match_ids=new_processed_ids,
    )


def apply_match_results_to_season_state(
    state: CompetitionSeasonState,
    results: Sequence[MatchResult],
) -> CompetitionSeasonState:
    current_state = state
    for result in results:
        current_state = apply_match_result_to_season_state(current_state, result)
    return current_state


def get_ranked_standings(
    state: CompetitionSeasonState,
) -> tuple[StandingEntry, ...]:
    return rank_standings(state.standings)


def get_season_club_rank(
    state: CompetitionSeasonState,
    club_id: int,
) -> int:
    return get_club_rank(state.standings, club_id)


def get_club_form(
    state: CompetitionSeasonState,
    club_id: int,
) -> FormRecord:
    if club_id not in state.form_table:
        raise ValueError(f"club_id '{club_id}' not found in season state form table")
    return state.form_table[club_id]
