from dataclasses import dataclass
from datetime import date
from random import Random

from app.world.calculations import club_current_strength, league_strength, normalize_external_value, squad_depth
from app.world.entities import Club, ClubMembership, Competition, Country, League, Manager, SquadRole
from app.world.generation import generate_generic_squad


@dataclass(frozen=True)
class World:
    countries: tuple[Country, ...]
    leagues: tuple[League, ...]
    managers: tuple[Manager, ...]
    clubs: tuple[Club, ...]
    competitions: tuple[Competition, ...]


def generate_world(seed: int, definitions: dict) -> World:
    rng = Random(seed)
    role_weights = {
        SquadRole(role): weight for role, weight in definitions.get("role_weights", {}).items()
    }
    if not role_weights:
        from app.world.calculations import ROLE_WEIGHTS

        role_weights = ROLE_WEIGHTS
    countries = tuple(Country(**country) for country in definitions["countries"])
    raw_values = [club["uefa_coefficient_raw"] for club in definitions["clubs"]]
    minimum, maximum = min(raw_values), max(raw_values)
    managers_by_name: dict[str, Manager] = {}
    clubs: list[Club] = []

    for definition in definitions["clubs"]:
        manager_definition = definition["manager"]
        manager = managers_by_name.setdefault(manager_definition["name"], Manager(**manager_definition))
        squad = generate_generic_squad(
            definition["target_strength"], rng, definition["name"], definition["country_code"]
        )
        roles = (SquadRole.STARTER, SquadRole.ROTATION, SquadRole.BACKUP, SquadRole.YOUTH)
        memberships = tuple(
            ClubMembership(
                player_id=player.id,
                club_id=definition["name"],
                role=roles[index % len(roles)],
                start_date=date(2026, 7, 1),
            )
            for index, player in enumerate(squad)
        )
        clubs.append(
            Club(
                name=definition["name"],
                country_code=definition["country_code"],
                league_code=definition["league_code"],
                manager=manager,
                prestige=definition["prestige"],
                financial_power=definition["financial_power"],
                academy_quality=definition["academy_quality"],
                facilities=definition["facilities"],
                fan_pressure=definition["fan_pressure"],
                squad_depth=squad_depth(squad, memberships),
                uefa_coefficient_raw=definition["uefa_coefficient_raw"],
                uefa_coefficient_normalized=normalize_external_value(definition["uefa_coefficient_raw"], minimum, maximum),
                domestic_reputation=definition["domestic_reputation"],
                international_reputation=definition["international_reputation"],
                momentum=definition.get("momentum", 0.0),
                squad=squad,
                memberships=memberships,
            )
        )

    leagues = tuple(
        League(
            name=definition["name"],
            country_code=definition["country_code"],
            tier=definition["tier"],
            prestige=definition["prestige"],
            financial_strength=definition["financial_strength"],
            european_performance=definition["european_performance"],
            global_reputation=definition["global_reputation"],
            current_strength=league_strength(
                [club_current_strength(club, role_weights) for club in clubs if club.league_code == definition["code"]]
            ),
        )
        for definition in definitions["leagues"]
    )
    competitions = tuple(Competition(**competition) for competition in definitions["competitions"])
    return World(countries, leagues, tuple(managers_by_name.values()), tuple(clubs), competitions)
