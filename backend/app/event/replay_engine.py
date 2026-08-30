import hashlib
import json
from pathlib import Path
from types import MappingProxyType
from typing import Any

from app.event.career_domain import CareerRecord
from app.event.narrative_domain import NarrativeStory
from app.event.presentation_domain import CareerPresentation, CareerStatus, VisualPriority
from app.event.replay_domain import (
    CaptureFrame,
    CapturePreset,
    CapturePresetType,
    CareerReplay,
    ContentScene,
    ContentStory,
    ContentStoryBuildResult,
    ReplayBuildResult,
    ReplayErrorCode,
    ReplayMoment,
    ReplayMomentType,
    ReplayProcessingException,
    ReplaySeason,
    ScenePriority,
    SceneType,
)
from app.event.script_domain import StoryScript

RULES_PATH = Path(__file__).resolve().parent.parent.parent / "data" / "rules" / "replay.json"

_RULES_CACHE: dict[str, Any] | None = None


def load_replay_rules() -> dict[str, Any]:
    global _RULES_CACHE
    if _RULES_CACHE is not None:
        return _RULES_CACHE

    if not RULES_PATH.exists():
        _RULES_CACHE = {
            "version": 1,
            "moment_priority": {
                "CAREER_START": "MEDIUM",
                "DEBUT": "HIGH",
                "GOAL_MILESTONE": "HIGH",
                "STAT_MILESTONE": "MEDIUM",
                "TRANSFER": "CRITICAL",
                "ACHIEVEMENT": "CRITICAL",
                "CONFLICT": "HIGH",
                "TURNING_POINT": "CRITICAL",
                "BREAKTHROUGH": "HIGH",
                "COMEBACK": "HIGH",
                "CAREER_PEAK": "CRITICAL",
                "CAREER_END": "HIGH",
                "SEASON": "MEDIUM",
                "OTHER": "LOW",
            },
            "duration": {"default_scene_seconds": 10.0, "words_per_minute": 150},
            "capture": {
                "default_width": 1920,
                "default_height": 1080,
                "default_preset": "CINEMATIC",
            },
            "limits": {"max_scenes_per_story": 50},
            "presets": {
                "CINEMATIC": {
                    "show_navigation": False,
                    "show_controls": False,
                    "show_branding": True,
                    "show_statistics": True,
                    "show_player_identity": True,
                    "show_season": True,
                },
                "MATCHDAY": {
                    "show_navigation": False,
                    "show_controls": False,
                    "show_branding": True,
                    "show_statistics": True,
                    "show_player_identity": True,
                    "show_season": True,
                },
                "DOCUMENTARY": {
                    "show_navigation": False,
                    "show_controls": False,
                    "show_branding": True,
                    "show_statistics": False,
                    "show_player_identity": True,
                    "show_season": True,
                },
                "PROFILE": {
                    "show_navigation": False,
                    "show_controls": False,
                    "show_branding": True,
                    "show_statistics": True,
                    "show_player_identity": True,
                    "show_season": True,
                },
            },
        }
        return _RULES_CACHE

    with open(RULES_PATH, "r", encoding="utf-8") as f:
        _RULES_CACHE = json.load(f)

    return _RULES_CACHE  # type: ignore[return-value]


def _hash_id(prefix: str, *components: Any) -> str:
    raw = ":".join(str(c) for c in components)
    digest = hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]
    return f"{prefix}_{digest}"


