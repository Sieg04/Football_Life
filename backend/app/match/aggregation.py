from dataclasses import dataclass
import math

from app.match.domain import MatchResult, PlayerMatchPerformance


@dataclass
class SeasonPerformance:
    player_id: str
    season_number: int
    appearances: int
    starts: int
    substitute_appearances: int
    minutes_played: int
    goals: int
    assists: int
    total_shots: int
    shots_on_target: int
    key_passes: int
    tackles: int
    interceptions: int
    clearances: int
    clean_sheets: int
    average_rating: float
    performance_factor: float
    playing_time_factor: float


def calculate_performance_factor(average_rating: float) -> float:
    raw_factor = 1.0 + ((average_rating - 6.8) / 10.0)
    clamped_factor = max(0.80, min(1.20, raw_factor))
    return round(clamped_factor, 4)


def calculate_playing_time_factor(minutes_played: int) -> float:
    if minutes_played <= 300:
        return 0.30
    elif minutes_played <= 750:
        return 0.55
    elif minutes_played <= 1400:
        return 0.80
    elif minutes_played <= 2200:
        return 1.00
    elif minutes_played <= 3000:
        return 1.05
    else:
        return 1.00


def aggregate_season_performance(
    player_id: str,
    season_number: int,
    performances: list[PlayerMatchPerformance],
    match_results_map: dict[str, MatchResult] | None = None,
    player_club_id: int | None = None,
) -> SeasonPerformance:
    if match_results_map is None:
        match_results_map = {}

    # Handle empty season explicitly
    if not performances:
        return SeasonPerformance(
            player_id=player_id,
            season_number=season_number,
            appearances=0,
            starts=0,
            substitute_appearances=0,
            minutes_played=0,
            goals=0,
            assists=0,
            total_shots=0,
            shots_on_target=0,
            key_passes=0,
            tackles=0,
            interceptions=0,
            clearances=0,
            clean_sheets=0,
            average_rating=6.8,
            performance_factor=1.00,
            playing_time_factor=0.30,
        )

    # Sort deterministically by match_id for input-order independence
    sorted_performances = sorted(performances, key=lambda p: p.match_id)

    # Input validation
    seen_match_ids = set()
    for p in sorted_performances:
        if p.player_id != player_id:
            raise ValueError(f"Mixed player IDs in season aggregation: expected '{player_id}', got '{p.player_id}'")
        if p.match_id in seen_match_ids:
            raise ValueError(f"Duplicate match record for match_id '{p.match_id}' and player_id '{player_id}'")
        seen_match_ids.add(p.match_id)

        if not (0 <= p.minutes <= 120):
            raise ValueError(f"Invalid minutes '{p.minutes}' for match_id '{p.match_id}'")
        if not (1.0 <= p.rating <= 10.0):
            raise ValueError(f"Invalid rating '{p.rating}' for match_id '{p.match_id}'")
        if p.goals < 0 or p.assists < 0 or p.shots < 0 or p.shots_on_target < 0:
            raise ValueError(f"Negative counting statistics for match_id '{p.match_id}'")

    appearances = sum(1 for p in sorted_performances if p.minutes > 0)
    starts = sum(1 for p in sorted_performances if p.starter and p.minutes > 0)
    substitute_appearances = sum(1 for p in sorted_performances if not p.starter and p.minutes > 0)

    minutes_played = sum(p.minutes for p in sorted_performances)
    goals = sum(p.goals for p in sorted_performances)
    assists = sum(p.assists for p in sorted_performances)
    total_shots = sum(p.shots for p in sorted_performances)
    shots_on_target = sum(p.shots_on_target for p in sorted_performances)
    key_passes = sum(p.key_passes for p in sorted_performances)
    tackles = sum(p.tackles for p in sorted_performances)
    interceptions = sum(p.interceptions for p in sorted_performances)
    clearances = sum(p.clearances for p in sorted_performances)

    # Clean sheet calculation
    clean_sheets = 0
    for p in sorted_performances:
        if p.minutes > 0 and p.match_id in match_results_map:
            res = match_results_map[p.match_id]
            if player_club_id is not None:
                is_home = (res.home_club_id == player_club_id)
                conceded = res.away_score if is_home else res.home_score
            else:
                conceded = res.away_score

            if conceded == 0:
                clean_sheets += 1

    # Weighted average rating by minutes
    if minutes_played > 0:
        weighted_rating_sum = sum(p.rating * p.minutes for p in sorted_performances if p.minutes > 0)
        weighted_average_rating = weighted_rating_sum / minutes_played
    else:
        weighted_average_rating = 6.8

    average_rating_final = round(weighted_average_rating, 2)
    performance_factor = calculate_performance_factor(weighted_average_rating)
    playing_time_factor = calculate_playing_time_factor(minutes_played)

    return SeasonPerformance(
        player_id=player_id,
        season_number=season_number,
        appearances=appearances,
        starts=starts,
        substitute_appearances=substitute_appearances,
        minutes_played=minutes_played,
        goals=goals,
        assists=assists,
        total_shots=total_shots,
        shots_on_target=shots_on_target,
        key_passes=key_passes,
        tackles=tackles,
        interceptions=interceptions,
        clearances=clearances,
        clean_sheets=clean_sheets,
        average_rating=average_rating_final,
        performance_factor=performance_factor,
        playing_time_factor=playing_time_factor,
    )
