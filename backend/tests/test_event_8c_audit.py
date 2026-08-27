import json
import subprocess
import sys
import pytest

from app.event import (
    ConditionCompositionNode,
    ConditionCompositionType,
    EventCandidate,
    EventCondition,
    EventContext,
    EventDefinition,
    EventReason,
    EventStatus,
    EventType,
    ProbabilityModifier,
    ProbabilityModifierType,
    ConditionOperator,
    create_event_definition,
    create_event_instance,
    evaluate_event_candidate,
    evaluate_event_candidates,
    to_json_bytes,
)


def test_100_repeated_evaluations_determinism():
    defn = create_event_definition(
        event_type=EventType.CAREER,
        name="Contract Extension Offer",
        description_key="event.career.extension",
        priority=85,
        definition_id="def_contract_ext",
    )
    ctx = EventContext(
        season=2026,
        player_id="player_888",
        club_id="club_01",
        attributes={"ovr": 82, "morale": 90, "age": 24},
    )
    cond = EventCondition(id="c_ovr", field_path="attributes.ovr", operator=ConditionOperator.GTE, expected_value=80)
    mod = ProbabilityModifier(id="m_morale", modifier_type=ProbabilityModifierType.ADDITIVE, value=0.10)

    base_candidate = evaluate_event_candidate(
        definition=defn,
        context=ctx,
        seed="repeat_eval_seed_8c",
        entity_id="player_888",
        entity_type="PLAYER",
        base_probability=0.20,
        conditions=[cond],
        modifiers=[mod],
    )
    base_bytes = to_json_bytes(base_candidate.instance) if base_candidate.instance else b"NONE"

    for i in range(100):
        cand = evaluate_event_candidate(
            definition=defn,
            context=ctx,
            seed="repeat_eval_seed_8c",
            entity_id="player_888",
            entity_type="PLAYER",
            base_probability=0.20,
            conditions=[cond],
            modifiers=[mod],
        )
        assert cand.eligible == base_candidate.eligible
        assert cand.probability == base_candidate.probability
        assert cand.roll_value == base_candidate.roll_value
        assert cand.triggered == base_candidate.triggered
        inst_bytes = to_json_bytes(cand.instance) if cand.instance else b"NONE"
        assert inst_bytes == base_bytes


def test_cross_process_eval_determinism():
    script = """
import sys
import json
from app.event import create_event_definition, EventContext, evaluate_event_candidate, EventType, EventCondition, ConditionOperator

defn = create_event_definition(
    event_type=EventType.TRANSFER,
    name="Big Money Bid",
    description_key="event.transfer.big_bid",
    priority=95,
    definition_id="def_big_bid"
)
ctx = EventContext(season=2027, player_id="p99", attributes={"market_value": 50000000})
cond = EventCondition(id="c_val", field_path="attributes.market_value", operator=ConditionOperator.GTE, expected_value=40000000)

cand = evaluate_event_candidate(
    definition=defn,
    context=ctx,
    seed="cross_proc_seed_8c",
    entity_id="p99",
    entity_type="PLAYER",
    base_probability=0.15,
    conditions=[cond]
)

out = {
    "eligible": cand.eligible,
    "probability": cand.probability,
    "roll_value": cand.roll_value,
    "triggered": cand.triggered,
    "inst_id": cand.instance.id if cand.instance else None
}
sys.stdout.buffer.write(json.dumps(out, sort_keys=True).encode("utf-8"))
"""
    cmd = [sys.executable, "-c", script]
    res1 = subprocess.run(cmd, capture_output=True, check=True, env={"PYTHONPATH": "backend"})
    res2 = subprocess.run(cmd, capture_output=True, check=True, env={"PYTHONPATH": "backend"})

    assert res1.stdout == res2.stdout
    assert len(res1.stdout) > 0


def test_candidate_ranking():
    def_low_prio = create_event_definition(event_type=EventType.PLAYER, name="Low", description_key="low", priority=20, definition_id="def_20")
    def_high_prio = create_event_definition(event_type=EventType.PLAYER, name="High", description_key="high", priority=90, definition_id="def_90")
    def_mid_prio = create_event_definition(event_type=EventType.PLAYER, name="Mid", description_key="mid", priority=50, definition_id="def_50")

    ctx = EventContext(season=2025, player_id="p1")

    cand1 = evaluate_event_candidate(def_low_prio, ctx, "seed", "p1", "PLAYER", base_probability=0.5)
    cand2 = evaluate_event_candidate(def_high_prio, ctx, "seed", "p1", "PLAYER", base_probability=0.5)
    cand3 = evaluate_event_candidate(def_mid_prio, ctx, "seed", "p1", "PLAYER", base_probability=0.5)

    sorted_cands = evaluate_event_candidates([cand1, cand1, cand2, cand3])
    ordered_ids = [c.definition.id for c in sorted_cands]
    assert ordered_ids == ["def_90", "def_50", "def_20", "def_20"]


def test_large_scale_distribution_audit():
    categories = list(EventType)
    definitions: list[EventDefinition] = []

    # Generate 500 event definitions
    for i in range(500):
        cat = categories[i % len(categories)]
        defn = create_event_definition(
            event_type=cat,
            name=f"Synth Def {i}",
            description_key=f"synth.def.{i}",
            priority=(i * 13) % 101,
            definition_id=f"def_synth_{i:04d}",
            enabled=(i % 20 != 0),  # 5% disabled
        )
        definitions.append(defn)

    candidates: list[EventCandidate] = []
    triggered_count = 0
    eligible_count = 0

    # 5,000 synthetic evaluations
    for j in range(5000):
        defn = definitions[j % 500]
        season = 2025 + (j % 5)
        entity_id = f"player_{j % 200}"
        ctx = EventContext(
            season=season,
            player_id=entity_id,
            attributes={"ovr": 50 + (j % 45), "age": 17 + (j % 18)},
        )

        cond = EventCondition(
            id=f"c_{j}",
            field_path="attributes.ovr",
            operator=ConditionOperator.GTE,
            expected_value=60,
        )

        mod = ProbabilityModifier(
            id=f"m_{j}",
            modifier_type=ProbabilityModifierType.ADDITIVE,
            value=0.02 * (j % 5),
        )

        cand = evaluate_event_candidate(
            definition=defn,
            context=ctx,
            seed=f"audit_seed_{j % 20}",
            entity_id=entity_id,
            entity_type="PLAYER",
            base_probability=0.10,
            conditions=[cond],
            modifiers=[mod],
        )

        candidates.append(cand)
        if cand.eligible:
            eligible_count += 1
        if cand.triggered:
            triggered_count += 1

    # Verify plausible distribution metrics
    assert eligible_count > 0, "At least some events should be eligible"
    assert triggered_count > 0, "At least some events should trigger"
    assert triggered_count < eligible_count, "Not all eligible events should trigger"

    trigger_rate = triggered_count / eligible_count
    assert 0.05 <= trigger_rate <= 0.35, f"Trigger rate {trigger_rate} should be within realistic probability range"
