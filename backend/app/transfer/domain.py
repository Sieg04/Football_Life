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
