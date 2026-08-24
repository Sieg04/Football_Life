import json
import subprocess
import sys
from datetime import date

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.career.domain import (
    CareerPhase,
    SeasonalEnvironmentInput,
    SeasonalPerformanceInput,
    SeasonalPlayingTimeInput,
)
from app.career.engine import (
    allocate_two_stage_development,
    apply_decline_effects,
    calculate_career_phase,
    calculate_development_budget,
    create_career,
    get_sha256_rng,
    simulate_season,
)
from app.career.repository import CareerRepository
from app.models.base import Base
from app.models.career import CareerModel
from app.models.world import ClubModel, CountryModel, LeagueModel, ManagerModel, PlayerModel
from app.player.domain import DevelopmentProfile, Player, PlayerState
from app.player.engine import DEFAULT_GROUPS, current_ability, position_ovr, weighted_values
from app.player.generation import generate_player


def test_calculate_career_phase_boundaries():
    assert calculate_career_phase(16) == CareerPhase.YOUTH
    assert calculate_career_phase(17) == CareerPhase.YOUTH
    assert calculate_career_phase(18) == CareerPhase.EARLY_PRO
    assert calculate_career_phase(20) == CareerPhase.EARLY_PRO
    assert calculate_career_phase(21) == CareerPhase.DEVELOPMENT
    assert calculate_career_phase(23) == CareerPhase.DEVELOPMENT
    assert calculate_career_phase(24) == CareerPhase.PRIME
    assert calculate_career_phase(28) == CareerPhase.PRIME
    assert calculate_career_phase(29) == CareerPhase.LATE_PRIME
    assert calculate_career_phase(31) == CareerPhase.LATE_PRIME
    assert calculate_career_phase(32) == CareerPhase.DECLINE
    assert calculate_career_phase(34) == CareerPhase.DECLINE
    assert calculate_career_phase(35) == CareerPhase.VETERAN
    assert calculate_career_phase(38) == CareerPhase.VETERAN


def test_neutral_performance_input_gives_1_factor():
    player = generate_player(42, "p1", "Test", "User", "ST", "ESP", 70.0)
    rng = get_sha256_rng("FL-TEST", "p1", 1)
    budget_neutral = calculate_development_budget(
        player=player,
        starting_age=18,
        playing_time=SeasonalPlayingTimeInput(2000),
        performance=SeasonalPerformanceInput(6.8),
        environment=SeasonalEnvironmentInput(50.0, 50.0),
        rng=rng,
    )
    assert budget_neutral > 0.0


def test_group_budget_preservation_and_normalization():
    # A 0.50 SHO group budget must produce approximately +0.50 weighted SHO growth before soft caps
    player = generate_player(101, "p-norm", "Group", "Norm", "ST", "ESP", 60.0)
    # Set shooting attributes < 80 so soft caps multiplier is 1.0
    for attr in DEFAULT_GROUPS["SHO"]:
        setattr(player.attributes, attr, 60.0)

    group_summary, raw_changes = allocate_two_stage_development(player, 1.0)
    sho_group_budget = group_summary["SHO"]

    sho_weights = DEFAULT_GROUPS["SHO"]
    weighted_sho_delta = sum(raw_changes[attr] * sho_weights[attr] for attr in sho_weights)

    # Before soft caps, weighted group average delta should match group budget (~0.50)
    assert pytest.approx(weighted_sho_delta, abs=1e-3) == sho_group_budget


def test_age_order_and_multipliers():
    player = generate_player(42, "p-age", "Young", "Talent", "ST", "ESP", 65.0)
    career = create_career("c-age", player, 1, date(2028, 7, 1), seed="FL-AGE")
    assert career.snapshots[0].starting_age == 20

    season1 = simulate_season(career)
    assert season1.starting_age == 20
    assert season1.ending_age == 21
    assert season1.career_phase_at_start == CareerPhase.EARLY_PRO
    assert season1.career_phase_at_end == CareerPhase.DEVELOPMENT


def test_two_stage_development_and_soft_caps():
    player = generate_player(100, "p-dev", "Finisher", "One", "ST", "ESP", 75.0)
    player.development_profile = DevelopmentProfile.FINISHER
    player.attributes.finishing = 91.0  # In 90-94 soft cap tier (0.6 multiplier)

    career = create_career("c-dev", player, 1, date(2028, 7, 1), seed="FL-DEV")
    season = simulate_season(career)

    assert "SHO" in season.development_summary
    assert "finishing" in season.attribute_changes


