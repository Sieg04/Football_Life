import json
from collections.abc import Mapping
from datetime import date
from pathlib import Path

from app.player.domain import DevelopmentProfile, Player


DEFAULT_GROUPS = {
    "PAC": {"acceleration": 0.5, "sprint_speed": 0.5},
    "SHO": {"finishing": 0.35, "shot_power": 0.2, "long_shots": 0.2, "volleys": 0.15, "penalties": 0.1},
    "PAS": {"vision": 0.25, "short_passing": 0.3, "long_passing": 0.2, "crossing": 0.15, "curve": 0.1},
    "DRI": {"agility": 0.2, "balance": 0.15, "ball_control": 0.25, "dribbling": 0.25, "reactions": 0.15},
    "DEF": {"defensive_awareness": 0.3, "standing_tackle": 0.25, "interceptions": 0.25, "heading": 0.2},
    "PHY": {"strength": 0.3, "stamina": 0.3, "jumping": 0.2, "aggression": 0.2},
    "MENTAL": {"decision_making": 0.2, "composure": 0.15, "creativity": 0.15, "positioning": 0.15, "concentration": 0.15, "work_rate": 0.1, "leadership": 0.1},
}

DEFAULT_ABILITY_WEIGHTS = {"PAC": 0.15, "SHO": 0.15, "PAS": 0.15, "DRI": 0.15, "DEF": 0.15, "PHY": 0.15, "MENTAL": 0.1}

DEFAULT_POSITION_WEIGHTS = {
    "ST": {"SHO": 0.35, "PAC": 0.2, "DRI": 0.2, "PHY": 0.1, "PAS": 0.1, "MENTAL": 0.05},
    "LW": {"DRI": 0.25, "PAC": 0.25, "SHO": 0.2, "PAS": 0.15, "PHY": 0.1, "MENTAL": 0.05},
    "RW": {"DRI": 0.25, "PAC": 0.25, "SHO": 0.2, "PAS": 0.15, "PHY": 0.1, "MENTAL": 0.05},
    "CAM": {"PAS": 0.25, "DRI": 0.2, "MENTAL": 0.2, "SHO": 0.15, "PAC": 0.1, "PHY": 0.1},
    "AM": {"PAS": 0.25, "DRI": 0.2, "MENTAL": 0.2, "SHO": 0.15, "PAC": 0.1, "PHY": 0.1},
    "CM": {"PAS": 0.25, "DRI": 0.2, "MENTAL": 0.2, "DEF": 0.15, "PHY": 0.1, "SHO": 0.1},
    "DM": {"DEF": 0.25, "PAS": 0.25, "MENTAL": 0.2, "PHY": 0.15, "DRI": 0.1, "SHO": 0.05},
    "CB": {"DEF": 0.35, "PHY": 0.25, "MENTAL": 0.15, "PAS": 0.15, "PAC": 0.1},
    "LB": {"DEF": 0.25, "PAC": 0.2, "PHY": 0.15, "PAS": 0.15, "DRI": 0.15, "MENTAL": 0.1},
    "RB": {"DEF": 0.25, "PAC": 0.2, "PHY": 0.15, "PAS": 0.15, "DRI": 0.15, "MENTAL": 0.1},
}

DEFAULT_PROFILE_FACTORS = {
    DevelopmentProfile.BALANCED: {group: 1.0 for group in DEFAULT_ABILITY_WEIGHTS},
    DevelopmentProfile.TECHNICAL: {"PAC": 1.0, "SHO": 1.0, "PAS": 1.2, "DRI": 1.2, "DEF": 0.9, "PHY": 0.9, "MENTAL": 1.0},
    DevelopmentProfile.PHYSICAL: {"PAC": 1.1, "SHO": 1.0, "PAS": 0.9, "DRI": 1.0, "DEF": 1.0, "PHY": 1.2, "MENTAL": 0.9},
    DevelopmentProfile.CREATIVE: {"PAC": 0.95, "SHO": 0.95, "PAS": 1.2, "DRI": 1.15, "DEF": 0.9, "PHY": 0.9, "MENTAL": 1.2},
    DevelopmentProfile.DEFENSIVE: {"PAC": 1.0, "SHO": 0.85, "PAS": 1.0, "DRI": 0.9, "DEF": 1.3, "PHY": 1.2, "MENTAL": 1.1},
    DevelopmentProfile.FINISHER: {"PAC": 1.05, "SHO": 1.3, "PAS": 1.0, "DRI": 1.1, "DEF": 0.9, "PHY": 1.0, "MENTAL": 1.05},
    DevelopmentProfile.PLAYMAKER: {"PAC": 0.95, "SHO": 0.95, "PAS": 1.3, "DRI": 1.15, "DEF": 0.95, "PHY": 0.9, "MENTAL": 1.25},
    DevelopmentProfile.ATHLETIC: {"PAC": 1.3, "SHO": 1.0, "PAS": 0.95, "DRI": 1.1, "DEF": 1.0, "PHY": 1.3, "MENTAL": 0.95},
    DevelopmentProfile.LATE_BLOOMER: {group: 1.0 for group in DEFAULT_ABILITY_WEIGHTS},
}

