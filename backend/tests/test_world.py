import json
from datetime import date
from pathlib import Path
from random import Random

from app.world.calculations import (
    club_current_strength,
    league_strength,
    manager_quality,
    momentum_normalized,
    normalize_external_value,
    squad_base,
    squad_depth,
)
from app.world.data import generate_world
from app.player.domain import DevelopmentProfile
from app.world.entities import (
    Club,
    ClubMembership,
    Competition,
    Country,
    Manager,
    Player,
    PlayerAttributes,
    PlayerState,
    SquadRole,
)
from app.world.generation import generate_generic_squad


DATA_PATH = Path(__file__).parents[1] / "data" / "world.json"


def load_definitions() -> dict:
    return json.loads(DATA_PATH.read_text(encoding="utf-8"))


def test_world_entities_can_be_created() -> None:
    manager = Manager("Coach", 80, 80, 80, 80, 80, "balanced", 70, 80)
    country = Country("ES", "Spain")
    competition = Competition("La Liga", "LEAGUE", "ES", 1, 80, 85)
    attributes = PlayerAttributes(*([80.0] * 38))
    player = Player("player-1", "Test", "Player", "ES", date(2000, 1, 1), 180, 75, "RIGHT", "ST", (), attributes, 80, 90, 1.0, DevelopmentProfile.BALANCED)
    membership = ClubMembership("player-1", "Test FC", SquadRole.STARTER, date(2026, 7, 1))
    club = Club("Test FC", "ES", "ESP1", manager, 70, 70, 70, 70, 70, 70, 50, 50, 70, 70, squad=(player,), memberships=(membership,))

    assert country.code == "ES"
    assert competition.name == "La Liga"
    assert club.manager.name == "Coach"
    assert player.state == PlayerState()
    assert membership.player_id == player.id


def test_generic_and_career_players_share_the_same_model() -> None:
    generated = generate_generic_squad(80, Random(7), "Test FC", "ES")[0]
    career_player = Player(
        id="career-1",
        name="Diego",
        surname="Santos",
        nationality="ES",
        birth_date=date(2010, 1, 1),
        height=180,
        weight=75,
        preferred_foot="RIGHT",
        primary_position="ST",
        secondary_positions=(),
        attributes=generated.attributes,
        current_ability=generated.current_ability,
        potential=92,
        development_rate=1.0,
        development_profile=DevelopmentProfile.BALANCED,
    )

    assert type(generated) is Player
    assert type(career_player) is type(generated)
    assert career_player.attributes.finishing == generated.attributes.finishing


def test_squad_calculations_and_strength_are_plausible() -> None:
    squad = generate_generic_squad(80, Random(7))
    manager = Manager("Coach", 80, 80, 80, 80, 80, "balanced", 70, 80)
    club = Club("Test FC", "ES", "ESP1", manager, 95, 70, 70, 70, 70, 70, 50, 50, 70, 70, squad=squad)

    assert len(squad) == 40
    assert 0 <= squad_base(squad) <= 100
    assert 0 <= squad_depth(squad) <= 100
    assert 0 <= club_current_strength(club) <= 100


def test_league_strength_uses_ranked_formula() -> None:
    result = league_strength([100, 90, 80, 70, 60, 50, 40, 30, 20, 10])

    expected = 85 * 0.35 + 65 * 0.25 + 55 * 0.20 + 25 * 0.10 + 55 * 0.10
    assert result == expected


def test_normalization_and_momentum() -> None:
    assert normalize_external_value(50, 0, 100) == 50
    assert normalize_external_value(-10, 0, 100) == 0
    assert normalize_external_value(110, 0, 100) == 100
    assert momentum_normalized(-100) == 0
    assert momentum_normalized(0) == 50
    assert momentum_normalized(100) == 100


def test_manager_quality_calculation() -> None:
    manager = Manager("Coach", 100, 80, 60, 40, 20, "balanced", 70, 80)

    assert manager_quality(manager) == 69


def test_world_generation_is_deterministic() -> None:
    definitions = load_definitions()

    first = generate_world(20260824, definitions)
    second = generate_world(20260824, definitions)

    assert first == second
    assert len(first.countries) == 5
    assert len(first.leagues) == 5
    assert len(first.clubs) == 20
    assert len(first.managers) == 20
    assert len(first.competitions) == 16
    assert all(len(club.squad) == 40 for club in first.clubs)
    assert all(len(club.memberships) == len(club.squad) for club in first.clubs)
    assert all({membership.player_id for membership in club.memberships} == {player.id for player in club.squad} for club in first.clubs)


def test_world_player_generation_has_broad_balance_ranges() -> None:
    world = generate_world(20260824, load_definitions())
    players = [player for club in world.clubs for player in club.squad]
    potential_100 = sum(player.potential == 100 for player in players)
    potential_90 = sum(player.potential >= 90 for player in players)
    ca_90 = sum(player.current_ability >= 90 for player in players)
    secondary_counts = {count: sum(len(player.secondary_positions) == count for player in players) for count in (0, 1, 2)}

    assert potential_100 < len(players) * 0.05
    assert potential_90 < len(players) * 0.60
    assert ca_90 < len(players) * 0.10
    assert secondary_counts[0] > len(players) * 0.30
    assert secondary_counts[1] > len(players) * 0.30
    assert secondary_counts[2] > 0
    assert len({player.traits for player in players}) > 10
    assert len({player.primary_position for player in players}) == 10
