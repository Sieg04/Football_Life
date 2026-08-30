import json
import subprocess
import sys
import pytest
from datetime import date
from types import MappingProxyType

from app.event import (
    ActType,
    BeatType,
    CareerEvent,
    CareerMilestone,
    CareerRecord,
    CareerRelationship,
    CareerTurningPoint,
    ClosingType,
    Decision,
    DecisionOption,
    DecisionResolutionType,
    EffectApplicationResult,
    EventCategory,
    EventContext,
    EventEffect,
    EventEffectType,
    EventOutcome,
    EventResolution,
    EventSignificance,
    EventType,
    HookType,
    MilestoneType,
    NarrativeBeat,
    NarrativeProtagonist,
    NarrativeStory,
    NarrationStyle,
    NarrationTone,
    OpeningStrategy,
    PremiseType,
    RelationshipType,
    ResolutionType,
    ScriptClosing,
    ScriptDensity,
    ScriptErrorCode,
    ScriptHook,
    ScriptMetadata,
    ScriptProcessingException,
    ScriptSection,
    ScriptSectionType,
    ScriptSegment,
    ScriptSegmentType,
    ScriptSourceReference,
    StoryDensity,
    StoryPremise,
    StoryScript,
    TransitionType,
    apply_event_resolution,
    build_narrative_story,
    build_script_introduction,
    build_script_metadata,
    build_script_sections,
    build_script_segments,
    build_script_transitions,
    build_story_script,
    calculate_script_word_count,
    create_event_definition,
    create_event_instance,
    estimate_script_duration,
    generate_script_closing,
    generate_story_hook,
    process_career_event,
    render_script_climax,
    render_script_resolution,
    resolve_decision,
    resolve_event,
    to_json_bytes,
    validate_script_coherence,
)
from app.player.domain import DevelopmentProfile, Player, PlayerAttributes, PlayerState


def create_test_player(pid: str = "p_phase11") -> Player:
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
        id=pid, name="Phase11", surname="Tester", nationality="England", birth_date=date(2005, 1, 1),
        height=180.0, weight=75.0, preferred_foot="Right", primary_position="CM", secondary_positions=(),
        attributes=attrs, current_ability=70.0, potential=85.0, development_rate=75.0,
        development_profile=DevelopmentProfile.BALANCED, state=pstate,
    )


# 1. Domain Primitive Construction & Validation
def test_phase11_domain_primitives():
    ref = ScriptSourceReference(story_id="s1", act_ids=("a1",), beat_ids=("b1",))
    assert ref.story_id == "s1"
    assert ref.act_ids == ("a1",)

    with pytest.raises(ValueError):
        ScriptSourceReference(story_id="")

    seg = ScriptSegment(
        segment_id="seg1", sequence=1, segment_type=ScriptSegmentType.NARRATION,
        text="Sample text", word_count=2, estimated_duration_seconds=0.8,
        source_reference=ref,
    )
    assert seg.segment_id == "seg1"
    assert seg.word_count == 2

    with pytest.raises(ValueError):
        ScriptSegment(
            segment_id="", sequence=1, segment_type=ScriptSegmentType.NARRATION,
            text="Text", word_count=1, estimated_duration_seconds=1.0,
        )


# 2. Immutability & Nested Immutability
def test_immutability_and_nested_immutability():
    ev = CareerEvent(
        event_id="ce1", source_event_id="se1", player_id="p1", season=1, sequence=1,
        event_type=EventType.PLAYER, category=EventCategory.DEBUT, significance=EventSignificance.MAJOR,
    )
    rec = CareerRecord(player_id="p1", events=(ev,))
    story = build_narrative_story(rec)
    script = build_story_script(story, rec)

    with pytest.raises(AttributeError):
        script.title = "New Title"  # type: ignore

    with pytest.raises(AttributeError):
        script.metadata.words_per_minute = 200  # type: ignore


