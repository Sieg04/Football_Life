from collections import defaultdict
from app.football.award_domain import Award, Trophy
from app.football.international_domain import InternationalCallUp
from app.football.statistics_domain import (
    CareerStatistics,
    CompetitionStatistics,
    SeasonStatisticsSnapshot,
)
from app.match.domain import PlayerMatchPerformance


def aggregate_season_statistics(
    season_number: int,
    season_label: str,
    club_id: str | int,
    club_name: str,
    match_performances: list[tuple[str, str, PlayerMatchPerformance]],
) -> SeasonStatisticsSnapshot:
    total_apps = len(match_performances)
    total_starts = sum(1 for _, _, p in match_performances if p.starter)
    total_mins = sum(p.minutes for _, _, p in match_performances)
    total_goals = sum(p.goals for _, _, p in match_performances)
    total_assists = sum(p.assists for _, _, p in match_performances)
    total_yellows = 0
    total_reds = 0

    ratings = [p.rating for _, _, p in match_performances if p.rating > 0.0]
    avg_rating = round(sum(ratings) / len(ratings), 2) if ratings else 6.5

    comp_groups = defaultdict(list)
    for comp_id, comp_name, perf in match_performances:
        comp_groups[(comp_id, comp_name)].append(perf)

    comp_stats_list: list[CompetitionStatistics] = []
    for (c_id, c_name), perfs in comp_groups.items():
        c_apps = len(perfs)
        c_starts = sum(1 for p in perfs if p.starter)
        c_mins = sum(p.minutes for p in perfs)
        c_goals = sum(p.goals for p in perfs)
        c_assists = sum(p.assists for p in perfs)
        c_ratings = [p.rating for p in perfs if p.rating > 0.0]
        c_avg_rating = round(sum(c_ratings) / len(c_ratings), 2) if c_ratings else 6.5

        comp_stats_list.append(
            CompetitionStatistics(
                competition_id=c_id,
                competition_name=c_name,
                appearances=c_apps,
                starts=c_starts,
                minutes=c_mins,
                goals=c_goals,
                assists=c_assists,
                yellow_cards=0,
                red_cards=0,
                average_rating=c_avg_rating,
            )
        )

    return SeasonStatisticsSnapshot(
        season_number=season_number,
        season_label=season_label,
        club_id=club_id,
        club_name=club_name,
        appearances=total_apps,
        starts=total_starts,
        minutes=total_mins,
        goals=total_goals,
        assists=total_assists,
        yellow_cards=total_yellows,
        red_cards=total_reds,
        average_rating=avg_rating,
        competition_stats=tuple(comp_stats_list),
    )


def calculate_career_totals(
    season_snapshots: list[SeasonStatisticsSnapshot],
    trophies: list[Trophy],
    awards: list[Award],
    international_call_ups: list[InternationalCallUp],
) -> CareerStatistics:
    total_apps = sum(s.appearances for s in season_snapshots)
    total_starts = sum(s.starts for s in season_snapshots)
    total_mins = sum(s.minutes for s in season_snapshots)
    total_goals = sum(s.goals for s in season_snapshots)
    total_assists = sum(s.assists for s in season_snapshots)
    total_yellows = sum(s.yellow_cards for s in season_snapshots)
    total_reds = sum(s.red_cards for s in season_snapshots)

    all_ratings = [s.average_rating for s in season_snapshots if s.appearances > 0]
    overall_avg_rating = round(sum(all_ratings) / len(all_ratings), 2) if all_ratings else 0.0

    int_caps = sum(c.caps for c in international_call_ups)
    int_goals = sum(c.goals for c in international_call_ups)
    int_assists = sum(c.assists for c in international_call_ups)

    return CareerStatistics(
        total_appearances=total_apps,
        total_starts=total_starts,
        total_minutes=total_mins,
        total_goals=total_goals,
        total_assists=total_assists,
        total_yellow_cards=total_yellows,
        total_red_cards=total_reds,
        overall_average_rating=overall_avg_rating,
        total_trophies=len(trophies),
        total_awards=len(awards),
        international_caps=int_caps,
        international_goals=int_goals,
        international_assists=int_assists,
    )
