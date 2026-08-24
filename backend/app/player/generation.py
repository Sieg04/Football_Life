import json
from datetime import date
from pathlib import Path
from random import Random

from app.player.domain import DevelopmentProfile, Player, PlayerAttributes, PlayerState
from app.player.engine import DEFAULT_GROUPS, current_ability, group_ratings

PERSONALITY_KEYS = ("ambition", "loyalty", "professionalism", "ego", "temper", "leadership", "sociability")
RULES_PATH = Path(__file__).resolve().parents[2] / "data" / "rules"


def _load_rules(filename: str) -> dict:
    return json.loads((RULES_PATH / filename).read_text(encoding="utf-8"))


def generate_player(seed: int, player_id: str = "generated-player", name: str = "World", surname: str = "Player", position: str = "CM", nationality: str = "UNK", target_ability: float = 70.0) -> Player:
    rng = Random(seed)
    archetype_rules = _load_rules("player_archetypes.json")
    archetypes = archetype_rules["archetypes"].get(position, archetype_rules["archetypes"]["DEFAULT"])
    archetype_id = rng.choice(tuple(archetypes))
    archetype = archetypes[archetype_id]
    group_values = {
        group: max(1.0, min(100.0, target_ability * archetype.get(group, 1.0) + rng.uniform(-9.0, 9.0)))
        for group in DEFAULT_GROUPS
    }
    values = {
        attribute: round(max(1.0, min(100.0, group_values[group] + rng.uniform(-4.0, 4.0))), 2)
        for group, weights in DEFAULT_GROUPS.items()
        for attribute in weights
    }
    values.update({
        attribute: round(max(1.0, min(100.0, target_ability + rng.uniform(-9.0, 9.0))), 2)
        for attribute in ("diving", "handling", "kicking", "reflexes", "speed", "goalkeeper_positioning")
    })
    attributes = PlayerAttributes(**{name: round(value, 2) for name, value in values.items()})
    current = round(target_ability, 2)
    potential = 100.0
    profile = rng.choice(tuple(DevelopmentProfile))
    role_definitions = _load_rules("player_roles.json")["roles"]
    secondary_positions = tuple(
        position_name
        for position_name in archetype_rules["secondary_positions"].get(position, [])
        if rng.random() < 0.55
    )
    familiarity = {
        role_id: round(
            rng.uniform(80, 95)
            if position in definition["compatible_positions"]
            else rng.uniform(55, 80)
            if any(secondary in definition["compatible_positions"] for secondary in secondary_positions)
            else rng.uniform(20, 50),
            2,
        )
        for role_id, definition in role_definitions.items()
    }
    personality = {key: round(rng.uniform(0, 100), 2) for key in PERSONALITY_KEYS}
    traits = tuple(sorted(rng.sample(tuple(_load_rules("player_traits.json")["traits"]), 2)))
    player = Player(
        id=player_id,
        name=name,
        surname=surname,
        nationality=nationality,
        birth_date=date(2008, 1, 1),
        height=180.0,
        weight=75.0,
        preferred_foot="RIGHT",
        primary_position=position,
        secondary_positions=secondary_positions,
        attributes=attributes,
        current_ability=current,
        potential=potential,
        development_rate=round(rng.uniform(0, 100), 2),
        development_profile=profile,
        role_familiarity=familiarity,
        traits=traits,
        personality=personality,
        state=PlayerState(),
        archetype=archetype_id,
    )
    player.current_ability = round(current_ability(player), 2)
    gap = rng.choices(
        (rng.randint(5, 8), rng.randint(9, 15), rng.randint(16, 24), rng.randint(25, 30)),
        weights=(70, 22, 7, 1),
    )[0]
    player.potential = min(99.0, player.current_ability + gap)
    if player.current_ability >= 95.0 and rng.random() < 0.05:
        player.potential = 100.0
    player.traits = _generate_traits(player, group_ratings(player))
    return player


def _generate_traits(player: Player, groups: dict[str, float]) -> tuple[str, ...]:
    rng = Random(f"{player.id}:{player.current_ability}")
    rules = _load_rules("player_traits.json")
    count = rng.choices((0, 1, 2, 3), weights=tuple(rules["distribution"][str(i)] for i in range(4)))[0]
    eligible = [trait for trait, definition in rules["traits"].items() if all(groups.get(group, 0) >= threshold for group, threshold in definition["requirement"].items())]
    return tuple(sorted(rng.sample(eligible, min(count, len(eligible)))))


DEFAULT_ATTRIBUTE_NAMES = tuple(
    name for group in DEFAULT_GROUPS.values() for name in group
)
