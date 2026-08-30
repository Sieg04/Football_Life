import hashlib
import json
import os
from types import MappingProxyType
from typing import Any

from app.event.career_domain import CareerRecord, MilestoneType
from app.event.narrative_domain import (
    ActType,
    BeatType,
    ConflictType,
    NarrativeAct,
    NarrativeBeat,
    NarrativeStory,
    OpeningStrategy,
    PremiseType,
    ResolutionType,
    StoryDensity,
)
from app.event.script_domain import (
    ClosingType,
    HookType,
    NarrationPacing,
    NarrationStyle,
    NarrationTone,
    ScriptBuildResult,
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
    ScriptTransition,
    StoryScript,
    TransitionType,
)

# Load configuration rules lazily or at import time safely
_RULES_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "data", "rules", "script.json")


def _load_script_rules() -> dict[str, Any]:
    try:
        with open(_RULES_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        # Fallback inline config if file reading fails
        return {
            "default_words_per_minute": 150,
            "densities": {
                "COMPACT": {"max_total_beats": 5},
                "STANDARD": {"max_total_beats": 12},
                "DETAILED": {"max_total_beats": 25},
                "COMPLETE": {"max_total_beats": 999},
            },
        }


_SCRIPT_RULES = _load_script_rules()


def _hash_id(prefix: str, payload: str) -> str:
    digest = hashlib.sha256(payload.encode("utf-8")).hexdigest()[:16]
    return f"{prefix}_{digest}"


def calculate_script_word_count(item: Any) -> int:
    """Calculates word count deterministically using whitespace splitting."""
    if item is None:
        return 0
    if isinstance(item, str):
        return len(item.split())
    if isinstance(item, (ScriptSegment, ScriptTransition)):
        return len(item.text.split())
    if isinstance(item, ScriptSection):
        return sum(calculate_script_word_count(seg) for seg in item.segments)
    if isinstance(item, (tuple, list)):
        return sum(calculate_script_word_count(x) for x in item)
    if isinstance(item, StoryScript):
        total = 0
        if item.hook:
            total += calculate_script_word_count(item.hook.segment)
        if item.introduction:
            total += calculate_script_word_count(item.introduction)
        total += sum(calculate_script_word_count(sec) for sec in item.sections)
        total += sum(calculate_script_word_count(tr) for tr in item.transitions)
        if item.resolution:
            total += calculate_script_word_count(item.resolution)
        if item.closing:
            total += calculate_script_word_count(item.closing.segment)
        return total
    return 0


def estimate_script_duration(word_count: int, words_per_minute: int = 150) -> float:
    """Estimates script duration in seconds based on word count and words_per_minute."""
    if words_per_minute <= 0:
        words_per_minute = 150
    return round((word_count / float(words_per_minute)) * 60.0, 2)


def build_script_metadata(
    story: NarrativeStory,
    density: ScriptDensity = ScriptDensity.STANDARD,
    style: NarrationStyle = NarrationStyle.DOCUMENTARY,
    tone: NarrationTone = NarrationTone.NEUTRAL,
    target_duration_seconds: float | None = None,
    words_per_minute: int = 150,
) -> ScriptMetadata:
    if not isinstance(story, NarrativeStory):
        raise ScriptProcessingException(
            ScriptErrorCode.INVALID_NARRATIVE_STORY, "Expected NarrativeStory object"
        )

    eff_target_duration = (
        target_duration_seconds
        if target_duration_seconds is not None
        else story.target_duration_seconds
    )

    return ScriptMetadata(
        story_id=story.story_id,
        player_id=story.player_id,
        density=density,
        style=style,
        tone=tone,
        target_duration_seconds=eff_target_duration,
        words_per_minute=words_per_minute,
        created_version="1.0",
    )


def _is_career_retired(story: NarrativeStory, career_record: CareerRecord | None = None) -> bool:
    if story.resolution_type == ResolutionType.RETIREMENT:
        return True
    if career_record is not None:
        has_ret_event = any(
            e.category.value == "RETIREMENT" or e.event_type.value == "RETIREMENT"
            for e in career_record.events
        )
        has_ret_milestone = any(
            m.milestone_type == MilestoneType.RETIREMENT for m in career_record.milestones
        )
        if has_ret_event or has_ret_milestone:
            return True
    return False


def generate_story_hook(
    story: NarrativeStory, career_record: CareerRecord | None = None
) -> ScriptHook:
    if not isinstance(story, NarrativeStory):
        raise ScriptProcessingException(
            ScriptErrorCode.INVALID_NARRATIVE_STORY, "Expected NarrativeStory object"
        )

    player_name = (
        story.title_context
        if story.title_context
        else f"Player {story.player_id}"
    )

    # Determine best hook strategy
    hook_type = HookType.ORIGIN_HOOK
    hook_text = ""
    source_ref = ScriptSourceReference(story_id=story.story_id)

    # Candidate 1: Climax / Major Achievement
    climax_beat = next(
        (b for b in story.narrative_beats if b.beat_id == story.climax_beat_id), None
    )
    major_beat = next(
        (b for b in story.narrative_beats if b.beat_type == BeatType.MAJOR_ACHIEVEMENT), None
    )

    if climax_beat and climax_beat.source_milestone_ids:
        hook_type = HookType.MAJOR_ACHIEVEMENT
        source_ref = ScriptSourceReference(
            story_id=story.story_id,
            beat_ids=(climax_beat.beat_id,),
            milestone_ids=climax_beat.source_milestone_ids,
            event_ids=climax_beat.source_event_ids,
        )
        hook_text = f"Before reaching the summit of his career, {player_name} faced the ultimate test."
    elif major_beat:
        hook_type = HookType.MAJOR_ACHIEVEMENT
        source_ref = ScriptSourceReference(
            story_id=story.story_id,
            beat_ids=(major_beat.beat_id,),
            milestone_ids=major_beat.source_milestone_ids,
            event_ids=major_beat.source_event_ids,
        )
        hook_text = f"A career defined by defining moments began with a milestone for {player_name}."
    elif story.premise.premise_type == PremiseType.COMEBACK:
        hook_type = HookType.COMEBACK
        hook_text = f"Few believed {player_name} could rebuild after career-altering adversity."
    elif story.premise.premise_type == PremiseType.RIVALRY:
        hook_type = HookType.RIVALRY
        hook_text = f"Every great player needs a defining clash, and {player_name} found his on the pitch."
    elif story.opening_strategy == OpeningStrategy.COLD_OPEN:
        hook_type = HookType.COLD_OPEN
        hook_text = f"At the height of competition, {player_name} stood at a decisive turning point."
    elif story.protagonist.origin:
        hook_type = HookType.ORIGIN_HOOK
        hook_text = f"From {story.protagonist.origin}, {player_name} set out to build a career in professional football."
    else:
        hook_type = HookType.ORIGIN_HOOK
        hook_text = f"This is the football journey of {player_name}."

    w_count = calculate_script_word_count(hook_text)
    dur = estimate_script_duration(w_count)

    seg_id = _hash_id("seg_hook", f"{story.story_id}:{hook_type.value}:{hook_text}")
    segment = ScriptSegment(
        segment_id=seg_id,
        sequence=0,
        segment_type=ScriptSegmentType.HOOK,
        text=hook_text,
        word_count=w_count,
        estimated_duration_seconds=dur,
        pacing=NarrationPacing.MODERATE,
        importance=1.0,
        source_reference=source_ref,
    )

    hook_id = _hash_id("hook", seg_id)
    return ScriptHook(
        hook_id=hook_id,
        hook_type=hook_type,
        text=hook_text,
        segment=segment,
        source_reference=source_ref,
    )


def build_script_introduction(
    story: NarrativeStory, career_record: CareerRecord | None = None
) -> ScriptSection:
    if not isinstance(story, NarrativeStory):
        raise ScriptProcessingException(
            ScriptErrorCode.INVALID_NARRATIVE_STORY, "Expected NarrativeStory object"
        )

    player_name = story.title_context if story.title_context else f"Player {story.player_id}"
    protagonist = story.protagonist

    # Template safety: build intro string strictly from present attributes
    intro_parts = []
    intro_parts.append(f"This is the narrative of {player_name}.")
    if protagonist.position:
        intro_parts.append(f"Playing as a {protagonist.position},")
    if protagonist.origin:
        intro_parts.append(f"hailing from {protagonist.origin},")

    if protagonist.important_clubs:
        club_list = ", ".join(protagonist.important_clubs[:2])
        intro_parts.append(f"his journey features key spells at {club_list}.")
    else:
        intro_parts.append("his career unfolded on the professional stage.")

    text = " ".join(intro_parts)
    w_count = calculate_script_word_count(text)
    dur = estimate_script_duration(w_count)

    source_ref = ScriptSourceReference(story_id=story.story_id)
    seg_id = _hash_id("seg_intro", f"{story.story_id}:{text}")
    segment = ScriptSegment(
        segment_id=seg_id,
        sequence=0,
        segment_type=ScriptSegmentType.INTRODUCTION,
        text=text,
        word_count=w_count,
        estimated_duration_seconds=dur,
        pacing=NarrationPacing.MODERATE,
        importance=0.9,
        source_reference=source_ref,
    )

    sec_id = _hash_id("sec_intro", story.story_id)
    return ScriptSection(
        section_id=sec_id,
        section_type=ScriptSectionType.INTRODUCTION,
        sequence=0,
        title="Introduction",
        segments=(segment,),
        source_reference=source_ref,
    )


def _map_act_type_to_section_type(act_type: ActType) -> ScriptSectionType:
    mapping = {
        ActType.ORIGIN: ScriptSectionType.ORIGIN,
        ActType.SETUP: ScriptSectionType.SETUP,
        ActType.RISE: ScriptSectionType.RISE,
        ActType.CONFLICT: ScriptSectionType.CONFLICT,
        ActType.CRISIS: ScriptSectionType.CRISIS,
        ActType.BREAKTHROUGH: ScriptSectionType.BREAKTHROUGH,
        ActType.PEAK: ScriptSectionType.PEAK,
        ActType.FALL: ScriptSectionType.FALL,
        ActType.RECOVERY: ScriptSectionType.RECOVERY,
        ActType.RESOLUTION: ScriptSectionType.RESOLUTION,
        ActType.LEGACY: ScriptSectionType.LEGACY,
    }
    return mapping.get(act_type, ScriptSectionType.SETUP)


def render_beat_narration(
    story: NarrativeStory, beat: NarrativeBeat, career_record: CareerRecord | None = None
) -> str:
    """Renders factual narration string safely from beat factual context."""
    fc = beat.factual_context
    player_name = story.title_context if story.title_context else f"Player {story.player_id}"

    b_type = beat.beat_type.value if hasattr(beat.beat_type, "value") else str(beat.beat_type)

    if b_type == "FIRST_CHANCE":
        club = fc.get("club_id", fc.get("club", ""))
        if club:
            return f"{player_name} earned his first chance with {club}."
        return f"{player_name} made his senior debut, stepping onto the pitch for his first real opportunity."

    if b_type == "EARLY_SUCCESS":
        return f"{player_name} quickly established his quality with impactful performances early in his career."

    if b_type == "SETBACK":
        return f"Adversity struck as {player_name} faced a difficult setback during the campaign."

    if b_type == "CONFLICT":
        return f"Tension grew on and off the pitch as competitive pressure mounted for {player_name}."

    if b_type == "BREAKTHROUGH":
        return f"{player_name} achieved a career breakthrough, establishing himself as a key player."

    if b_type == "MAJOR_ACHIEVEMENT":
        m_val = fc.get("value", fc.get("milestone_type", ""))
        if m_val:
            return f"{player_name} reached a major landmark, capturing {m_val}."
        return f"{player_name} reached a monumental achievement in his football career."

    if b_type == "CRISIS":
        return f"{player_name} confronted a severe career crisis that jeopardized his momentum."

    if b_type == "COMEBACK":
        return f"Demonstrating resilience, {player_name} mounted a decisive career comeback."

    if b_type == "CLIMAX":
        return f"{player_name} reached the defining climax of his story on the grandest stage."

    if b_type == "PEAK":
        return f"{player_name} played at the absolute peak of his abilities, dominating matches."

    if b_type == "DECLINE":
        return f"As seasons advanced, {player_name} navigated the changing phase of his career."

    if b_type == "FINAL_CHAPTER":
        if _is_career_retired(story, career_record):
            return f"{player_name} entered the final chapter of his playing days."
        return f"{player_name} continued writing another chapter in his active career."

    if b_type == "LEGACY":
        return f"The impact of {player_name} left a lasting footprint on the game."

    return f"{player_name} continued his career progression, marking sequence {beat.sequence}."


def build_script_segments(
    story: NarrativeStory,
    beats: tuple[NarrativeBeat, ...] | tuple[str, ...],
    act: NarrativeAct | None = None,
    career_record: CareerRecord | None = None,
    density: ScriptDensity = ScriptDensity.STANDARD,
    words_per_minute: int = 150,
) -> tuple[ScriptSegment, ...]:
    if not isinstance(story, NarrativeStory):
        raise ScriptProcessingException(
            ScriptErrorCode.INVALID_NARRATIVE_STORY, "Expected NarrativeStory object"
        )

    # Resolve beat objects
    beat_objs: list[NarrativeBeat] = []
    for b in beats:
        if isinstance(b, NarrativeBeat):
            beat_objs.append(b)
        elif isinstance(b, str):
            found = next((nb for nb in story.narrative_beats if nb.beat_id == b), None)
            if found:
                beat_objs.append(found)

    segments: list[ScriptSegment] = []
    act_id_tuple = (act.act_id,) if act else ()

    for idx, beat in enumerate(beat_objs):
        is_climax = (beat.beat_id == story.climax_beat_id) or (beat.beat_type == BeatType.CLIMAX)
        seg_type = ScriptSegmentType.CLIMAX if is_climax else ScriptSegmentType.NARRATION

        text = render_beat_narration(story, beat, career_record)
        w_count = calculate_script_word_count(text)
        dur = estimate_script_duration(w_count, words_per_minute)

        pacing_val = (
            NarrationPacing.CLIMACTIC
            if is_climax
            else NarrationPacing(beat.pacing.value)
        )

        source_ref = ScriptSourceReference(
            story_id=story.story_id,
            act_ids=act_id_tuple,
            beat_ids=(beat.beat_id,),
            event_ids=beat.source_event_ids,
            milestone_ids=beat.source_milestone_ids,
            turning_point_ids=beat.source_turning_point_ids,
            seed_ids=beat.source_seed_ids,
        )

        seg_id = _hash_id("seg", f"{story.story_id}:{beat.beat_id}:{idx}")
        segment = ScriptSegment(
            segment_id=seg_id,
            sequence=idx + 1,
            segment_type=seg_type,
            text=text,
            word_count=w_count,
            estimated_duration_seconds=dur,
            pacing=pacing_val,
            importance=beat.importance,
            source_reference=source_ref,
        )
        segments.append(segment)

    return tuple(segments)


def build_script_sections(
    story: NarrativeStory,
    career_record: CareerRecord | None = None,
    density: ScriptDensity = ScriptDensity.STANDARD,
    words_per_minute: int = 150,
) -> tuple[ScriptSection, ...]:
    if not isinstance(story, NarrativeStory):
        raise ScriptProcessingException(
            ScriptErrorCode.INVALID_NARRATIVE_STORY, "Expected NarrativeStory object"
        )

    sections: list[ScriptSection] = []

    # Map density max beats limit
    density_str = density.value if hasattr(density, "value") else str(density)
    max_beats = _SCRIPT_RULES.get("densities", {}).get(density_str, {}).get("max_total_beats", 12)

    if story.acts:
        current_seq = 1
        total_beats_included = 0
        for act in story.acts:
            if total_beats_included >= max_beats:
                break

            act_beats = [b for b in story.narrative_beats if b.beat_id in act.beat_ids]
            if not act_beats:
                # If act beat_ids are missing or not in narrative_beats, fallback filter by sequence
                act_beats = [
                    b for b in story.narrative_beats
                    if act.start_sequence <= b.sequence <= act.end_sequence
                ]

            # Apply density limit
            remaining = max_beats - total_beats_included
            selected_beats = act_beats[:remaining]
            total_beats_included += len(selected_beats)

            segments = build_script_segments(
                story=story,
                beats=tuple(selected_beats),
                act=act,
                career_record=career_record,
                density=density,
                words_per_minute=words_per_minute,
            )

            sec_type = _map_act_type_to_section_type(act.act_type)
            sec_id = _hash_id("sec", f"{story.story_id}:{act.act_id}")

            all_beat_ids = tuple(b.beat_id for b in selected_beats)
            all_event_ids = tuple(e for b in selected_beats for e in b.source_event_ids)
            all_ms_ids = tuple(m for b in selected_beats for m in b.source_milestone_ids)
            all_tp_ids = tuple(tp for b in selected_beats for tp in b.source_turning_point_ids)

            source_ref = ScriptSourceReference(
                story_id=story.story_id,
                act_ids=(act.act_id,),
                beat_ids=all_beat_ids,
                event_ids=all_event_ids,
                milestone_ids=all_ms_ids,
                turning_point_ids=all_tp_ids,
            )

            section = ScriptSection(
                section_id=sec_id,
                section_type=sec_type,
                sequence=current_seq,
                title=act.title if act.title else sec_type.value.title(),
                segments=segments,
                act_id=act.act_id,
                source_reference=source_ref,
            )
            sections.append(section)
            current_seq += 1
    else:
        # Fallback if acts are empty: create a single RISE/SETUP section from beats
        selected_beats = list(story.narrative_beats[:max_beats])
        segments = build_script_segments(
            story=story,
            beats=tuple(selected_beats),
            career_record=career_record,
            density=density,
            words_per_minute=words_per_minute,
        )
        sec_id = _hash_id("sec_main", story.story_id)
        source_ref = ScriptSourceReference(
            story_id=story.story_id,
            beat_ids=tuple(b.beat_id for b in selected_beats),
        )
        section = ScriptSection(
            section_id=sec_id,
            section_type=ScriptSectionType.RISE,
            sequence=1,
            title="Career Narrative",
            segments=segments,
            source_reference=source_ref,
        )
        sections.append(section)

    return tuple(sections)


def build_script_transitions(
    sections: tuple[ScriptSection, ...],
    style: NarrationStyle = NarrationStyle.DOCUMENTARY,
    words_per_minute: int = 150,
) -> tuple[ScriptTransition, ...]:
    transitions: list[ScriptTransition] = []
    if len(sections) < 2:
        return ()

    for i in range(len(sections) - 1):
        from_sec = sections[i]
        to_sec = sections[i + 1]

        # Determine transition type cleanly without unsupported causality
        t_type = TransitionType.TIME_ADVANCE
        if to_sec.section_type in (ScriptSectionType.CONFLICT, ScriptSectionType.CRISIS):
            t_type = TransitionType.ESCALATION
        elif to_sec.section_type == ScriptSectionType.BREAKTHROUGH:
            t_type = TransitionType.TURNING_POINT
        elif to_sec.section_type == ScriptSectionType.RECOVERY:
            t_type = TransitionType.RECOVERY
        elif to_sec.section_type == ScriptSectionType.PEAK:
            t_type = TransitionType.PEAK
        elif to_sec.section_type == ScriptSectionType.RESOLUTION:
            t_type = TransitionType.RESOLUTION

        if t_type == TransitionType.ESCALATION:
            text = "As expectations rose, new challenges tested his resolve."
        elif t_type == TransitionType.TURNING_POINT:
            text = "Then came the moment that altered the trajectory of his career."
        elif t_type == TransitionType.RECOVERY:
            text = "Rebuilding step by step, he fought to reclaim his position."
        elif t_type == TransitionType.PEAK:
            text = "This marked the beginning of his finest form on the pitch."
        elif t_type == TransitionType.RESOLUTION:
            text = "Looking back across the campaign, the outcome became clear."
        else:
            text = "Moving forward to the next chapter of his journey,"

        w_count = calculate_script_word_count(text)
        dur = estimate_script_duration(w_count, words_per_minute)

        tr_id = _hash_id("tr", f"{from_sec.section_id}:{to_sec.section_id}")
        source_ref = ScriptSourceReference(
            story_id=from_sec.source_reference.story_id,
            act_ids=tuple(
                filter(
                    None,
                    [
                        from_sec.act_id,
                        to_sec.act_id,
                    ],
                )
            ),
        )

        transition = ScriptTransition(
            transition_id=tr_id,
            transition_type=t_type,
            from_section_id=from_sec.section_id,
            to_section_id=to_sec.section_id,
            text=text,
            word_count=w_count,
            estimated_duration_seconds=dur,
            source_reference=source_ref,
        )
        transitions.append(transition)

    return tuple(transitions)


def render_script_climax(
    story: NarrativeStory,
    career_record: CareerRecord | None = None,
    words_per_minute: int = 150,
) -> ScriptSegment | None:
    if not story.climax_beat_id:
        return None

    climax_beat = next(
        (b for b in story.narrative_beats if b.beat_id == story.climax_beat_id), None
    )
    if not climax_beat:
        return None

    player_name = story.title_context if story.title_context else f"Player {story.player_id}"
    text = render_beat_narration(story, climax_beat, career_record)
    if not text.endswith("."):
        text += "."
    text = f"The defining moment of the story arrived: {text}"

    w_count = calculate_script_word_count(text)
    dur = estimate_script_duration(w_count, words_per_minute)

    source_ref = ScriptSourceReference(
        story_id=story.story_id,
        beat_ids=(climax_beat.beat_id,),
        event_ids=climax_beat.source_event_ids,
        milestone_ids=climax_beat.source_milestone_ids,
        turning_point_ids=climax_beat.source_turning_point_ids,
        seed_ids=climax_beat.source_seed_ids,
    )

    seg_id = _hash_id("seg_climax", f"{story.story_id}:{climax_beat.beat_id}")
    return ScriptSegment(
        segment_id=seg_id,
        sequence=99,
        segment_type=ScriptSegmentType.CLIMAX,
        text=text,
        word_count=w_count,
        estimated_duration_seconds=dur,
        pacing=NarrationPacing.CLIMACTIC,
        importance=2.0,
        source_reference=source_ref,
    )


def render_script_resolution(
    story: NarrativeStory,
    career_record: CareerRecord | None = None,
    words_per_minute: int = 150,
) -> ScriptSection:
    if not isinstance(story, NarrativeStory):
        raise ScriptProcessingException(
            ScriptErrorCode.INVALID_NARRATIVE_STORY, "Expected NarrativeStory object"
        )

    player_name = story.title_context if story.title_context else f"Player {story.player_id}"
    is_retired = _is_career_retired(story, career_record)

    # ACTIVE vs RETIRED safety
    if is_retired:
        text = f"{player_name} brought his playing days to a conclusion, leaving behind his career record."
    else:
        text = f"With his career still active, {player_name} continues to write his story in upcoming seasons."

    w_count = calculate_script_word_count(text)
    dur = estimate_script_duration(w_count, words_per_minute)

    source_ref = ScriptSourceReference(story_id=story.story_id)
    seg_id = _hash_id("seg_res", f"{story.story_id}:{text}")
    segment = ScriptSegment(
        segment_id=seg_id,
        sequence=1,
        segment_type=ScriptSegmentType.RESOLUTION,
        text=text,
        word_count=w_count,
        estimated_duration_seconds=dur,
        pacing=NarrationPacing.SLOW,
        importance=1.0,
        source_reference=source_ref,
    )

    sec_id = _hash_id("sec_res", story.story_id)
    return ScriptSection(
        section_id=sec_id,
        section_type=ScriptSectionType.RESOLUTION,
        sequence=998,
        title="Resolution",
        segments=(segment,),
        source_reference=source_ref,
    )


def generate_script_closing(
    story: NarrativeStory,
    resolution_section: ScriptSection | None = None,
    career_record: CareerRecord | None = None,
    words_per_minute: int = 150,
) -> ScriptClosing:
    if not isinstance(story, NarrativeStory):
        raise ScriptProcessingException(
            ScriptErrorCode.INVALID_NARRATIVE_STORY, "Expected NarrativeStory object"
        )

    player_name = story.title_context if story.title_context else f"Player {story.player_id}"
    is_retired = _is_career_retired(story, career_record)

    closing_type = ClosingType.ONGOING
    if is_retired:
        closing_type = ClosingType.RETIREMENT
        text = f"That marks the end of {player_name}'s professional career."
    else:
        closing_type = ClosingType.ONGOING
        text = f"The story of {player_name} remains open-ended as new chapters await."

    w_count = calculate_script_word_count(text)
    dur = estimate_script_duration(w_count, words_per_minute)

    source_ref = ScriptSourceReference(story_id=story.story_id)
    seg_id = _hash_id("seg_closing", f"{story.story_id}:{closing_type.value}:{text}")
    segment = ScriptSegment(
        segment_id=seg_id,
        sequence=999,
        segment_type=ScriptSegmentType.CLOSING,
        text=text,
        word_count=w_count,
        estimated_duration_seconds=dur,
        pacing=NarrationPacing.REFLECTIVE,
        importance=1.0,
        source_reference=source_ref,
    )

    closing_id = _hash_id("closing", seg_id)
    return ScriptClosing(
        closing_id=closing_id,
        closing_type=closing_type,
        text=text,
        segment=segment,
        source_reference=source_ref,
    )


def validate_script_coherence(
    story: NarrativeStory,
    script: StoryScript,
    career_record: CareerRecord | None = None,
) -> bool:
    """Validates script invariants factually, chronologically, and structurally."""
    if not isinstance(story, NarrativeStory):
        raise ScriptProcessingException(
            ScriptErrorCode.INVALID_NARRATIVE_STORY, "Expected NarrativeStory object"
        )
    if not isinstance(script, StoryScript):
        raise ScriptProcessingException(
            ScriptErrorCode.SCRIPT_BUILD_ERROR, "Expected StoryScript object"
        )

    is_retired = _is_career_retired(story, career_record)

    # Invariant: Active career safety
    forbidden_retirement_phrases = [
        "his career ended",
        "his final season",
        "he retired",
        "former player",
        "brought his playing days to a conclusion",
        "end of his professional career",
    ]

    all_texts = []
    if script.hook:
        all_texts.append(script.hook.text)
    if script.introduction:
        all_texts.extend(s.text for s in script.introduction.segments)
    for sec in script.sections:
        all_texts.extend(s.text for s in sec.segments)
    for tr in script.transitions:
        all_texts.append(tr.text)
    if script.climax:
        all_texts.append(script.climax.text)
    if script.resolution:
        all_texts.extend(s.text for s in script.resolution.segments)
    if script.closing:
        all_texts.append(script.closing.text)

    full_script_text_lower = " ".join(all_texts).lower()

    if not is_retired:
        for forbidden in forbidden_retirement_phrases:
            if forbidden in full_script_text_lower:
                raise ScriptProcessingException(
                    ScriptErrorCode.RETIREMENT_INCONSISTENCY,
                    f"Active career script produced forbidden retirement phrase: '{forbidden}'",
                )

    # Invariant: Climax preservation
    if story.climax_beat_id:
        has_climax_ref = (
            (script.climax and script.climax.source_reference.beat_ids == (story.climax_beat_id,))
            or any(
                s.source_reference.beat_ids and story.climax_beat_id in s.source_reference.beat_ids
                for sec in script.sections
                for s in sec.segments
            )
        )
        if not has_climax_ref:
            raise ScriptProcessingException(
                ScriptErrorCode.MISSING_CLIMAX,
                f"Story climax beat '{story.climax_beat_id}' was not preserved in script",
            )

    # Invariant: Source reference traceability for factual segments
    for sec in script.sections:
        for seg in sec.segments:
            ref = seg.source_reference
            if (
                seg.segment_type in (ScriptSegmentType.NARRATION, ScriptSegmentType.CLIMAX)
                and not ref.story_id
                and not ref.beat_ids
                and not ref.event_ids
                and not ref.milestone_ids
                and not ref.turning_point_ids
            ):
                raise ScriptProcessingException(
                    ScriptErrorCode.INVALID_SOURCE_REFERENCE,
                    f"Factual ScriptSegment '{seg.segment_id}' is completely untraceable",
                )

    # Invariant: Unique segment/section IDs
    seen_ids = set()
    all_segment_ids = []
    if script.hook:
        all_segment_ids.append(script.hook.segment.segment_id)
    if script.introduction:
        all_segment_ids.extend(s.segment_id for s in script.introduction.segments)
    for sec in script.sections:
        all_segment_ids.extend(s.segment_id for s in sec.segments)
    if script.climax:
        all_segment_ids.append(script.climax.segment_id)
    if script.resolution:
        all_segment_ids.extend(s.segment_id for s in script.resolution.segments)
    if script.closing:
        all_segment_ids.append(script.closing.segment.segment_id)

    for sid in all_segment_ids:
        if sid in seen_ids:
            raise ScriptProcessingException(
                ScriptErrorCode.COHERENCE_VALIDATION_ERROR,
                f"Duplicate ScriptSegment ID found: '{sid}'",
            )
        seen_ids.add(sid)

    return True


def build_story_script(
    story: NarrativeStory,
    career_record: CareerRecord | None = None,
    density: ScriptDensity = ScriptDensity.STANDARD,
    style: NarrationStyle = NarrationStyle.DOCUMENTARY,
    tone: NarrationTone = NarrationTone.NEUTRAL,
    target_duration_seconds: float | None = None,
    words_per_minute: int = 150,
) -> StoryScript:
    """Main atomic orchestrator converting NarrativeStory -> StoryScript."""
    if not isinstance(story, NarrativeStory):
        raise ScriptProcessingException(
            ScriptErrorCode.INVALID_NARRATIVE_STORY,
            f"Expected NarrativeStory object, got {type(story)}",
        )

    # Build components atomically
    metadata = build_script_metadata(
        story=story,
        density=density,
        style=style,
        tone=tone,
        target_duration_seconds=target_duration_seconds,
        words_per_minute=words_per_minute,
    )

    hook = generate_story_hook(story, career_record)
    introduction = build_script_introduction(story, career_record)
    sections = build_script_sections(
        story=story,
        career_record=career_record,
        density=density,
        words_per_minute=words_per_minute,
    )
    transitions = build_script_transitions(
        sections=sections, style=style, words_per_minute=words_per_minute
    )
    climax = render_script_climax(story, career_record, words_per_minute)
    resolution = render_script_resolution(story, career_record, words_per_minute)
    closing = generate_script_closing(story, resolution, career_record, words_per_minute)

    # Construct preliminary script to calculate total word count & duration
    script_id = _hash_id(
        "script",
        f"{story.story_id}:{density.value if hasattr(density, 'value') else str(density)}:{words_per_minute}",
    )
    title = f"Narration Script: {story.title_context}" if story.title_context else f"Narration Script: Player {story.player_id}"

    prelim_script = StoryScript(
        script_id=script_id,
        metadata=metadata,
        title=title,
        hook=hook,
        introduction=introduction,
        sections=sections,
        transitions=transitions,
        climax=climax,
        resolution=resolution,
        closing=closing,
        word_count=0,
        estimated_duration_seconds=0.0,
        source_reference=ScriptSourceReference(story_id=story.story_id),
    )

    total_words = calculate_script_word_count(prelim_script)
    total_duration = estimate_script_duration(total_words, words_per_minute)

    final_script = StoryScript(
        script_id=script_id,
        metadata=metadata,
        title=title,
        hook=hook,
        introduction=introduction,
        sections=sections,
        transitions=transitions,
        climax=climax,
        resolution=resolution,
        closing=closing,
        word_count=total_words,
        estimated_duration_seconds=total_duration,
        source_reference=ScriptSourceReference(story_id=story.story_id),
    )

    # Validate coherence atomically
    validate_script_coherence(story, final_script, career_record)

    return final_script
