import pytest
from app.event.career_domain import (
    ArcStatus,
    ArcType,
    CareerArc,
    CareerEvent,
    CareerMilestone,
    CareerRecord,
    CareerRelationship,
    CareerTurningPoint,
    EventCategory,
    EventSignificance,
    MilestoneType,
    RelationshipStatus,
    RelationshipType,
    TurningPointType,
)
from app.event.domain import to_json_bytes
from app.event.narrative_domain import (
    ActType,
    BeatType,
    EmotionalDirection,
    NarrativeAct,
    NarrativeBeat,
    NarrativeFunction,
    NarrativePacing,
    NarrativeProtagonist,
    NarrativeStory,
    OpeningStrategy,
    PremiseType,
    ResolutionType,
    StoryDensity,
    StoryPremise,
)
from app.event.presentation_domain import (
    CareerArcPresentation,
    CareerHighlight,
    CareerOverview,
    CareerPresentation,
    CareerStatistics,
    CareerStatus,
    ClubPresentation,
    HighlightType,
    NarrativePresentation,
    PlayerPresentation,
    PresentationBuildResult,
    PresentationDensity,
    PresentationErrorCode,
    PresentationMetadata,
    PresentationProcessingException,
    PresentationSectionType,
    PresentationSourceReference,
    RelationshipPresentation,
    ScriptPresentation,
    SeasonPresentation,
    TimelineEntry,
    TimelineEntryType,
    VisualPriority,
)
from app.event.presentation_engine import (
    build_career_arc_presentation,
    build_career_highlights,
    build_career_overview,
    build_career_presentation,
    build_career_statistics,
    build_career_timeline,
    build_club_presentations,
    build_narrative_presentation,
    build_player_presentation,
    build_presentation_metadata,
    build_relationship_presentations,
    build_script_presentation,
    build_season_presentations,
    validate_career_presentation,
)
from app.event.script_domain import (
    ClosingType,
    HookType,
    NarrationStyle,
    NarrationTone,
    ScriptClosing,
    ScriptHook,
    ScriptMetadata,
    ScriptSection,
    ScriptSectionType,
    ScriptSegment,
    ScriptSegmentType,
    ScriptSourceReference,
    StoryScript,
)


def create_sample_career_record() -> CareerRecord:
    ev1 = CareerEvent(
        event_id="ev_001",
        source_event_id="src_ev_001",
        player_id="player_7",
        season=2024,
        sequence=1,
        event_type="DEVELOPMENT",
        category=EventCategory.DEBUT,
        significance=EventSignificance.MAJOR,
        clubs=("FC Barcelona",),
        state_changes={"matches": 1, "goals": 1, "rating": 8.5},
    )
    ev2 = CareerEvent(
        event_id="ev_002",
        source_event_id="src_ev_002",
        player_id="player_7",
        season=2024,
        sequence=2,
        event_type="TRANSFER",
        category=EventCategory.TRANSFER,
        significance=EventSignificance.CRITICAL,
        clubs=("FC Barcelona", "PSG"),
        state_changes={"matches": 0},
    )

    ms1 = CareerMilestone(
        milestone_id="ms_001",
        player_id="player_7",
        season=2024,
        sequence=1,
        milestone_type=MilestoneType.FIRST_TROPHY,
        significance=EventSignificance.CRITICAL,
        value="La Liga Title",
        club_id="FC Barcelona",
        metadata={"title": "La Liga Champions"},
    )

    tp1 = CareerTurningPoint(
        turning_point_id="tp_001",
        player_id="player_7",
        season=2024,
        sequence=2,
        turning_point_type=TurningPointType.BREAKTHROUGH,
        significance=EventSignificance.CRITICAL,
        source_event_id="ev_001",
    )

    arc1 = CareerArc(
        arc_id="arc_001",
        player_id="player_7",
        arc_type=ArcType.BREAKTHROUGH,
        status=ArcStatus.ACTIVE,
        start_sequence=1,
        event_ids=("ev_001",),
        milestone_ids=("ms_001",),
        turning_point_ids=("tp_001",),
    )

    rel1 = CareerRelationship(
        relationship_id="rel_001",
        player_id="player_7",
        source_entity="player_7",
        target_entity="Manager X",
        relationship_type=RelationshipType.MENTOR,
        status=RelationshipStatus.ACTIVE,
        strength=0.9,
        start_sequence=1,
        last_updated_sequence=2,
        event_ids=("ev_001",),
    )

    return CareerRecord(
        player_id="player_7",
        events=(ev1, ev2),
        milestones=(ms1,),
        turning_points=(tp1,),
        arcs=(arc1,),
        relationships=(rel1,),
        last_sequence=2,
    )


def create_sample_narrative_story() -> NarrativeStory:
    premise = StoryPremise(
        premise_type=PremiseType.RISE,
        protagonist_goal="Reach world class level",
        central_conflict_id="conf_001",
        primary_arc_id="arc_001",
    )
    protagonist = NarrativeProtagonist(
        player_id="player_7",
        position="ST",
        origin="Spain",
        important_clubs=("FC Barcelona",),
    )
    beat1 = NarrativeBeat(
        beat_id="beat_001",
        sequence=1,
        beat_type=BeatType.BREAKTHROUGH,
        narrative_function=NarrativeFunction.PAYOFF,
        emotional_direction=EmotionalDirection.TRIUMPH,
        pacing=NarrativePacing.CLIMACTIC,
        importance=1.5,
        source_event_ids=("ev_001",),
        source_milestone_ids=("ms_001",),
    )
    act1 = NarrativeAct(
        act_id="act_001",
        sequence=1,
        act_type=ActType.RISE,
        title="The Rise",
        description="The early rise phase",
        start_sequence=1,
        end_sequence=2,
        beat_ids=("beat_001",),
    )
    return NarrativeStory(
        story_id="story_001",
        player_id="player_7",
        density=StoryDensity.STANDARD,
        premise=premise,
        protagonist=protagonist,
        acts=(act1,),
        narrative_beats=(beat1,),
        opening_beat_id="beat_001",
        climax_beat_id="beat_001",
        title_context="Player 7 Story",
        resolution_type=ResolutionType.ONGOING,
    )


