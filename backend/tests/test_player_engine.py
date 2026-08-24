from datetime import date

import pytest

from app.player.domain import DevelopmentProfile, Player, PlayerAttributes, PlayerState
from app.player.engine import attribute_fit, age_factor, current_ability, development_factor, goalkeeper_ovr, group_ratings, position_ovr, role_effectiveness
from app.player.generation import generate_player


def make_player() -> Player:
    values = [70.0] * 38
    values[2] = 90.0
    values[7] = 50.0
    values[17] = 40.0
    attributes = PlayerAttributes(*values)
    return Player("p1", "Diego", "Santos", "ES", date(2008, 1, 1), 180, 75, "RIGHT", "ST", (), attributes, 70, 90, 70, DevelopmentProfile.FINISHER, {"ADVANCED_FORWARD": 90}, ("FIRST_TOUCH",), {"professionalism": 80})


def test_attributes_groups_and_current_ability() -> None:
    player = make_player()
    groups = group_ratings(player)

    assert set(groups) == {"PAC", "SHO", "PAS", "DRI", "DEF", "PHY", "MENTAL"}
    assert groups == {"PAC": 70, "SHO": 77, "PAS": 65, "DRI": 70, "DEF": 61, "PHY": 70, "MENTAL": 70}
    assert current_ability(player) == 68.95


def test_position_ovr_changes_without_mutating_attributes() -> None:
    player = make_player()
    before = vars(player.attributes).copy()

    assert position_ovr(player, "ST") != position_ovr(player, "CM")
    assert vars(player.attributes) == before


def test_roles_and_effectiveness() -> None:
    player = make_player()
    roles = {"ADVANCED_FORWARD": {"attribute_weights": {"SHO": 0.3, "PAC": 0.2, "DRI": 0.15, "MENTAL": 0.15, "PHY": 0.1, "PAS": 0.1}}}

    assert attribute_fit(player, roles["ADVANCED_FORWARD"]["attribute_weights"]) == 71.6
    assert role_effectiveness(player, "ADVANCED_FORWARD", roles) == pytest.approx(77.12)


def test_generation_is_deterministic_and_valid() -> None:
    first = generate_player(42)
    second = generate_player(42)

    assert first == second
    assert first.potential >= first.current_ability
    assert 0 <= first.development_rate <= 100
    assert len(first.traits) == 2
    assert all(1 <= value <= 100 for value in vars(first.attributes).values())


def test_profiles_and_age_factor() -> None:
    player = make_player()

    assert development_factor(player, "SHO") == 1.3
    assert age_factor(date(2008, 1, 1), date(2024, 1, 1)) == 1.4
    assert age_factor(date(2008, 1, 1), date(2043, 1, 1)) == 0.1


def test_goalkeeper_ovr_uses_goalkeeper_attributes() -> None:
    player = make_player()
    player.attributes.diving = 95
    player.attributes.handling = 95
    player.attributes.kicking = 95
    player.attributes.reflexes = 95
    player.attributes.speed = 95
    player.attributes.goalkeeper_positioning = 95

    assert goalkeeper_ovr(player) == 95
    assert position_ovr(player, "GK") == 95


def test_state_and_attribute_validation() -> None:
    assert PlayerState().fitness == 100
    with pytest.raises(ValueError):
        PlayerAttributes(*([101.0] * 38))
    with pytest.raises(ValueError):
        PlayerState(confidence=-1)