# 3. Hook Generation Strategies
def test_hook_generation_strategies():
    ev = CareerEvent(
        event_id="ce1", source_event_id="se1", player_id="p1", season=1, sequence=1,
        event_type=EventType.PLAYER, category=EventCategory.DEBUT, significance=EventSignificance.MAJOR,
    )
    rec = CareerRecord(player_id="p1", events=(ev,))
    story = build_narrative_story(rec)

    hook = generate_story_hook(story, rec)
    assert hook.hook_type in (HookType.MAJOR_ACHIEVEMENT, HookType.ORIGIN_HOOK, HookType.COLD_OPEN)
    assert len(hook.text) > 0
    assert hook.source_reference.story_id == story.story_id


# 4. Introduction & Template Safety
def test_introduction_template_safety():
    protagonist = NarrativeProtagonist(player_id="p1", position="ST", origin="Spain")
    premise = StoryPremise(premise_type=PremiseType.RISE)
    story = NarrativeStory(
        story_id="s1", player_id="p1", title_context="Juan", premise=premise, protagonist=protagonist
    )
    intro = build_script_introduction(story)
    assert "Juan" in intro.segments[0].text
    assert "ST" in intro.segments[0].text
    assert "Spain" in intro.segments[0].text


# 5. Section Assembly & Density Modes
def test_section_assembly_and_densities():
    events = [
        CareerEvent(
            event_id=f"ce_{i}", source_event_id=f"se_{i}", player_id="p1", season=1, sequence=i,
            event_type=EventType.PLAYER, category=EventCategory.APPEARANCE,
            significance=EventSignificance.MINOR if i % 2 == 0 else EventSignificance.MAJOR,
        )
        for i in range(1, 20)
    ]
    rec = CareerRecord(player_id="p1", events=tuple(events))
    story = build_narrative_story(rec, density=StoryDensity.DETAILED)

    script_compact = build_story_script(story, rec, density=ScriptDensity.COMPACT)
    script_complete = build_story_script(story, rec, density=ScriptDensity.COMPLETE)

    assert script_compact.word_count <= script_complete.word_count


# 6. Active vs Retired Career Safety Invariant
def test_active_vs_retired_safety():
    # Active Career
    ev_app = CareerEvent(
        event_id="ce_act", source_event_id="se_act", player_id="p_act", season=1, sequence=1,
        event_type=EventType.PLAYER, category=EventCategory.APPEARANCE, significance=EventSignificance.MINOR,
    )
    rec_act = CareerRecord(player_id="p_act", events=(ev_app,))
    story_act = build_narrative_story(rec_act)
    script_act = build_story_script(story_act, rec_act)

    assert script_act.closing.closing_type == ClosingType.ONGOING
    assert "retired" not in script_act.closing.text.lower()
    assert "career ended" not in script_act.closing.text.lower()

    # Retired Career
    ev_ret = CareerEvent(
        event_id="ce_ret", source_event_id="se_ret", player_id="p_ret", season=10, sequence=10,
        event_type=EventType.PLAYER, category=EventCategory.RETIREMENT, significance=EventSignificance.MAJOR,
    )
    rec_ret = CareerRecord(player_id="p_ret", events=(ev_ret,))
    story_ret = build_narrative_story(rec_ret)
    script_ret = build_story_script(story_ret, rec_ret)

    assert script_ret.closing.closing_type == ClosingType.RETIREMENT


# 7. Climax Preservation & Traceability
ev_trophy_sample = CareerEvent(
    event_id="ce_climax", source_event_id="se_climax", player_id="p1", season=1, sequence=5,
    event_type=EventType.PLAYER, category=EventCategory.TROPHY, significance=EventSignificance.CRITICAL,
)
def test_climax_preservation():
    rec = CareerRecord(player_id="p1", events=(ev_trophy_sample,))
    story = build_narrative_story(rec)
    script = build_story_script(story, rec)

    if story.climax_beat_id:
        assert script.climax is not None
        assert script.climax.source_reference.beat_ids == (story.climax_beat_id,)


