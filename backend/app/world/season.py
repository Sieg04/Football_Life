import json
from collections.abc import Sequence
from dataclasses import dataclass, field, replace
from datetime import date
from enum import StrEnum
from pathlib import Path
from types import MappingProxyType
from typing import Any

from app.player.domain import Player
from app.transfer.domain import ContractState, TransferApplication, TransferHistoryRecord
from app.world.data import World
from app.world.entities import Club


class SeasonTransitionStatus(StrEnum):
    PENDING = "PENDING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


@dataclass(frozen=True)
class SeasonState:
    season_id: str
    season_year: int
    label: str
    start_date: date
    end_date: date
    is_closed: bool = False

    def __post_init__(self) -> None:
        if not self.season_id or not self.season_id.strip():
            raise ValueError("season_id must be a non-empty string")
        if self.season_year <= 0:
            raise ValueError("season_year must be positive")
        if not self.label or not self.label.strip():
            raise ValueError("label must be a non-empty string")
        if self.start_date > self.end_date:
            raise ValueError("start_date must be <= end_date")


@dataclass(frozen=True)
class SeasonTransition:
    transition_id: str
    source_season_id: str
    target_season_id: str
    status: SeasonTransitionStatus = SeasonTransitionStatus.PENDING
    details: MappingProxyType = field(default_factory=lambda: MappingProxyType({}))

    def __post_init__(self) -> None:
        if not self.transition_id or not self.transition_id.strip():
            raise ValueError("transition_id must be a non-empty string")
        if not self.source_season_id or not self.source_season_id.strip():
            raise ValueError("source_season_id must be a non-empty string")
        if not self.target_season_id or not self.target_season_id.strip():
            raise ValueError("target_season_id must be a non-empty string")
        if self.source_season_id == self.target_season_id:
            raise ValueError("source_season_id and target_season_id must be different")

        if not isinstance(self.details, MappingProxyType):
            object.__setattr__(self, "details", MappingProxyType(dict(self.details)))


@dataclass(frozen=True)
class SeasonTransitionResult:
    transition: SeasonTransition
    previous_season_id: str
    next_season_id: str
    world: World
    updated_contracts: dict[str, ContractState]
    history_records: tuple[TransferHistoryRecord, ...]
    applied_transfers_count: int = 0
    validation_status: str = "VALID"


def advance_season(season: int | str) -> int | str:
    """Advances season identifier deterministically.

    Supports integer years (e.g., 2025 -> 2026), string integer years (e.g. "2025" -> "2026"),
    and slash formats (e.g., "2025/26" -> "2026/27", "2025/2026" -> "2026/2027").
    Raises ValueError for missing, malformed, or invalid season formats.
    """
    if season is None or season == "":
        raise ValueError("Season identifier cannot be empty or None")

    if isinstance(season, int):
        if season <= 0:
            raise ValueError(f"Invalid integer season year: {season}")
        return season + 1

    if not isinstance(season, str):
        raise ValueError(f"Unsupported season type: {type(season)}")

    season_str = season.strip()
    if not season_str:
        raise ValueError("Season string cannot be empty")

    if season_str.isdigit():
        val = int(season_str)
        if val <= 0:
            raise ValueError(f"Invalid season year: {val}")
        return str(val + 1)

    if "/" in season_str:
        parts = season_str.split("/")
        if len(parts) != 2:
            raise ValueError(f"Malformed season label: '{season_str}'")
        start_str, end_str = parts[0].strip(), parts[1].strip()
        if not start_str.isdigit() or not end_str.isdigit():
            raise ValueError(f"Malformed season label: '{season_str}'")

        start_yr = int(start_str)
        if len(end_str) == 2:
            next_start = start_yr + 1
            next_end = (int(end_str) + 1) % 100
            return f"{next_start}/{next_end:02d}"
        elif len(end_str) == 4:
            next_start = start_yr + 1
            next_end = int(end_str) + 1
            return f"{next_start}/{next_end}"
        else:
            raise ValueError(f"Malformed season label: '{season_str}'")

    raise ValueError(f"Unrecognized season format: '{season_str}'")


def create_season_transition(
    source_season_id: str,
    target_season_id: str,
    transition_id: str | None = None,
    details: dict[str, Any] | None = None,
) -> SeasonTransition:
    """Creates a SeasonTransition object with validation."""
    if transition_id is None:
        transition_id = f"trans_{source_season_id}_to_{target_season_id}"

    details_map = MappingProxyType(details if details is not None else {})
    return SeasonTransition(
        transition_id=transition_id,
        source_season_id=str(source_season_id),
        target_season_id=str(target_season_id),
        status=SeasonTransitionStatus.PENDING,
        details=details_map,
    )


