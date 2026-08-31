from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any

from app.player.domain import Player


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
    match_club = None
    if world_clubs_data:
        for c in world_clubs_data:
            if c.get("name") == club_name_or_id or str(c.get("id")) == str(club_name_or_id):
                match_club = c
                break

    if match_club:
        name = match_club.get("name", str(club_name_or_id))
        country_code = match_club.get("country_code", "ESP")
        league_code = match_club.get("league_code", "ESP1")
        prestige = float(match_club.get("prestige", 70.0))
        target_strength = float(match_club.get("target_strength", 75.0))
        academy = float(match_club.get("academy_quality", 70.0))
    else:
        name = str(club_name_or_id)
        country_code = "ESP"
        league_code = "ESP1"
        prestige = 85.0 if "Real Madrid" in name or "Barcelona" in name else 70.0
        target_strength = 85.0 if "Real Madrid" in name or "Barcelona" in name else 75.0
        academy = 75.0

    league_prestige = prestige * 0.95
    league_tier = 1
    if world_leagues_data:
        for lg in world_leagues_data:
            if lg.get("code") == league_code:
                league_prestige = float(lg.get("prestige", league_prestige))
                league_tier = int(lg.get("tier", 1))
                break

    visibility = min(100.0, max(10.0, (prestige * 0.6) + (league_prestige * 0.4)))
    expected_ovr = max(55.0, min(88.0, target_strength * 0.98))
    competition = min(100.0, max(20.0, target_strength * 1.05))

    return ClubContext(
        club_id=str(club_name_or_id),
        club_name=name,
        country_code=country_code,
        league_code=league_code,
        club_prestige=prestige,
        league_prestige=league_prestige,
        league_tier=league_tier,
        squad_quality=target_strength,
        squad_depth=75.0,
        youth_development=academy,
        player_visibility=visibility,
        expected_starting_ovr=expected_ovr,
        competition_for_minutes=competition,
        transfer_market_strength=prestige,
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

    target_comp = positional_competition_ovr if positional_competition_ovr is not None else club_context.squad_quality
    ovr_diff = player_ovr - target_comp
    form_bonus = (form - 70.0) / 10.0

    effective_diff = ovr_diff + form_bonus

    if effective_diff >= 3.0:
        role = SquadPlayingRole.STARTER
        prob = min(0.95, 0.85 + (effective_diff * 0.02))
        starts = int(32 + min(6, effective_diff))
        minutes = int(2700 + min(500, effective_diff * 40))
        pt_factor = 1.2
    elif effective_diff >= -2.0:
        role = SquadPlayingRole.ROTATION
        prob = 0.65 + (effective_diff * 0.04)
        starts = int(18 + (effective_diff * 3))
        minutes = int(1600 + (effective_diff * 150))
        pt_factor = 1.0
    elif effective_diff >= -7.0:
        role = SquadPlayingRole.BACKUP
        prob = 0.35 + (effective_diff * 0.04)
        starts = int(8 + (effective_diff * 1.5))
        minutes = int(800 + (effective_diff * 100))
        pt_factor = 0.75
    else:
        role = SquadPlayingRole.PROSPECT if player_ovr < 72 else SquadPlayingRole.BENCH
        prob = max(0.05, 0.15 + (effective_diff * 0.02))
        starts = max(0, int(2 + effective_diff))
        minutes = max(100, int(300 + (effective_diff * 30)))
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
