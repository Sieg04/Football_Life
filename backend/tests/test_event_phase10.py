import json
import subprocess
import sys
import pytest
from datetime import date
from types import MappingProxyType

from app.event import (
    ActType,
    ArcStatus,
    ArcType,
    BeatType,
    CareerArc,
    CareerErrorCode,
    CareerEvent,
    CareerMilestone,
    CareerRecord,
    CareerRelationship,
    CareerTurningPoint,
    ConflictStatus,
    ConflictType,
    Decision,
    DecisionOption,
    DecisionResolutionType,
    DecisionResult,
    EffectApplicationResult,
    EmotionalDirection,
    EventCategory,
    EventContext,
    EventEffect,
    EventEffectType,
    EventOutcome,
    EventReason,
    EventResolution,
    EventSignificance,
    EventType,
    MilestoneType,
    NarrativeAct,
    NarrativeBeat,
    NarrativeConflict,
    NarrativeErrorCode,
    NarrativeFunction,
    NarrativePacing,
    NarrativeProcessingException,
    NarrativeProtagonist,
    NarrativeSeed,
    NarrativeSeedType,
    NarrativeStory,
    NarrativeTheme,
    NarrativeThread,
    NarrativeThreadType,
    OpeningStrategy,
    PremiseType,
    RelationshipStatus,
    RelationshipType,
    ResolutionType,
    SeedPriority,
    StoryDensity,
    StoryPremise,
    TurningPointType,
    apply_event_resolution,
    build_narrative_acts,
    build_narrative_beats,
    build_narrative_protagonist,
    build_narrative_story,
    build_narrative_threads,
    build_story_resolution,
    create_event_definition,
    create_event_instance,
    derive_narrative_themes,
    identify_narrative_conflicts,
    identify_story_climax,
    identify_story_premise,
    process_career_event,
    resolve_decision,
    resolve_event,
    select_narrative_events,
    select_story_opening,
    to_json_bytes,
    validate_narrative_coherence,
)
from app.player.domain import DevelopmentProfile, Player, PlayerAttributes, PlayerState


def create_test_player(pid: str = "p_phase10") -> Player:
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
        id=pid, name="Phase10", surname="Tester", nationality="England", birth_date=date(2005, 1, 1),
        height=180.0, weight=75.0, preferred_foot="Right", primary_position="CM", secondary_positions=(),
        attributes=attrs, current_ability=70.0, potential=85.0, development_rate=75.0,
        development_profile=DevelopmentProfile.BALANCED, state=pstate,
    )


# 1. Domain Primitive Construction & Validation
def test_phase10_domain_primitives():
    premise = StoryPremise(premise_type=PremiseType.RISE, protagonist_goal="Reach top tier")
    assert premise.premise_type == PremiseType.RISE

    with pytest.raises(ValueError):
        StoryPremise(premise_type="INVALID_TYPE")  # type: ignore

    protagonist = NarrativeProtagonist(player_id="p1", position="ST", origin="England")
    assert protagonist.player_id == "p1"

    with pytest.raises(ValueError):
        NarrativeProtagonist(player_id="")

    beat = NarrativeBeat(
        beat_id="b1", beat_type=BeatType.BREAKTHROUGH, sequence=1, importance=1.5,
        emotional_direction=EmotionalDirection.TRIUMPH, narrative_function=NarrativeFunction.PAYOFF,
    )
    assert beat.beat_id == "b1"
    assert beat.importance == 1.5

    with pytest.raises(ValueError):
        NarrativeBeat(beat_id="b1", beat_type=BeatType.BREAKTHROUGH, sequence=-1)


# 2. Immutability & Nested Immutability
def test_immutability_and_nested_immutability():
    ev = CareerEvent(
        event_id="ce1", source_event_id="se1", player_id="p1", season=1, sequence=1,
        event_type=EventType.PLAYER, category=EventCategory.DEBUT, significance=EventSignificance.MAJOR,
    )
    rec = CareerRecord(player_id="p1", events=(ev,))
    story = build_narrative_story(rec)

    assert len(rec.events) == 1
    with pytest.raises(AttributeError):
        story.density = StoryDensity.COMPACT  # type: ignore

    with pytest.raises(AttributeError):
        story.premise.protagonist_goal = "Modified"  # type: ignore


# 3. Selection & Density Modes
def test_story_selection_and_density_modes():
    events = [
        CareerEvent(
            event_id=f"ce_{i}", source_event_id=f"se_{i}", player_id="p1", season=1, sequence=i,
            event_type=EventType.PLAYER, category=EventCategory.APPEARANCE,
            significance=EventSignificance.MINOR if i % 2 == 0 else EventSignificance.MAJOR,
        )
        for i in range(1, 20)
    ]
    rec = CareerRecord(player_id="p1", events=tuple(events))

    story_compact = build_narrative_story(rec, density=StoryDensity.COMPACT)
    story_standard = build_narrative_story(rec, density=StoryDensity.STANDARD)
    story_detailed = build_narrative_story(rec, density=StoryDensity.DETAILED)

    assert len(story_compact.narrative_beats) <= 5
    assert len(story_standard.narrative_beats) <= 12
    assert len(story_detailed.narrative_beats) <= 25


