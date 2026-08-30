import hashlib
import json
import os
from types import MappingProxyType
from typing import Any

from app.event.career_domain import (
    ArcStatus,
    CareerArc,
    CareerEvent,
    CareerMilestone,
    CareerRecord,
    CareerRelationship,
    CareerTurningPoint,
    EventSignificance,
    MilestoneType,
)
from app.event.narrative_domain import NarrativeStory, ResolutionType
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
from app.event.script_domain import StoryScript

_RULES_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "data", "rules", "presentation.json")


def _load_presentation_rules() -> dict[str, Any]:
    try:
        with open(_RULES_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {
            "default_density": "STANDARD",
            "default_section_order": [
                "PLAYER",
                "OVERVIEW",
                "CAREER",
                "STATISTICS",
                "TIMELINE",
                "HIGHLIGHTS",
                "CAREER_ARC",
                "RELATIONSHIPS",
                "STORY",
                "SCRIPT",
            ],
            "timeline_display_limits": {
                "COMPACT": 10,
                "STANDARD": 25,
                "DETAILED": 50,
                "COMPLETE": 999,
            },
            "highlight_caps": {
                "COMPACT": 3,
                "STANDARD": 5,
                "DETAILED": 10,
                "COMPLETE": 999,
            },
        }


_PRESENTATION_RULES = _load_presentation_rules()


def _hash_id(prefix: str, payload: str) -> str:
    digest = hashlib.sha256(payload.encode("utf-8")).hexdigest()[:16]
    return f"{prefix}_{digest}"


def _is_career_retired(career_record: CareerRecord | None, story: Any | None) -> bool:
    if story and getattr(story, "resolution_type", None) == ResolutionType.RETIREMENT:
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


def build_player_presentation(
    career_record: CareerRecord | None = None,
    story: Any | None = None,
    script: StoryScript | None = None,
    player_id: str | None = None,
) -> PlayerPresentation:
    pid = player_id
    if not pid and story:
        pid = getattr(story, "player_id", None) or getattr(getattr(story, "player", None), "id", None)
    if not pid and career_record:
        pid = career_record.player_id
    if not pid:
        pid = "player_unknown"

    name = None
    if story and hasattr(story, "player"):
        p = story.player
        name = f"{p.name} {p.surname}".strip()
    elif story and hasattr(story, "title_context") and story.title_context:
        name = story.title_context
    if not name:
        name = f"Player {pid}"

    position = None
    if story and hasattr(story, "player"):
        position = str(getattr(story.player, "primary_position", ""))
    elif story and hasattr(story, "protagonist") and story.protagonist:
        position = story.protagonist.position

    current_club = None
    if story and hasattr(story, "current_club_id"):
        current_club = str(story.current_club_id)
    elif story and hasattr(story, "protagonist") and story.protagonist and story.protagonist.important_clubs:
        current_club = story.protagonist.important_clubs[0]

    if not current_club and career_record and career_record.events:
        for ev in reversed(career_record.events):
            if ev.clubs:
                current_club = ev.clubs[0]
                break

    status = CareerStatus.RETIRED if _is_career_retired(career_record, story) else CareerStatus.ACTIVE

    return PlayerPresentation(
        player_id=pid,
        name=name,
        position=position,
        current_club=current_club,
        career_status=status,
    )


def build_career_overview(
    career_record: CareerRecord | None = None,
    story: Any | None = None,
    script: StoryScript | None = None,
) -> CareerOverview:
    if not career_record and not story:
        return CareerOverview()

    events = career_record.events if career_record else ()
    milestones = career_record.milestones if career_record else ()
    turning_points = career_record.turning_points if career_record else ()
    arcs = career_record.arcs if career_record else ()

    seasons = set()
    for ev in events:
        seasons.add(str(ev.season))
    for ms in milestones:
        seasons.add(str(ms.season))
    for tp in turning_points:
        seasons.add(str(tp.season))

    sorted_seasons = sorted(list(seasons))
    career_start = sorted_seasons[0] if sorted_seasons else None
    career_end = sorted_seasons[-1] if sorted_seasons else None
    years_active = len(sorted_seasons)

    clubs = set()
    for ev in events:
        clubs.update(ev.clubs)
    if story and getattr(story, "protagonist", None):
        clubs.update(story.protagonist.important_clubs)
    clubs_count = len(clubs)

    matches = 0
    goals = 0
    assists = 0
    for ev in events:
        sc = ev.state_changes
        sd = ev.summary_data
        matches += int(sc.get("matches", sd.get("matches", 0)))
        goals += int(sc.get("goals", sd.get("goals", 0)))
        assists += int(sc.get("assists", sd.get("assists", 0)))

    trophies_count = sum(
        1 for m in milestones if m.milestone_type in (MilestoneType.FIRST_TROPHY,) or "TROPHY" in m.milestone_type.value
    )

    peak_arc = next((a.arc_type.value for a in arcs if a.status == ArcStatus.ACTIVE), None)
    if not peak_arc and arcs:
        peak_arc = arcs[-1].arc_type.value

    return CareerOverview(
        career_start=career_start,
        career_end=career_end,
        years_active=years_active,
        clubs_count=clubs_count,
        matches=matches,
        goals=goals,
        assists=assists,
        trophies=trophies_count,
        milestones=len(milestones),
        turning_points=len(turning_points),
        career_arc=peak_arc,
    )


def build_career_statistics(
    career_record: CareerRecord | None = None,
    story: NarrativeStory | None = None,
) -> CareerStatistics:
    if not career_record:
        return CareerStatistics()

    appearances = 0
    goals = 0
    assists = 0
    clean_sheets = 0
    minutes = 0
    ratings = []

    for ev in career_record.events:
        sc = ev.state_changes
        sd = ev.summary_data
        appearances += int(sc.get("appearances", sc.get("matches", sd.get("appearances", sd.get("matches", 0)))))
        goals += int(sc.get("goals", sd.get("goals", 0)))
        assists += int(sc.get("assists", sd.get("assists", 0)))
        clean_sheets += int(sc.get("clean_sheets", sd.get("clean_sheets", 0)))
        minutes += int(sc.get("minutes", sd.get("minutes", 0)))
        if "rating" in sc and isinstance(sc["rating"], (int, float)):
            ratings.append(float(sc["rating"]))
        elif "rating" in sd and isinstance(sd["rating"], (int, float)):
            ratings.append(float(sd["rating"]))

    avg_rating = round(sum(ratings) / len(ratings), 2) if ratings else None

    trophies = []
    awards = []
    for ms in career_record.milestones:
        if ms.milestone_type in (MilestoneType.FIRST_TROPHY,) or "TROPHY" in ms.milestone_type.value:
            title = str(ms.metadata.get("title", ms.milestone_type.value))
            trophies.append(title)
        elif ms.milestone_type in (MilestoneType.FIRST_MAJOR_AWARD,) or "AWARD" in ms.milestone_type.value:
            title = str(ms.metadata.get("title", ms.milestone_type.value))
            awards.append(title)

    return CareerStatistics(
        appearances=appearances,
        goals=goals,
        assists=assists,
        clean_sheets=clean_sheets,
        minutes=minutes,
        average_rating=avg_rating,
        trophies=tuple(trophies),
        awards=tuple(awards),
    )


def build_club_presentations(
    career_record: CareerRecord | None = None,
    story: NarrativeStory | None = None,
) -> tuple[ClubPresentation, ...]:
    if not career_record:
        return ()

    club_stats: dict[str, dict[str, Any]] = {}

    for ev in career_record.events:
        for club in ev.clubs:
            if club not in club_stats:
                club_stats[club] = {
                    "club_id": club,
                    "club_name": club,
                    "seasons": set(),
                    "appearances": 0,
                    "goals": 0,
                    "assists": 0,
                    "trophies": [],
                    "first_seq": ev.sequence,
                }
            c_data = club_stats[club]
            c_data["seasons"].add(str(ev.season))
            sc = ev.state_changes
            sd = ev.summary_data
            c_data["appearances"] += int(sc.get("appearances", sc.get("matches", sd.get("appearances", 0))))
            c_data["goals"] += int(sc.get("goals", sd.get("goals", 0)))
            c_data["assists"] += int(sc.get("assists", sd.get("assists", 0)))

    for ms in career_record.milestones:
        if ms.club_id and ms.club_id in club_stats:
            if ms.milestone_type in (MilestoneType.FIRST_TROPHY,) or "TROPHY" in ms.milestone_type.value:
                title = str(ms.metadata.get("title", ms.milestone_type.value))
                club_stats[ms.club_id]["trophies"].append(title)

    sorted_clubs = sorted(club_stats.values(), key=lambda x: (x["first_seq"], x["club_name"]))

    presentations = []
    for c in sorted_clubs:
        sorted_seasons = sorted(list(c["seasons"]))
        start_date = sorted_seasons[0] if sorted_seasons else None
        end_date = sorted_seasons[-1] if sorted_seasons else None
        presentations.append(
            ClubPresentation(
                club_id=c["club_id"],
                club_name=c["club_name"],
                start_date=start_date,
                end_date=end_date,
                season_count=len(sorted_seasons),
                appearances=c["appearances"],
                goals=c["goals"],
                assists=c["assists"],
                trophies=tuple(c["trophies"]),
            )
        )

    return tuple(presentations)


def build_season_presentations(
    career_record: CareerRecord | None = None,
    story: NarrativeStory | None = None,
) -> tuple[SeasonPresentation, ...]:
    if not career_record:
        return ()

    season_data: dict[str, dict[str, Any]] = {}

    for ev in career_record.events:
        s_key = str(ev.season)
        if s_key not in season_data:
            season_data[s_key] = {
                "season_id": s_key,
                "season_label": f"Season {s_key}",
                "club_id": ev.clubs[0] if ev.clubs else None,
                "club_name": ev.clubs[0] if ev.clubs else None,
                "appearances": 0,
                "goals": 0,
                "assists": 0,
                "ratings": [],
                "trophies": [],
                "important_events": [],
                "milestones": [],
                "turning_points": [],
            }
        sd_dict = season_data[s_key]
        sc = ev.state_changes
        sd = ev.summary_data
        sd_dict["appearances"] += int(sc.get("appearances", sc.get("matches", sd.get("appearances", 0))))
        sd_dict["goals"] += int(sc.get("goals", sd.get("goals", 0)))
        sd_dict["assists"] += int(sc.get("assists", sd.get("assists", 0)))
        if "rating" in sc and isinstance(sc["rating"], (int, float)):
            sd_dict["ratings"].append(float(sc["rating"]))
        if ev.significance in (EventSignificance.CRITICAL, EventSignificance.MAJOR):
            sd_dict["important_events"].append(ev.event_id)

    for ms in career_record.milestones:
        s_key = str(ms.season)
        if s_key in season_data:
            season_data[s_key]["milestones"].append(ms.milestone_id)
            if ms.milestone_type in (MilestoneType.FIRST_TROPHY,) or "TROPHY" in ms.milestone_type.value:
                title = str(ms.metadata.get("title", ms.milestone_type.value))
                season_data[s_key]["trophies"].append(title)

    for tp in career_record.turning_points:
        s_key = str(tp.season)
        if s_key in season_data:
            season_data[s_key]["turning_points"].append(tp.turning_point_id)

    sorted_seasons = sorted(season_data.values(), key=lambda x: str(x["season_id"]))

    presentations = []
    for s in sorted_seasons:
        ratings = s["ratings"]
        avg_rating = round(sum(ratings) / len(ratings), 2) if ratings else None
        presentations.append(
            SeasonPresentation(
                season_id=s["season_id"],
                season_label=s["season_label"],
                club_id=s["club_id"],
                club_name=s["club_name"],
                appearances=s["appearances"],
                goals=s["goals"],
                assists=s["assists"],
                average_rating=avg_rating,
                trophies=tuple(s["trophies"]),
                important_events=tuple(s["important_events"]),
                milestones=tuple(s["milestones"]),
                turning_points=tuple(s["turning_points"]),
            )
        )

    return tuple(presentations)


def build_career_timeline(
    career_record: CareerRecord | None = None,
    story: Any | None = None,
    script: StoryScript | None = None,
    density: PresentationDensity = PresentationDensity.STANDARD,
) -> tuple[TimelineEntry, ...]:
    if not career_record:
        return ()

    raw_entries: list[tuple[Any, TimelineEntry]] = []

    # Map events
    for ev in career_record.events:
        e_type = TimelineEntryType.EVENT
        if ev.significance == EventSignificance.CRITICAL:
            prio = VisualPriority.CRITICAL
        elif ev.significance == EventSignificance.MAJOR:
            prio = VisualPriority.HIGH
        else:
            prio = VisualPriority.MEDIUM

        if ev.category.value == "TRANSFER":
            e_type = TimelineEntryType.TRANSFER
        elif ev.category.value == "TROPHY":
            e_type = TimelineEntryType.TROPHY

        t_id = _hash_id("tl_ev", ev.event_id)
        src_ref = PresentationSourceReference(
            career_record_id=career_record.player_id,
            event_ids=(ev.event_id,),
            story_id=getattr(story, "story_id", None),
            script_id=getattr(script, "script_id", None),
        )

        entry = TimelineEntry(
            timeline_id=t_id,
            date_or_season=str(ev.season),
            entry_type=e_type,
            title=ev.event_type.value.replace("_", " ").title(),
            summary=f"Event recorded in season {ev.season}.",
            importance=1.0 if prio in (VisualPriority.CRITICAL, VisualPriority.HIGH) else 0.5,
            priority=prio,
            source_reference=src_ref,
        )
        raw_entries.append((str(ev.season), ev.sequence, ev.event_id, entry))

    # Map milestones
    for ms in career_record.milestones:
        t_id = _hash_id("tl_ms", ms.milestone_id)
        src_ref = PresentationSourceReference(
            career_record_id=career_record.player_id,
            milestone_ids=(ms.milestone_id,),
            story_id=getattr(story, "story_id", None),
            script_id=getattr(script, "script_id", None),
        )
        entry = TimelineEntry(
            timeline_id=t_id,
            date_or_season=str(ms.season),
            entry_type=TimelineEntryType.MILESTONE,
            title=ms.milestone_type.value.replace("_", " ").title(),
            summary=f"Milestone reached: {ms.value}",
            importance=1.2,
            priority=VisualPriority.HIGH,
            source_reference=src_ref,
        )
        raw_entries.append((str(ms.season), ms.sequence, ms.milestone_id, entry))

    # Map turning points
    for tp in career_record.turning_points:
        t_id = _hash_id("tl_tp", tp.turning_point_id)
        src_ref = PresentationSourceReference(
            career_record_id=career_record.player_id,
            turning_point_ids=(tp.turning_point_id,),
            story_id=getattr(story, "story_id", None),
            script_id=getattr(script, "script_id", None),
        )
        entry = TimelineEntry(
            timeline_id=t_id,
            date_or_season=str(tp.season),
            entry_type=TimelineEntryType.TURNING_POINT,
            title=tp.turning_point_type.value.replace("_", " ").title(),
            summary="Key turning point in career trajectory.",
            importance=1.5,
            priority=VisualPriority.CRITICAL,
            source_reference=src_ref,
        )
        raw_entries.append((str(tp.season), tp.sequence, tp.turning_point_id, entry))

    raw_entries.sort(key=lambda x: (x[0], x[1], x[2]))
    limit = _PRESENTATION_RULES.get("timeline_display_limits", {}).get(density.value, 25)
    selected_entries = [item[3] for item in raw_entries[:limit]]

    return tuple(selected_entries)


def build_career_highlights(
    career_record: CareerRecord | None = None,
    story: Any | None = None,
    script: StoryScript | None = None,
    density: PresentationDensity = PresentationDensity.STANDARD,
) -> tuple[CareerHighlight, ...]:
    highlights: list[CareerHighlight] = []

    if career_record:
        for ms in career_record.milestones:
            if ms.milestone_type in (MilestoneType.FIRST_TROPHY,) or "TROPHY" in ms.milestone_type.value:
                h_id = _hash_id("hl_ms", ms.milestone_id)
                src_ref = PresentationSourceReference(
                    career_record_id=career_record.player_id,
                    milestone_ids=(ms.milestone_id,),
                    story_id=getattr(story, "story_id", None),
                )
                highlights.append(
                    CareerHighlight(
                        highlight_id=h_id,
                        highlight_type=HighlightType.MAJOR_TROPHY,
                        title=f"Trophy: {ms.metadata.get('title', ms.milestone_type.value)}",
                        description=f"Won major trophy in season {ms.season}.",
                        priority=VisualPriority.CRITICAL,
                        source_reference=src_ref,
                    )
                )

        for tp in career_record.turning_points:
            h_id = _hash_id("hl_tp", tp.turning_point_id)
            src_ref = PresentationSourceReference(
                career_record_id=career_record.player_id,
                turning_point_ids=(tp.turning_point_id,),
                story_id=getattr(story, "story_id", None),
            )
            highlights.append(
                CareerHighlight(
                    highlight_id=h_id,
                    highlight_type=HighlightType.TURNING_POINT,
                    title=f"Turning Point: {tp.turning_point_type.value.replace('_', ' ').title()}",
                    description=f"Career defined by turning point in season {tp.season}.",
                    priority=VisualPriority.HIGH,
                    source_reference=src_ref,
                )
            )

    climax_beat_id = getattr(story, "climax_beat_id", None)
    if story and climax_beat_id:
        climax_beat = next((b for b in getattr(story, "narrative_beats", ()) if b.beat_id == climax_beat_id), None)
        if climax_beat:
            h_id = _hash_id("hl_climax", climax_beat_id)
            src_ref = PresentationSourceReference(
                story_id=climax_beat_id,
                beat_ids=(climax_beat_id,),
                event_ids=climax_beat.source_event_ids,
                milestone_ids=climax_beat.source_milestone_ids,
            )
            highlights.append(
                CareerHighlight(
                    highlight_id=h_id,
                    highlight_type=HighlightType.CLIMAX,
                    title="Narrative Climax",
                    description="The defining moment of the story.",
                    priority=VisualPriority.CRITICAL,
                    source_reference=src_ref,
                )
            )

    prio_map = {VisualPriority.CRITICAL: 0, VisualPriority.HIGH: 1, VisualPriority.MEDIUM: 2, VisualPriority.LOW: 3}
    highlights.sort(key=lambda x: (prio_map.get(x.priority, 9), x.highlight_id))

    cap = _PRESENTATION_RULES.get("highlight_caps", {}).get(density.value, 5)
    return tuple(highlights[:cap])


def build_career_arc_presentation(
    career_record: CareerRecord | None = None,
    story: NarrativeStory | None = None,
) -> tuple[CareerArcPresentation, ...]:
    if not career_record:
        return ()

    presentations = []
    for arc in career_record.arcs:
        src_ref = PresentationSourceReference(
            career_record_id=career_record.player_id,
            arc_ids=(arc.arc_id,),
            event_ids=arc.event_ids,
            milestone_ids=arc.milestone_ids,
            turning_point_ids=arc.turning_point_ids,
        )
        presentations.append(
            CareerArcPresentation(
                arc_id=arc.arc_id,
                arc_type=arc.arc_type.value,
                status=arc.status.value,
                start_reference=str(arc.start_sequence),
                end_reference=str(arc.end_sequence) if arc.end_sequence is not None else None,
                phases=(arc.arc_type.value,),
                current_phase=arc.arc_type.value if arc.status == ArcStatus.ACTIVE else None,
                history=(arc.arc_type.value,),
                source_reference=src_ref,
            )
        )
    return tuple(presentations)


def build_relationship_presentations(
    career_record: CareerRecord | None = None,
) -> tuple[RelationshipPresentation, ...]:
    if not career_record:
        return ()

    presentations = []
    for rel in career_record.relationships:
        src_ref = PresentationSourceReference(
            career_record_id=career_record.player_id,
            relationship_ids=(rel.relationship_id,),
            event_ids=rel.event_ids,
        )
        presentations.append(
            RelationshipPresentation(
                relationship_id=rel.relationship_id,
                target_entity_id=rel.target_entity,
                target_entity_name=rel.target_entity,
                relationship_type=rel.relationship_type.value,
                status=rel.status.value,
                strength=rel.strength,
                start_reference=str(rel.start_sequence),
                end_reference=str(rel.last_updated_sequence),
                source_reference=src_ref,
            )
        )
    return tuple(presentations)


def build_narrative_presentation(
    story: Any | None = None,
) -> NarrativePresentation | None:
    if not story or not isinstance(story, NarrativeStory):
        return None

    src_ref = PresentationSourceReference(
        story_id=story.story_id,
        act_ids=tuple(a.act_id for a in story.acts),
        beat_ids=tuple(b.beat_id for b in story.narrative_beats),
        thread_ids=tuple(th.thread_id for th in story.threads),
        conflict_ids=tuple(c.conflict_id for c in story.conflicts),
    )

    acts_dict = tuple(
        MappingProxyType({
            "act_id": a.act_id,
            "title": a.title,
            "act_type": a.act_type.value,
            "sequence": a.sequence,
        })
        for a in story.acts
    )

    beats_dict = tuple(
        MappingProxyType({
            "beat_id": b.beat_id,
            "beat_type": b.beat_type.value,
            "sequence": b.sequence,
            "importance": b.importance,
        })
        for b in story.narrative_beats
    )

    threads_dict = tuple(
        MappingProxyType({
            "thread_id": th.thread_id,
            "thread_type": th.thread_type.value,
            "importance": th.importance,
        })
        for th in story.threads
    )

    conflicts_dict = tuple(
        MappingProxyType({
            "conflict_id": c.conflict_id,
            "conflict_type": c.conflict_type.value,
            "intensity": c.intensity,
        })
        for c in story.conflicts
    )

    premise_str = story.premise.protagonist_goal if story.premise else "Football Career Story"

    return NarrativePresentation(
        story_id=story.story_id,
        premise=premise_str,
        theme=tuple(t.value if hasattr(t, "value") else str(t) for t in story.themes),
        acts=acts_dict,
        beats=beats_dict,
        threads=threads_dict,
        conflicts=conflicts_dict,
        opening=story.opening_beat_id,
        climax=story.climax_beat_id,
        resolution=story.resolution_type.value if story.resolution_type else None,
        source_reference=src_ref,
    )


def build_script_presentation(
    script: StoryScript | None = None,
) -> ScriptPresentation | None:
    if not script:
        return None

    src_ref = PresentationSourceReference(script_id=script.script_id)

    sec_dicts = tuple(
        MappingProxyType({
            "section_id": sec.section_id,
            "title": sec.title,
            "section_type": sec.section_type.value,
        })
        for sec in script.sections
    )

    seg_dicts = []
    if script.hook:
        seg_dicts.append(MappingProxyType({"segment_id": script.hook.segment.segment_id, "text": script.hook.text}))
    for sec in script.sections:
        for seg in sec.segments:
            seg_dicts.append(MappingProxyType({"segment_id": seg.segment_id, "text": seg.text}))
    if script.climax:
        seg_dicts.append(MappingProxyType({"segment_id": script.climax.segment_id, "text": script.climax.text}))
    if script.closing:
        seg_dicts.append(MappingProxyType({"segment_id": script.closing.segment.segment_id, "text": script.closing.text}))

    tr_dicts = tuple(
        MappingProxyType({
            "transition_id": tr.transition_id,
            "transition_type": tr.transition_type.value,
            "text": tr.text,
        })
        for tr in script.transitions
    )

    return ScriptPresentation(
        script_id=script.script_id,
        hook=script.hook.text if script.hook else None,
        introduction=script.introduction.segments[0].text if script.introduction and script.introduction.segments else None,
        sections=sec_dicts,
        segments=tuple(seg_dicts),
        transitions=tr_dicts,
        climax=script.climax.text if script.climax else None,
        resolution=script.resolution.segments[0].text if script.resolution and script.resolution.segments else None,
        closing=script.closing.text if script.closing else None,
        word_count=script.word_count,
        estimated_duration=script.estimated_duration_seconds,
        source_reference=src_ref,
    )


def build_presentation_metadata(
    player_id: str,
    story: Any | None = None,
    script: StoryScript | None = None,
    density: PresentationDensity = PresentationDensity.STANDARD,
) -> PresentationMetadata:
    p_id = _hash_id("pres", f"{player_id}:{getattr(story, 'story_id', 'none')}:{getattr(script, 'script_id', 'none')}:{density.value}")
    sec_order = (
        PresentationSectionType.PLAYER,
        PresentationSectionType.OVERVIEW,
        PresentationSectionType.CAREER,
        PresentationSectionType.STATISTICS,
        PresentationSectionType.TIMELINE,
        PresentationSectionType.HIGHLIGHTS,
        PresentationSectionType.CAREER_ARC,
        PresentationSectionType.RELATIONSHIPS,
        PresentationSectionType.STORY,
        PresentationSectionType.SCRIPT,
    )
    return PresentationMetadata(
        presentation_id=p_id,
        player_id=player_id,
        created_from_story_id=getattr(story, "story_id", None),
        created_from_script_id=getattr(script, "script_id", None),
        density=density,
        section_order=sec_order,
        version="1.0",
    )


def validate_career_presentation(
    presentation: CareerPresentation,
    career_record: CareerRecord | None = None,
    story: Any | None = None,
    script: StoryScript | None = None,
) -> bool:
    if not isinstance(presentation, CareerPresentation):
        raise PresentationProcessingException(
            PresentationErrorCode.INVALID_PRESENTATION, "Expected CareerPresentation object"
        )

    is_retired = _is_career_retired(career_record, story)
    if not is_retired and presentation.player.career_status == CareerStatus.RETIRED:
        raise PresentationProcessingException(
            PresentationErrorCode.INCONSISTENT_DATA, "Active career presentation cannot show RETIRED player status"
        )

    if story and isinstance(story, NarrativeStory) and story.climax_beat_id:
        has_climax = any(
            h.highlight_type == HighlightType.CLIMAX and story.climax_beat_id in h.source_reference.beat_ids
            for h in presentation.highlights
        )
        if not has_climax and presentation.narrative and presentation.narrative.climax != story.climax_beat_id:
            raise PresentationProcessingException(
                PresentationErrorCode.INCONSISTENT_DATA,
                f"Story climax beat '{story.climax_beat_id}' was not preserved in presentation",
            )

    if career_record:
        rec_ev_ids = {e.event_id for e in career_record.events}
        rec_ms_ids = {m.milestone_id for m in career_record.milestones}
        rec_tp_ids = {tp.turning_point_id for tp in career_record.turning_points}
        rec_rel_ids = {r.relationship_id for r in career_record.relationships}
        rec_arc_ids = {a.arc_id for a in career_record.arcs}

        for entry in presentation.timeline:
            s_ref = entry.source_reference
            for eid in s_ref.event_ids:
                if eid not in rec_ev_ids:
                    raise PresentationProcessingException(
                        PresentationErrorCode.INVALID_REFERENCE, f"Orphaned event reference '{eid}'"
                    )
            for mid in s_ref.milestone_ids:
                if mid not in rec_ms_ids:
                    raise PresentationProcessingException(
                        PresentationErrorCode.INVALID_REFERENCE, f"Orphaned milestone reference '{mid}'"
                    )
            for tpid in s_ref.turning_point_ids:
                if tpid not in rec_tp_ids:
                    raise PresentationProcessingException(
                        PresentationErrorCode.INVALID_REFERENCE, f"Orphaned turning point reference '{tpid}'"
                    )

        for rel in presentation.relationships:
            s_ref = rel.source_reference
            for rid in s_ref.relationship_ids:
                if rid not in rec_rel_ids:
                    raise PresentationProcessingException(
                        PresentationErrorCode.INVALID_REFERENCE, f"Orphaned relationship reference '{rid}'"
                    )

        for arc in presentation.career_arcs:
            s_ref = arc.source_reference
            for aid in s_ref.arc_ids:
                if aid not in rec_arc_ids:
                    raise PresentationProcessingException(
                        PresentationErrorCode.INVALID_REFERENCE, f"Orphaned arc reference '{aid}'"
                    )

    if story and isinstance(story, NarrativeStory) and presentation.narrative:
        if presentation.narrative.source_reference.story_id != story.story_id:
            raise PresentationProcessingException(
                PresentationErrorCode.INVALID_REFERENCE, "Narrative presentation story_id mismatch"
            )

    if script and presentation.script:
        if presentation.script.source_reference.script_id != script.script_id:
            raise PresentationProcessingException(
                PresentationErrorCode.INVALID_REFERENCE, "Script presentation script_id mismatch"
            )

    return True


def build_career_presentation(
    career_record: CareerRecord | None = None,
    story: Any | None = None,
    script: StoryScript | None = None,
    density: PresentationDensity = PresentationDensity.STANDARD,
) -> CareerPresentation:
    pid = "unknown"
    if story:
        pid = getattr(story, "player_id", None) or getattr(getattr(story, "player", None), "id", "unknown")
    elif career_record:
        pid = career_record.player_id

    player = build_player_presentation(career_record=career_record, story=story, script=script, player_id=pid)
    overview = build_career_overview(career_record=career_record, story=story, script=script)
    statistics = build_career_statistics(career_record=career_record, story=story)
    clubs = build_club_presentations(career_record=career_record, story=story)
    seasons = build_season_presentations(career_record=career_record, story=story)
    timeline = build_career_timeline(career_record=career_record, story=story, script=script, density=density)
    highlights = build_career_highlights(career_record=career_record, story=story, script=script, density=density)
    career_arcs = build_career_arc_presentation(career_record=career_record, story=story)
    relationships = build_relationship_presentations(career_record=career_record)
    narrative = build_narrative_presentation(story=story if isinstance(story, NarrativeStory) else None)
    script_pres = build_script_presentation(script=script)
    metadata = build_presentation_metadata(player_id=pid, story=story, script=script, density=density)

    src_ref = PresentationSourceReference(
        career_record_id=career_record.player_id if career_record else None,
        story_id=getattr(story, "story_id", None),
        script_id=getattr(script, "script_id", None),
    )

    presentation = CareerPresentation(
        presentation_id=metadata.presentation_id,
        player=player,
        overview=overview,
        statistics=statistics,
        clubs=clubs,
        seasons=seasons,
        timeline=timeline,
        highlights=highlights,
        career_arcs=career_arcs,
        relationships=relationships,
        narrative=narrative,
        script=script_pres,
        metadata=metadata,
        source_reference=src_ref,
    )

    validate_career_presentation(presentation, career_record=career_record, story=story, script=script)

    return presentation
