import hashlib
import json
import os
from types import MappingProxyType
from typing import Any

from app.event.career_domain import (
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
    NarrativeSeed,
    NarrativeSeedType,
    RelationshipType,
    SeedPriority,
    TurningPointType,
)
from app.event.narrative_domain import (
    ActType,
    BeatType,
    ConflictStatus,
    ConflictType,
    EmotionalDirection,
    NarrativeAct,
    NarrativeBeat,
    NarrativeBuildResult,
    NarrativeConflict,
    NarrativeErrorCode,
    NarrativeFunction,
    NarrativePacing,
    NarrativeProtagonist,
    NarrativeStory,
    NarrativeTheme,
    NarrativeThread,
    NarrativeThreadType,
    OpeningStrategy,
    PremiseType,
    ResolutionType,
    StoryDensity,
    StoryPremise,
)


class NarrativeProcessingException(Exception):
    def __init__(self, code: NarrativeErrorCode, message: str) -> None:
        super().__init__(message)
        self.code = code
        self.message = message


_DEFAULT_CONFIG: dict[str, Any] | None = None


def load_default_narrative_config() -> dict[str, Any]:
    global _DEFAULT_CONFIG
    if _DEFAULT_CONFIG is not None:
        return _DEFAULT_CONFIG

    config_path = os.path.join(os.path.dirname(__file__), "..", "..", "data", "rules", "narrative.json")
    if os.path.exists(config_path):
        with open(config_path, "r", encoding="utf-8") as f:
            _DEFAULT_CONFIG = json.load(f)
    else:
        _DEFAULT_CONFIG = {
            "density_max_beats": {
                "COMPACT": 5,
                "STANDARD": 12,
                "DETAILED": 25,
                "COMPLETE": 1000,
            },
            "significance_weights": {
                "TRIVIAL": 0.1,
                "MINOR": 0.3,
                "MODERATE": 0.6,
                "MAJOR": 1.0,
                "CRITICAL": 1.5,
                "LEGENDARY": 2.0,
            },
            "seed_priority_weights": {
                "LOW": 0.2,
                "MEDIUM": 0.5,
                "HIGH": 0.8,
                "CRITICAL": 1.0,
            },
            "pacing_seconds_per_beat": 15.0,
            "opening_strategy_weights": {
                "CHRONOLOGICAL_ORIGIN": 1.0,
                "COLD_OPEN": 1.2,
                "MAJOR_ACHIEVEMENT": 1.3,
            },
        }
    return _DEFAULT_CONFIG


def _generate_deterministic_id(prefix: str, *components: Any) -> str:
    raw = ":".join(str(c) for c in components)
    h = hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]
    return f"{prefix}_{h}"


def _get_significance_weight(sig: EventSignificance, config: dict[str, Any]) -> float:
    weights = config.get("significance_weights", {})
    return float(weights.get(sig.value, 1.0))


def _get_seed_priority_weight(prio: SeedPriority, config: dict[str, Any]) -> float:
    weights = config.get("seed_priority_weights", {})
    return float(weights.get(prio.value, 0.5))


