from dataclasses import dataclass
from typing import Mapping, Sequence

from app.competition.domain import (
    CompetitionSeason,
    CompetitionStage,
    CompetitionStageType,
)
from app.competition.fixtures import Fixture
from app.competition.standings import (
    apply_match_result,
    initialize_standings,
    rank_standings,
)
from app.match.domain import MatchResult


@dataclass(frozen=True)
class ProgressionResult:
    competition_season_id: str
    stage_completed: bool
    current_stage_index: int
    advanced_club_ids: tuple[int, ...]
    eliminated_club_ids: tuple[int, ...]
    winner_club_id: int | None = None
    next_stage_id: str | None = None

    def __post_init__(self) -> None:
        if not self.competition_season_id or not self.competition_season_id.strip():
            raise ValueError("competition_season_id must be a non-empty string")
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


@dataclass(frozen=True)
class TieBreakResult:
    winner_club_id: int | None
    method: str

    def __post_init__(self) -> None:
        if not self.method or not self.method.strip():
            raise ValueError("method must be a non-empty string")
        if self.method not in ("PENALTIES", "EXTRA_TIME"):
            raise ValueError(f"Invalid tiebreak method '{self.method}'. Must be 'PENALTIES' or 'EXTRA_TIME'")
        if self.winner_club_id is not None and self.winner_club_id <= 0:
            raise ValueError("winner_club_id must be a positive integer when present")


def evaluate_round_robin_completion(
    competition_season: CompetitionSeason,
    stage: CompetitionStage,
    fixtures: Sequence[Fixture],
    match_results: Sequence[MatchResult],
    qualification_slots: int | None = None,
) -> ProgressionResult:
    if stage.competition_season_id != competition_season.id:
        raise ValueError(
            f"Stage competition_season_id '{stage.competition_season_id}' "
            f"does not match season id '{competition_season.id}'"
        )

    season_club_ids = {p.club_id for p in competition_season.participants}
    if any(cid not in season_club_ids for cid in stage.participant_club_ids):
        raise ValueError("Stage participant club IDs must belong to competition season participants")

    participant_count = len(stage.participant_club_ids)

    if qualification_slots is not None:
        if qualification_slots < 1:
            raise ValueError("qualification_slots must be >= 1")
        if qualification_slots > participant_count:
            raise ValueError(
                f"qualification_slots ({qualification_slots}) cannot exceed participant count ({participant_count})"
            )

    seen_fixture_ids = set()
    for f in fixtures:
        if f.competition_season_id != competition_season.id:
            raise ValueError(f"Fixture '{f.id}' season id '{f.competition_season_id}' does not match '{competition_season.id}'")
        if f.stage_id != stage.id:
            raise ValueError(f"Fixture '{f.id}' stage id '{f.stage_id}' does not match '{stage.id}'")
        if f.id in seen_fixture_ids:
            raise ValueError(f"Duplicate fixture id '{f.id}'")
        seen_fixture_ids.add(f.id)

    fixture_map = {f.id: f for f in fixtures}

    seen_result_ids = set()
    result_map: dict[str, MatchResult] = {}
    for res in match_results:
        if res.match_id in seen_result_ids:
            raise ValueError(f"Duplicate match result id '{res.match_id}'")
        seen_result_ids.add(res.match_id)
        if res.match_id not in fixture_map:
            raise ValueError(f"Match result id '{res.match_id}' does not correspond to any fixture in stage '{stage.id}'")
        result_map[res.match_id] = res

    if len(result_map) < len(fixtures) or len(fixtures) == 0:
        return ProgressionResult(
            competition_season_id=competition_season.id,
            stage_completed=False,
            current_stage_index=competition_season.current_stage_index,
            advanced_club_ids=(),
            eliminated_club_ids=(),
            winner_club_id=None,
            next_stage_id=None,
        )

    standings = initialize_standings(competition_season)
    for res in match_results:
        standings = apply_match_result(standings, res)

    ranked_entries = rank_standings(standings)
    stage_participant_set = set(stage.participant_club_ids)
    stage_ranked_entries = [e for e in ranked_entries if e.club_id in stage_participant_set]

    winner_club_id = stage_ranked_entries[0].club_id

    if qualification_slots is not None:
        advanced_club_ids = tuple(e.club_id for e in stage_ranked_entries[:qualification_slots])
    else:
        advanced_club_ids = (winner_club_id,)

    advanced_set = set(advanced_club_ids)
    eliminated_club_ids = tuple(sorted(cid for cid in stage.participant_club_ids if cid not in advanced_set))

    return ProgressionResult(
        competition_season_id=competition_season.id,
        stage_completed=True,
        current_stage_index=competition_season.current_stage_index,
        advanced_club_ids=advanced_club_ids,
        eliminated_club_ids=eliminated_club_ids,
        winner_club_id=winner_club_id,
        next_stage_id=None,
    )


