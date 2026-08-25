from datetime import date
import pytest

from app.match.lineup import (
    FORMATION_PRESETS,
    EffectiveTeamStrength,
    Lineup,
    LineupSlot,
    TacticalPreset,
    calculate_effective_team_strength,
    calculate_tactical_fit,
    calculate_xi_quality,
    select_lineup,
)
from app.player.domain import DevelopmentProfile, Player, PlayerAttributes, PlayerState


def _create_mock_player(
    player_id: str,
    pos: str,
    ca: float = 70.0,
    pot: float = 80.0,
    form: float = 70.0,
    fitness: float = 100.0,
    sec_positions: tuple[str, ...] = (),
    attr_val: float = 70.0,
) -> Player:
    attrs = PlayerAttributes(
        acceleration=attr_val,
        sprint_speed=attr_val,
        finishing=attr_val,
        shot_power=attr_val,
        long_shots=attr_val,
        volleys=attr_val,
        penalties=attr_val,
        vision=attr_val,
        short_passing=attr_val,
        long_passing=attr_val,
        crossing=attr_val,
        curve=attr_val,
        agility=attr_val,
        balance=attr_val,
        ball_control=attr_val,
        dribbling=attr_val,
        reactions=attr_val,
        defensive_awareness=attr_val,
        standing_tackle=attr_val,
        interceptions=attr_val,
        heading=attr_val,
        strength=attr_val,
        stamina=attr_val,
        jumping=attr_val,
        aggression=attr_val,
        decision_making=attr_val,
        composure=attr_val,
        creativity=attr_val,
        positioning=attr_val,
        concentration=attr_val,
        work_rate=attr_val,
        leadership=attr_val,
        diving=attr_val if pos == "GK" else 10.0,
        handling=attr_val if pos == "GK" else 10.0,
        kicking=attr_val if pos == "GK" else 10.0,
        reflexes=attr_val if pos == "GK" else 10.0,
        speed=attr_val if pos == "GK" else 10.0,
        goalkeeper_positioning=attr_val if pos == "GK" else 10.0,
    )
    return Player(
        id=player_id,
        name="Name",
        surname=player_id,
        nationality="ARG",
        birth_date=date(2000, 1, 1),
        height=180.0,
        weight=75.0,
        preferred_foot="RIGHT",
        primary_position=pos,
        secondary_positions=sec_positions,
        attributes=attrs,
        current_ability=ca,
        potential=pot,
        development_rate=70.0,
        development_profile=DevelopmentProfile.BALANCED,
        role_familiarity={"POACHER": 85.0, "PLAYMAKER": 80.0, "CENTRE_BACK": 80.0, "TRADITIONAL_KEEPER": 90.0},
        state=PlayerState(form=form, fitness=fitness),
    )


def _create_full_squad() -> list[Player]:
    squad = [
        _create_mock_player("GK1", "GK", attr_val=75.0),
        _create_mock_player("GK2", "GK", attr_val=65.0),
        _create_mock_player("CB1", "CB", attr_val=78.0),
        _create_mock_player("CB2", "CB", attr_val=76.0),
        _create_mock_player("CB3", "CB", attr_val=70.0),
        _create_mock_player("LB1", "LB", attr_val=74.0),
        _create_mock_player("RB1", "RB", attr_val=74.0),
        _create_mock_player("CM1", "CM", attr_val=77.0),
        _create_mock_player("CM2", "CM", attr_val=75.0),
        _create_mock_player("CAM1", "CAM", attr_val=79.0),
        _create_mock_player("LW1", "LW", attr_val=78.0),
        _create_mock_player("RW1", "RW", attr_val=77.0),
        _create_mock_player("ST1", "ST", attr_val=82.0),
        _create_mock_player("ST2", "ST", attr_val=72.0),
        _create_mock_player("CM3", "CM", attr_val=68.0),
    ]
    return squad


def test_1_formation_presets() -> None:
    for name in ("4-3-3", "4-2-3-1", "4-4-2", "3-5-2", "3-4-3", "4-1-4-1"):
        assert name in FORMATION_PRESETS
        preset = FORMATION_PRESETS[name]
        assert len(preset.position_slots) == 11