def select_narrative_events(
    career_record: CareerRecord,
    configuration: dict[str, Any] | None = None,
    density: StoryDensity = StoryDensity.STANDARD,
    target_duration_seconds: float | None = None,
) -> tuple[
    tuple[CareerEvent, ...],
    tuple[CareerMilestone, ...],
    tuple[CareerTurningPoint, ...],
    tuple[NarrativeSeed, ...],
]:
    config = configuration or load_default_narrative_config()

    if density == StoryDensity.COMPLETE and target_duration_seconds is None:
        return (
            career_record.events,
            career_record.milestones,
            career_record.turning_points,
            career_record.narrative_seeds,
        )

    max_beats = config.get("density_max_beats", {}).get(density.value, 12)
    if target_duration_seconds is not None:
        pacing_sec = config.get("pacing_seconds_per_beat", 15.0)
        target_max = max(1, int(target_duration_seconds / pacing_sec))
        max_beats = min(max_beats, target_max)

    # Calculate weights for events
    scored_events: list[tuple[float, int, CareerEvent]] = []
    for ev in career_record.events:
        score = _get_significance_weight(ev.significance, config)
        if ev.category in (EventCategory.DEBUT, EventCategory.TROPHY, EventCategory.AWARD, EventCategory.BREAKTHROUGH):
            score += 0.5
        scored_events.append((score, ev.sequence, ev))

    # Milestones score
    scored_milestones: list[tuple[float, int, CareerMilestone]] = []
    for ms in career_record.milestones:
        score = _get_significance_weight(ms.significance, config) + 0.5
        scored_milestones.append((score, ms.sequence, ms))

    # Turning points score
    scored_tp: list[tuple[float, int, CareerTurningPoint]] = []
    for tp in career_record.turning_points:
        score = _get_significance_weight(tp.significance, config) + 0.8
        scored_tp.append((score, tp.sequence, tp))

    # Seeds score
    scored_seeds: list[tuple[float, int, NarrativeSeed]] = []
    for ns in career_record.narrative_seeds:
        score = ns.narrative_weight + _get_seed_priority_weight(ns.priority, config)
        scored_seeds.append((score, ns.sequence, ns))

    # Sort deterministically (score desc, sequence asc)
    scored_events.sort(key=lambda x: (-x[0], x[1], x[2].event_id))
    scored_milestones.sort(key=lambda x: (-x[0], x[1], x[2].milestone_id))
    scored_tp.sort(key=lambda x: (-x[0], x[1], x[2].turning_point_id))
    scored_seeds.sort(key=lambda x: (-x[0], x[1], x[2].seed_id))

    selected_events = tuple(ev for _, _, ev in scored_events[:max_beats])
    selected_milestones = tuple(ms for _, _, ms in scored_milestones[:max_beats])
    selected_tp = tuple(tp for _, _, tp in scored_tp[:max_beats])
    selected_seeds = tuple(ns for _, _, ns in scored_seeds[:max_beats])

    return selected_events, selected_milestones, selected_tp, selected_seeds


def identify_story_premise(
    career_record: CareerRecord,
    configuration: dict[str, Any] | None = None,
) -> StoryPremise:
    if (
        not career_record.events
        and not career_record.milestones
        and not career_record.turning_points
        and not career_record.arcs
        and not career_record.relationships
        and not career_record.narrative_seeds
    ):
        return StoryPremise(
            premise_type=PremiseType.JOURNEY,
            protagonist_goal="Establish career",
            resolution_type=ResolutionType.ONGOING,
        )

    primary_arc_id = career_record.arcs[0].arc_id if career_record.arcs else None
    resolution_type = ResolutionType.ONGOING
    has_retired = (
        any(ev.category == EventCategory.RETIREMENT for ev in career_record.events)
        or any(ms.milestone_type == MilestoneType.RETIREMENT for ms in career_record.milestones)
    )
    if has_retired:
        resolution_type = ResolutionType.RETIREMENT

    # Check for Comeback
    has_injury = any(
        tp.turning_point_type in (TurningPointType.SERIOUS_SETBACK, TurningPointType.CAREER_DECLINE)
        for tp in career_record.turning_points
    )
    has_recovery = any(
        tp.turning_point_type in (TurningPointType.CAREER_RECOVERY, TurningPointType.BREAKTHROUGH)
        for tp in career_record.turning_points
    )
    if has_injury and has_recovery:
        return StoryPremise(
            premise_type=PremiseType.COMEBACK,
            primary_arc_id=primary_arc_id,
            protagonist_goal="Return to elite performance",
            resolution_type=ResolutionType.COMEBACK if not has_retired else ResolutionType.RETIREMENT,
            supporting_facts=MappingProxyType({"reason": "Injury followed by recovery"}),
        )

    # Check for Rivalry
    rivalries = [r for r in career_record.relationships if r.relationship_type == RelationshipType.RIVAL]
    if rivalries:
        return StoryPremise(
            premise_type=PremiseType.RIVALRY,
            primary_arc_id=primary_arc_id,
            central_conflict_id=rivalries[0].relationship_id,
            protagonist_goal="Overcome primary rival",
            resolution_type=resolution_type,
            supporting_facts=MappingProxyType({"rival": rivalries[0].target_entity}),
        )

    # Check for Triumph / Legacy
    trophies = [ms for ms in career_record.milestones if ms.milestone_type in (MilestoneType.FIRST_TROPHY, MilestoneType.FIRST_MAJOR_AWARD, MilestoneType.RECORD_BROKEN)]
    if len(trophies) >= 2 or any(ms.significance in (EventSignificance.CRITICAL, EventSignificance.LEGENDARY) for ms in trophies):
        p_type = PremiseType.LEGACY if has_retired else PremiseType.TRIUMPH
        return StoryPremise(
            premise_type=p_type,
            primary_arc_id=primary_arc_id,
            protagonist_goal="Achieve ultimate football greatness",
            resolution_type=ResolutionType.TRIUMPH if not has_retired else ResolutionType.LEGACY,
            supporting_facts=MappingProxyType({"trophy_count": len(trophies)}),
        )

    # Check for Rise / Underdog
    has_breakthrough = any(
        tp.turning_point_type == TurningPointType.BREAKTHROUGH
        for tp in career_record.turning_points
    ) or any(
        arc.arc_type in (ArcType.ACADEMY_RISE, ArcType.BREAKTHROUGH)
        for arc in career_record.arcs
    )
    if has_breakthrough:
        return StoryPremise(
            premise_type=PremiseType.RISE,
            primary_arc_id=primary_arc_id,
            protagonist_goal="Rise from academy to starting line-up",
            resolution_type=resolution_type,
            supporting_facts=MappingProxyType({"breakthrough": True}),
        )

    return StoryPremise(
        premise_type=PremiseType.JOURNEY,
        primary_arc_id=primary_arc_id,
        protagonist_goal="Build professional career",
        resolution_type=resolution_type,
    )


