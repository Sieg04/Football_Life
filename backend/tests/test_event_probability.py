import pytest

from app.event import (
    EventContext,
    EventDefinition,
    EventType,
    ProbabilityCalculationResult,
    ProbabilityModifier,
    ProbabilityModifierType,
    calculate_event_probability,
    create_event_definition,
    derive_deterministic_roll,
    evaluate_event_candidate,
)


def test_probability_modifier_valid():
    mod = ProbabilityModifier(
        id="mod_form",
        modifier_type=ProbabilityModifierType.ADDITIVE,
        value=0.10,
        description="High form boost",
    )
    assert mod.id == "mod_form"
    assert mod.modifier_type == ProbabilityModifierType.ADDITIVE
    assert mod.value == 0.10


def test_probability_modifier_validation():
    with pytest.raises(ValueError, match="id must be a non-empty string"):
        ProbabilityModifier(id="", modifier_type=ProbabilityModifierType.ADDITIVE, value=0.1)

    with pytest.raises(ValueError, match="value must not be NaN or Infinity"):
        ProbabilityModifier(id="m1", modifier_type=ProbabilityModifierType.ADDITIVE, value=float("nan"))


def test_calculate_probability_additive_and_multiplicative():
    base = 0.10
    mod_add = ProbabilityModifier(id="add", modifier_type=ProbabilityModifierType.ADDITIVE, value=0.05)
    mod_mult = ProbabilityModifier(id="mult", modifier_type=ProbabilityModifierType.MULTIPLICATIVE, value=2.0)

    res = calculate_event_probability(base, [mod_add, mod_mult])
    # (0.10 + 0.05) * 2.0 = 0.30
    assert res.base_probability == 0.10
    assert abs(res.final_probability - 0.30) < 1e-6
    assert len(res.modifiers) == 2


def test_calculate_probability_clamping():
    # Clamp upper bound to 1.0
    mod_huge = ProbabilityModifier(id="huge", modifier_type=ProbabilityModifierType.ADDITIVE, value=5.0)
    res_upper = calculate_event_probability(0.5, [mod_huge])
    assert res_upper.final_probability == 1.0

    # Clamp lower bound to 0.0
    mod_neg = ProbabilityModifier(id="neg", modifier_type=ProbabilityModifierType.ADDITIVE, value=-10.0)
    res_lower = calculate_event_probability(0.5, [mod_neg])
    assert res_lower.final_probability == 0.0


def test_calculate_probability_override():
    base = 0.20
    mod_override = ProbabilityModifier(id="override", modifier_type=ProbabilityModifierType.OVERRIDE, value=0.85)
    res = calculate_event_probability(base, [mod_override])
    assert res.final_probability == 0.85


def test_derive_deterministic_roll_reproducibility():
    roll1 = derive_deterministic_roll("seed_1", 2025, "PLAYER", "p100", "def_breakthrough")
    roll2 = derive_deterministic_roll("seed_1", 2025, "PLAYER", "p100", "def_breakthrough")
    roll_other = derive_deterministic_roll("seed_2", 2025, "PLAYER", "p100", "def_breakthrough")

    assert roll1 == roll2
    assert 0.0 <= roll1 <= 1.0
    assert roll1 != roll_other


def test_evaluate_candidate_probability_trigger():
    defn = create_event_definition(
        event_type=EventType.DEVELOPMENT,
        name="Stat Boost",
        description_key="dev.boost",
        priority=70,
        definition_id="def_boost",
    )
    ctx = EventContext(season=2025, player_id="p1", attributes={"age": 19})

    # High probability -> guaranteed trigger
    cand_triggered = evaluate_event_candidate(
        definition=defn,
        context=ctx,
        seed="master_seed",
        entity_id="p1",
        entity_type="PLAYER",
        base_probability=1.0,
    )
    assert cand_triggered.eligible is True
    assert cand_triggered.probability == 1.0
    assert cand_triggered.triggered is True
    assert cand_triggered.instance is not None

    # Zero probability -> guaranteed non-trigger
    cand_zero = evaluate_event_candidate(
        definition=defn,
        context=ctx,
        seed="master_seed",
        entity_id="p1",
        entity_type="PLAYER",
        base_probability=0.0,
    )
    assert cand_zero.eligible is True
    assert cand_zero.probability == 0.0
    assert cand_zero.triggered is False
    assert cand_zero.instance is None