def calculate_aggregate_score(
    fixtures: Sequence[Fixture],
    match_results: Sequence[MatchResult],
    club_id: int,
) -> int:
    if club_id <= 0:
        raise ValueError("club_id must be a positive integer")

    club_fixtures = [f for f in fixtures if f.home_club_id == club_id or f.away_club_id == club_id]
    if not club_fixtures:
        raise ValueError(f"No fixtures found involving club_id {club_id}")

    opponents = {f.away_club_id if f.home_club_id == club_id else f.home_club_id for f in club_fixtures}
    if len(opponents) != 1:
        raise ValueError(f"Fixtures involving club_id {club_id} are not part of a single tie (multiple opponents: {opponents})")

    opponent_id = next(iter(opponents))

    tie_fixtures = [
        f for f in fixtures
        if (f.home_club_id == club_id and f.away_club_id == opponent_id)
        or (f.home_club_id == opponent_id and f.away_club_id == club_id)
    ]

    if len(tie_fixtures) != 2:
        raise ValueError(f"Expected exactly 2 legs between club {club_id} and club {opponent_id}, found {len(tie_fixtures)}")

    home_legs = [f for f in tie_fixtures if f.home_club_id == club_id]
    away_legs = [f for f in tie_fixtures if f.away_club_id == club_id]

    if len(home_legs) != 1 or len(away_legs) != 1:
        raise ValueError("Tie must consist of exactly 1 home leg and 1 away leg for each club")

    seen_result_ids = set()
    result_map = {}
    for res in match_results:
        if res.match_id in seen_result_ids:
            raise ValueError(f"Duplicate match result id '{res.match_id}'")
        seen_result_ids.add(res.match_id)
        result_map[res.match_id] = res

    goals = 0
    for f in tie_fixtures:
        if f.id not in result_map:
            raise ValueError(f"Missing result for tie fixture '{f.id}'")
        res = result_map[f.id]
        if res.home_club_id == club_id:
            goals += res.home_score
        elif res.away_club_id == club_id:
            goals += res.away_score

    return goals


def resolve_two_leg_tie(
    fixtures: Sequence[Fixture],
    match_results: Sequence[MatchResult],
    club_a_id: int,
    club_b_id: int,
    tiebreak: TieBreakResult | None = None,
) -> int | None:
    if club_a_id <= 0 or club_b_id <= 0:
        raise ValueError("club IDs must be positive integers")
    if club_a_id == club_b_id:
        raise ValueError("club_a_id and club_b_id must be distinct")

    agg_a = calculate_aggregate_score(fixtures, match_results, club_a_id)
    agg_b = calculate_aggregate_score(fixtures, match_results, club_b_id)

    if agg_a > agg_b:
        return club_a_id
    elif agg_b > agg_a:
        return club_b_id
    else:
        if tiebreak is not None and tiebreak.winner_club_id in (club_a_id, club_b_id):
            return tiebreak.winner_club_id
        return None