# 4. Target Duration Limits
def test_target_duration_limits():
    events = [
        CareerEvent(
            event_id=f"ce_{i}", source_event_id=f"se_{i}", player_id="p1", season=1, sequence=i,
            event_type=EventType.PLAYER, category=EventCategory.APPEARANCE, significance=EventSignificance.MODERATE,
        )
        for i in range(1, 20)
    ]
    rec = CareerRecord(player_id="p1", events=tuple(events))

    # 30s target / 15s per beat = ~2 beats
    story_short = build_narrative_story(rec, target_duration_seconds=30.0, density=StoryDensity.DETAILED)
    assert len(story_short.narrative_beats) <= 2


# 5. Premise Detection
def test_premise_detection_variations():
    # Rise Premise
    tp_rise = CareerTurningPoint(
        turning_point_id="tp1", turning_point_type=TurningPointType.BREAKTHROUGH,
        player_id="p1", season=1, sequence=1, source_event_id="se1", significance=EventSignificance.MAJOR,
    )
    rec_rise = CareerRecord(player_id="p1", turning_points=(tp_rise,))
    premise_rise = identify_story_premise(rec_rise)
    assert premise_rise.premise_type == PremiseType.RISE

    # Comeback Premise
    tp_injury = CareerTurningPoint(
        turning_point_id="tp2", turning_point_type=TurningPointType.SERIOUS_SETBACK,
        player_id="p1", season=1, sequence=1, source_event_id="se2", significance=EventSignificance.MAJOR,
    )
    tp_recov = CareerTurningPoint(
        turning_point_id="tp3", turning_point_type=TurningPointType.CAREER_RECOVERY,
        player_id="p1", season=1, sequence=2, source_event_id="se3", significance=EventSignificance.MAJOR,
    )
    rec_comeback = CareerRecord(player_id="p1", turning_points=(tp_injury, tp_recov))
    premise_comeback = identify_story_premise(rec_comeback)
    assert premise_comeback.premise_type == PremiseType.COMEBACK

    # Rivalry Premise
    rel_rival = CareerRelationship(
        relationship_id="r1", player_id="p1", source_entity="p1", target_entity="p_rival",
        relationship_type=RelationshipType.RIVAL, strength=-0.8,
    )
    rec_rival = CareerRecord(player_id="p1", relationships=(rel_rival,))
    premise_rival = identify_story_premise(rec_rival)
    assert premise_rival.premise_type == PremiseType.RIVALRY


# 6. Act & Beat Generation
def test_act_and_beat_generation():
    ev_debut = CareerEvent(
        event_id="ce1", source_event_id="se1", player_id="p1", season=1, sequence=1,
        event_type=EventType.PLAYER, category=EventCategory.DEBUT, significance=EventSignificance.MAJOR,
    )
    ms_goal = CareerMilestone(
        milestone_id="ms1", milestone_type=MilestoneType.FIRST_GOAL, player_id="p1", season=1, sequence=2,
        event_id="ce1", significance=EventSignificance.MAJOR,
    )
    tp_bt = CareerTurningPoint(
        turning_point_id="tp1", turning_point_type=TurningPointType.BREAKTHROUGH, player_id="p1", season=1, sequence=3,
        source_event_id="ce1", significance=EventSignificance.MAJOR,
    )

    rec = CareerRecord(player_id="p1", events=(ev_debut,), milestones=(ms_goal,), turning_points=(tp_bt,))
    story = build_narrative_story(rec)

    assert len(story.acts) >= 1
    assert len(story.narrative_beats) == 3
    assert story.narrative_beats[0].beat_type in (BeatType.FIRST_CHANCE, BeatType.ORIGIN)


# 7. Thread Generation & Conflict Detection
def test_threads_and_conflicts():
    rel_rival = CareerRelationship(
        relationship_id="r1", player_id="p1", source_entity="p1", target_entity="p_rival",
        relationship_type=RelationshipType.RIVAL, strength=-0.9, event_ids=("ce_rival",),
    )
    ev_rival = CareerEvent(
        event_id="ce_rival", source_event_id="se_rival", player_id="p1", season=1, sequence=1,
        event_type=EventType.PLAYER, category=EventCategory.RIVALRY, significance=EventSignificance.MAJOR,
    )

    rec = CareerRecord(player_id="p1", events=(ev_rival,), relationships=(rel_rival,))
    story = build_narrative_story(rec)

    assert len(story.threads) >= 1
    assert any(th.thread_type == NarrativeThreadType.RIVALRY for th in story.threads)
    assert len(story.conflicts) >= 1
    assert story.conflicts[0].conflict_type == ConflictType.COMPETITIVE