def build_narrative_protagonist(
    career_record: CareerRecord,
    player_state: Any = None,
) -> NarrativeProtagonist:
    player_id = career_record.player_id
    position = ""
    origin = ""
    if player_state:
        position = getattr(player_state, "primary_position", "")
        origin = getattr(player_state, "nationality", "")

    clubs: list[str] = []
    for ev in career_record.events:
        for c in ev.clubs:
            if c not in clubs:
                clubs.append(c)

    rel_targets = [r.target_entity for r in career_record.relationships]
    defining_evs = [
        ev.event_id for ev in career_record.events
        if ev.significance in (EventSignificance.MAJOR, EventSignificance.CRITICAL, EventSignificance.LEGENDARY)
    ]

    stage = "ACTIVE"
    if any(ev.category == EventCategory.RETIREMENT for ev in career_record.events):
        stage = "RETIRED"

    return NarrativeProtagonist(
        player_id=player_id,
        position=position,
        origin=origin,
        career_stage=stage,
        key_traits=("DETERMINED",) if len(career_record.events) > 5 else ("EMERGIN",),
        important_clubs=tuple(clubs),
        important_relationships=tuple(rel_targets),
        defining_events=tuple(defining_evs),
    )


def build_narrative_beats(
    career_record: CareerRecord,
    selected_events: tuple[CareerEvent, ...],
    selected_milestones: tuple[CareerMilestone, ...],
    selected_turning_points: tuple[CareerTurningPoint, ...],
    selected_seeds: tuple[NarrativeSeed, ...],
    configuration: dict[str, Any] | None = None,
) -> tuple[NarrativeBeat, ...]:
    config = configuration or load_default_narrative_config()
    beats: list[NarrativeBeat] = []

    # Map sequences to items
    seq_map: dict[int, dict[str, list[Any]]] = {}

    for ev in selected_events:
        seq_map.setdefault(ev.sequence, {}).setdefault("events", []).append(ev)
    for ms in selected_milestones:
        seq_map.setdefault(ms.sequence, {}).setdefault("milestones", []).append(ms)
    for tp in selected_turning_points:
        seq_map.setdefault(tp.sequence, {}).setdefault("turning_points", []).append(tp)
    for seed in selected_seeds:
        seq_map.setdefault(seed.sequence, {}).setdefault("seeds", []).append(seed)

    sorted_seqs = sorted(seq_map.keys())

    beat_index = 0
    for seq in sorted_seqs:
        items = seq_map[seq]
        evs = items.get("events", [])
        mss = items.get("milestones", [])
        tps = items.get("turning_points", [])
        seeds = items.get("seeds", [])

        # Determine beat type and narrative function
        beat_type = BeatType.FIRST_CHANCE
        narr_func = NarrativeFunction.SETUP
        emo_dir = EmotionalDirection.NEUTRAL
        importance = 1.0

        if tps:
            tp = tps[0]
            importance = max(importance, _get_significance_weight(tp.significance, config))
            if tp.turning_point_type == TurningPointType.BREAKTHROUGH:
                beat_type = BeatType.BREAKTHROUGH
                narr_func = NarrativeFunction.PAYOFF
                emo_dir = EmotionalDirection.TRIUMPH
            elif tp.turning_point_type in (TurningPointType.SERIOUS_SETBACK, TurningPointType.CAREER_DECLINE):
                beat_type = BeatType.SETBACK
                narr_func = NarrativeFunction.CONFLICT
                emo_dir = EmotionalDirection.LOSS
            elif tp.turning_point_type == TurningPointType.CAREER_RECOVERY:
                beat_type = BeatType.COMEBACK
                narr_func = NarrativeFunction.PAYOFF
                emo_dir = EmotionalDirection.HOPE

        elif mss:
            ms = mss[0]
            importance = max(importance, _get_significance_weight(ms.significance, config))
            if ms.milestone_type in (MilestoneType.FIRST_GOAL, MilestoneType.FIRST_TEAM_DEBUT):
                beat_type = BeatType.ORIGIN
                narr_func = NarrativeFunction.SETUP
                emo_dir = EmotionalDirection.POSITIVE
            elif ms.milestone_type in (MilestoneType.FIRST_TROPHY, MilestoneType.FIRST_MAJOR_AWARD):
                beat_type = BeatType.MAJOR_ACHIEVEMENT
                narr_func = NarrativeFunction.CLIMAX
                emo_dir = EmotionalDirection.TRIUMPH
            elif ms.milestone_type == MilestoneType.RETIREMENT:
                beat_type = BeatType.FINAL_CHAPTER
                narr_func = NarrativeFunction.RESOLUTION
                emo_dir = EmotionalDirection.BITTERSWEET

        elif evs:
            ev = evs[0]
            importance = max(importance, _get_significance_weight(ev.significance, config))
            if ev.category == EventCategory.DEBUT:
                beat_type = BeatType.FIRST_CHANCE
                narr_func = NarrativeFunction.SETUP
                emo_dir = EmotionalDirection.HOPE
            elif ev.category == EventCategory.RIVALRY:
                beat_type = BeatType.RIVAL_APPEARANCE
                narr_func = NarrativeFunction.CONFLICT
                emo_dir = EmotionalDirection.TENSION
            elif ev.category in (EventCategory.TROPHY, EventCategory.AWARD):
                beat_type = BeatType.MAJOR_ACHIEVEMENT
                narr_func = NarrativeFunction.PAYOFF
                emo_dir = EmotionalDirection.TRIUMPH

        if seeds:
            seed = seeds[0]
            try:
                emo_dir = EmotionalDirection(seed.emotional_direction)
            except ValueError:
                pass

        ev_ids = tuple(sorted([e.event_id for e in evs]))
        ms_ids = tuple(sorted([m.milestone_id for m in mss]))
        tp_ids = tuple(sorted([t.turning_point_id for t in tps]))
        seed_ids = tuple(sorted([s.seed_id for s in seeds]))

        beat_id = _generate_deterministic_id(
            "beat", career_record.player_id, seq, beat_index, ev_ids, ms_ids, tp_ids, seed_ids
        )

        beat = NarrativeBeat(
            beat_id=beat_id,
            beat_type=beat_type,
            sequence=seq,
            importance=importance,
            source_event_ids=ev_ids,
            source_milestone_ids=ms_ids,
            source_turning_point_ids=tp_ids,
            source_seed_ids=seed_ids,
            emotional_direction=emo_dir,
            narrative_function=narr_func,
            pacing=NarrativePacing.MODERATE,
            factual_context=MappingProxyType({"sequence": seq}),
        )
        beats.append(beat)
        beat_index += 1

    return tuple(beats)


