import subprocess
import sys
import pytest

from app.event import (
    ConditionCompositionNode,
    ConditionCompositionType,
    EventCondition,
    EventContext,
    EventDefinition,
    EventEffect,
    EventEffectType,
    EventInstance,
    EventOutcome,
    EventReason,
    EventResolution,
    EventResolutionStatus,
    EventStatus,
    EventType,
    create_event_definition,
    create_event_instance,
    resolve_event,
    resolve_event_outcome,
    select_event_outcome,
    to_json_bytes,
)


def test_event_effect_validation():
    # Empty ID
    with pytest.raises(ValueError, match="EventEffect id must be a non-empty string"):
        EventEffect(
            id="",
            effect_type=EventEffectType.PLAYER_MORALE_CHANGE,
            target_id="p1",
            target_type="PLAYER",
            delta_or_value=5.0,
        )

    # Invalid Effect Type
    with pytest.raises(ValueError, match="Invalid EventEffectType"):
        EventEffect(
            id="eff1",
            effect_type="INVALID_EFFECT_TYPE",
            target_id="p1",
            target_type="PLAYER",
            delta_or_value=5.0,
        )

    # NaN delta_or_value
    with pytest.raises(ValueError, match="NaN or Infinity"):
        EventEffect(
            id="eff1",
            effect_type=EventEffectType.PLAYER_MORALE_CHANGE,
            target_id="p1",
            target_type="PLAYER",
            delta_or_value=float("nan"),
        )

    # min_bound > max_bound
    with pytest.raises(ValueError, match="min_bound .* cannot exceed max_bound"):
        EventEffect(
            id="eff1",
            effect_type=EventEffectType.PLAYER_MORALE_CHANGE,
            target_id="p1",
            target_type="PLAYER",
            delta_or_value=5.0,
            min_bound=100.0,
            max_bound=50.0,
        )


def test_event_outcome_validation():
    # Negative weight
    with pytest.raises(ValueError, match="weight must be non-negative"):
        EventOutcome(id="out1", label="Outcome 1", weight=-1.0)

    # NaN weight
    with pytest.raises(ValueError, match="NaN or Infinity"):
        EventOutcome(id="out1", label="Outcome 1", weight=float("nan"))

    # Empty label
    with pytest.raises(ValueError, match="label must be a non-empty string"):
        EventOutcome(id="out1", label=" ", weight=1.0)


def test_event_resolution_validation():
    # Invalid status
    with pytest.raises(ValueError, match="Invalid EventResolutionStatus"):
        EventResolution(
            event_id="def1",
            event_instance_id="inst1",
            status="UNKNOWN_STATUS",
            outcome_id="out1",
            outcome_label="Label",
            effects=(),
            reasons=(),
            resolution_score=0.5,
            seed="seed1",
        )

    # Invalid score range
    with pytest.raises(ValueError, match="resolution_score must be between 0.0 and 1.0"):
        EventResolution(
            event_id="def1",
            event_instance_id="inst1",
            status=EventResolutionStatus.RESOLVED,
            outcome_id="out1",
            outcome_label="Label",
            effects=(),
            reasons=(),
            resolution_score=1.5,
            seed="seed1",
        )


def test_resolution_single_outcome():
    context = EventContext(player_id="p100", season=2026)
    defn = create_event_definition(
        event_type=EventType.PLAYER,
        name="Contract Milestone",
        description_key="evt.contract",
        priority=50,
        definition_id="def_contract",
    )
    inst = create_event_instance(
        definition=defn,
        season=2026,
        entity_id="p100",
        entity_type="PLAYER",
        seed="resolution_seed_1",
    )

    effect = EventEffect(
        id="eff_morale",
        effect_type=EventEffectType.PLAYER_MORALE_CHANGE,
        target_id="p100",
        target_type="PLAYER",
        delta_or_value=10.0,
    )
    outcome = EventOutcome(
        id="out_success",
        label="Success",
        weight=1.0,
        effects=(effect,),
        reasons=(EventReason(code="CONTRACT_RENEWED", value=True),),
    )

    resolution = resolve_event(
        definition=defn,
        instance=inst,
        context=context,
        outcomes=(outcome,),
        seed="resolution_seed_1",
    )

    assert resolution.status == EventResolutionStatus.RESOLVED
    assert resolution.outcome_id == "out_success"
    assert resolution.outcome_label == "Success"
    assert len(resolution.effects) == 1
    assert resolution.effects[0].id == "eff_morale"
    assert resolution.effects[0].delta_or_value == 10.0
    assert len(resolution.reasons) == 1
    assert resolution.reasons[0].code == "CONTRACT_RENEWED"


