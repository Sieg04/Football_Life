import json
import subprocess
import sys
import pytest
from datetime import date
from types import MappingProxyType

from app.event import (
    ArcStatus,
    ArcType,
    CareerArc,
    CareerErrorCode,
    CareerEvent,
    CareerMilestone,
    CareerProcessingException,
    CareerRecord,
    CareerRelationship,
    CareerTurningPoint,
    Decision,
    DecisionOption,
    DecisionResolutionType,
    DecisionResult,
    EffectApplicationResult,
    EventCategory,
    EventContext,
    EventEffect,
    EventEffectType,
    EventInstance,
    EventOutcome,
    EventReason,
    EventResolution,
    EventResolutionStatus,
    EventSignificance,
    EventType,
    MilestoneType,
    NarrativeSeed,
    NarrativeSeedType,
    RelationshipStatus,
    RelationshipType,
    SeedPriority,
    TurningPointType,
    apply_effects,
    apply_event_resolution,
    create_event_definition,
    create_event_instance,
    detect_milestones,
    detect_turning_points,
    generate_narrative_seeds,
    process_career_event,
    process_career_events,
    record_career_event,
    replay_career_history,
    resolve_decision,
    resolve_event,
    to_json_bytes,
    update_career_arcs,
    update_relationships,
)
from app.player.domain import DevelopmentProfile, Player, PlayerAttributes, PlayerState


def create_test_player(pid: str = "p_phase9") -> Player:
    attrs = PlayerAttributes(
        acceleration=70.0, sprint_speed=70.0, finishing=70.0, shot_power=70.0, long_shots=70.0,
        volleys=70.0, penalties=70.0, vision=70.0, short_passing=70.0, long_passing=70.0,
        crossing=70.0, curve=70.0, agility=70.0, balance=70.0, ball_control=70.0, dribbling=70.0,
        reactions=70.0, defensive_awareness=70.0, standing_tackle=70.0, interceptions=70.0, heading=70.0,
        strength=70.0, stamina=70.0, jumping=70.0, aggression=70.0, decision_making=70.0, composure=70.0,
        creativity=70.0, positioning=70.0, concentration=70.0, work_rate=70.0, leadership=70.0,
        diving=10.0, handling=10.0, kicking=10.0, reflexes=10.0, speed=10.0, goalkeeper_positioning=10.0,
    )
    pstate = PlayerState(
        confidence=50.0, morale=50.0, form=50.0, fitness=100.0, fatigue=0.0, happiness=50.0, reputation=50.0,
    )
    return Player(
        id=pid, name="Phase9", surname="Tester", nationality="England", birth_date=date(2005, 1, 1),
        height=180.0, weight=75.0, preferred_foot="Right", primary_position="CM", secondary_positions=(),
        attributes=attrs, current_ability=70.0, potential=85.0, development_rate=75.0,
        development_profile=DevelopmentProfile.BALANCED, state=pstate,
    )


# 1. Domain Primitive Construction & Validation
def test_domain_primitives_construction_and_validation():
    ev = CareerEvent(
        event_id="ce_1", source_event_id="se_1", player_id="p_1", season=1, sequence=1,
        event_type=EventType.PLAYER, category=EventCategory.DEBUT, significance=EventSignificance.MAJOR,
    )
    assert ev.season == 1
    assert ev.category == EventCategory.DEBUT

    with pytest.raises(ValueError):
        CareerEvent(
            event_id="", source_event_id="se_1", player_id="p_1", season=1, sequence=1,
            event_type=EventType.PLAYER, category=EventCategory.DEBUT, significance=EventSignificance.MAJOR,
        )

    with pytest.raises(ValueError):
        CareerRelationship(
            relationship_id="rel_1", player_id="p_1", source_entity="p_1", target_entity="p_2",
            relationship_type=RelationshipType.TEAMMATE, strength=1.5,
        )


# 2. Immutability Verification
def test_immutability_of_domain_objects():
    rec = CareerRecord(player_id="p_1")
    inst = create_event_instance(
        definition=create_event_definition(EventType.PLAYER, "Debut", "desc_debut", 10),
        season=1, entity_id="p_1", entity_type="PLAYER", seed="s1", metadata={"category": "DEBUT"},
    )
    rec_after = process_career_event(rec, inst)

    assert len(rec.events) == 0
    assert len(rec_after.events) == 1
    with pytest.raises(AttributeError):
        rec_after.last_sequence = 100  # type: ignore


