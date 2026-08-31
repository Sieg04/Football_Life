import hashlib
import json
from pathlib import Path

from app.football.award_domain import Award, AwardType, Trophy


def _hash_seed(seed_str: str) -> int:
    return int(hashlib.sha256(seed_str.encode("utf-8")).hexdigest(), 16)


def _load_rules(filename: str) -> dict:
    path = Path(__file__).resolve().parents[2] / "data" / "rules" / filename
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return {}


AWARD_RULES = _load_rules("awards.json")


def evaluate_season_awards(
    player_id: str,
    player_name: str,
    player_age: int,
    club_name: str,
    season_number: int,
    goals: int,
    assists: int,
    appearances: int,
    average_rating: float,
    league_position: int,
    won_cup: bool,
    won_continental: bool,
    seed: str = "AWARD_SEED",
) -> tuple[tuple[Trophy, ...], tuple[Award, ...]]:
    trophies: list[Trophy] = []
    awards: list[Award] = []

    h = _hash_seed(f"{seed}_{player_id}_{season_number}")

    if league_position == 1:
        trophies.append(
            Trophy(
                id=f"TR_LEAGUE_{season_number}_{player_id}",
                competition_id="LEAGUE",
                competition_name="League Title",
                season_number=season_number,
                winner_club_id=club_name,
                winner_club_name=club_name,
                player_involvement="WINNER",
            )
        )

    if won_cup:
        trophies.append(
            Trophy(
                id=f"TR_CUP_{season_number}_{player_id}",
                competition_id="DOMESTIC_CUP",
                competition_name="Domestic Cup",
                season_number=season_number,
                winner_club_id=club_name,
                winner_club_name=club_name,
                player_involvement="WINNER",
            )
        )

    if won_continental:
        trophies.append(
            Trophy(
                id=f"TR_CONT_{season_number}_{player_id}",
                competition_id="CONTINENTAL",
                competition_name="UEFA Champions League",
                season_number=season_number,
                winner_club_id=club_name,
                winner_club_name=club_name,
                player_involvement="WINNER",
            )
        )

    if appearances >= 20:
        if goals >= 18 or (goals >= 12 and h % 3 == 0):
            awards.append(
                Award(
                    id=f"AW_GB_{season_number}_{player_id}",
                    name="Golden Boot",
                    award_type=AwardType.LEAGUE,
                    season_number=season_number,
                    winner_player_id=player_id,
                    winner_player_name=player_name,
                    club_name=club_name,
                    description=f"Top goalscorer with {goals} goals",
                )
            )

        if player_age <= 21 and average_rating >= 7.2:
            if h % 2 == 0:
                awards.append(
                    Award(
                        id=f"AW_YPOTY_{season_number}_{player_id}",
                        name="Young Player of the Season",
                        award_type=AwardType.LEAGUE,
                        season_number=season_number,
                        winner_player_id=player_id,
                        winner_player_name=player_name,
                        club_name=club_name,
                        description="Voted best young player of the season",
                    )
                )

        if average_rating >= 7.6 and (goals + assists >= 20 or league_position == 1):
            awards.append(
                Award(
                    id=f"AW_POTY_{season_number}_{player_id}",
                    name="Player of the Season",
                    award_type=AwardType.LEAGUE,
                    season_number=season_number,
                    winner_player_id=player_id,
                    winner_player_name=player_name,
                    club_name=club_name,
                    description="Voted league player of the season",
                )
            )

        if average_rating >= 7.3:
            awards.append(
                Award(
                    id=f"AW_TOTS_{season_number}_{player_id}",
                    name="Team of the Season",
                    award_type=AwardType.LEAGUE,
                    season_number=season_number,
                    winner_player_id=player_id,
                    winner_player_name=player_name,
                    club_name=club_name,
                    description="Selected in the league Team of the Season",
                )
            )

        if average_rating >= 8.0 and (won_continental or league_position == 1) and (goals + assists >= 30):
            awards.append(
                Award(
                    id=f"AW_BALLON_{season_number}_{player_id}",
                    name="World Player of the Year",
                    award_type=AwardType.GLOBAL,
                    season_number=season_number,
                    winner_player_id=player_id,
                    winner_player_name=player_name,
                    club_name=club_name,
                    description="Winner of the prestigious World Player of the Year award",
                )
            )

    return tuple(trophies), tuple(awards)
