from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Any

from app.competition.domain import (
    CompetitionSeason,
    CompetitionStage,
    CompetitionStageType,
)
from app.competition.fixtures import Fixture
from app.competition.progression import (
    ProgressionResult,
    TieBreakResult,
    evaluate_knockout_stage_progression,
    evaluate_round_robin_completion,
)
from app.competition.season_state import CompetitionSeasonState
from app.match.domain import MatchResult


@dataclass(frozen=True)
class CompetitionProgressionState:
    competition_season_id: str
    current_stage_id: str
    current_stage_index: int
    completed: bool
    winner_club_id: int | None
    advanced_club_ids: tuple[int, ...]
    eliminated_club_ids: tuple[int, ...]
    next_stage_id: str | None

    def __post_init__(self) -> None:
        if not self.competition_season_id or not self.competition_season_id.strip():
            raise ValueError("competition_season_id must be a non-empty string")
        if not self.current_stage_id or not self.current_stage_id.strip():
            raise ValueError("current_stage_id must be a non-empty string")
        if self.current_stage_index < 0:
            raise ValueError("current_stage_index must be >= 0")

        if not isinstance(self.advanced_club_ids, tuple):
            object.__setattr__(self, "advanced_club_ids", tuple(self.advanced_club_ids))
        if not isinstance(self.eliminated_club_ids, tuple):
            object.__setattr__(self, "eliminated_club_ids", tuple(self.eliminated_club_ids))

        for cid in self.advanced_club_ids:
            if cid <= 0:
                raise ValueError("all advanced club IDs must be positive integers")
        for cid in self.eliminated_club_ids:
            if cid <= 0:
                raise ValueError("all eliminated club IDs must be positive integers")

        if len(self.advanced_club_ids) != len(set(self.advanced_club_ids)):
            raise ValueError("advanced_club_ids contains duplicate club IDs")
        if len(self.eliminated_club_ids) != len(set(self.eliminated_club_ids)):
            raise ValueError("eliminated_club_ids contains duplicate club IDs")

        overlap = set(self.advanced_club_ids) & set(self.eliminated_club_ids)
        if overlap:
            raise ValueError(f"clubs appear in both advanced and eliminated lists: {overlap}")

        if self.winner_club_id is not None and self.winner_club_id <= 0:
            raise ValueError("winner_club_id must be a positive integer when present")

        if self.next_stage_id is not None and not self.next_stage_id.strip():
            raise ValueError("next_stage_id must be a non-empty string when present")


def initialize_competition_progression_state(
    competition_season: CompetitionSeason,
) -> CompetitionProgressionState:
    if not competition_season.stages:
        raise ValueError("competition_season must contain at least one stage")

    if not (0 <= competition_season.current_stage_index < len(competition_season.stages)):
        raise ValueError(
            f"current_stage_index ({competition_season.current_stage_index}) is out of bounds for stages count ({len(competition_season.stages)})"
        )

    current_stage = competition_season.stages[competition_season.current_stage_index]

    return CompetitionProgressionState(
        competition_season_id=competition_season.id,
        current_stage_id=current_stage.id,
        current_stage_index=competition_season.current_stage_index,
        completed=False,
        winner_club_id=None,
        advanced_club_ids=(),
        eliminated_club_ids=(),
        next_stage_id=None,
    )


def _validate_inputs_and_season_state(
    competition_season: CompetitionSeason,
    stage: CompetitionStage,
    season_state: CompetitionSeasonState | None,
    match_results: Sequence[MatchResult],
) -> None:
    if stage.competition_season_id != competition_season.id:
        raise ValueError(
            f"Stage competition_season_id '{stage.competition_season_id}' "
            f"does not match competition_season id '{competition_season.id}'"
        )

    current_stage = competition_season.stages[competition_season.current_stage_index]
    if stage.id != current_stage.id:
        raise ValueError(
            f"Provided stage '{stage.id}' is not the current active stage '{current_stage.id}'"
        )

    if season_state is not None:
        if season_state.competition_season_id != competition_season.id:
            raise ValueError(
                f"season_state competition_season_id '{season_state.competition_season_id}' "
                f"does not match competition_season id '{competition_season.id}'"
            )

        if season_state.processed_match_ids:
            processed_set = set(season_state.processed_match_ids)
            for res in match_results:
                if res.match_id not in processed_set:
                    raise ValueError(
                        f"MatchResult id '{res.match_id}' has not been processed in season_state"
                    )


