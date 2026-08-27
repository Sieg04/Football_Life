import hashlib
import json
from datetime import date, timedelta
from pathlib import Path
from random import Random

from app.player.domain import Player
from app.transfer.domain import ContractState, ContractStatus

RULES_PATH = Path(__file__).resolve().parents[2] / "data" / "rules" / "transfers.json"


def _load_transfer_rules() -> dict:
    if RULES_PATH.exists():
        return json.loads(RULES_PATH.read_text(encoding="utf-8"))
    return {}


def calculate_contract_years_remaining(contract_end: date, evaluation_date: date) -> float:
    """Calculates non-negative fractional years remaining on a contract."""
    if evaluation_date >= contract_end:
        return 0.0
    days_remaining = (contract_end - evaluation_date).days
    return round(days_remaining / 365.25, 4)


def calculate_contract_status(
    contract_end: date,
    evaluation_date: date,
    thresholds: dict | None = None,
) -> ContractStatus:
    """Determines ContractStatus (ACTIVE, EXPIRING_SOON, EXPIRED) based on evaluation_date."""
    if evaluation_date >= contract_end:
        return ContractStatus.EXPIRED

    years_remaining = calculate_contract_years_remaining(contract_end, evaluation_date)
    if thresholds is None:
        rules = _load_transfer_rules()
        thresholds = rules.get("contract_status_thresholds", {})

    active_min = thresholds.get("active_min_years", 1.0)

    if years_remaining > active_min:
        return ContractStatus.ACTIVE
    if years_remaining > 0.0:
        return ContractStatus.EXPIRING_SOON
    return ContractStatus.EXPIRED


def calculate_contract_pressure(
    contract_end: date,
    evaluation_date: date,
    pressure_rules: dict | None = None,
) -> float:
    """Calculates a 0–100 transfer pressure score derived from contract duration remaining."""
    years_remaining = calculate_contract_years_remaining(contract_end, evaluation_date)
    if pressure_rules is None:
        rules = _load_transfer_rules()
        pressure_rules = rules.get("contract_pressure_rules", {})

    p_3_plus = pressure_rules.get("three_plus_years", 15.0)
    p_2_years = pressure_rules.get("two_years", 35.0)
    p_1_year = pressure_rules.get("one_year", 65.0)
    p_sub_year = pressure_rules.get("sub_year", 85.0)
    p_expired = pressure_rules.get("expired", 100.0)

    if years_remaining >= 3.0:
        return p_3_plus
    if years_remaining >= 2.0:
        # Interpolate between 2 and 3 years
        fraction = years_remaining - 2.0
        return round(p_2_years + (p_3_plus - p_2_years) * fraction, 2)
    if years_remaining >= 1.0:
        # Interpolate between 1 and 2 years
        fraction = years_remaining - 1.0
        return round(p_1_year + (p_2_years - p_1_year) * fraction, 2)
    if years_remaining > 0.0:
        # Interpolate between 0 and 1 year
        fraction = years_remaining
        return round(p_sub_year + (p_1_year - p_sub_year) * fraction, 2)
    return p_expired


def generate_initial_contract(
    player: Player,
    club_prestige: float = 50.0,
    evaluation_date: date = date(2025, 7, 1),
    seed: str | None = None,
) -> ContractState:
    """Deterministically generates a plausible initial ContractState for a player."""
    seed_material = seed or f"{player.id}:{player.current_ability}"
    seed_hash = hashlib.sha256(f"{seed_material}:contract".encode("utf-8")).hexdigest()
    rng = Random(int(seed_hash[:16], 16))

    # Determine age
    birth_date = player.birth_date
    age = evaluation_date.year - birth_date.year - ((evaluation_date.month, evaluation_date.day) < (birth_date.month, birth_date.day))

    # Younger / key players tend to get 3-5 year contracts, older 1-3
    if age <= 23:
        years = rng.choice((3, 4, 5))
    elif age <= 29:
        years = rng.choice((3, 4))
    elif age <= 33:
        years = rng.choice((2, 3))
    else:
        years = rng.choice((1, 2))

    # Contract start is 0 to (years - 1) years prior to evaluation_date
    elapsed_years = rng.choice(tuple(range(max(1, years))))
    start_year = evaluation_date.year - elapsed_years
    contract_start = date(start_year, 7, 1)
    contract_end = date(start_year + years, 6, 30)

    # Ensure contract_end > evaluation_date for newly generated initial contract
    if contract_end <= evaluation_date:
        contract_end = date(evaluation_date.year + years, 6, 30)
        contract_start = date(evaluation_date.year, 7, 1)

    # Plausible wage calculation
    ability_ratio = max(1.0, player.current_ability) / 50.0
    wage_base = (ability_ratio ** 3.8) * 4000.0
    prestige_modifier = 0.8 + (max(1.0, min(100.0, club_prestige)) / 250.0)
    wage = round(max(500.0, wage_base * prestige_modifier * rng.uniform(0.9, 1.1)), 2)

    return ContractState(
        contract_start=contract_start,
        contract_end=contract_end,
        wage_band=wage,
    )