def build_replay_seasons(
    presentation: CareerPresentation | None = None,
    career_record: CareerRecord | None = None,
) -> tuple[ReplaySeason, ...]:
    seasons_list: list[ReplaySeason] = []

    if presentation and presentation.seasons:
        for idx, s in enumerate(presentation.seasons, start=1):
            s_id = s.season_id or f"S{idx}"
            s_label = s.season_label or f"Season {idx}"
            c_id = s.club_id or "club_1"
            c_name = s.club_name or "Club"
            ovr = presentation.player.overall_rating if presentation.player else 75
            trophies = tuple(sorted(s.trophies)) if s.trophies else ()

            season_obj = ReplaySeason(
                season_id=s_id,
                season_label=s_label,
                season_index=idx,
                club_id=c_id,
                club_name=c_name,
                appearances=s.appearances,
                goals=s.goals,
                assists=s.assists,
                trophies=trophies,
                ovr=ovr,
                moment_ids=(),
                source_references=MappingProxyType({"season_id": s_id}),
            )
            seasons_list.append(season_obj)
    elif career_record and career_record.events:
        seasons_set: dict[str, list[Any]] = {}
        for ev in sorted(career_record.events, key=lambda x: (str(x.season), x.sequence)):
            s_key = str(ev.season)
            if s_key not in seasons_set:
                seasons_set[s_key] = []
            seasons_set[s_key].append(ev)

        for idx, (s_key, ev_list) in enumerate(sorted(seasons_set.items()), start=1):
            club_id = ev_list[0].clubs[0] if ev_list[0].clubs else "club_1"
            season_obj = ReplaySeason(
                season_id=s_key,
                season_label=f"Season {s_key}",
                season_index=idx,
                club_id=club_id,
                club_name=f"Club {club_id}",
                appearances=len(ev_list),
                goals=sum(e.summary_data.get("goals", 0) for e in ev_list),
                assists=sum(e.summary_data.get("assists", 0) for e in ev_list),
                trophies=(),
                ovr=75,
                moment_ids=(),
                source_references=MappingProxyType({"season_id": s_key}),
            )
            seasons_list.append(season_obj)
    else:
        # Default single season fallback
        seasons_list.append(
            ReplaySeason(
                season_id="2026/27",
                season_label="Season 2026/27",
                season_index=1,
                club_id="club_1",
                club_name="FC Barcelona",
                appearances=0,
                goals=0,
                assists=0,
                trophies=(),
                ovr=75,
                moment_ids=(),
                source_references=MappingProxyType({"season_id": "2026/27"}),
            )
        )

    return tuple(seasons_list)