def test_physical_decline_hierarchy_post_28():
    # Generate player aged 30
    player = generate_player(200, "p-veteran", "Old", "Winger", "LW", "ESP", 82.0)
    player.birth_date = date(1998, 1, 1)  # Age 30 in 2028

    decline_changes = {}
    apply_decline_effects(player, 30, decline_changes)

    phys_attrs = ["acceleration", "sprint_speed", "agility", "stamina", "jumping", "reactions"]
    tech_attrs = ["finishing", "short_passing", "long_passing", "dribbling"]
    ment_attrs = ["decision_making", "composure", "creativity"]

    phys_loss_per_attr = abs(decline_changes["acceleration"])
    tech_loss_per_attr = abs(decline_changes["finishing"])
    ment_loss_per_attr = abs(decline_changes["decision_making"])

    # Physical > Technical > Mental (zero/near-zero)
    assert phys_loss_per_attr > tech_loss_per_attr
    assert tech_loss_per_attr > ment_loss_per_attr
    assert ment_loss_per_attr == 0.0


def test_peak_tracking():
    player = generate_player(300, "p-peak", "Wonder", "Kid", "ST", "ESP", 68.0)
    player.potential = 95.0
    career = create_career("c-peak", player, 10, date(2028, 7, 1), seed="FL-PEAK")

    initial_peak_ca = career.peak_ability
    initial_peak_ovr = career.peak_ovr

    for _ in range(5):
        simulate_season(career)

    assert career.peak_ability >= initial_peak_ca
    assert career.peak_ovr >= initial_peak_ovr


def test_cross_process_sha256_determinism():
    cmd = [
        sys.executable,
        "-c",
        (
            "import json; "
            "from datetime import date; "
            "from app.player.generation import generate_player; "
            "from app.career.engine import create_career, simulate_season; "
            "p = generate_player(999, 'p-det', 'Det', 'User', 'CM', 'ESP', 70.0); "
            "c = create_career('c-det', p, 1, date(2028, 7, 1), seed='FL-DETERMINISM'); "
            "[simulate_season(c) for _ in range(5)]; "
            "print(json.dumps({'ca': c.player.current_ability, 'ovr': c.peak_ovr, 'seasons': len(c.seasons)}))"
        ),
    ]

    res1 = subprocess.check_output(cmd, env={"PYTHONPATH": "backend"}).decode().strip()
    res2 = subprocess.check_output(cmd, env={"PYTHONPATH": "backend"}).decode().strip()

    assert res1 == res2
    data = json.loads(res1)
    assert data["seasons"] == 5


def test_persistence_roundtrip_in_memory():
    engine = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()

    country = CountryModel(code="ESP", name="Spain")
    league = LeagueModel(
        code="L1", name="La Liga", country_code="ESP", tier=1, current_strength=80.0,
        prestige=80.0, financial_strength=80.0, european_performance=80.0, global_reputation=80.0
    )
    manager = ManagerModel(
        name="Boss", tactical_quality=70, player_development=70, game_management=70,
        rotation=70, adaptability=70, tactical_style="BALANCED", youth_preference=70, discipline=70
    )
    club = ClubModel(
        id=1, name="FC Test", country_code="ESP", league_code="L1", manager_id=1,
        current_strength=75.0, prestige=75.0, financial_power=75.0, academy_quality=75.0,
        facilities=75.0, fan_pressure=75.0, squad_depth=75.0, uefa_coefficient_raw=100.0,
        uefa_coefficient_normalized=75.0, domestic_reputation=75.0, international_reputation=75.0, momentum=0.0
    )
    session.add_all([country, league, manager, club])
    session.commit()

    player = generate_player(1234, "p-db", "DB", "Player", "CM", "ESP", 72.0)
    db_player = PlayerModel(
        id=player.id, name=player.name, surname=player.surname, nationality=player.nationality,
        birth_date=player.birth_date, height=player.height, weight=player.weight, preferred_foot=player.preferred_foot,
        primary_position=player.primary_position, secondary_positions=list(player.secondary_positions),
        internal_attributes=vars(player.attributes), current_ability=player.current_ability, potential=player.potential,
        development_rate=player.development_rate, development_profile=player.development_profile.value,
        role_familiarity=player.role_familiarity, traits=list(player.traits), personality=player.personality,
        archetype=player.archetype, confidence=70.0, morale=70.0, form=70.0, fitness=100.0, fatigue=0.0,
        happiness=70.0, reputation=0.0
    )
    session.add(db_player)
    session.commit()

    career = create_career("c-db", player, club_id=1, start_date=date(2028, 7, 1), seed="FL-DB")
    simulate_season(career)
    simulate_season(career)

    repo = CareerRepository(session)
    repo.save(career)

    loaded_career = repo.get_by_id("c-db", player)
    assert loaded_career is not None
    assert loaded_career.id == "c-db"
    assert len(loaded_career.seasons) == 2
    assert len(loaded_career.snapshots) == 3  # Initial + 2 seasons
    assert loaded_career.current_season_number == 3
    assert loaded_career.peak_ability == career.peak_ability