def test_2_valid_xi_generation() -> None:
    squad = _create_full_squad()
    lineup = select_lineup(squad, club_id=1, formation=FORMATION_PRESETS["4-3-3"])
    assert isinstance(lineup, Lineup)
    assert lineup.club_id == 1
    assert lineup.formation.formation_name == "4-3-3"


def test_3_exactly_11_starters() -> None:
    squad = _create_full_squad()
    lineup = select_lineup(squad, club_id=1)
    assert len(lineup.starters) == 11


def test_4_no_duplicate_starters() -> None:
    squad = _create_full_squad()
    lineup = select_lineup(squad, club_id=1)
    starter_ids = [slot.player.id for slot in lineup.starters]
    assert len(starter_ids) == len(set(starter_ids))


def test_5_bench_excludes_starters() -> None:
    squad = _create_full_squad()
    lineup = select_lineup(squad, club_id=1)
    starter_ids = {slot.player.id for slot in lineup.starters}
    bench_ids = {p.id for p in lineup.bench}
    assert starter_ids.isdisjoint(bench_ids)
    assert len(starter_ids) + len(bench_ids) == len(squad)


def test_6_goalkeeper_slot_uses_gk() -> None:
    squad = _create_full_squad()
    lineup = select_lineup(squad, club_id=1)
    gk_slot = next(s for s in lineup.starters if s.slot_position == "GK")
    assert gk_slot.player.primary_position == "GK"


def test_7_correct_positional_allocation() -> None:
    squad = _create_full_squad()
    preset = FORMATION_PRESETS["4-3-3"]
    lineup = select_lineup(squad, club_id=1, formation=preset)
    allocated_positions = [s.slot_position for s in lineup.starters]
    assert tuple(allocated_positions) == preset.position_slots


def test_8_high_ovr_player_preferred() -> None:
    squad = [
        _create_mock_player("GK1", "GK", attr_val=70.0),
        _create_mock_player("CB1", "CB", attr_val=70.0),
        _create_mock_player("CB2", "CB", attr_val=70.0),
        _create_mock_player("LB1", "LB", attr_val=70.0),
        _create_mock_player("RB1", "RB", attr_val=70.0),
        _create_mock_player("CM1", "CM", attr_val=70.0),
        _create_mock_player("CM2", "CM", attr_val=70.0),
        _create_mock_player("CAM1", "CAM", attr_val=70.0),
        _create_mock_player("LW1", "LW", attr_val=70.0),
        _create_mock_player("RW1", "RW", attr_val=70.0),
        _create_mock_player("ST_LOW", "ST", attr_val=60.0),
        _create_mock_player("ST_HIGH", "ST", attr_val=85.0),
    ]
    lineup = select_lineup(squad, club_id=1)
    st_slot = next(s for s in lineup.starters if s.slot_position == "ST")
    assert st_slot.player.id == "ST_HIGH"


def test_9_poor_role_fit_reduces_score() -> None:
    p1 = _create_mock_player("ST1", "ST", attr_val=75.0)
    p2 = _create_mock_player("ST2", "ST", attr_val=75.0)
    p2.role_familiarity["POACHER"] = 10.0  # Poor role familiarity

    squad = [
        _create_mock_player("GK1", "GK"), _create_mock_player("CB1", "CB"),
        _create_mock_player("CB2", "CB"), _create_mock_player("LB1", "LB"),
        _create_mock_player("RB1", "RB"), _create_mock_player("CM1", "CM"),
        _create_mock_player("CM2", "CM"), _create_mock_player("CAM1", "CAM"),
        _create_mock_player("LW1", "LW"), _create_mock_player("RW1", "RW"),
        p1, p2,
    ]
    lineup = select_lineup(squad, club_id=1)
    st_slot = next(s for s in lineup.starters if s.slot_position == "ST")
    assert st_slot.player.id == "ST1"