def identify_replay_moments(
    career_record: CareerRecord | None = None,
    narrative_story: NarrativeStory | None = None,
    story_script: StoryScript | None = None,
    presentation: CareerPresentation | None = None,
    rules: dict[str, Any] | None = None,
    career_id: str = "default_career",
) -> tuple[ReplayMoment, ...]:
    if rules is None:
        rules = load_replay_rules()

    prio_rules = rules.get("moment_priority", {})
    moments: list[ReplayMoment] = []

    def _get_priority(m_type: ReplayMomentType) -> tuple[ScenePriority, VisualPriority]:
        prio_str = prio_rules.get(m_type.value, "MEDIUM")
        if prio_str == "CRITICAL":
            return ScenePriority.CRITICAL, VisualPriority.CRITICAL
        elif prio_str == "HIGH":
            return ScenePriority.HIGH, VisualPriority.HIGH
        elif prio_str == "LOW":
            return ScenePriority.LOW, VisualPriority.LOW
        return ScenePriority.MEDIUM, VisualPriority.MEDIUM

    # 1. CAREER_START / DEBUT
    if presentation and presentation.player:
        p_name = presentation.player.name
        s_id = presentation.seasons[0].season_id if presentation.seasons else "2026/27"
        prio, vis_prio = _get_priority(ReplayMomentType.CAREER_START)
        m_id = _hash_id("mom", career_id, "CAREER_START", s_id)
        moments.append(
            ReplayMoment(
                moment_id=m_id,
                moment_type=ReplayMomentType.CAREER_START,
                title=f"The Journey Begins: {p_name}",
                description=f"{p_name} begins his professional career.",
                season_id=s_id,
                priority=prio,
                visual_priority=vis_prio,
            )
        )

    # 2. Milestones & Achievements
    if career_record and career_record.milestones:
        for ms in sorted(career_record.milestones, key=lambda x: (str(x.season), x.sequence)):
            m_type_val = ms.milestone_type.value if hasattr(ms.milestone_type, "value") else str(ms.milestone_type)
            if "GOAL" in m_type_val.upper():
                r_type = ReplayMomentType.GOAL_MILESTONE
            elif "TRANSFER" in m_type_val.upper():
                r_type = ReplayMomentType.TRANSFER
            elif "TROPHY" in m_type_val.upper() or "TITLE" in m_type_val.upper():
                r_type = ReplayMomentType.ACHIEVEMENT
            else:
                r_type = ReplayMomentType.STAT_MILESTONE

            prio, vis_prio = _get_priority(r_type)
            s_id = str(ms.season)
            m_id = _hash_id("mom", career_id, ms.milestone_id)
            moments.append(
                ReplayMoment(
                    moment_id=m_id,
                    moment_type=r_type,
                    title=f"Milestone: {m_type_val.replace('_', ' ').title()}",
                    description=f"Achieved {m_type_val} with value {ms.value}.",
                    season_id=s_id,
                    priority=prio,
                    visual_priority=vis_prio,
                    source_milestone_ids=(ms.milestone_id,),
                    source_event_ids=(ms.event_id,) if ms.event_id else (),
                )
            )

    # 3. Turning Points
    if career_record and career_record.turning_points:
        for tp in sorted(career_record.turning_points, key=lambda x: (str(x.season), x.sequence)):
            tp_type_val = tp.turning_point_type.value if hasattr(tp.turning_point_type, "value") else str(tp.turning_point_type)
            prio, vis_prio = _get_priority(ReplayMomentType.TURNING_POINT)
            s_id = str(tp.season)
            m_id = _hash_id("mom", career_id, tp.turning_point_id)
            moments.append(
                ReplayMoment(
                    moment_id=m_id,
                    moment_type=ReplayMomentType.TURNING_POINT,
                    title=f"Turning Point: {tp_type_val.replace('_', ' ').title()}",
                    description=f"Career defined by a critical {tp_type_val.replace('_', ' ').lower()}.",
                    season_id=s_id,
                    priority=prio,
                    visual_priority=vis_prio,
                    source_turning_point_ids=(tp.turning_point_id,),
                    source_event_ids=(tp.source_event_id,) if tp.source_event_id else (),
                )
            )

    # 4. Narrative Conflicts / Climax
    if narrative_story and narrative_story.conflicts:
        for cfl in sorted(narrative_story.conflicts, key=lambda x: x.conflict_id):
            c_type_val = cfl.conflict_type.value if hasattr(cfl.conflict_type, "value") else str(cfl.conflict_type)
            prio, vis_prio = _get_priority(ReplayMomentType.CONFLICT)
            m_id = _hash_id("mom", career_id, cfl.conflict_id)
            moments.append(
                ReplayMoment(
                    moment_id=m_id,
                    moment_type=ReplayMomentType.CONFLICT,
                    title=f"Conflict: {c_type_val.replace('_', ' ').title()}",
                    description=f"Key career conflict with intensity {cfl.intensity}.",
                    season_id="2026/27",
                    priority=prio,
                    visual_priority=vis_prio,
                    source_event_ids=tuple(cfl.source_events),
                )
            )

    # 5. Presentation Highlights
    if presentation and presentation.highlights and not moments:
        for h in presentation.highlights:
            prio, vis_prio = _get_priority(ReplayMomentType.ACHIEVEMENT)
            m_id = _hash_id("mom", career_id, h.highlight_id)
            moments.append(
                ReplayMoment(
                    moment_id=m_id,
                    moment_type=ReplayMomentType.ACHIEVEMENT,
                    title=h.title,
                    description=h.description,
                    season_id="2026/27",
                    priority=prio,
                    visual_priority=vis_prio,
                )
            )

    # 6. Fallback default moments if empty
    if not moments:
        s_id = presentation.seasons[0].season_id if presentation and presentation.seasons else "2026/27"
        prio, vis_prio = _get_priority(ReplayMomentType.CAREER_START)
        m_id = _hash_id("mom", career_id, "default_debut")
        moments.append(
            ReplayMoment(
                moment_id=m_id,
                moment_type=ReplayMomentType.CAREER_START,
                title="Professional Debut",
                description="First official appearance in senior football.",
                season_id=s_id,
                priority=prio,
                visual_priority=vis_prio,
            )
        )

        prio_tp, vis_prio_tp = _get_priority(ReplayMomentType.BREAKTHROUGH)
        m_id_tp = _hash_id("mom", career_id, "default_breakthrough")
        moments.append(
            ReplayMoment(
                moment_id=m_id_tp,
                moment_type=ReplayMomentType.BREAKTHROUGH,
                title="First Professional Goal",
                description="Scored the winning goal in a dramatic performance.",
                season_id=s_id,
                priority=prio_tp,
                visual_priority=vis_prio_tp,
            )
        )

    # If career is retired, add CAREER_END moment
    if presentation and presentation.player and presentation.player.career_status == CareerStatus.RETIRED:
        last_s = presentation.seasons[-1].season_id if presentation.seasons else "2026/27"
        prio_end, vis_end = _get_priority(ReplayMomentType.CAREER_END)
        m_id_end = _hash_id("mom", career_id, "career_end")
        moments.append(
            ReplayMoment(
                moment_id=m_id_end,
                moment_type=ReplayMomentType.CAREER_END,
                title="Career Retirement",
                description="Hangs up the boots after an outstanding career.",
                season_id=last_s,
                priority=prio_end,
                visual_priority=vis_end,
            )
        )

    return tuple(sorted(moments, key=lambda m: (m.season_id, m.moment_id)))


