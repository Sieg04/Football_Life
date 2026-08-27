import json
from datetime import date
from pathlib import Path

from app.player.domain import Player
from app.player.engine import position_ovr
from app.transfer.contracts import calculate_contract_years_remaining
from app.transfer.domain import ContractState, MarketValue
from app.world.entities import Club

RULES_PATH = Path(__file__).resolve().parents[2] / "data" / "rules" / "transfers.json"


def _load_transfer_rules() -> dict:
    if RULES_PATH.exists():
        return json.loads(RULES_PATH.read_text(encoding="utf-8"))
    return {}


def _get_age_multiplier(age: int, age_multipliers: dict) -> float:
    for max_age_str, mult in sorted(age_multipliers.items(), key=lambda x: int(x[0])):
        if age <= int(max_age_str):
            return float(mult)
    return 0.20


def calculate_market_value(
    player: Player,
    contract: ContractState | None = None,
    club: Club | None = None,
    season_performance: object | None = None,
    evaluation_date: date = date(2025, 7, 1),
    rules: dict | None = None,
) -> MarketValue:
    """Calculates pure deterministic MarketValue for a player."""
    if rules is None:
        rules = _load_transfer_rules()

    mv_rules = rules.get("market_value", {})
    min_value = mv_rules.get("min_value", 10000.0)
    max_value = mv_rules.get("max_value", 350000000.0)

    # 1. Base ability / position OVR value
    ovr = position_ovr(player, player.primary_position)
    base_scale = mv_rules.get("base_scale", 100000.0)
    ovr_pivot = mv_rules.get("ovr_pivot", 50.0)
    ovr_growth_rate = mv_rules.get("ovr_growth_rate", 1.115)

    base_value = base_scale * (ovr_growth_rate ** (ovr - ovr_pivot))

    # 2. Age factor
    birth_date = player.birth_date
    age = evaluation_date.year - birth_date.year - ((evaluation_date.month, evaluation_date.day) < (birth_date.month, birth_date.day))
    age_mults = mv_rules.get(
        "age_multipliers",
        {"17": 1.15, "20": 1.25, "23": 1.20, "28": 1.10, "31": 0.85, "34": 0.50, "999": 0.20},
    )
    age_factor = _get_age_multiplier(age, age_mults)

    # 3. Potential factor (young upside)
    potential_gap = max(0.0, player.potential - player.current_ability)
    gap_weight = mv_rules.get("potential_gap_weight", 0.035)
    max_pot_mult = mv_rules.get("max_potential_bonus_multiplier", 1.80)

    if age <= 21:
        pot_factor = 1.0 + (potential_gap * gap_weight)
    elif age <= 24:
        decay = (25.0 - age) / 4.0
        pot_factor = 1.0 + (potential_gap * gap_weight * decay)
    else:
        pot_factor = 1.0

    pot_factor = min(pot_factor, max_pot_mult)

    # 4. Contract duration factor
    if contract is not None:
        years_remaining = calculate_contract_years_remaining(contract.contract_end, evaluation_date)
        if years_remaining >= 3.0:
            contract_factor = 1.15
        elif years_remaining >= 2.0:
            contract_factor = 1.00 + (years_remaining - 2.0) * 0.15
        elif years_remaining >= 1.0:
            contract_factor = 0.75 + (years_remaining - 1.0) * 0.25
        elif years_remaining > 0.0:
            contract_factor = 0.50 + years_remaining * 0.25
        else:
            contract_factor = 0.25
    else:
        contract_factor = 1.00

    # 5. Position scarcity factor
    pos_factors = mv_rules.get("position_factors", {})
    position_factor = float(pos_factors.get(player.primary_position, 1.00))

    # 6. Performance & playing time factor
    perf_factor = 1.00
    pt_factor = 1.00
    if season_performance is not None:
        # Check average_rating
        avg_rating = getattr(season_performance, "average_rating", None)
        if avg_rating is not None and isinstance(avg_rating, (int, float)):
            perf_factor = max(0.80, min(1.20, 1.0 + (float(avg_rating) - 6.8) * 0.05))
        # Check playing_time_factor
        pt_mult = getattr(season_performance, "playing_time_factor", None)
        if pt_mult is not None and isinstance(pt_mult, (int, float)):
            pt_factor = max(0.85, min(1.10, float(pt_mult)))

    # 7. Club exposure / prestige factor
    club_exposure_factor = 1.00
    if club is not None:
        prestige = max(1.0, min(100.0, getattr(club, "prestige", 50.0)))
        prestige_weight = mv_rules.get("club_exposure_factors", {}).get("prestige_weight", 0.003)
        club_exposure_factor = max(0.80, min(1.25, 1.0 + (prestige - 50.0) * prestige_weight))

    # Calculate raw market value
    raw_value = (
        base_value
        * age_factor
        * pot_factor
        * contract_factor
        * position_factor
        * perf_factor
        * pt_factor
        * club_exposure_factor
    )

    clamped_value = max(min_value, min(max_value, raw_value))

    # Round appropriately
    if clamped_value >= 1000000.0:
        final_value = round(clamped_value / 10000.0) * 10000.0
    else:
        final_value = round(clamped_value / 1000.0) * 1000.0

    breakdown = {
        "base_value": round(base_value, 2),
        "ovr": round(ovr, 2),
        "age": age,
        "age_factor": round(age_factor, 2),
        "potential_factor": round(pot_factor, 2),
        "contract_factor": round(contract_factor, 2),
        "position_factor": round(position_factor, 2),
        "performance_factor": round(perf_factor, 2),
        "playing_time_factor": round(pt_factor, 2),
        "club_exposure_factor": round(club_exposure_factor, 2),
    }

    return MarketValue(
        value=final_value,
        currency="EUR",
        breakdown=breakdown,
    )