def advance_round_robin_stage(
    competition_season: CompetitionSeason,
    stage: CompetitionStage,
    fixtures: Sequence[Fixture],
    match_results: Sequence[MatchResult],
    season_state: CompetitionSeasonState | None = None,
    qualification_slots: int | None = None,
) -> CompetitionProgressionState:
    _validate_inputs_and_season_state(
        competition_season=competition_season,
        stage=stage,
        season_state=season_state,
        match_results=match_results,
    )

    progression = evaluate_round_robin_completion(
        competition_season=competition_season,
        stage=stage,
        fixtures=fixtures,
        match_results=match_results,
        qualification_slots=qualification_slots,
    )

    if not progression.stage_completed:
        raise ValueError(
            f"Round-robin stage '{stage.id}' cannot be completed with the provided fixtures/match results"
        )

    has_next_stage = competition_season.current_stage_index + 1 < len(competition_season.stages)
    if has_next_stage:
        next_stage = competition_season.stages[competition_season.current_stage_index + 1]
        next_stage_id: str | None = next_stage.id
        completed = False
        winner_club_id = None
    else:
        next_stage_id = None
        completed = True
        winner_club_id = progression.winner_club_id
        if winner_club_id is None:
            raise ValueError(f"Final round-robin stage '{stage.id}' completed but winner_club_id is None")

    return CompetitionProgressionState(
        competition_season_id=competition_season.id,
        current_stage_id=stage.id,
        current_stage_index=competition_season.current_stage_index,
        completed=completed,
        winner_club_id=winner_club_id,
        advanced_club_ids=progression.advanced_club_ids,
        eliminated_club_ids=progression.eliminated_club_ids,
        next_stage_id=next_stage_id,
    )


def advance_knockout_stage(
    competition_season: CompetitionSeason,
    stage: CompetitionStage,
    fixtures: Sequence[Fixture],
    match_results: Sequence[MatchResult],
    tiebreaks: Mapping[str, TieBreakResult] | None = None,
    season_state: CompetitionSeasonState | None = None,
) -> CompetitionProgressionState:
    _validate_inputs_and_season_state(
        competition_season=competition_season,
        stage=stage,
        season_state=season_state,
        match_results=match_results,
    )

    progression = evaluate_knockout_stage_progression(
        competition_season=competition_season,
        stage=stage,
        fixtures=fixtures,
        match_results=match_results,
        tiebreaks=tiebreaks,
    )

    if not progression.stage_completed:
        raise ValueError(
            f"Knockout stage '{stage.id}' cannot be completed (missing fixture results or unresolved tie)"
        )

    has_next_stage = competition_season.current_stage_index + 1 < len(competition_season.stages)
    if has_next_stage:
        next_stage = competition_season.stages[competition_season.current_stage_index + 1]
        next_stage_id: str | None = next_stage.id
        completed = False
        winner_club_id = None
    else:
        next_stage_id = None
        completed = True
        if stage.stage_type == CompetitionStageType.FINAL or len(progression.advanced_club_ids) == 1:
            winner_club_id = progression.winner_club_id
            if winner_club_id is None and len(progression.advanced_club_ids) == 1:
                winner_club_id = progression.advanced_club_ids[0]
            if winner_club_id is None:
                raise ValueError(f"Final knockout stage '{stage.id}' completed but winner_club_id is None")
        else:
            winner_club_id = progression.winner_club_id

    return CompetitionProgressionState(
        competition_season_id=competition_season.id,
        current_stage_id=stage.id,
        current_stage_index=competition_season.current_stage_index,
        completed=completed,
        winner_club_id=winner_club_id,
        advanced_club_ids=progression.advanced_club_ids,
        eliminated_club_ids=progression.eliminated_club_ids,
        next_stage_id=next_stage_id,
    )


def advance_current_stage(
    competition_season: CompetitionSeason,
    season_state: CompetitionSeasonState | None = None,
    progression_state: CompetitionProgressionState | None = None,
    fixtures: Sequence[Fixture] = (),
    match_results: Sequence[MatchResult] = (),
    tiebreaks: Mapping[str, TieBreakResult] | None = None,
    qualification_slots: int | None = None,
) -> CompetitionProgressionState:
    if progression_state is not None:
        if progression_state.competition_season_id != competition_season.id:
            raise ValueError(
                f"progression_state competition_season_id '{progression_state.competition_season_id}' "
                f"does not match competition_season id '{competition_season.id}'"
            )
        if progression_state.completed:
            raise ValueError("Cannot advance a competition season that is already completed")

    if not (0 <= competition_season.current_stage_index < len(competition_season.stages)):
        raise ValueError(
            f"current_stage_index ({competition_season.current_stage_index}) is out of bounds for stages count ({len(competition_season.stages)})"
        )

    current_stage = competition_season.stages[competition_season.current_stage_index]

    if current_stage.stage_type in (
        CompetitionStageType.REGULAR_SEASON,
        CompetitionStageType.GROUP_STAGE,
        CompetitionStageType.LEAGUE_PHASE,
    ):
        return advance_round_robin_stage(
            competition_season=competition_season,
            stage=current_stage,
            fixtures=fixtures,
            match_results=match_results,
            season_state=season_state,
            qualification_slots=qualification_slots,
        )
    elif current_stage.stage_type in (
        CompetitionStageType.ROUND_OF_32,
        CompetitionStageType.ROUND_OF_16,
        CompetitionStageType.QUARTER_FINAL,
        CompetitionStageType.SEMI_FINAL,
        CompetitionStageType.FINAL,
    ):
        return advance_knockout_stage(
            competition_season=competition_season,
            stage=current_stage,
            fixtures=fixtures,
            match_results=match_results,
            tiebreaks=tiebreaks,
            season_state=season_state,
        )
    else:
        raise ValueError(f"Unsupported stage_type '{current_stage.stage_type}'")