def build_narrative_acts(
    career_record: CareerRecord,
    beats: tuple[NarrativeBeat, ...],
    configuration: dict[str, Any] | None = None,
) -> tuple[NarrativeAct, ...]:
    if not beats:
        act_id = _generate_deterministic_id("act", career_record.player_id, "empty")
        return (
            NarrativeAct(
                act_id=act_id,
                act_type=ActType.ORIGIN,
                sequence=0,
                title="Beginning",
                description="Early career steps",
                start_sequence=0,
                end_sequence=0,
                beat_ids=(),
            ),
        )

    # Divide beats into logical acts based on beat content
    acts: list[NarrativeAct] = []

    # Group beats by stage
    origin_beats = [b for b in beats if b.beat_type in (BeatType.ORIGIN, BeatType.INTRODUCTION, BeatType.FIRST_CHANCE)]
    breakthrough_beats = [b for b in beats if b.beat_type in (BeatType.EARLY_SUCCESS, BeatType.BREAKTHROUGH)]
    conflict_beats = [b for b in beats if b.beat_type in (BeatType.SETBACK, BeatType.CONFLICT, BeatType.CRISIS, BeatType.RIVAL_APPEARANCE)]
    peak_beats = [b for b in beats if b.beat_type in (BeatType.MAJOR_ACHIEVEMENT, BeatType.CLIMAX, BeatType.PEAK, BeatType.COMEBACK)]
    resolution_beats = [b for b in beats if b.beat_type in (BeatType.DECLINE, BeatType.FINAL_CHAPTER, BeatType.LEGACY)]

    act_idx = 0

    if origin_beats:
        b_ids = tuple(b.beat_id for b in origin_beats)
        acts.append(
            NarrativeAct(
                act_id=_generate_deterministic_id("act", career_record.player_id, act_idx, "ORIGIN"),
                act_type=ActType.ORIGIN,
                sequence=act_idx,
                title="Act I: Origins",
                description="The early beginnings",
                start_sequence=origin_beats[0].sequence,
                end_sequence=origin_beats[-1].sequence,
                beat_ids=b_ids,
            )
        )
        act_idx += 1

    if breakthrough_beats:
        b_ids = tuple(b.beat_id for b in breakthrough_beats)
        acts.append(
            NarrativeAct(
                act_id=_generate_deterministic_id("act", career_record.player_id, act_idx, "RISE"),
                act_type=ActType.RISE,
                sequence=act_idx,
                title="Act II: The Breakthrough",
                description="Rising up the ranks",
                start_sequence=breakthrough_beats[0].sequence,
                end_sequence=breakthrough_beats[-1].sequence,
                beat_ids=b_ids,
            )
        )
        act_idx += 1

    if conflict_beats:
        b_ids = tuple(b.beat_id for b in conflict_beats)
        acts.append(
            NarrativeAct(
                act_id=_generate_deterministic_id("act", career_record.player_id, act_idx, "CONFLICT"),
                act_type=ActType.CONFLICT,
                sequence=act_idx,
                title="Act III: Adversity",
                description="Facing trials and struggles",
                start_sequence=conflict_beats[0].sequence,
                end_sequence=conflict_beats[-1].sequence,
                beat_ids=b_ids,
            )
        )
        act_idx += 1

    if peak_beats:
        b_ids = tuple(b.beat_id for b in peak_beats)
        acts.append(
            NarrativeAct(
                act_id=_generate_deterministic_id("act", career_record.player_id, act_idx, "PEAK"),
                act_type=ActType.PEAK,
                sequence=act_idx,
                title="Act IV: Pinnacle",
                description="Reaching the top of the game",
                start_sequence=peak_beats[0].sequence,
                end_sequence=peak_beats[-1].sequence,
                beat_ids=b_ids,
            )
        )
        act_idx += 1

    if resolution_beats:
        b_ids = tuple(b.beat_id for b in resolution_beats)
        acts.append(
            NarrativeAct(
                act_id=_generate_deterministic_id("act", career_record.player_id, act_idx, "RESOLUTION"),
                act_type=ActType.RESOLUTION,
                sequence=act_idx,
                title="Act V: Final Chapter",
                description="Career conclusion and legacy",
                start_sequence=resolution_beats[0].sequence,
                end_sequence=resolution_beats[-1].sequence,
                beat_ids=b_ids,
            )
        )
        act_idx += 1

    # Fallback if beats didn't match the specific buckets
    if not acts:
        b_ids = tuple(b.beat_id for b in beats)
        acts.append(
            NarrativeAct(
                act_id=_generate_deterministic_id("act", career_record.player_id, 0, "JOURNEY"),
                act_type=ActType.SETUP,
                sequence=0,
                title="The Journey",
                description="Career development",
                start_sequence=beats[0].sequence,
                end_sequence=beats[-1].sequence,
                beat_ids=b_ids,
            )
        )

    return tuple(acts)


