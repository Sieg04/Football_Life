import json
from dataclasses import dataclass, field
from enum import StrEnum
from pathlib import Path
from typing import Any

from app.player.domain import Player


def _load_world_data() -> dict[str, Any]:
    world_path = Path(__file__).resolve().parents[2] / "data" / "world.json"
    if not world_path.exists():
        return {"clubs": [], "leagues": []}
    return json.loads(world_path.read_text(encoding="utf-8"))


class SquadPlayingRole(StrEnum):
    STARTER = "STARTER"
    ROTATION = "ROTATION"
    BACKUP = "BACKUP"
    PROSPECT = "PROSPECT"
    BENCH = "BENCH"


@dataclass(frozen=True)
class ClubContext:
    club_id: str
    club_name: str
    country_id: str
    league_id: str
    country_code: str
    league_code: str
    club_prestige: float
    league_prestige: float
    league_tier: int
    squad_quality: float
    squad_depth: float
    youth_development: float
    player_visibility: float
    expected_starting_ovr: float
    competition_for_minutes: float
    transfer_market_strength: float
    domestic_competition_level: float
    international_competition_level: float
    expected_player_quality: float


@dataclass(frozen=True)
class PlayingTimeResult:
    expected_role: SquadPlayingRole
    expected_starts: int
    expected_minutes: int
    selection_probability: float
    confidence_level: float
    competition_level: float
    playing_time_factor: float


def build_club_context(
    club_name_or_id: str,
    world_clubs_data: list[dict[str, Any]] | None = None,
    world_leagues_data: list[dict[str, Any]] | None = None,
) -> ClubContext:
    """Builds a deterministic ClubContext based on curated world data or defaults."""
    world_data = _load_world_data()
    if world_clubs_data is None:
        world_clubs_data = world_data.get("clubs", [])
    if world_leagues_data is None:
        world_leagues_data = world_data.get("leagues", [])

    match_club = None
    if world_clubs_data:
        for c in world_clubs_data:
            if c.get("name") == club_name_or_id or str(c.get("id")) == str(club_name_or_id):
                match_club = c
                break

    normalized_name = str(club_name_or_id).lower()
    if match_club:
        name = match_club.get("name", str(club_name_or_id))
        country_code = match_club.get("country_code", "ES")
        country_id = match_club.get("country_id", country_code)
        league_code = match_club.get("league_code", "ESP1")
        league_id = match_club.get("league_id", league_code)
        prestige = float(match_club.get("prestige", 70.0))
        target_strength = float(match_club.get("target_strength", 75.0))
        academy = float(match_club.get("academy_quality", 70.0))
        squad_depth = float(match_club.get("squad_depth", 75.0))
    else:
        name = str(club_name_or_id)
        lower_name = name.lower()
        if "real madrid" in lower_name:
            country_code, country_id, league_code, league_id = "ES", "ES", "ESP1", "ESP1"
            prestige, target_strength, academy, squad_depth = 100.0, 95.0, 82.0, 94.0
        elif "barcelona" in lower_name:
            country_code, country_id, league_code, league_id = "ES", "ES", "ESP1", "ESP1"
            prestige, target_strength, academy, squad_depth = 98.0, 91.0, 97.0, 88.0
        elif "atletico" in lower_name or "betis" in lower_name or "valencia" in lower_name:
            country_code, country_id, league_code, league_id = "ES", "ES", "ESP1", "ESP1"
            prestige, target_strength, academy, squad_depth = 82.0 if "betis" in lower_name else 80.0 if "valencia" in lower_name else 91.0, 82.0 if "betis" in lower_name else 80.0 if "valencia" in lower_name else 87.0, 80.0 if "betis" in lower_name else 88.0 if "valencia" in lower_name else 76.0, 72.0 if "betis" in lower_name else 72.0 if "valencia" in lower_name else 84.0
        elif "arsenal" in lower_name or "liverpool" in lower_name or "manchester" in lower_name:
            country_code, country_id, league_code, league_id = "GB-ENG", "GB-ENG", "ENG1", "ENG1"
            prestige = 93.0 if "arsenal" in lower_name or "liverpool" in lower_name else 90.0
            target_strength = prestige + 1.5
            academy = 89.0 if "arsenal" in lower_name or "liverpool" in lower_name else 86.0
            squad_depth = 84.0 if "arsenal" in lower_name or "liverpool" in lower_name else 83.0
        elif "lyon" in lower_name or "marseille" in lower_name or "monaco" in lower_name or "psg" in lower_name:
            country_code, country_id, league_code, league_id = "FR", "FR", "FRA1", "FRA1"
            prestige = 83.0 if "lyon" in lower_name else 84.0 if "marseille" in lower_name else 78.0 if "monaco" in lower_name else 91.0
            target_strength = 79.0 if "lyon" in lower_name else 82.0 if "marseille" in lower_name else 78.0 if "monaco" in lower_name else 92.0
            academy = 96.0 if "lyon" in lower_name else 77.0 if "marseille" in lower_name else 91.0 if "monaco" in lower_name else 90.0
            squad_depth = 72.0 if "lyon" in lower_name else 76.0 if "marseille" in lower_name else 74.0 if "monaco" in lower_name else 90.0
        else:
            country_code = "ES" if "real" in normalized_name or "barca" in normalized_name or "valencia" in normalized_name else "GB-ENG" if "arsenal" in normalized_name or "liverpool" in normalized_name or "city" in normalized_name else "DE" if "bayern" in normalized_name or "dortmund" in normalized_name else "FR"
            country_id = country_code
            league_code = "ESP1" if country_code == "ES" else "ENG1" if country_code == "GB-ENG" else "DEU1" if country_code == "DE" else "FRA1"
            league_id = league_code
            prestige = 85.0 if "real" in normalized_name else 80.0 if "betis" in normalized_name else 78.0 if "lyon" in normalized_name else 70.0
            target_strength = prestige + 2.0
            academy = 90.0 if prestige >= 95.0 else 85.0 if prestige >= 80.0 else 75.0
            squad_depth = 85.0 if prestige >= 90.0 else 78.0

    league_prestige = prestige * 0.95
    league_tier = 1
    if world_leagues_data:
        for lg in world_leagues_data:
            if lg.get("code") == league_code or lg.get("id") == league_code:
                league_prestige = float(lg.get("prestige", league_prestige))
                league_tier = int(lg.get("tier", 1))
                break

    visibility = min(100.0, max(10.0, (prestige * 0.6) + (league_prestige * 0.4)))
    domestic_level = min(100.0, max(20.0, (target_strength * 0.9) + (league_prestige * 0.25)))
    international_level = min(100.0, max(10.0, (prestige * 0.55) + (league_prestige * 0.45)))
    expected_quality = min(100.0, max(55.0, (target_strength * 0.75) + (academy * 0.2) + (league_prestige * 0.12)))
    expected_ovr = max(55.0, min(90.0, expected_quality * 0.96))
    competition = min(100.0, max(20.0, target_strength * 1.05))

    return ClubContext(
        club_id=str(club_name_or_id),
        club_name=name,
        country_id=country_id,
        league_id=league_id,
        country_code=country_code,
        league_code=league_code,
        club_prestige=prestige,
        league_prestige=league_prestige,
        league_tier=league_tier,
        squad_quality=target_strength,
        squad_depth=squad_depth,
        youth_development=academy,
        player_visibility=visibility,
        expected_starting_ovr=round(expected_ovr, 1),
        competition_for_minutes=round(competition, 1),
        transfer_market_strength=prestige,
        domestic_competition_level=round(domestic_level, 1),
        international_competition_level=round(international_level, 1),
        expected_player_quality=round(expected_quality, 1),
    )


