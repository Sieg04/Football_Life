import hashlib
import json
from pathlib import Path

from app.football.award_engine import evaluate_season_awards
from app.football.injury_engine import create_injury
from app.football.international_engine import evaluate_international_call_up
from app.football.match_engine import simulate_single_match
from app.football.season_domain import LeagueStandingEntry, SeasonSummary
from app.football.statistics_engine import aggregate_season_statistics
from app.match.domain import PlayerMatchPerformance


def _hash_seed(seed_str: str) -> int:
    return int(hashlib.sha256(seed_str.encode("utf-8")).hexdigest(), 16)


def _load_rules(filename: str) -> dict:
    path = Path(__file__).resolve().parents[2] / "data" / "rules" / filename
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return {}


COMP_RULES = _load_rules("competitions.json")
WORLD_DATA_PATH = Path(__file__).resolve().parents[2] / "data" / "world.json"


def _load_world_json() -> dict:
    if WORLD_DATA_PATH.exists():
        return json.loads(WORLD_DATA_PATH.read_text(encoding="utf-8"))
    return {}


def simulate_full_season(
    season_number: int,
    season_label: str,
    player_id: str,
    player_name: str,
    player_age: int,
    player_nationality: str,
    player_position: str,
    player_ovr: float,
    club_name: str,
    league_code: str = "ESP1",
    seed: str = "SEASON_SEED",
) -> SeasonSummary:
    world_def = _load_world_json()
    clubs_in_world = world_def.get("clubs", [])

    league_clubs = [c for c in clubs_in_world if c.get("league_code") == league_code]
    if not any(c["name"] == club_name for c in league_clubs):
        league_clubs.append({"name": club_name, "target_strength": int(player_ovr)})

    while len(league_clubs) < 18:
        league_clubs.append({"name": f"Club_{len(league_clubs) + 1}", "target_strength": 72 + (len(league_clubs) % 12)})

    club_names = [c["name"] for c in league_clubs]
    club_strengths = {c["name"]: float(c.get("target_strength", 75)) for c in league_clubs}

    standings_map = {
        name: {"P": 0, "W": 0, "D": 0, "L": 0, "GF": 0, "GA": 0, "PTS": 0}
        for name in club_names
    }

    match_performances: list[tuple[str, str, PlayerMatchPerformance]] = []
    injuries_list = []
    is_injured_flag = False
    matches_missed_left = 0

    h_base = _hash_seed(f"{seed}_L_{season_number}_{player_id}")

    fixture_index = 0
    for home_club in club_names:
        for away_club in club_names:
            if home_club == away_club:
                continue
            fixture_index += 1
            m_id = f"M_L_{season_number}_{fixture_index}"
            m_seed = f"{seed}_{m_id}"

            outcome = simulate_single_match(
                match_id=m_id,
                home_club_id=home_club,
                away_club_id=away_club,
                home_strength=club_strengths[home_club],
                away_strength=club_strengths[away_club],
                protagonist_id=player_id,
                protagonist_club_id=club_name,
                protagonist_ovr=player_ovr,
                protagonist_pos=player_position,
                protagonist_form=1.0,
                is_injured=is_injured_flag,
                seed=m_seed,
            )

            st_h = standings_map[home_club]
            st_a = standings_map[away_club]

            st_h["P"] += 1
            st_a["P"] += 1
            st_h["GF"] += outcome.home_score
            st_h["GA"] += outcome.away_score
            st_a["GF"] += outcome.away_score
            st_a["GA"] += outcome.home_score

            if outcome.winner_club_id == home_club:
                st_h["W"] += 1
                st_h["PTS"] += 3
                st_a["L"] += 1
            elif outcome.winner_club_id == away_club:
                st_a["W"] += 1
                st_a["PTS"] += 3
                st_h["L"] += 1
            else:
                st_h["D"] += 1
                st_a["D"] += 1
                st_h["PTS"] += 1
                st_a["PTS"] += 1

            if outcome.protagonist_performance:
                match_performances.append((league_code, "Domestic League", outcome.protagonist_performance))

            if is_injured_flag:
                matches_missed_left -= 1
                if matches_missed_left <= 0:
                    is_injured_flag = False

            if outcome.protagonist_injured and outcome.injury_severity:
                inj = create_injury(
                    injury_id=f"INJ_{season_number}_{fixture_index}",
                    player_id=player_id,
                    category=outcome.injury_severity,
                    start_season=season_number,
                    start_matchday=fixture_index,
                    seed=m_seed,
                )
                injuries_list.append(inj)
                is_injured_flag = True
                matches_missed_left = inj.matches_missed

    sorted_standings = sorted(
        standings_map.items(),
        key=lambda item: (item[1]["PTS"], item[1]["GF"] - item[1]["GA"], item[1]["GF"]),
        reverse=True,
    )

    standing_entries = []
    player_club_position = 1
    for pos, (c_name, stats) in enumerate(sorted_standings, start=1):
        if c_name == club_name:
            player_club_position = pos
        standing_entries.append(
            LeagueStandingEntry(
                position=pos,
                club_id=c_name,
                club_name=c_name,
                played=stats["P"],
                won=stats["W"],
                drawn=stats["D"],
                lost=stats["L"],
                goals_for=stats["GF"],
                goals_against=stats["GA"],
                goal_difference=stats["GF"] - stats["GA"],
                points=stats["PTS"],
            )
        )

    h_cup = (h_base // 100) % 100
    if h_cup < 30:
        cup_progress = "Quarter-final"
        won_cup = False
    elif h_cup < 70:
        cup_progress = "Semi-final"
        won_cup = False
    elif h_cup < 90:
        cup_progress = "Runner-up"
        won_cup = False
    else:
        cup_progress = "Winner"
        won_cup = True

    won_continental = False
    if player_club_position <= 4 or player_ovr >= 82.0:
        h_cont = (h_base // 10000) % 100
        if h_cont < 40:
            continental_progress = "Round of 16"
        elif h_cont < 70:
            continental_progress = "Quarter-final"
        elif h_cont < 85:
            continental_progress = "Semi-final"
        elif h_cont < 95:
            continental_progress = "Runner-up"
        else:
            continental_progress = "Winner"
            won_continental = True
    else:
        continental_progress = "Not Qualified"

    intl_country = player_nationality if player_nationality else "Spain"
    intl_call_up = evaluate_international_call_up(
        call_up_id=f"INT_{season_number}_{player_id}",
        player_id=player_id,
        country_code=intl_country,
        season_number=season_number,
        player_ovr=player_ovr,
        player_form=1.0,
        position=player_position,
        seed=f"{seed}_INT",
    )

    stats_snapshot = aggregate_season_statistics(
        season_number=season_number,
        season_label=season_label,
        club_id=club_name,
        club_name=club_name,
        match_performances=match_performances,
    )

    trophies, awards = evaluate_season_awards(
        player_id=player_id,
        player_name=player_name,
        player_age=player_age,
        club_name=club_name,
        season_number=season_number,
        goals=stats_snapshot.goals,
        assists=stats_snapshot.assists,
        appearances=stats_snapshot.appearances,
        average_rating=stats_snapshot.average_rating,
        league_position=player_club_position,
        won_cup=won_cup,
        won_continental=won_continental,
        seed=f"{seed}_AWARDS",
    )

    return SeasonSummary(
        season_number=season_number,
        season_label=season_label,
        club_id=club_name,
        club_name=club_name,
        league_code=league_code,
        league_name=COMP_RULES.get("leagues", {}).get(league_code, {}).get("name", "League"),
        league_position=player_club_position,
        league_standings=tuple(standing_entries),
        cup_progress=cup_progress,
        continental_progress=continental_progress,
        statistics=stats_snapshot,
        international_call_up=intl_call_up,
        injuries=tuple(injuries_list),
        trophies=trophies,
        awards=awards,
    )