# 3. Deduplication & Idempotency
def test_idempotency_and_deduplication():
    rec = CareerRecord(player_id="p_1")
    inst = create_event_instance(
        definition=create_event_definition(EventType.PLAYER, "Debut", "desc_debut", 10),
        season=1, entity_id="p_1", entity_type="PLAYER", seed="s1", metadata={"category": "DEBUT"},
    )

    rec1 = process_career_event(rec, inst)
    rec2 = process_career_event(rec1, inst)

    assert len(rec1.events) == 1
    assert len(rec2.events) == 1
    assert rec1 == rec2
    assert to_json_bytes(rec1) == to_json_bytes(rec2)


# 4. Atomicity Guarantee
def test_atomicity_on_error():
    rec = CareerRecord(player_id="p_1")
    with pytest.raises(CareerProcessingException) as exc_info:
        process_career_event(rec, None)

    assert exc_info.value.code == CareerErrorCode.INVALID_EVENT
    assert len(rec.events) == 0


# 5. Milestones Detection
def test_milestone_detection():
    rec = CareerRecord(player_id="p_1")
    inst = create_event_instance(
        definition=create_event_definition(EventType.PLAYER, "First Goal", "desc_goal", 10),
        season=1, entity_id="p_1", entity_type="PLAYER", seed="s1", metadata={"category": "GOAL"},
    )
    rec_after = process_career_event(rec, inst)

    assert len(rec_after.milestones) == 1
    assert rec_after.milestones[0].milestone_type == MilestoneType.FIRST_GOAL


# 6. Relationships & Rivalries
def test_relationship_and_rivalry_tracking():
    rec = CareerRecord(player_id="p_1")
    inst1 = create_event_instance(
        definition=create_event_definition(EventType.PLAYER, "Conflict", "desc_conf", 10),
        season=1, entity_id="p_1", entity_type="PLAYER", seed="s1",
        metadata={"category": "RIVALRY", "participant_id": "p_rival", "relationship_delta": -0.6},
    )
    rec_after = process_career_event(rec, inst1)

    assert len(rec_after.relationships) == 1
    rel = rec_after.relationships[0]
    assert rel.target_entity == "p_rival"
    assert rel.relationship_type == RelationshipType.RIVAL
    assert rel.strength == -0.6


# 7. Turning Points & Arcs Evolution
def test_turning_points_and_arcs():
    rec = CareerRecord(player_id="p_1")
    inst = create_event_instance(
        definition=create_event_definition(EventType.PLAYER, "Breakthrough", "desc_bt", 10),
        season=1, entity_id="p_1", entity_type="PLAYER", seed="s1", metadata={"category": "BREAKTHROUGH"},
    )
    rec_after = process_career_event(rec, inst)

    assert len(rec_after.turning_points) == 1
    assert rec_after.turning_points[0].turning_point_type == TurningPointType.BREAKTHROUGH
    assert len(rec_after.arcs) == 1
    assert rec_after.arcs[0].arc_type == ArcType.BREAKTHROUGH


# 8. Narrative Seed Generation
def test_narrative_seed_generation():
    rec = CareerRecord(player_id="p_1")
    inst = create_event_instance(
        definition=create_event_definition(EventType.PLAYER, "Debut", "desc_debut", 10),
        season=1, entity_id="p_1", entity_type="PLAYER", seed="s1", metadata={"category": "DEBUT"},
    )
    rec_after = process_career_event(rec, inst)

    assert len(rec_after.narrative_seeds) > 0
    top_seed = rec_after.narrative_seeds[0]
    assert top_seed.seed_type in (NarrativeSeedType.BREAKTHROUGH, NarrativeSeedType.TRIUMPH)


# 9. Batch Processing & Replayability
def test_batch_and_replayability():
    player_id = "p_replay"
    events = [
        create_event_instance(
            definition=create_event_definition(EventType.PLAYER, f"Ev {i}", f"desc_{i}", 10),
            season=1, entity_id=player_id, entity_type="PLAYER", seed=f"s_{i}", metadata={"category": "APPEARANCE"},
        )
        for i in range(5)
    ]

    rec_empty = CareerRecord(player_id=player_id)
    rec_batch = process_career_events(rec_empty, events)
    rec_replay = replay_career_history(player_id, events)

    assert rec_batch == rec_replay
    assert to_json_bytes(rec_batch) == to_json_bytes(rec_replay)