def test_10_low_fitness_reduces_selection() -> None:
    p_fit = _create_mock_player("ST_FIT", "ST", attr_val=75.0, fitness=100.0)
    p_tired = _create_mock_player("ST_TIRED", "ST", attr_val=76.0, fitness=30.0)

    squad = [
        _create_mock_player("GK1", "GK"), _create_mock_player("CB1", "CB"),
        _create_mock_player("CB2", "CB"), _create_mock_player("LB1", "LB"),
        _create_mock_player("RB1", "RB"), _create_mock_player("CM1", "CM"),
        _create_mock_player("CM2", "CM"), _create_mock_player("CAM1", "CAM"),
        _create_mock_player("LW1", "LW"), _create_mock_player("RW1", "RW"),
        p_fit, p_tired,
    ]
    lineup = select_lineup(squad, club_id=1)
    st_slot = next(s for s in lineup.starters if s.slot_position == "ST")
    assert st_slot.player.id == "ST_FIT"


def test_11_form_affects_selection() -> None:
    p_good = _create_mock_player("ST_FORM", "ST", attr_val=75.0, form=90.0)
    p_bad = _create_mock_player("ST_COLD", "ST", attr_val=76.0, form=20.0)

    squad = [
        _create_mock_player("GK1", "GK"), _create_mock_player("CB1", "CB"),
        _create_mock_player("CB2", "CB"), _create_mock_player("LB1", "LB"),
        _create_mock_player("RB1", "RB"), _create_mock_player("CM1", "CM"),
        _create_mock_player("CM2", "CM"), _create_mock_player("CAM1", "CAM"),
        _create_mock_player("LW1", "LW"), _create_mock_player("RW1", "RW"),
        p_good, p_bad,
    ]
    lineup = select_lineup(squad, club_id=1)
    st_slot = next(s for s in lineup.starters if s.slot_position == "ST")
    assert st_slot.player.id == "ST_FORM"


def test_12_manager_preference_affects_selection() -> None:
    p1 = _create_mock_player("ST_FAV", "ST", attr_val=74.0)
    p2 = _create_mock_player("ST_NORM", "ST", attr_val=75.0)

    squad = [
        _create_mock_player("GK1", "GK"), _create_mock_player("CB1", "CB"),
        _create_mock_player("CB2", "CB"), _create_mock_player("LB1", "LB"),
        _create_mock_player("RB1", "RB"), _create_mock_player("CM1", "CM"),
        _create_mock_player("CM2", "CM"), _create_mock_player("CAM1", "CAM"),
        _create_mock_player("LW1", "LW"), _create_mock_player("RW1", "RW"),
        p1, p2,
    ]
    prefs = {"ST_FAV": 100.0, "ST_NORM": 10.0}
    lineup = select_lineup(squad, club_id=1, manager_pref_map=prefs)
    st_slot = next(s for s in lineup.starters if s.slot_position == "ST")
    assert st_slot.player.id == "ST_FAV"


def test_13_tactical_fit_range() -> None:
    squad = _create_full_squad()
    lineup = select_lineup(squad, club_id=1)
    assert 0.0 <= lineup.tactical_fit <= 100.0


def test_14_natural_position_lineup_better_tactical_fit() -> None:
    squad_natural = _create_full_squad()
    lineup_nat = select_lineup(squad_natural, club_id=1)

    # Forced out of position squad (all defenders forced to play ST/LW/RW)
    squad_forced = [
        _create_mock_player("GK1", "GK"),
        _create_mock_player("CB1", "CB"), _create_mock_player("CB2", "CB"),
        _create_mock_player("CB3", "CB"), _create_mock_player("CB4", "CB"),
        _create_mock_player("CB5", "CB"), _create_mock_player("CB6", "CB"),
        _create_mock_player("CB7", "CB"), _create_mock_player("CB8", "CB"),
        _create_mock_player("CB9", "CB"), _create_mock_player("CB10", "CB"),
    ]
    lineup_forced = select_lineup(squad_forced, club_id=1, formation=FORMATION_PRESETS["4-3-3"])
    assert lineup_nat.tactical_fit > lineup_forced.tactical_fit


def test_15_xi_quality_weighting() -> None:
    squad = _create_full_squad()
    lineup = select_lineup(squad, club_id=1)
    xi_qual = calculate_xi_quality(lineup.starters, lineup.formation)
    assert 1.0 <= xi_qual <= 100.0