def test_resolution_all_zero_weights_blocked():
    context = EventContext(player_id="p100", season=2026)
    defn = create_event_definition(
        event_type=EventType.PLAYER,
        name="Zero Weight Event",
        description_key="evt.zero",
        priority=50,
        definition_id="def_zero",
    )
    inst = create_event_instance(
        definition=defn,
        season=2026,
        entity_id="p100",
        entity_type="PLAYER",
        seed="zero_weight_seed",
    )

    outcome = EventOutcome(
        id="out_zero",
        label="Zero Weight Outcome",
        weight=0.0,
    )

    resolution = resolve_event(
        definition=defn,
        instance=inst,
        context=context,
        outcomes=(outcome,),
    )

    assert resolution.status == EventResolutionStatus.BLOCKED
    assert resolution.outcome_id is None
    assert any(r.code == "ALL_ZERO_WEIGHTS" for r in resolution.reasons)


def test_resolution_outcome_condition_failure():
    context = EventContext(player_id="p100", attributes={"morale": 30.0})
    defn = create_event_definition(
        event_type=EventType.PLAYER,
        name="Morale Event",
        description_key="evt.morale",
        priority=50,
        definition_id="def_morale",
    )
    inst = create_event_instance(
        definition=defn,
        season=2026,
        entity_id="p100",
        entity_type="PLAYER",
        seed="morale_seed",
    )

    cond = EventCondition(
        id="cond_high_morale",
        field_path="attributes.morale",
        operator="GT",
        expected_value=50.0,
    )
    outcome = EventOutcome(
        id="out_high_morale_only",
        label="High Morale Boost",
        weight=1.0,
        conditions=(cond,),
    )

    resolution = resolve_event(
        definition=defn,
        instance=inst,
        context=context,
        outcomes=(outcome,),
    )

    assert resolution.status == EventResolutionStatus.BLOCKED
    assert resolution.outcome_id is None
    assert any(r.code == "NO_ELIGIBLE_OUTCOMES" or r.code == "OUTCOME_CONDITION_FAILED" for r in resolution.reasons)


def test_resolution_disabled_definition_blocked():
    context = EventContext(player_id="p100")
    defn = create_event_definition(
        event_type=EventType.PLAYER,
        name="Disabled Event",
        description_key="evt.disabled",
        priority=50,
        definition_id="def_disabled",
        enabled=False,
    )
    inst = create_event_instance(
        definition=defn,
        season=2026,
        entity_id="p100",
        entity_type="PLAYER",
        seed="disabled_seed",
    )

    outcome = EventOutcome(id="out1", label="Label", weight=1.0)

    resolution = resolve_event(
        definition=defn,
        instance=inst,
        context=context,
        outcomes=(outcome,),
    )

    assert resolution.status == EventResolutionStatus.BLOCKED
    assert any(r.code == "EVENT_DEFINITION_DISABLED" for r in resolution.reasons)