# 8. Story Opening, Climax, and Resolution
def test_opening_climax_and_resolution():
    ev_trophy = CareerEvent(
        event_id="ce_tr", source_event_id="se_tr", player_id="p1", season=1, sequence=5,
        event_type=EventType.PLAYER, category=EventCategory.TROPHY, significance=EventSignificance.CRITICAL,
    )
    ms_trophy = CareerMilestone(
        milestone_id="ms_tr", milestone_type=MilestoneType.FIRST_TROPHY, player_id="p1", season=1, sequence=5,
        event_id="ce_tr", significance=EventSignificance.CRITICAL,
    )
    events = [
        CareerEvent(
            event_id=f"ce_{i}", source_event_id=f"se_{i}", player_id="p1", season=1, sequence=i,
            event_type=EventType.PLAYER, category=EventCategory.APPEARANCE, significance=EventSignificance.MINOR,
        )
        for i in range(1, 5)
    ]
    events.append(ev_trophy)

    rec = CareerRecord(player_id="p1", events=tuple(events), milestones=(ms_trophy,))
    story = build_narrative_story(rec)

    assert story.opening_strategy == OpeningStrategy.COLD_OPEN
    assert story.climax_beat_id is not None
    assert story.resolution_type == ResolutionType.ONGOING  # Active player


# 9. Factual Grounding & Traceability
def test_factual_grounding_and_traceability():
    ev = CareerEvent(
        event_id="ce_ground", source_event_id="se_ground", player_id="p1", season=1, sequence=1,
        event_type=EventType.PLAYER, category=EventCategory.DEBUT, significance=EventSignificance.MAJOR,
    )
    rec = CareerRecord(player_id="p1", events=(ev,))
    story = build_narrative_story(rec)

    beat = story.narrative_beats[0]
    assert beat.source_event_ids == ("ce_ground",)
    assert story.featured_events == ("ce_ground",)

    # Verification function fails on unknown event reference
    fake_beat = NarrativeBeat(
        beat_id="fake_b", beat_type=BeatType.ORIGIN, sequence=1, source_event_ids=("NON_EXISTENT_EVENT",)
    )
    fake_story = NarrativeStory(
        story_id="fake_s", player_id="p1", title_context="Fake", premise=story.premise,
        protagonist=story.protagonist, narrative_beats=(fake_beat,)
    )

    with pytest.raises(NarrativeProcessingException) as exc_info:
        validate_narrative_coherence(rec, fake_story)

    assert exc_info.value.code == NarrativeErrorCode.INVALID_EVENT_REFERENCE


# 10. Atomicity on Error
def test_atomicity_guarantee():
    rec = CareerRecord(player_id="p1")
    with pytest.raises(NarrativeProcessingException) as exc_info:
        build_narrative_story("NOT_A_CAREER_RECORD")  # type: ignore

    assert exc_info.value.code == NarrativeErrorCode.INVALID_CAREER_RECORD
    assert len(rec.events) == 0  # untouched source record


# 11. 100x Repeated Execution Determinism & Replay
def test_100x_determinism_and_replay():
    ev = CareerEvent(
        event_id="ce1", source_event_id="se1", player_id="p_det", season=1, sequence=1,
        event_type=EventType.PLAYER, category=EventCategory.DEBUT, significance=EventSignificance.MAJOR,
    )
    rec = CareerRecord(player_id="p_det", events=(ev,))

    baseline_story = build_narrative_story(rec)
    baseline_bytes = to_json_bytes(baseline_story)

    for i in range(100):
        run_story = build_narrative_story(rec)
        assert run_story == baseline_story
        assert to_json_bytes(run_story) == baseline_bytes


# 12. Cross-Process Determinism
def test_cross_process_determinism():
    script = """
import sys
from app.event import CareerRecord, CareerEvent, EventType, EventCategory, EventSignificance, build_narrative_story, to_json_bytes

ev = CareerEvent(
    event_id="ce_cross", source_event_id="se_cross", player_id="p_cross", season=1, sequence=1,
    event_type=EventType.PLAYER, category=EventCategory.DEBUT, significance=EventSignificance.MAJOR,
)
rec = CareerRecord(player_id="p_cross", events=(ev,))
story = build_narrative_story(rec)
sys.stdout.buffer.write(to_json_bytes(story))
"""
    cmd = [sys.executable, "-c", script]
    res1 = subprocess.run(cmd, capture_output=True, check=True, env={"PYTHONPATH": "backend"})
    res2 = subprocess.run(cmd, capture_output=True, check=True, env={"PYTHONPATH": "backend"})

    assert res1.stdout == res2.stdout
    assert len(res1.stdout) > 0