def build_narrative_threads(
    career_record: CareerRecord,
    beats: tuple[NarrativeBeat, ...],
    configuration: dict[str, Any] | None = None,
) -> tuple[NarrativeThread, ...]:
    threads: list[NarrativeThread] = []

    if beats:
        all_beat_ids = tuple(b.beat_id for b in beats)
        t_id = _generate_deterministic_id("thread", career_record.player_id, "rise")
        threads.append(
            NarrativeThread(
                thread_id=t_id,
                thread_type=NarrativeThreadType.CAREER_RISE,
                beat_ids=all_beat_ids,
                start_sequence=beats[0].sequence,
                end_sequence=beats[-1].sequence,
                importance=1.0,
                status="ACTIVE",
            )
        )

    # Check for rivalry thread
    rival_beats = [b for b in beats if b.beat_type == BeatType.RIVAL_APPEARANCE]
    if rival_beats:
        r_ids = tuple(b.beat_id for b in rival_beats)
        t_id = _generate_deterministic_id("thread", career_record.player_id, "rivalry")
        threads.append(
            NarrativeThread(
                thread_id=t_id,
                thread_type=NarrativeThreadType.RIVALRY,
                beat_ids=r_ids,
                start_sequence=rival_beats[0].sequence,
                end_sequence=rival_beats[-1].sequence,
                importance=0.8,
                status="ACTIVE",
            )
        )

    # Check for recovery thread
    recovery_beats = [b for b in beats if b.beat_type in (BeatType.SETBACK, BeatType.COMEBACK)]
    if recovery_beats:
        rec_ids = tuple(b.beat_id for b in recovery_beats)
        t_id = _generate_deterministic_id("thread", career_record.player_id, "recovery")
        threads.append(
            NarrativeThread(
                thread_id=t_id,
                thread_type=NarrativeThreadType.RECOVERY,
                beat_ids=rec_ids,
                start_sequence=recovery_beats[0].sequence,
                end_sequence=recovery_beats[-1].sequence,
                importance=0.9,
                status="RESOLVED" if any(b.beat_type == BeatType.COMEBACK for b in recovery_beats) else "ACTIVE",
            )
        )

    return tuple(threads)