def build_career_replay(
    career_record: CareerRecord | None = None,
    narrative_story: NarrativeStory | None = None,
    story_script: StoryScript | None = None,
    presentation: CareerPresentation | None = None,
    career_id: str = "default_career",
    player_id: str = "P_001",
    player_name: str = "Adrian Martínez",
) -> ReplayBuildResult:
    try:
        seasons = build_replay_seasons(presentation=presentation, career_record=career_record)
        moments = identify_replay_moments(
            career_record=career_record,
            narrative_story=narrative_story,
            story_script=story_script,
            presentation=presentation,
            career_id=career_id,
        )

        # Associate moment_ids back into seasons deterministically
        updated_seasons: list[ReplaySeason] = []
        for s in seasons:
            s_moments = tuple(m.moment_id for m in moments if m.season_id == s.season_id)
            if not s_moments and moments:
                s_moments = (moments[0].moment_id,)
            updated_seasons.append(
                ReplaySeason(
                    season_id=s.season_id,
                    season_label=s.season_label,
                    season_index=s.season_index,
                    club_id=s.club_id,
                    club_name=s.club_name,
                    appearances=s.appearances,
                    goals=s.goals,
                    assists=s.assists,
                    trophies=s.trophies,
                    ovr=s.ovr,
                    moment_ids=s_moments,
                    source_references=s.source_references,
                )
            )

        c_status = presentation.player.career_status if presentation and presentation.player else CareerStatus.ACTIVE
        p_id = presentation.player.player_id if presentation and presentation.player else player_id
        p_name = presentation.player.name if presentation and presentation.player else player_name

        replay_id = _hash_id("replay", career_id, p_id)
        replay = CareerReplay(
            replay_id=replay_id,
            career_id=career_id,
            player_id=p_id,
            player_name=p_name,
            career_status=c_status,
            seasons=tuple(updated_seasons),
            moments=moments,
            source_story_id=narrative_story.story_id if narrative_story else None,
            source_script_id=story_script.script_id if story_script else None,
            source_presentation_id=presentation.presentation_id if presentation else None,
        )

        return ReplayBuildResult(success=True, replay=replay, errors=(), warnings=())
    except Exception as e:
        return ReplayBuildResult(
            success=False, replay=None, errors=(str(e),), warnings=()
        )


def build_replay(
    career_record: CareerRecord | None = None,
    narrative_story: NarrativeStory | None = None,
    story_script: StoryScript | None = None,
    presentation: CareerPresentation | None = None,
    career_id: str = "default_career",
) -> ReplayBuildResult:
    return build_career_replay(
        career_record=career_record,
        narrative_story=narrative_story,
        story_script=story_script,
        presentation=presentation,
        career_id=career_id,
    )


def build_content_scene(
    moment: ReplayMoment | None = None,
    scene_type: SceneType = SceneType.CAREER_MOMENT,
    title: str = "Career Scene",
    subtitle: str = "Key Moment",
    description: str = "Details of this career scene.",
    order_index: int = 0,
    priority: ScenePriority = ScenePriority.MEDIUM,
    season_id: str | None = None,
    script_segment_ids: tuple[str, ...] = (),
    source_references: dict[str, Any] | MappingProxyType = MappingProxyType({}),
    presentation_references: dict[str, Any] | MappingProxyType = MappingProxyType({}),
) -> ContentScene:
    m_id = moment.moment_id if moment else None
    s_id = season_id or (moment.season_id if moment else "2026/27")
    s_type = scene_type
    if moment and scene_type == SceneType.CAREER_MOMENT:
        m_t = moment.moment_type
        if m_t == ReplayMomentType.CAREER_START:
            s_type = SceneType.INTRO
        elif m_t == ReplayMomentType.TRANSFER:
            s_type = SceneType.TRANSFER
        elif m_t in (ReplayMomentType.ACHIEVEMENT, ReplayMomentType.GOAL_MILESTONE):
            s_type = SceneType.ACHIEVEMENT
        elif m_t == ReplayMomentType.CONFLICT:
            s_type = SceneType.CONFLICT
        elif m_t == ReplayMomentType.TURNING_POINT:
            s_type = SceneType.TURNING_POINT
        elif m_t == ReplayMomentType.CAREER_END:
            s_type = SceneType.ENDING

    sc_title = title if not moment else moment.title
    sc_desc = description if not moment else moment.description
    sc_prio = priority if not moment else moment.priority

    scene_id = _hash_id("scene", m_id or sc_title, order_index)

    return ContentScene(
        scene_id=scene_id,
        scene_type=s_type,
        title=sc_title,
        subtitle=subtitle,
        description=sc_desc,
        order_index=order_index,
        priority=sc_prio,
        moment_id=m_id,
        season_id=s_id,
        source_references=source_references if isinstance(source_references, MappingProxyType) else MappingProxyType(source_references or {}),
        script_segment_ids=tuple(script_segment_ids),
        presentation_references=presentation_references if isinstance(presentation_references, MappingProxyType) else MappingProxyType(presentation_references or {}),
    )