# 8. Atomicity on Error
def test_atomicity_on_error():
    story = build_narrative_story(CareerRecord(player_id="p1"))
    fake_story = "NOT_A_STORY"

    with pytest.raises(ScriptProcessingException) as exc_info:
        build_story_script(fake_story)  # type: ignore

    assert exc_info.value.code == ScriptErrorCode.INVALID_NARRATIVE_STORY


# 9. 100x Determinism & Replay
def test_100x_determinism_and_replay():
    ev = CareerEvent(
        event_id="ce_det", source_event_id="se_det", player_id="p_det", season=1, sequence=1,
        event_type=EventType.PLAYER, category=EventCategory.DEBUT, significance=EventSignificance.MAJOR,
    )
    rec = CareerRecord(player_id="p_det", events=(ev,))
    story = build_narrative_story(rec)

    baseline_script = build_story_script(story, rec)
    baseline_bytes = to_json_bytes(baseline_script)

    for i in range(100):
        run_script = build_story_script(story, rec)
        assert run_script == baseline_script
        assert to_json_bytes(run_script) == baseline_bytes


# 10. Cross-Process Determinism
def test_cross_process_determinism():
    script = """
import sys
from app.event import CareerRecord, CareerEvent, EventType, EventCategory, EventSignificance, build_narrative_story, build_story_script, to_json_bytes

ev = CareerEvent(
    event_id="ce_cross", source_event_id="se_cross", player_id="p_cross", season=1, sequence=1,
    event_type=EventType.PLAYER, category=EventCategory.DEBUT, significance=EventSignificance.MAJOR,
)
rec = CareerRecord(player_id="p_cross", events=(ev,))
story = build_narrative_story(rec)
script_obj = build_story_script(story, rec)
sys.stdout.buffer.write(to_json_bytes(script_obj))
"""
    cmd = [sys.executable, "-c", script]
    res1 = subprocess.run(cmd, capture_output=True, check=True, env={"PYTHONPATH": "backend"})
    res2 = subprocess.run(cmd, capture_output=True, check=True, env={"PYTHONPATH": "backend"})

    assert res1.stdout == res2.stdout
    assert len(res1.stdout) > 0


# 11. End-to-End Integration (Phase 8 -> Phase 9 -> Phase 10 -> Phase 11)
def test_full_e2e_phase8_to_11_pipeline():
    player = create_test_player("p_e2e_p11")
    def_eb = create_event_definition(
        event_type=EventType.PLAYER, name="Senior Callup", description_key="desc_callup", priority=90,
    )
    inst_eb = create_event_instance(
        definition=def_eb, season=1, entity_id=player.id, entity_type="PLAYER", seed="e2e_p11_seed",
    )
    context_8c = EventContext(season=1, player_id=player.id, club_id="c_top")

    # Phase 8D
    eff = EventEffect(
        id="eff_rep", effect_type=EventEffectType.PLAYER_REPUTATION_CHANGE, target_id=player.id, target_type="PLAYER", delta_or_value=20.0,
    )
    outcome = EventOutcome(id="out_star", label="Star Performance", weight=1.0, effects=(eff,))
    resolution_8d = resolve_event(definition=def_eb, instance=inst_eb, context=context_8c, outcomes=[outcome], seed="e2e_p11_seed")

    # Phase 8E
    app_res_8e = apply_event_resolution(state=player, resolution=resolution_8d, context=context_8c)
    updated_player_state = app_res_8e.resulting_state

    # Phase 9
    career_rec = CareerRecord(player_id=player.id)
    career_rec = process_career_event(career_rec, resolution_8d, simulation_state=updated_player_state, context=context_8c)

    # Phase 10
    narrative_story = build_narrative_story(career_rec, player_state=updated_player_state)

    # Phase 11
    story_script = build_story_script(narrative_story, career_rec)

    assert story_script.metadata.player_id == player.id
    assert story_script.word_count > 0
    assert story_script.estimated_duration_seconds > 0.0
    assert to_json_bytes(story_script) is not None