def identify_narrative_conflicts(
    career_record: CareerRecord,
    beats: tuple[NarrativeBeat, ...],
    configuration: dict[str, Any] | None = None,
) -> tuple[NarrativeConflict, ...]:
    conflicts: list[NarrativeConflict] = []

    # Detect relationship conflicts
    for rel in career_record.relationships:
        if rel.relationship_type == RelationshipType.RIVAL or rel.strength < -0.3:
            c_id = _generate_deterministic_id("conflict", career_record.player_id, rel.relationship_id)
            ev_sources = tuple(rel.event_ids)
            conflicts.append(
                NarrativeConflict(
                    conflict_id=c_id,
                    conflict_type=ConflictType.RELATIONSHIP if rel.relationship_type != RelationshipType.RIVAL else ConflictType.COMPETITIVE,
                    source_events=ev_sources,
                    start_sequence=rel.start_sequence,
                    end_sequence=rel.last_updated_sequence if rel.status != "ACTIVE" else None,
                    intensity=abs(rel.strength),
                    resolution_status=ConflictStatus.RESOLVED if rel.status != "ACTIVE" else ConflictStatus.ESCALATING,
                )
            )

    # Detect injury setbacks
    injury_tps = [tp for tp in career_record.turning_points if tp.turning_point_type == TurningPointType.SERIOUS_SETBACK]
    for tp in injury_tps:
        c_id = _generate_deterministic_id("conflict", career_record.player_id, tp.turning_point_id)
        has_recovered = any(
            rec_tp.sequence > tp.sequence and rec_tp.turning_point_type == TurningPointType.CAREER_RECOVERY
            for rec_tp in career_record.turning_points
        )
        conflicts.append(
            NarrativeConflict(
                conflict_id=c_id,
                conflict_type=ConflictType.INJURY,
                source_events=(tp.source_event_id,),
                start_sequence=tp.sequence,
                intensity=1.2,
                resolution_status=ConflictStatus.RESOLVED if has_recovered else ConflictStatus.UNRESOLVED,
            )
        )

    return tuple(conflicts)