def build_content_story(
    replay: CareerReplay,
    moment_ids: tuple[str, ...] | list[str] | None = None,
    story_script: StoryScript | None = None,
    title: str = "My Career Story",
) -> ContentStoryBuildResult:
    try:
        if not isinstance(replay, CareerReplay):
            raise ReplayProcessingException(
                ReplayErrorCode.INVALID_SOURCE, "replay must be a CareerReplay instance"
            )

        selected_moments: list[ReplayMoment] = []

        if moment_ids:
            moment_map = {m.moment_id: m for m in replay.moments}
            seen_ids = set()
            for m_id in moment_ids:
                if m_id not in moment_map:
                    raise ReplayProcessingException(
                        ReplayErrorCode.INVALID_MOMENT,
                        f"Moment ID '{m_id}' not found in replay",
                    )
                if m_id in seen_ids:
                    # Ignore duplicate moment references silently or fail if invalid duplicate
                    continue
                seen_ids.add(m_id)
                selected_moments.append(moment_map[m_id])
        else:
            # Select default scenes from moments
            selected_moments = list(replay.moments)

        if not selected_moments:
            return ContentStoryBuildResult(
                success=False,
                content_story=None,
                errors=("No moments selected for content story",),
            )

        scenes: list[ContentScene] = []
        rules = load_replay_rules()
        def_seconds = rules.get("duration", {}).get("default_scene_seconds", 10.0)

        for idx, m in enumerate(selected_moments):
            matched_segment_ids: list[str] = []
            if story_script and story_script.sections:
                for sec in story_script.sections:
                    for seg in sec.segments:
                        if m.source_event_ids and any(e_id in seg.source_reference.event_ids for e_id in m.source_event_ids):
                            matched_segment_ids.append(seg.segment_id)

            scene = build_content_scene(
                moment=m,
                title=m.title,
                subtitle=f"Season {m.season_id}",
                description=m.description,
                order_index=idx,
                priority=m.priority,
                season_id=m.season_id,
                script_segment_ids=tuple(matched_segment_ids),
            )
            scenes.append(scene)

        story_id = _hash_id("cstory", replay.career_id, len(scenes))
        total_duration = float(len(scenes) * def_seconds)

        content_story = ContentStory(
            content_story_id=story_id,
            career_id=replay.career_id,
            title=title,
            scenes=tuple(scenes),
            total_scenes=len(scenes),
            estimated_duration_seconds=total_duration,
            source_story_id=replay.source_story_id,
            source_script_id=replay.source_script_id,
        )

        return ContentStoryBuildResult(
            success=True, content_story=content_story, errors=(), warnings=()
        )
    except ReplayProcessingException as e:
        return ContentStoryBuildResult(
            success=False, content_story=None, errors=(e.message,)
        )
    except Exception as e:
        return ContentStoryBuildResult(
            success=False, content_story=None, errors=(str(e),)
        )


