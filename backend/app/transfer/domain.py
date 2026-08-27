from dataclasses import dataclass, field
from datetime import date
from enum import StrEnum


class ContractStatus(StrEnum):
    ACTIVE = "ACTIVE"
    EXPIRING_SOON = "EXPIRING_SOON"
    EXPIRED = "EXPIRED"


class TransferWindow(StrEnum):
    SUMMER_WINDOW = "SUMMER_WINDOW"
    WINTER_WINDOW = "WINTER_WINDOW"


class StructuredReason(StrEnum):
    DEPTH = "DEPTH"
    STARTING_ROLE = "STARTING_ROLE"
    YOUTH_INVESTMENT = "YOUTH_INVESTMENT"
    STAR_REPLACEMENT = "STAR_REPLACEMENT"
    CONTRACT_EXPIRY = "CONTRACT_EXPIRY"
    VALUE_OPPORTUNITY = "VALUE_OPPORTUNITY"


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
class TransferCandidate:
    player_id: str
    selling_club_id: int | str
    buying_club_id: int | str
    market_value: float
    fit_score: float
    interest_score: float
    priority_score: float

    def __post_init__(self) -> None:
        if self.selling_club_id == self.buying_club_id:
            raise ValueError("buying_club_id and selling_club_id must be different")
        if self.market_value < 0:
            raise ValueError(f"market_value ({self.market_value}) cannot be negative")
        if not (0.0 <= self.fit_score <= 100.0):
            raise ValueError(f"fit_score ({self.fit_score}) must be between 0 and 100")
        if not (0.0 <= self.interest_score <= 100.0):
            raise ValueError(f"interest_score ({self.interest_score}) must be between 0 and 100")


@dataclass(frozen=True)
class TransferOffer:
    id: str
    player_id: str
    selling_club_id: int | str
    buying_club_id: int | str
    transfer_fee: float
    wage_offer: float
    contract_years: int
    structured_reason: StructuredReason
    seed: str

    def __post_init__(self) -> None:
        if self.selling_club_id == self.buying_club_id:
            raise ValueError("buying_club_id and selling_club_id must be different")
        if self.transfer_fee < 0:
            raise ValueError(f"transfer_fee ({self.transfer_fee}) cannot be negative")
        if self.wage_offer < 0:
            raise ValueError(f"wage_offer ({self.wage_offer}) cannot be negative")
        if self.contract_years <= 0:
            raise ValueError(f"contract_years ({self.contract_years}) must be strictly positive")