def validate_world_state(world: World, contracts: dict[str, ContractState] | None = None) -> None:
    """Validates resulting world state for consistency and structural integrity."""
    if world is None:
        raise ValueError("World state cannot be None")

    seen_players: dict[str, str] = {}
    sorted_clubs = sorted(world.clubs, key=lambda c: str(c.name))

    for club in sorted_clubs:
        if not club.name:
            raise ValueError("Club with empty name detected")
        for player in club.squad:
            if player.id in seen_players:
                raise ValueError(
                    f"Player '{player.id}' appears in multiple club squads: '{seen_players[player.id]}' and '{club.name}'"
                )
            seen_players[player.id] = str(club.name)

    if contracts is not None:
        for player_id, contract in sorted(contracts.items(), key=lambda item: item[0]):
            if contract.contract_start > contract.contract_end:
                raise ValueError(f"Player '{player_id}' has invalid contract dates")


def transition_to_next_season(
    world: World,
    current_season: int | str,
    contracts: dict[str, ContractState] | None = None,
    applications: Sequence[TransferApplication] | None = None,
    transition: SeasonTransition | None = None,
    history: tuple[TransferHistoryRecord, ...] | None = None,
) -> SeasonTransitionResult:
    """Executes the deterministic season transition pipeline from Season N to Season N+1.

    Guarantees copy-on-write immutability: input world, contracts, and applications are never mutated.
    """
    from app.transfer.application import apply_transfers

    if world is None:
        raise ValueError("world state must be provided")

    # Step 1: Validate input world state
    validate_world_state(world, contracts)

    # Calculate next season identifier
    next_season = advance_season(current_season)
    source_season_str = str(current_season)
    target_season_str = str(next_season)

    # Step 2: Transition object / double-transition safety
    if transition is not None:
        if transition.status == SeasonTransitionStatus.COMPLETED:
            raise ValueError(f"Transition '{transition.transition_id}' has already been completed.")
        if transition.source_season_id != source_season_str:
            raise ValueError(
                f"Transition source_season_id '{transition.source_season_id}' does not match current_season '{source_season_str}'"
            )
        current_trans = transition
    else:
        current_trans = create_season_transition(source_season_str, target_season_str)

    # Step 3: Apply pending accepted transfers via Phase 7E
    current_contracts = dict(contracts) if contracts is not None else {}
    apps_sequence = tuple(applications) if applications is not None else ()

    numeric_season = int(source_season_str.split("/")[0]) if isinstance(source_season_str, str) else int(source_season_str)
    applied_date = date(numeric_season + 1, 7, 1)

    transfer_result = apply_transfers(
        clubs=world.clubs,
        contracts=current_contracts,
        applications=apps_sequence,
        season=numeric_season,
        applied_date=applied_date,
    )

    # Update clubs map based on transfer execution results
    updated_club_map = transfer_result.updated_clubs
    updated_contracts = transfer_result.updated_contracts

    # Step 4: Reset transient seasonal state (e.g., reset club momentum to 0.0)
    # Sort clubs deterministically by name
    sorted_clubs = sorted(world.clubs, key=lambda c: str(c.name))
    next_season_clubs: list[Club] = []

    for c in sorted_clubs:
        c_id = c.name
        club_to_reset = updated_club_map.get(c_id, c)
        # Apply transient state resets: reset momentum to 0.0 while maintaining squad/memberships
        next_club = replace(club_to_reset, momentum=0.0)
        next_season_clubs.append(next_club)

    # Step 5: Reconstruct immutable next-season World
    next_world = replace(
        world,
        clubs=tuple(next_season_clubs),
    )

    # Step 6: Validate resulting world state
    validate_world_state(next_world, updated_contracts)

    # Step 7: Finalize transition object
    completed_trans = replace(
        current_trans,
        status=SeasonTransitionStatus.COMPLETED,
    )

    # Total applied history
    existing_history = tuple(history) if history is not None else ()
    combined_history = existing_history + transfer_result.history_records

    return SeasonTransitionResult(
        transition=completed_trans,
        previous_season_id=source_season_str,
        next_season_id=target_season_str,
        world=next_world,
        updated_contracts=updated_contracts,
        history_records=combined_history,
        applied_transfers_count=len(transfer_result.history_records),
        validation_status="VALID",
    )