def reorder_content_scenes(
    story: ContentStory,
    scene_ids: tuple[str, ...] | list[str],
) -> ContentStory:
    if not isinstance(story, ContentStory):
        raise ReplayProcessingException(
            ReplayErrorCode.INVALID_SOURCE, "story must be a ContentStory instance"
        )

    requested_ids = tuple(scene_ids)
    existing_map = {s.scene_id: s for s in story.scenes}

    if len(requested_ids) != len(story.scenes):
        raise ReplayProcessingException(
            ReplayErrorCode.INVALID_ORDER,
            f"Requested {len(requested_ids)} scene IDs but story has {len(story.scenes)} scenes",
        )

    if set(requested_ids) != set(existing_map.keys()):
        raise ReplayProcessingException(
            ReplayErrorCode.INVALID_ORDER,
            "Requested scene IDs do not match existing story scenes",
        )

    new_scenes: list[ContentScene] = []
    for new_idx, s_id in enumerate(requested_ids):
        orig_s = existing_map[s_id]
        updated_s = ContentScene(
            scene_id=orig_s.scene_id,
            scene_type=orig_s.scene_type,
            title=orig_s.title,
            subtitle=orig_s.subtitle,
            description=orig_s.description,
            order_index=new_idx,
            priority=orig_s.priority,
            moment_id=orig_s.moment_id,
            season_id=orig_s.season_id,
            source_references=orig_s.source_references,
            script_segment_ids=orig_s.script_segment_ids,
            presentation_references=orig_s.presentation_references,
        )
        new_scenes.append(updated_s)

    return ContentStory(
        content_story_id=story.content_story_id,
        career_id=story.career_id,
        title=story.title,
        scenes=tuple(new_scenes),
        total_scenes=story.total_scenes,
        estimated_duration_seconds=story.estimated_duration_seconds,
        source_story_id=story.source_story_id,
        source_script_id=story.source_script_id,
    )


def build_capture_frame(
    scene: ContentScene,
    replay: CareerReplay,
    preset_type: CapturePresetType | str = CapturePresetType.CINEMATIC,
    story_script: StoryScript | None = None,
) -> CaptureFrame:
    if isinstance(preset_type, str):
        preset_type = CapturePresetType(preset_type)

    rules = load_replay_rules()
    preset_configs = rules.get("presets", {}).get(preset_type.value, {})

    preset = CapturePreset(
        preset_id=f"preset_{preset_type.value.lower()}",
        preset_type=preset_type,
        width=rules.get("capture", {}).get("default_width", 1920),
        height=rules.get("capture", {}).get("default_height", 1080),
        show_navigation=preset_configs.get("show_navigation", False),
        show_controls=preset_configs.get("show_controls", False),
        show_branding=preset_configs.get("show_branding", True),
        show_statistics=preset_configs.get("show_statistics", True),
        show_player_identity=preset_configs.get("show_player_identity", True),
        show_season=preset_configs.get("show_season", True),
    )

    player_name = replay.player_name
    season_label = scene.season_id or (replay.seasons[0].season_id if replay.seasons else "2026/27")
    club_name = replay.seasons[0].club_name if replay.seasons else "FC Barcelona"

    matched_season = next((s for s in replay.seasons if s.season_id == scene.season_id), None)
    if matched_season:
        club_name = matched_season.club_name

    headline = scene.title
    subheadline = scene.description

    stats_dict: dict[str, Any] = {
        "OVR": matched_season.ovr if matched_season else 80,
        "Appearances": matched_season.appearances if matched_season else 0,
        "Goals": matched_season.goals if matched_season else 0,
        "Assists": matched_season.assists if matched_season else 0,
    }

    script_text: str | None = None
    if story_script and scene.script_segment_ids:
        for sec in story_script.sections:
            for seg in sec.segments:
                if seg.segment_id in scene.script_segment_ids:
                    script_text = seg.text
                    break

    frame_id = _hash_id("frame", scene.scene_id, preset_type.value)

    return CaptureFrame(
        frame_id=frame_id,
        scene_id=scene.scene_id,
        preset=preset,
        player_name=player_name,
        club_name=club_name,
        season=season_label,
        headline=headline,
        subheadline=subheadline,
        statistics=MappingProxyType(stats_dict),
        visual_priority=scene.priority,
        script_text=script_text,
        metadata=MappingProxyType({"career_id": replay.career_id}),
    )


def validate_career_replay(replay: CareerReplay) -> tuple[str, ...]:
    errors: list[str] = []
    if not replay.career_id:
        errors.append("Career replay missing career_id")
    if not replay.player_name:
        errors.append("Career replay missing player_name")
    return tuple(errors)


def validate_content_story(
    story: ContentStory, replay: CareerReplay | None = None
) -> tuple[str, ...]:
    errors: list[str] = []
    if not story.content_story_id:
        errors.append("Content story missing content_story_id")
    if story.total_scenes != len(story.scenes):
        errors.append("Content story scene count mismatch")
    return tuple(errors)