def select_story_opening(
    career_record: CareerRecord,
    beats: tuple[NarrativeBeat, ...],
    configuration: dict[str, Any] | None = None,
) -> tuple[OpeningStrategy, str | None]:
    if not beats:
        return OpeningStrategy.CHRONOLOGICAL_ORIGIN, None

    # Check for major achievement cold open
    major_beats = [b for b in beats if b.beat_type == BeatType.MAJOR_ACHIEVEMENT]
    if major_beats and len(beats) > 3:
        return OpeningStrategy.COLD_OPEN, major_beats[0].beat_id

    return OpeningStrategy.CHRONOLOGICAL_ORIGIN, beats[0].beat_id


def identify_story_climax(
    career_record: CareerRecord,
    beats: tuple[NarrativeBeat, ...],
    configuration: dict[str, Any] | None = None,
) -> str | None:
    climax_candidates = [
        b for b in beats
        if b.beat_type in (BeatType.MAJOR_ACHIEVEMENT, BeatType.CLIMAX, BeatType.BREAKTHROUGH, BeatType.COMEBACK)
    ]
    if not climax_candidates:
        return beats[-1].beat_id if beats else None

    # Pick beat with highest importance
    best_beat = max(climax_candidates, key=lambda b: (b.importance, b.sequence))
    return best_beat.beat_id


def build_story_resolution(
    career_record: CareerRecord,
    beats: tuple[NarrativeBeat, ...],
    configuration: dict[str, Any] | None = None,
) -> ResolutionType:
    has_retired = (
        any(ev.category == EventCategory.RETIREMENT for ev in career_record.events)
        or any(ms.milestone_type == MilestoneType.RETIREMENT for ms in career_record.milestones)
    )
    if not has_retired:
        return ResolutionType.ONGOING

    has_trophy = any(ms.milestone_type in (MilestoneType.FIRST_TROPHY, MilestoneType.FIRST_MAJOR_AWARD) for ms in career_record.milestones)
    if has_trophy:
        return ResolutionType.LEGACY
    return ResolutionType.RETIREMENT


def derive_narrative_themes(
    career_record: CareerRecord,
    beats: tuple[NarrativeBeat, ...],
    configuration: dict[str, Any] | None = None,
) -> tuple[NarrativeTheme, ...]:
    themes: list[NarrativeTheme] = []

    # Check PERSEVERANCE / ADVERSITY
    if any(b.beat_type in (BeatType.SETBACK, BeatType.COMEBACK) for b in beats):
        themes.append(NarrativeTheme.PERSEVERANCE)
        themes.append(NarrativeTheme.ADVERSITY)

    # Check RIVALRY
    if any(b.beat_type == BeatType.RIVAL_APPEARANCE for b in beats):
        themes.append(NarrativeTheme.RIVALRY)

    # Check SUCCESS / LEGACY
    if any(b.beat_type == BeatType.MAJOR_ACHIEVEMENT for b in beats):
        themes.append(NarrativeTheme.SUCCESS)

    has_retired = (
        any(ev.category == EventCategory.RETIREMENT for ev in career_record.events)
        or any(ms.milestone_type == MilestoneType.RETIREMENT for ms in career_record.milestones)
    )
    if has_retired:
        themes.append(NarrativeTheme.LEGACY)

    if not themes:
        themes.append(NarrativeTheme.AMBITION)

    return tuple(dict.fromkeys(themes))  # Deduplicate while preserving order