def test_input_immutability():
    context = EventContext(player_id="p100", season=2026, attributes={"form": 7.5})
    defn = create_event_definition(
        event_type=EventType.PLAYER,
        name="Immutability Event",
        description_key="evt.immutable",
        priority=50,
        definition_id="def_immut",
        metadata={"key": "val"},
    )
    inst = create_event_instance(
        definition=defn,
        season=2026,
        entity_id="p100",
        entity_type="PLAYER",
        seed="immut_seed",
        metadata={"step": 1},
    )
    effect = EventEffect(
        id="eff1",
        effect_type=EventEffectType.PLAYER_FORM_CHANGE,
        target_id="p100",
        target_type="PLAYER",
        delta_or_value=1.0,
    )
    outcome = EventOutcome(id="out1", label="Outcome 1", weight=1.0, effects=(effect,))

    # Record serialization bytes before
    bytes_context_before = to_json_bytes(context)
    bytes_defn_before = to_json_bytes(defn)
    bytes_inst_before = to_json_bytes(inst)

    resolution = resolve_event(
        definition=defn,
        instance=inst,
        context=context,
        outcomes=(outcome,),
    )

    # Verify bytes after match exactly
    assert to_json_bytes(context) == bytes_context_before
    assert to_json_bytes(defn) == bytes_defn_before
    assert to_json_bytes(inst) == bytes_inst_before


def test_100x_determinism():
    context = EventContext(player_id="p100", season=2026, attributes={"morale": 70.0})
    defn = create_event_definition(
        event_type=EventType.DEVELOPMENT,
        name="Determinism Event",
        description_key="evt.det",
        priority=80,
        definition_id="def_det",
    )
    inst = create_event_instance(
        definition=defn,
        season=2026,
        entity_id="p100",
        entity_type="PLAYER",
        seed="det_seed_100x",
    )

    eff1 = EventEffect(
        id="eff_a",
        effect_type=EventEffectType.PLAYER_MORALE_CHANGE,
        target_id="p100",
        target_type="PLAYER",
        delta_or_value=5.0,
    )
    eff2 = EventEffect(
        id="eff_b",
        effect_type=EventEffectType.PLAYER_CONFIDENCE_CHANGE,
        target_id="p100",
        target_type="PLAYER",
        delta_or_value=-2.0,
    )

    out1 = EventOutcome(id="out_a", label="Option A", weight=30.0, effects=(eff1,))
    out2 = EventOutcome(id="out_b", label="Option B", weight=70.0, effects=(eff2,))

    baseline_res = resolve_event(
        definition=defn,
        instance=inst,
        context=context,
        outcomes=(out1, out2),
    )
    baseline_bytes = to_json_bytes(baseline_res)

    for i in range(100):
        run_res = resolve_event(
            definition=defn,
            instance=inst,
            context=context,
            outcomes=(out1, out2),
        )
        assert to_json_bytes(run_res) == baseline_bytes, f"Mismatch on iteration {i}"


def test_cross_process_determinism():
    script = """
import sys
from app.event import (
    EventContext,
    EventEffect,
    EventEffectType,
    EventOutcome,
    create_event_definition,
    create_event_instance,
    resolve_event,
    to_json_bytes,
)

context = EventContext(player_id="p_proc", season=2026)
defn = create_event_definition(
    event_type="CAREER",
    name="Proc Event",
    description_key="evt.proc",
    priority=60,
    definition_id="def_proc",
)
inst = create_event_instance(
    definition=defn,
    season=2026,
    entity_id="p_proc",
    entity_type="PLAYER",
    seed="cross_proc_seed_8d",
)

eff = EventEffect(
    id="eff_proc",
    effect_type=EventEffectType.CAREER_FLAG,
    target_id="p_proc",
    target_type="PLAYER",
    delta_or_value="WONDERKID_RECOGNIZED",
)
out = EventOutcome(id="out_proc", label="Proc Outcome", weight=100.0, effects=(eff,))

res = resolve_event(
    definition=defn,
    instance=inst,
    context=context,
    outcomes=(out,),
)

sys.stdout.buffer.write(to_json_bytes(res))
"""
    cmd = [sys.executable, "-c", script]
    res1 = subprocess.run(cmd, capture_output=True, check=True, env={"PYTHONPATH": "backend"})
    res2 = subprocess.run(cmd, capture_output=True, check=True, env={"PYTHONPATH": "backend"})

    assert res1.stdout == res2.stdout
    assert len(res1.stdout) > 0