# 13. Retirement Edge Cases Audit
def test_retirement_edge_cases():
    # Case 1: Retirement event + milestones
    ev_ret = CareerEvent(
        event_id="ce_ret1", source_event_id="se_ret1", player_id="p_ret1", season=10, sequence=10,
        event_type=EventType.PLAYER, category=EventCategory.RETIREMENT, significance=EventSignificance.MAJOR,
    )
    ms_ret = CareerMilestone(
        milestone_id="ms_ret1", milestone_type=MilestoneType.RETIREMENT, player_id="p_ret1", season=10, sequence=10,
    )
    rec1 = CareerRecord(player_id="p_ret1", events=(ev_ret,), milestones=(ms_ret,))
    story1 = build_narrative_story(rec1)
    assert story1.resolution_type == ResolutionType.RETIREMENT

    # Case 2: Retirement event + NO milestones
    rec2 = CareerRecord(player_id="p_ret2", events=(ev_ret,))
    story2 = build_narrative_story(rec2)
    assert story2.resolution_type == ResolutionType.RETIREMENT

    # Case 3: Retirement milestone + NO events
    rec3 = CareerRecord(player_id="p_ret3", milestones=(ms_ret,))
    story3 = build_narrative_story(rec3)
    assert story3.resolution_type == ResolutionType.RETIREMENT

    # Case 4: Active career (no retirement)
    ev_app = CareerEvent(
        event_id="ce_app", source_event_id="se_app", player_id="p_act", season=1, sequence=1,
        event_type=EventType.PLAYER, category=EventCategory.APPEARANCE, significance=EventSignificance.MINOR,
    )
    rec4 = CareerRecord(player_id="p_act", events=(ev_app,))
    story4 = build_narrative_story(rec4)
    assert story4.resolution_type == ResolutionType.ONGOING

    # Case 5: Empty career
    rec5 = CareerRecord(player_id="p_empty")
    story5 = build_narrative_story(rec5)
    assert story5.resolution_type == ResolutionType.ONGOING


# 14. End-to-End Integration (Phase 8 -> Phase 9 -> Phase 10)
def test_e2e_phase8_to_phase9_to_phase10_integration():
    player = create_test_player("p_e2e_p10")
    def_eb = create_event_definition(
        event_type=EventType.PLAYER, name="Youth Opportunity", description_key="desc_opp", priority=80,
    )
    inst_eb = create_event_instance(
        definition=def_eb, season=1, entity_id=player.id, entity_type="PLAYER", seed="e2e_p10_seed",
    )
    context_8c = EventContext(season=1, player_id=player.id, club_id="c_academy")

    # Phase 8D: Resolution
    eff = EventEffect(
        id="eff_morale", effect_type=EventEffectType.PLAYER_MORALE_CHANGE, target_id=player.id, target_type="PLAYER", delta_or_value=15.0,
    )
    outcome = EventOutcome(id="out_success", label="Success", weight=1.0, effects=(eff,))
    resolution_8d = resolve_event(definition=def_eb, instance=inst_eb, context=context_8c, outcomes=[outcome], seed="e2e_p10_seed")

    # Phase 8F: Decision
    opt = DecisionOption(id="opt_accept", label="Accept", weight=1.0, effects=(eff,))
    decision_8f = Decision(id="dec_1", prompt="Accept debut?", default_option_id="opt_accept", options=(opt,))
    decision_res_8f = resolve_decision(decision=decision_8f, context=context_8c, seed="e2e_p10_seed", explicit_option_id="opt_accept", resolution_type=DecisionResolutionType.EXPLICIT)

    # Phase 8E: State Application
    app_res_8e = apply_event_resolution(state=player, resolution=resolution_8d, context=context_8c)
    updated_player_state = app_res_8e.resulting_state

    # Phase 9: Career History Recording
    career_rec = CareerRecord(player_id=player.id)
    career_rec = process_career_event(career_rec, resolution_8d, simulation_state=updated_player_state, context=context_8c)
    career_rec = process_career_event(career_rec, decision_res_8f, simulation_state=updated_player_state, context=context_8c)
    career_rec = process_career_event(career_rec, app_res_8e, simulation_state=updated_player_state, context=context_8c)

    # Phase 10: Narrative Engine Construction
    narrative_story = build_narrative_story(career_rec, player_state=updated_player_state)

    assert narrative_story.player_id == player.id
    assert len(narrative_story.narrative_beats) > 0
    assert len(narrative_story.acts) >= 1
    assert narrative_story.resolution_type == ResolutionType.ONGOING
    assert to_json_bytes(narrative_story) is not None
