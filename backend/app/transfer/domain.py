from dataclasses import dataclass, field
from datetime import date
from enum import StrEnum


class ContractStatus(StrEnum):
    ACTIVE = "ACTIVE"
    EXPIRING_SOON = "EXPIRING_SOON"
    EXPIRED = "EXPIRED"


@dataclass(frozen=True)
class ContractState:
    contract_start: date
    contract_end: date
    wage_band: float
    release_clause: float | None = None

    def __post_init__(self) -> None:
        if self.contract_end <= self.contract_start:
            raise ValueError(
                f"contract_end ({self.contract_end}) must be strictly after contract_start ({self.contract_start})"
            )
        if self.wage_band < 0:
            raise ValueError(f"wage_band ({self.wage_band}) cannot be negative")
        if self.release_clause is not None and self.release_clause < 0:
            raise ValueError(f"release_clause ({self.release_clause}) cannot be negative")


@dataclass(frozen=True)
class MarketValue:
    value: float
    currency: str = "EUR"
    breakdown: dict[str, float] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.value < 0:
            raise ValueError(f"market value ({self.value}) cannot be negative")


@dataclass(frozen=True)
class ClubNeed:
    position: str
    need_score: float
    depth_gap: float = 0.0
    quality_gap: float = 0.0
    age_risk: float = 0.0
    role_gap: float = 0.0
    squad_balance: float = 0.0
    breakdown: dict[str, float] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not (0.0 <= self.need_score <= 100.0):
            raise ValueError(f"need_score ({self.need_score}) must be between 0 and 100")


@dataclass(frozen=True)
class PlayerFit:
    player_id: str
    club_id: int | str
    fit_score: float
    quality_fit: float = 0.0
    role_fit: float = 0.0
    tactical_fit: float = 0.0
    age_fit: float = 0.0
    squad_need_fit: float = 0.0
    breakdown: dict[str, float] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not (0.0 <= self.fit_score <= 100.0):
            raise ValueError(f"fit_score ({self.fit_score}) must be between 0 and 100")
