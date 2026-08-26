from dataclasses import dataclass
from typing import Sequence

from app.match.domain import MatchResult


@dataclass(frozen=True)
class FormRecord:
    club_id: int
    window_size: int = 5
    results: tuple[str, ...] = ()
    goals_for: tuple[int, ...] = ()
    goals_against: tuple[int, ...] = ()

    def __post_init__(self) -> None:
        if self.club_id <= 0:
            raise ValueError("club_id must be a positive integer")
        if self.window_size < 1:
            raise ValueError("window_size must be >= 1")

        if not isinstance(self.results, tuple):
            object.__setattr__(self, "results", tuple(self.results))
        if not isinstance(self.goals_for, tuple):
            object.__setattr__(self, "goals_for", tuple(self.goals_for))
        if not isinstance(self.goals_against, tuple):
            object.__setattr__(self, "goals_against", tuple(self.goals_against))

        if len(self.results) > self.window_size:
            raise ValueError(f"results length ({len(self.results)}) cannot exceed window_size ({self.window_size})")
        if len(self.goals_for) != len(self.results):
            raise ValueError("goals_for length must match results length")
        if len(self.goals_against) != len(self.results):
            raise ValueError("goals_against length must match results length")

        for r in self.results:
            if r not in ("W", "D", "L"):
                raise ValueError(f"Invalid form result string '{r}'. Must be 'W', 'D', or 'L'")

        for gf in self.goals_for:
            if gf < 0:
                raise ValueError("goals_for values must be >= 0")

        for ga in self.goals_against:
            if ga < 0:
                raise ValueError("goals_against values must be >= 0")


def record_form_result(
    form: FormRecord,
    result: MatchResult,
) -> FormRecord:
    if form.club_id == result.home_club_id:
        gf = result.home_score
        ga = result.away_score
    elif form.club_id == result.away_club_id:
        gf = result.away_score
        ga = result.home_score
    else:
        raise ValueError(f"form.club_id '{form.club_id}' is not involved in MatchResult (home: {result.home_club_id}, away: {result.away_club_id})")

    if gf > ga:
        res_char = "W"
    elif gf < ga:
        res_char = "L"
    else:
        res_char = "D"

    new_results = list(form.results) + [res_char]
    new_gf = list(form.goals_for) + [gf]
    new_ga = list(form.goals_against) + [ga]

    if len(new_results) > form.window_size:
        new_results = new_results[-form.window_size :]
        new_gf = new_gf[-form.window_size :]
        new_ga = new_ga[-form.window_size :]

    return FormRecord(
        club_id=form.club_id,
        window_size=form.window_size,
        results=tuple(new_results),
        goals_for=tuple(new_gf),
        goals_against=tuple(new_ga),
    )


def build_form_table(
    club_ids: Sequence[int],
    match_results: Sequence[MatchResult],
    window_size: int = 5,
) -> dict[int, FormRecord]:
    if window_size < 1:
        raise ValueError("window_size must be >= 1")

    club_id_list = list(club_ids)
    if len(club_id_list) != len(set(club_id_list)):
        raise ValueError("duplicate club IDs found in club_ids")

    form_map = {
        cid: FormRecord(club_id=cid, window_size=window_size)
        for cid in club_id_list
    }

    # Sort match results deterministically by match_id ASC
    sorted_matches = sorted(match_results, key=lambda m: m.match_id)

    for match in sorted_matches:
        if match.home_club_id in form_map:
            form_map[match.home_club_id] = record_form_result(form_map[match.home_club_id], match)
        if match.away_club_id in form_map:
            form_map[match.away_club_id] = record_form_result(form_map[match.away_club_id], match)

    return form_map


def calculate_form_points(form: FormRecord) -> int:
    points_map = {"W": 3, "D": 1, "L": 0}
    return sum(points_map[r] for r in form.results)


def calculate_form_rate(form: FormRecord) -> float:
    if not form.results:
        return 0.0
    pts = calculate_form_points(form)
    max_pts = len(form.results) * 3
    return pts / max_pts


def calculate_goal_difference(form: FormRecord) -> int:
    return sum(form.goals_for) - sum(form.goals_against)
