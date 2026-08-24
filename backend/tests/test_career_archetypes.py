from datetime import date

import pytest

from app.career.archetypes import CareerArchetypeResult, CareerArchetypeTag, classify_career
from app.career.engine import create_career, simulate_season
from app.player.domain import DevelopmentProfile
from app.player.generation import generate_player


def test_pure_solid_pro_fallback():
    player = generate_player(10, "p-solid", "Average", "Player", "CM", "ESP", 60.0)
    player.potential = 72.0
    player.birth_date = date(2008, 1, 1)

    career = create_career("c-solid", player, 1, date(2028, 7, 1), seed="FL-SOLID")
    for _ in range(5):
        simulate_season(career)

    res = classify_career(career)
    assert res.tags == [CareerArchetypeTag.SOLID_PRO]
    assert "SOLID_PRO" in res.evidence


def test_wonderkid_and_superstar_multi_label():
    player = generate_player(20, "p-star", "Wonder", "Superstar", "ST", "ESP", 80.0)
    player.potential = 95.0
    player.birth_date = date(2011, 1, 1)  # Age 17 in 2028

    career = create_career("c-star", player, 1, date(2028, 7, 1), seed="FL-STAR")
    for _ in range(18):
        simulate_season(career)

    career.peak_ovr = 91.0
    career.peak_ability = 88.0
    career.peak_age = 30
    for sn in career.snapshots[-19:]:
        sn.ending_ability = 87.0

    res = classify_career(career)
    assert CareerArchetypeTag.WONDERKID in res.tags
    assert CareerArchetypeTag.SUPERSTAR in res.tags
    assert CareerArchetypeTag.LONG_PRIME in res.tags
    assert CareerArchetypeTag.SOLID_PRO not in res.tags

    assert res.evidence[CareerArchetypeTag.SUPERSTAR]["peak_ovr"] == 91.0
    assert res.evidence[CareerArchetypeTag.SUPERSTAR]["threshold"] == 88.0


def test_failed_wonderkid():
    player = generate_player(30, "p-failed", "Failed", "Wonderkid", "LW", "ESP", 68.0)
    player.potential = 90.0
    player.birth_date = date(2011, 1, 1)  # Age 17 in 2028

    career = create_career("c-failed", player, 1, date(2028, 7, 1), seed="FL-FAILED")
    career.peak_ability = 72.0

    res = classify_career(career)
    assert CareerArchetypeTag.FAILED_WONDERKID in res.tags
    assert res.evidence[CareerArchetypeTag.FAILED_WONDERKID]["potential_realization_pct"] <= 82.0


def test_late_bloomer_and_early_decliner():
    player = generate_player(40, "p-late", "Late", "Bloomer", "CB", "ESP", 65.0)
    player.birth_date = date(2008, 1, 1)

    career = create_career("c-late", player, 1, date(2028, 7, 1), seed="FL-LATE")
    for _ in range(10):
        simulate_season(career)

    career.peak_age = 29
    for sn in career.snapshots:
        if sn.ending_age <= 24:
            sn.ending_ability = 60.0
        elif sn.ending_age >= 29:
            sn.ending_ability = 70.0
    career.peak_ability = 70.0

    res = classify_career(career)
    assert CareerArchetypeTag.LATE_BLOOMER in res.tags


def test_configurable_rules():
    player = generate_player(50, "p-custom", "Custom", "Rule", "ST", "ESP", 70.0)
    career = create_career("c-custom", player, 1, date(2028, 7, 1), seed="FL-CUSTOM")
    career.peak_ovr = 82.0

    custom_rules = {
        "superstar": {"min_peak_ovr": 80.0}
    }
    res = classify_career(career, rules=custom_rules)
    assert CareerArchetypeTag.SUPERSTAR in res.tags
    assert res.evidence[CareerArchetypeTag.SUPERSTAR]["threshold"] == 80.0