# 10. Single & 100x Repeated Execution Determinism
def test_100x_repeated_execution_determinism():
    player_id = "p_det_100x"
    inst = create_event_instance(
        definition=create_event_definition(EventType.PLAYER, "Transfer", "desc_trans", 10),
        season=1, entity_id=player_id, entity_type="PLAYER", seed="s_trans", metadata={"category": "TRANSFER", "club_id": "c_20"},
    )

    baseline_rec = process_career_event(CareerRecord(player_id=player_id), inst)
    baseline_bytes = to_json_bytes(baseline_rec)

    for i in range(100):
        run_rec = process_career_event(CareerRecord(player_id=player_id), inst)
        assert to_json_bytes(run_rec) == baseline_bytes, f"Determinism mismatch on run {i}"


# 11. Cross-Process Determinism
def test_cross_process_determinism():
    script = """
import sys
from app.event import (
    CareerRecord, create_event_definition, create_event_instance,
    EventType, process_career_event, to_json_bytes
)

rec = CareerRecord(player_id="p_cross")
inst = create_event_instance(
    definition=create_event_definition(EventType.PLAYER, "Debut", "desc_debut", 10),
    season=1, entity_id="p_cross", entity_type="PLAYER", seed="s_cross", metadata={"category": "DEBUT"}
)
res = process_career_event(rec, inst)
sys.stdout.buffer.write(to_json_bytes(res))
"""
    cmd = [sys.executable, "-c", script]
    res1 = subprocess.run(cmd, capture_output=True, check=True, env={"PYTHONPATH": "backend"})
    res2 = subprocess.run(cmd, capture_output=True, check=True, env={"PYTHONPATH": "backend"})

    assert res1.stdout == res2.stdout
    assert len(res1.stdout) > 0


# 12. Real Phase 8 -> Phase 9 End-to-End Integration Test
def test_real_phase8_to_phase9_integration():
    player = create_test_player("p_e2e")
    def_eb = create_event_definition(
        event_type=EventType.PLAYER, name="Youth Opportunity", description_key="desc_opp", priority=80,
    )
    inst_eb = create_event_instance(
        definition=def_eb, season=1, entity_id=player.id, entity_type="PLAYER", seed="e2e_seed",
    )
    context_8c = EventContext(season=1, player_id=player.id, club_id="c_academy")

    # Phase 8D: Resolution
    eff = EventEffect(
        id="eff_morale", effect_type=EventEffectType.PLAYER_MORALE_CHANGE, target_id=player.id, target_type="PLAYER", delta_or_value=15.0,
    )
    outcome = EventOutcome(id="out_success", label="Success", weight=1.0, effects=(eff,))
    resolution_8d = resolve_event(definition=def_eb, instance=inst_eb, context=context_8c, outcomes=[outcome], seed="e2e_seed")

    # Phase 8F: Decision
    opt = DecisionOption(id="opt_accept", label="Accept", weight=1.0, effects=(eff,))
    decision_8f = Decision(id="dec_1", prompt="Accept debut?", default_option_id="opt_accept", options=(opt,))
    decision_res_8f = resolve_decision(decision=decision_8f, context=context_8c, seed="e2e_seed", explicit_option_id="opt_accept", resolution_type=DecisionResolutionType.EXPLICIT)

    # Phase 8E: State Application
    app_res_8e = apply_event_resolution(state=player, resolution=resolution_8d, context=context_8c)
    updated_player_state = app_res_8e.resulting_state

    assert updated_player_state.state.morale == 65.0

    # Phase 9: Career History & Interpretation
    career_rec = CareerRecord(player_id=player.id)
    career_rec = process_career_event(career_rec, resolution_8d, simulation_state=updated_player_state, context=context_8c)
    career_rec = process_career_event(career_rec, decision_res_8f, simulation_state=updated_player_state, context=context_8c)
    career_rec = process_career_event(career_rec, app_res_8e, simulation_state=updated_player_state, context=context_8c)

    assert len(career_rec.events) == 3
    assert career_rec.last_sequence == 3
    assert len(career_rec.arcs) >= 1
    assert len(career_rec.narrative_seeds) >= 1
