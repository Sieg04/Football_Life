from dataclasses import dataclass, field
from datetime import date
from enum import StrEnum

from app.player.domain import Player, PlayerAttributes, PlayerState


class SquadRole(StrEnum):
    STARTER = "STARTER"
    ROTATION = "ROTATION"
    BACKUP = "BACKUP"
    YOUTH = "YOUTH"


class CompetitionType(StrEnum):
    LEAGUE = "LEAGUE"
    DOMESTIC_CUP = "DOMESTIC_CUP"
    EUROPEAN = "EUROPEAN"
    INTERNATIONAL = "INTERNATIONAL"


@dataclass(frozen=True)
class ClubMembership:
    player_id: str
    club_id: int | str
    role: SquadRole
    start_date: date
    end_date: date | None = None


@dataclass(frozen=True)
class Manager:
    name: str
    tactical_quality: float
    player_development: float
    game_management: float
    rotation: float
    adaptability: float
    tactical_style: str
    youth_preference: float
    discipline: float


@dataclass(frozen=True)
class Club:
    name: str
    country_code: str
    league_code: str
    manager: Manager
    prestige: float
    financial_power: float
    academy_quality: float
    facilities: float
    fan_pressure: float
    squad_depth: float
    uefa_coefficient_raw: float
    uefa_coefficient_normalized: float
    domestic_reputation: float
    international_reputation: float
    momentum: float = 0.0
    squad: tuple[Player, ...] = field(default_factory=tuple)
    memberships: tuple[ClubMembership, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class League:
    name: str
    country_code: str
    tier: int
    prestige: float
    financial_strength: float
    european_performance: float
    global_reputation: float
    current_strength: float


@dataclass(frozen=True)
class Country:
    code: str
    name: str
    fifa_rank: int | None = None
    fifa_points: float | None = None
    national_strength: float | None = None


@dataclass(frozen=True)
class Competition:
    name: str
    competition_type: CompetitionType
    country_code: str | None
    tier: int
    prestige: float
    strength: float