def evaluate_knockout_stage_progression(
    competition_season: CompetitionSeason,
    stage: CompetitionStage,
    fixtures: Sequence[Fixture],
    match_results: Sequence[MatchResult],
    tiebreaks: Mapping[str, TieBreakResult] | None = None,
) -> ProgressionResult:
    if stage.competition_season_id != competition_season.id:
        raise ValueError(
            f"Stage competition_season_id '{stage.competition_season_id}' "
            f"does not match season id '{competition_season.id}'"
        )

    season_club_ids = {p.club_id for p in competition_season.participants}
    if any(cid not in season_club_ids for cid in stage.participant_club_ids):
        raise ValueError("Stage participant club IDs must belong to competition season participants")

    seen_fixture_ids = set()
    for f in fixtures:
        if f.competition_season_id != competition_season.id:
            raise ValueError(f"Fixture '{f.id}' season id '{f.competition_season_id}' does not match '{competition_season.id}'")
        if f.stage_id != stage.id:
            raise ValueError(f"Fixture '{f.id}' stage id '{f.stage_id}' does not match '{stage.id}'")
        if f.id in seen_fixture_ids:
            raise ValueError(f"Duplicate fixture id '{f.id}'")
        seen_fixture_ids.add(f.id)

    fixture_map = {f.id: f for f in fixtures}

    seen_result_ids = set()
    result_map: dict[str, MatchResult] = {}
    for res in match_results:
        if res.match_id in seen_result_ids:
            raise ValueError(f"Duplicate match result id '{res.match_id}'")
        seen_result_ids.add(res.match_id)
        if res.match_id not in fixture_map:
            raise ValueError(f"Match result id '{res.match_id}' does not correspond to any fixture in stage '{stage.id}'")
        result_map[res.match_id] = res

    advanced_clubs: list[int] = []
    eliminated_clubs: list[int] = []

    if len(fixtures) == 0:
        return ProgressionResult(
            competition_season_id=competition_season.id,
            stage_completed=False,
            current_stage_index=competition_season.current_stage_index,
            advanced_club_ids=(),
            eliminated_club_ids=(),
            winner_club_id=None,
            next_stage_id=None,
        )

    is_two_leg = any(
        sum(1 for f2 in fixtures if set([f2.home_club_id, f2.away_club_id]) == set([f.home_club_id, f.away_club_id])) == 2
        for f in fixtures
    )

    if is_two_leg:
        ties: dict[tuple[int, int], list[Fixture]] = {}
        for f in fixtures:
            pair_key = tuple(sorted([f.home_club_id, f.away_club_id]))
            ties.setdefault(pair_key, []).append(f)

        for (club_a, club_b), tie_fxs in ties.items():
            if len(tie_fxs) != 2:
                return ProgressionResult(
                    competition_season_id=competition_season.id,
                    stage_completed=False,
                    current_stage_index=competition_season.current_stage_index,
                    advanced_club_ids=(),
                    eliminated_club_ids=(),
                    winner_club_id=None,
                    next_stage_id=None,
                )
            if not all(fx.id in result_map for fx in tie_fxs):
                return ProgressionResult(
                    competition_season_id=competition_season.id,
                    stage_completed=False,
                    current_stage_index=competition_season.current_stage_index,
                    advanced_club_ids=(),
                    eliminated_club_ids=(),
                    winner_club_id=None,
                    next_stage_id=None,
                )

            tb = None
            if tiebreaks is not None:
                for fx in tie_fxs:
                    if fx.id in tiebreaks:
                        tb = tiebreaks[fx.id]
                        break
                if tb is None:
                    pair_str = f"{club_a}:{club_b}"
                    if pair_str in tiebreaks:
                        tb = tiebreaks[pair_str]

            winner_id = resolve_two_leg_tie(fixtures, match_results, club_a, club_b, tiebreak=tb)
            if winner_id is None:
                return ProgressionResult(
                    competition_season_id=competition_season.id,
                    stage_completed=False,
                    current_stage_index=competition_season.current_stage_index,
                    advanced_club_ids=(),
                    eliminated_club_ids=(),
                    winner_club_id=None,
                    next_stage_id=None,
                )
            loser_id = club_b if winner_id == club_a else club_a
            advanced_clubs.append(winner_id)
            eliminated_clubs.append(loser_id)
    else:
        for f in fixtures:
            if f.id not in result_map:
                return ProgressionResult(
                    competition_season_id=competition_season.id,
                    stage_completed=False,
                    current_stage_index=competition_season.current_stage_index,
                    advanced_club_ids=(),
                    eliminated_club_ids=(),
                    winner_club_id=None,
                    next_stage_id=None,
                )
            res = result_map[f.id]
            if res.home_score > res.away_score:
                winner_id = res.home_club_id
                loser_id = res.away_club_id
            elif res.away_score > res.home_score:
                winner_id = res.away_club_id
                loser_id = res.home_club_id
            else:
                tb = None
                if tiebreaks is not None:
                    if f.id in tiebreaks:
                        tb = tiebreaks[f.id]
                    else:
                        pair_str = f"{min(f.home_club_id, f.away_club_id)}:{max(f.home_club_id, f.away_club_id)}"
                        if pair_str in tiebreaks:
                            tb = tiebreaks[pair_str]
                if tb is not None and tb.winner_club_id in (f.home_club_id, f.away_club_id):
                    winner_id = tb.winner_club_id
                    loser_id = f.away_club_id if winner_id == f.home_club_id else f.home_club_id
                else:
                    return ProgressionResult(
                        competition_season_id=competition_season.id,
                        stage_completed=False,
                        current_stage_index=competition_season.current_stage_index,
                        advanced_club_ids=(),
                        eliminated_club_ids=(),
                        winner_club_id=None,
                        next_stage_id=None,
                    )

            advanced_clubs.append(winner_id)
            eliminated_clubs.append(loser_id)

    winner_club_id = None
    if stage.stage_type == CompetitionStageType.FINAL:
        if len(advanced_clubs) == 1:
            winner_club_id = advanced_clubs[0]

    adv_tuple = tuple(sorted(advanced_clubs))
    elim_tuple = tuple(sorted(eliminated_clubs))

    return ProgressionResult(
        competition_season_id=competition_season.id,
        stage_completed=True,
        current_stage_index=competition_season.current_stage_index,
        advanced_club_ids=adv_tuple,
        eliminated_club_ids=elim_tuple,
        winner_club_id=winner_club_id,
        next_stage_id=None,
    )


def build_next_stage_participants(
    stage: CompetitionStage,
    progression: ProgressionResult,
    next_stage_id: str,
    next_stage_number: int,
    next_stage_type: CompetitionStageType,
) -> CompetitionStage:
    if not progression.stage_completed:
        raise ValueError("Cannot build next stage from an incomplete progression result")
    if not next_stage_id or not next_stage_id.strip():
        raise ValueError("next_stage_id must be a non-empty string")
    if next_stage_number < 1:
        raise ValueError("next_stage_number must be >= 1")
    if next_stage_number <= stage.stage_number:
        raise ValueError(
            f"next_stage_number ({next_stage_number}) must be greater than current stage_number ({stage.stage_number})"
        )

    return CompetitionStage(
        id=next_stage_id,
        competition_season_id=stage.competition_season_id,
        stage_type=next_stage_type,
        stage_number=next_stage_number,
        participant_club_ids=progression.advanced_club_ids,
        completed=False,
    )