def calculate_playing_time(
    player_ovr: float,
    player_position: str,
    club_context: ClubContext,
    form: float = 70.0,
    is_injured: bool = False,
    positional_competition_ovr: float | None = None,
) -> PlayingTimeResult:
    """Calculates deterministic playing time, expected role, starts, and minutes."""
    if is_injured:
        return PlayingTimeResult(
            expected_role=SquadPlayingRole.BENCH,
            expected_starts=0,
            expected_minutes=0,
            selection_probability=0.0,
            confidence_level=50.0,
            competition_level=club_context.competition_for_minutes,
            playing_time_factor=0.2,
        )

    club_quality_index = max(68.0, min(90.0, club_context.expected_player_quality * 0.78))
    if positional_competition_ovr is not None:
        target_comp = positional_competition_ovr
    else:
        target_comp = club_quality_index

    ovr_diff = player_ovr - target_comp
    form_bonus = (form - 70.0) / 10.0
    effective_diff = ovr_diff + form_bonus
    prestige_bonus = max(0.0, (club_context.club_prestige - 75.0) * 0.7)

    if player_ovr >= 87.0:
        role = SquadPlayingRole.STARTER
        prob = min(0.97, 0.80 + (player_ovr - 85.0) * 0.025 + max(0.0, form_bonus) * 0.15 + (club_context.club_prestige >= 90.0) * 0.08)
        starts = int(28 + (player_ovr - 85.0) * 1.7 + max(0.0, form_bonus) * 6.0 + (club_context.club_prestige >= 90.0) * 5.0)
        minutes = int(2500 + (player_ovr - 85.0) * 120.0 + max(0.0, form_bonus) * 180.0 + prestige_bonus)
        pt_factor = 1.2
    elif player_ovr >= 78.0:
        role = SquadPlayingRole.ROTATION
        prob = min(0.82, 0.60 + (player_ovr - 78.0) * 0.018 + max(0.0, form_bonus) * 0.10)
        starts = int(15 + (player_ovr - 78.0) * 1.9 + max(0.0, form_bonus) * 5.0)
        minutes = int(1700 + (player_ovr - 78.0) * 90.0 + max(0.0, form_bonus) * 120.0 + prestige_bonus * 0.6)
        pt_factor = 1.0
    elif player_ovr >= 70.0:
        role = SquadPlayingRole.BACKUP
        prob = min(0.65, 0.35 + (player_ovr - 70.0) * 0.015 + max(0.0, form_bonus) * 0.08)
        starts = int(8 + (player_ovr - 70.0) * 1.3 + max(0.0, form_bonus) * 3.0)
        minutes = int(950 + (player_ovr - 70.0) * 65.0 + max(0.0, form_bonus) * 80.0)
        pt_factor = 0.75
    else:
        role = SquadPlayingRole.PROSPECT if player_ovr < 72 else SquadPlayingRole.BENCH
        prob = max(0.08, 0.12 + (effective_diff * 0.02))
        starts = max(0, int(2 + effective_diff))
        minutes = max(120, int(250 + (effective_diff * 40.0)))
        pt_factor = 0.5

    starts = max(0, min(38, starts))
    minutes = max(0, min(3420, minutes))

    return PlayingTimeResult(
        expected_role=role,
        expected_starts=starts,
        expected_minutes=minutes,
        selection_probability=round(prob, 2),
        confidence_level=round(min(100.0, max(30.0, 70.0 + form_bonus * 5)), 1),
        competition_level=round(target_comp, 1),
        playing_time_factor=round(pt_factor, 2),
    )