AGE_FACTORS = ((18, 1.4), (21, 1.25), (24, 1.1), (27, 0.85), (30, 0.6), (33, 0.35), (999, 0.1))


def _load_rules(filename: str) -> dict:
    path = Path(__file__).resolve().parents[2] / "data" / "rules" / filename
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return {}


_attribute_rules = _load_rules("player_attributes.json")
DEFAULT_GROUPS = _attribute_rules.get("groups", DEFAULT_GROUPS)
DEFAULT_ABILITY_WEIGHTS = _attribute_rules.get("ability_weights", DEFAULT_ABILITY_WEIGHTS)
DEFAULT_POSITION_WEIGHTS = _attribute_rules.get("position_weights", DEFAULT_POSITION_WEIGHTS)
_development_rules = _load_rules("player_development.json")
DEFAULT_PROFILE_FACTORS = {
    DevelopmentProfile(profile): factors
    for profile, factors in _development_rules.get("profiles", {}).items()
} or DEFAULT_PROFILE_FACTORS
_age_factor_rules = _development_rules.get("age_factors", {})
AGE_FACTORS = tuple(
    (int(key.split("-")[-1]) if "-" in key else 999, value)
    for key, value in _age_factor_rules.items()
) or AGE_FACTORS


def weighted_values(values: Mapping[str, float], weights: Mapping[str, float]) -> float:
    return sum(values[name] * weight for name, weight in weights.items()) / sum(weights.values())


def group_ratings(player: Player, group_config: Mapping[str, Mapping[str, float]] = DEFAULT_GROUPS) -> dict[str, float]:
    values = vars(player.attributes)
    return {group: weighted_values(values, weights) for group, weights in group_config.items()}


def current_ability(player: Player, group_config=DEFAULT_GROUPS, ability_weights=DEFAULT_ABILITY_WEIGHTS) -> float:
    return max(1.0, min(100.0, weighted_values(group_ratings(player, group_config), ability_weights)))


def position_ovr(player: Player, position: str, group_config=DEFAULT_GROUPS, position_weights=DEFAULT_POSITION_WEIGHTS) -> float:
    if position == "GK":
        return goalkeeper_ovr(player)
    groups = group_ratings(player, group_config)
    weights = position_weights.get(position, position_weights["CM"])
    return max(1.0, min(100.0, weighted_values(groups, weights)))


def goalkeeper_ovr(player: Player) -> float:
    values = vars(player.attributes)
    weights = {"diving": 0.2, "handling": 0.2, "kicking": 0.15, "reflexes": 0.2, "speed": 0.1, "goalkeeper_positioning": 0.15}
    return max(1.0, min(100.0, weighted_values(values, weights)))


def attribute_fit(player: Player, role_weights: Mapping[str, float], group_config=DEFAULT_GROUPS) -> float:
    return weighted_values(group_ratings(player, group_config), role_weights)


def role_effectiveness(player: Player, role_id: str, role_definitions: Mapping[str, Mapping[str, object]], group_config=DEFAULT_GROUPS) -> float:
    definition = role_definitions[role_id]
    fit = attribute_fit(player, definition["attribute_weights"], group_config)
    familiarity = player.role_familiarity.get(role_id, 0.0)
    return fit * 0.7 + familiarity * 0.3


def age_factor(birth_date: date, as_of: date) -> float:
    age = as_of.year - birth_date.year - ((as_of.month, as_of.day) < (birth_date.month, birth_date.day))
    return next(factor for maximum_age, factor in AGE_FACTORS if age <= maximum_age)


def development_factor(player: Player, group: str) -> float:
    return DEFAULT_PROFILE_FACTORS[player.development_profile][group]