def test_16_effective_team_strength_calculation() -> None:
    eff_str = calculate_effective_team_strength(
        xi_quality=80.0,
        club_strength=75.0,
        manager_quality=70.0,
        tactical_fit=85.0,
        form_factor=70.0,
        fitness_factor=100.0,
        club_id=1,
    )
    assert isinstance(eff_str, EffectiveTeamStrength)
    assert 1.0 <= eff_str.effective_strength <= 100.0
    # Expected weighted sum calculation check
    expected = (80.0 * 0.65) + (75.0 * 0.15) + (70.0 * 0.05) + (85.0 * 0.05) + (70.0 * 0.05) + (100.0 * 0.05)
    assert abs(eff_str.effective_strength - expected) < 1e-4


def test_17_deterministic_lineup_selection() -> None:
    squad1 = _create_full_squad()
    squad2 = _create_full_squad()

    l1 = select_lineup(squad1, club_id=1)
    l2 = select_lineup(squad2, club_id=1)

    s1_ids = [s.player.id for s in l1.starters]
    s2_ids = [s.player.id for s in l2.starters]
    assert s1_ids == s2_ids


def test_18_stable_tie_breaking() -> None:
    # Two identical players
    p_b = _create_mock_player("B_PLAYER", "ST", attr_val=75.0)
    p_a = _create_mock_player("A_PLAYER", "ST", attr_val=75.0)

    squad = [
        _create_mock_player("GK1", "GK"), _create_mock_player("CB1", "CB"),
        _create_mock_player("CB2", "CB"), _create_mock_player("LB1", "LB"),
        _create_mock_player("RB1", "RB"), _create_mock_player("CM1", "CM"),
        _create_mock_player("CM2", "CM"), _create_mock_player("CAM1", "CAM"),
        _create_mock_player("LW1", "LW"), _create_mock_player("RW1", "RW"),
        p_b, p_a,
    ]
    lineup = select_lineup(squad, club_id=1)
    st_slot = next(s for s in lineup.starters if s.slot_position == "ST")
    # Alphabetically earlier ID ('A_PLAYER') wins stable tie-break
    assert st_slot.player.id == "A_PLAYER"


def test_19_no_potential_guarantee_for_youth() -> None:
    # High OVR veteran vs Low OVR wonderkid with 99 potential
    vet = _create_mock_player("VETERAN", "ST", ca=85.0, pot=85.0, attr_val=85.0)
    kid = _create_mock_player("YOUTH_POT99", "ST", ca=60.0, pot=99.0, attr_val=60.0)

    squad = [
        _create_mock_player("GK1", "GK"), _create_mock_player("CB1", "CB"),
        _create_mock_player("CB2", "CB"), _create_mock_player("LB1", "LB"),
        _create_mock_player("RB1", "RB"), _create_mock_player("CM1", "CM"),
        _create_mock_player("CM2", "CM"), _create_mock_player("CAM1", "CAM"),
        _create_mock_player("LW1", "LW"), _create_mock_player("RW1", "RW"),
        vet, kid,
    ]
    lineup = select_lineup(squad, club_id=1)
    st_slot = next(s for s in lineup.starters if s.slot_position == "ST")
    assert st_slot.player.id == "VETERAN"


def test_20_no_5c_plus_functionality() -> None:
    import ast
    from pathlib import Path

    lineup_path = Path(__file__).resolve().parents[1] / "app" / "match" / "lineup.py"
    tree = ast.parse(lineup_path.read_text(encoding="utf-8"))

    forbidden_terms = {"xg", "poisson", "simulate_match", "resolve_match", "sample_goals"}
    found_forbidden = set()

    for node in ast.walk(tree):
        if isinstance(node, ast.Name):
            if node.id.lower() in forbidden_terms:
                found_forbidden.add(node.id)
        elif isinstance(node, ast.FunctionDef):
            if node.name.lower() in forbidden_terms:
                found_forbidden.add(node.name)

    assert not found_forbidden, f"Found 5C+ match resolution references in lineup.py: {found_forbidden}"