def create_sample_script() -> StoryScript:
    meta = ScriptMetadata(
        story_id="story_001",
        player_id="player_7",
        density=PresentationDensity.STANDARD,
        style=NarrationStyle.DOCUMENTARY,
        tone=NarrationTone.NEUTRAL,
    )
    seg1 = ScriptSegment(
        segment_id="seg_001",
        sequence=1,
        segment_type=ScriptSegmentType.NARRATION,
        text="A rising star emerges.",
        word_count=4,
        estimated_duration_seconds=1.6,
        source_reference=ScriptSourceReference(story_id="story_001", beat_ids=("beat_001",)),
    )
    sec1 = ScriptSection(
        section_id="sec_001",
        section_type=ScriptSectionType.RISE,
        sequence=1,
        title="The Rise",
        segments=(seg1,),
        source_reference=ScriptSourceReference(story_id="story_001"),
    )
    hook_seg = ScriptSegment(
        segment_id="seg_hook",
        sequence=0,
        segment_type=ScriptSegmentType.HOOK,
        text="The beginning of greatness.",
        word_count=4,
        estimated_duration_seconds=1.6,
        source_reference=ScriptSourceReference(story_id="story_001"),
    )
    hook = ScriptHook(
        hook_id="hook_001",
        hook_type=HookType.ORIGIN_HOOK,
        text="The beginning of greatness.",
        segment=hook_seg,
        source_reference=ScriptSourceReference(story_id="story_001"),
    )
    closing_seg = ScriptSegment(
        segment_id="seg_close",
        sequence=999,
        segment_type=ScriptSegmentType.CLOSING,
        text="The journey continues.",
        word_count=3,
        estimated_duration_seconds=1.2,
        source_reference=ScriptSourceReference(story_id="story_001"),
    )
    closing = ScriptClosing(
        closing_id="close_001",
        closing_type=ClosingType.ONGOING,
        text="The journey continues.",
        segment=closing_seg,
        source_reference=ScriptSourceReference(story_id="story_001"),
    )
    return StoryScript(
        script_id="script_001",
        metadata=meta,
        title="Script Title",
        hook=hook,
        sections=(sec1,),
        climax=seg1,
        closing=closing,
        word_count=11,
        estimated_duration_seconds=4.4,
        source_reference=ScriptSourceReference(story_id="story_001"),
    )


def test_domain_construction_and_immutability():
    p = PlayerPresentation(player_id="p1", name="John Doe")
    assert p.player_id == "p1"
    assert p.career_status == CareerStatus.ACTIVE

    with pytest.raises(AttributeError):
        p.name = "Jane Doe"

    overview = CareerOverview(matches=10, goals=5)
    assert overview.matches == 10

    stats = CareerStatistics(goals=5, trophies=("Cup",))
    assert stats.trophies == ("Cup",)


def test_presentation_builders():
    rec = create_sample_career_record()
    story = create_sample_narrative_story()
    script = create_sample_script()

    player_p = build_player_presentation(career_record=rec, story=story, script=script)
    assert player_p.player_id == "player_7"
    assert player_p.current_club == "FC Barcelona"

    overview_p = build_career_overview(career_record=rec, story=story, script=script)
    assert overview_p.years_active == 1
    assert overview_p.goals == 1

    clubs_p = build_club_presentations(career_record=rec, story=story)
    assert len(clubs_p) == 2

    seasons_p = build_season_presentations(career_record=rec, story=story)
    assert len(seasons_p) == 1

    tl_p = build_career_timeline(career_record=rec, story=story, script=script)
    assert len(tl_p) == 4

    hl_p = build_career_highlights(career_record=rec, story=story, script=script)
    assert len(hl_p) >= 2

    arc_p = build_career_arc_presentation(career_record=rec, story=story)
    assert len(arc_p) == 1

    rel_p = build_relationship_presentations(career_record=rec)
    assert len(rel_p) == 1

    n_p = build_narrative_presentation(story=story)
    assert n_p.story_id == "story_001"

    s_p = build_script_presentation(script=script)
    assert s_p.script_id == "script_001"


def test_full_career_presentation():
    rec = create_sample_career_record()
    story = create_sample_narrative_story()
    script = create_sample_script()

    pres = build_career_presentation(career_record=rec, story=story, script=script)
    assert pres.player.player_id == "player_7"
    assert len(pres.timeline) > 0
    assert pres.narrative is not None
    assert pres.script is not None

    assert validate_career_presentation(pres, career_record=rec, story=story, script=script) is True


def test_empty_career_handling():
    pres = build_career_presentation()
    assert pres.player.player_id == "unknown"
    assert pres.overview.matches == 0
    assert len(pres.timeline) == 0
    assert pres.narrative is None
    assert pres.script is None


def test_active_career_safety_validation():
    rec = create_sample_career_record()
    story = create_sample_narrative_story()
    pres = build_career_presentation(career_record=rec, story=story)

    # Force invalid retired status on active career
    object.__setattr__(pres.player, "career_status", CareerStatus.RETIRED)

    with pytest.raises(PresentationProcessingException) as exc_info:
        validate_career_presentation(pres, career_record=rec, story=story)
    assert exc_info.value.code == PresentationErrorCode.INCONSISTENT_DATA