def validate_narrative_coherence(
    career_record: CareerRecord,
    story: NarrativeStory,
) -> None:
    # Check player_id match
    if story.player_id != career_record.player_id:
        raise NarrativeProcessingException(
            NarrativeErrorCode.NARRATIVE_VALIDATION_ERROR,
            f"Player ID mismatch: story '{story.player_id}' vs record '{career_record.player_id}'",
        )

    # Verify event IDs exist in record
    record_ev_ids = {ev.event_id for ev in career_record.events}
    record_ms_ids = {ms.milestone_id for ms in career_record.milestones}
    record_tp_ids = {tp.turning_point_id for tp in career_record.turning_points}
    record_seed_ids = {ns.seed_id for ns in career_record.narrative_seeds}

    for beat in story.narrative_beats:
        for ev_id in beat.source_event_ids:
            if ev_id not in record_ev_ids:
                raise NarrativeProcessingException(
                    NarrativeErrorCode.INVALID_EVENT_REFERENCE,
                    f"Beat '{beat.beat_id}' references unknown event '{ev_id}'",
                )
        for ms_id in beat.source_milestone_ids:
            if ms_id not in record_ms_ids:
                raise NarrativeProcessingException(
                    NarrativeErrorCode.INVALID_MILESTONE_REFERENCE,
                    f"Beat '{beat.beat_id}' references unknown milestone '{ms_id}'",
                )
        for tp_id in beat.source_turning_point_ids:
            if tp_id not in record_tp_ids:
                raise NarrativeProcessingException(
                    NarrativeErrorCode.INVALID_TURNING_POINT_REFERENCE,
                    f"Beat '{beat.beat_id}' references unknown turning point '{tp_id}'",
                )
        for seed_id in beat.source_seed_ids:
            if seed_id not in record_seed_ids:
                raise NarrativeProcessingException(
                    NarrativeErrorCode.INVALID_SEED_REFERENCE,
                    f"Beat '{beat.beat_id}' references unknown seed '{seed_id}'",
                )

    # Verify active player is not represented as retired resolution
    has_retired = (
        any(ev.category == EventCategory.RETIREMENT for ev in career_record.events)
        or any(ms.milestone_type == MilestoneType.RETIREMENT for ms in career_record.milestones)
    )
    if not has_retired and story.resolution_type in (ResolutionType.RETIREMENT, ResolutionType.LEGACY):
        raise NarrativeProcessingException(
            NarrativeErrorCode.NARRATIVE_VALIDATION_ERROR,
            "Active player cannot have RETIREMENT or LEGACY resolution",
        )


def build_narrative_story(
    career_record: CareerRecord,
    configuration: dict[str, Any] | None = None,
    target_duration_seconds: float | None = None,
    density: StoryDensity = StoryDensity.STANDARD,
    player_state: Any = None,
) -> NarrativeStory:
    if not isinstance(career_record, CareerRecord):
        raise NarrativeProcessingException(
            NarrativeErrorCode.INVALID_CAREER_RECORD,
            f"Expected CareerRecord, got {type(career_record)}",
        )

    config = configuration or load_default_narrative_config()

    sel_events, sel_ms, sel_tp, sel_seeds = select_narrative_events(
        career_record, config, density, target_duration_seconds
    )

    premise = identify_story_premise(career_record, config)
    protagonist = build_narrative_protagonist(career_record, player_state)
    beats = build_narrative_beats(career_record, sel_events, sel_ms, sel_tp, sel_seeds, config)
    acts = build_narrative_acts(career_record, beats, config)
    threads = build_narrative_threads(career_record, beats, config)
    conflicts = identify_narrative_conflicts(career_record, beats, config)
    op_strat, op_beat_id = select_story_opening(career_record, beats, config)
    climax_beat_id = identify_story_climax(career_record, beats, config)
    resolution_type = build_story_resolution(career_record, beats, config)
    themes = derive_narrative_themes(career_record, beats, config)

    featured_events = tuple(sorted([ev.event_id for ev in sel_events]))
    featured_ms = tuple(sorted([ms.milestone_id for ms in sel_ms]))
    featured_tp = tuple(sorted([tp.turning_point_id for tp in sel_tp]))
    featured_rels = tuple(sorted([rel.relationship_id for rel in career_record.relationships]))
    featured_arcs = tuple(sorted([arc.arc_id for arc in career_record.arcs]))

    story_id = _generate_deterministic_id(
        "story", career_record.player_id, density.value, len(beats), featured_events
    )

    story = NarrativeStory(
        story_id=story_id,
        player_id=career_record.player_id,
        title_context=f"The Story of Player {career_record.player_id}",
        premise=premise,
        protagonist=protagonist,
        density=density,
        target_duration_seconds=target_duration_seconds,
        opening_strategy=op_strat,
        opening_beat_id=op_beat_id,
        climax_beat_id=climax_beat_id,
        resolution_type=resolution_type,
        acts=acts,
        narrative_beats=beats,
        threads=threads,
        conflicts=conflicts,
        featured_events=featured_events,
        featured_relationships=featured_rels,
        featured_milestones=featured_ms,
        featured_turning_points=featured_tp,
        featured_arcs=featured_arcs,
        themes=themes,
    )

    validate_narrative_coherence(career_record, story)
    return story
