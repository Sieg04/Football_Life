import hashlib
import json
import math
from dataclasses import dataclass
from types import MappingProxyType
from typing import Any, Sequence

from app.event.career_domain import (
    ArcStatus,
    ArcType,
    CareerArc,
    CareerErrorCode,
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
    RelationshipStatus,
    RelationshipType,
    SeedPriority,
    TurningPointType,
)
from app.event.decisions import DecisionResult
from app.event.domain import EventContext, EventType
from app.event.effects import EffectApplicationResult
from app.event.resolution import EventResolution


class CareerProcessingException(Exception):
    def __init__(self, code: CareerErrorCode, message: str, details: dict[str, Any] | None = None) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.details = details or {}


CATEGORY_BASE_WEIGHTS: dict[EventCategory, float] = {
    EventCategory.TROPHY: 40.0,
    EventCategory.AWARD: 35.0,
    EventCategory.RETIREMENT: 50.0,
    EventCategory.TRANSFER: 30.0,
    EventCategory.DEBUT: 25.0,
    EventCategory.BREAKTHROUGH: 30.0,
    EventCategory.SETBACK: 25.0,
    EventCategory.INJURY: 20.0,
    EventCategory.PROMOTION: 25.0,
    EventCategory.RELEGATION: 25.0,
    EventCategory.INTERNATIONAL: 20.0,
    EventCategory.CONTRACT: 15.0,
    EventCategory.GOAL: 10.0,
    EventCategory.ASSIST: 8.0,
    EventCategory.RECOVERY: 15.0,
    EventCategory.RIVALRY: 20.0,
    EventCategory.CONTROVERSY: 20.0,
    EventCategory.FORM_CHANGE: 10.0,
    EventCategory.PERFORMANCE: 10.0,
    EventCategory.RELATIONSHIP: 10.0,
    EventCategory.DECISION: 10.0,
    EventCategory.APPEARANCE: 5.0,
    EventCategory.OTHER: 5.0,
}


def derive_event_category(
    event_type: EventType | str,
    metadata: MappingProxyType | dict,
    event_id_str: str = "",
) -> EventCategory:
    if "category" in metadata and metadata["category"]:
        try:
            return EventCategory(str(metadata["category"]))
        except ValueError:
            pass

    event_id_lower = event_id_str.lower()
    type_str = str(event_type).upper()

    if "trophy" in event_id_lower or "title" in event_id_lower or "champion" in event_id_lower:
        return EventCategory.TROPHY
    if "award" in event_id_lower or "ballon" in event_id_lower or "player_of_year" in event_id_lower:
        return EventCategory.AWARD
    if "transfer" in event_id_lower or type_str == "TRANSFER":
        return EventCategory.TRANSFER
    if "debut" in event_id_lower:
        return EventCategory.DEBUT
    if "contract" in event_id_lower:
        return EventCategory.CONTRACT
    if "injury" in event_id_lower or "injured" in event_id_lower:
        return EventCategory.INJURY
    if "recovery" in event_id_lower or "recovered" in event_id_lower:
        return EventCategory.RECOVERY
    if "goal" in event_id_lower:
        return EventCategory.GOAL
    if "assist" in event_id_lower:
        return EventCategory.ASSIST
    if "retirement" in event_id_lower or "retire" in event_id_lower:
        return EventCategory.RETIREMENT
    if "breakthrough" in event_id_lower:
        return EventCategory.BREAKTHROUGH
    if "setback" in event_id_lower:
        return EventCategory.SETBACK
    if "rivalry" in event_id_lower:
        return EventCategory.RIVALRY
    if "controversy" in event_id_lower:
        return EventCategory.CONTROVERSY
    if "promotion" in event_id_lower:
        return EventCategory.PROMOTION
    if "relegation" in event_id_lower:
        return EventCategory.RELEGATION

    return EventCategory.OTHER


def derive_event_significance(
    category: EventCategory,
    metadata: MappingProxyType | dict = MappingProxyType({}),
    state_changes: MappingProxyType | dict = MappingProxyType({}),
) -> EventSignificance:
    if "significance" in metadata and metadata["significance"]:
        try:
            return EventSignificance(str(metadata["significance"]))
        except ValueError:
            pass

    score = CATEGORY_BASE_WEIGHTS.get(category, 10.0)

    # State change magnitude impact
    for key, val in state_changes.items():
        if isinstance(val, (int, float)) and not isinstance(val, bool):
            score += abs(val) * 1.5

    # Metadata weight factors
    if "impact" in metadata and isinstance(metadata["impact"], (int, float)):
        score += float(metadata["impact"]) * 10.0
    if "priority" in metadata and isinstance(metadata["priority"], (int, float)):
        score += float(metadata["priority"]) * 0.2

    if score < 15.0:
        return EventSignificance.TRIVIAL
    if score < 30.0:
        return EventSignificance.MINOR
    if score < 55.0:
        return EventSignificance.MODERATE
    if score < 75.0:
        return EventSignificance.MAJOR
    if score < 90.0:
        return EventSignificance.CRITICAL
    return EventSignificance.LEGENDARY


def record_career_event(
    career_record: CareerRecord,
    source_event: Any,
    simulation_state: Any = None,
    context: EventContext | None = None,
) -> CareerRecord:
    if not isinstance(career_record, CareerRecord):
        raise CareerProcessingException(
            CareerErrorCode.INVALID_CAREER_RECORD,
            f"Expected CareerRecord, got {type(career_record)}",
        )
    if source_event is None:
        raise CareerProcessingException(
            CareerErrorCode.INVALID_EVENT,
            "source_event cannot be None",
        )

    # Extract source event ID and properties cleanly
    source_event_id = None
    event_type = EventType.PLAYER
    season = "1"
    metadata = {}
    summary_data = {}
    state_changes = {}
    participants = []
    clubs = []
    competitions = []
    tags = []

    if isinstance(source_event, EventResolution):
        source_event_id = source_event.event_instance_id or source_event.event_id
        metadata = dict(source_event.metadata)
        summary_data["outcome_id"] = source_event.outcome_id
        summary_data["outcome_label"] = source_event.outcome_label
        summary_data["status"] = source_event.status.value
    elif isinstance(source_event, DecisionResult):
        source_event_id = source_event.decision_id
        metadata = dict(source_event.metadata)
        summary_data["selected_option"] = source_event.selected_option.id if source_event.selected_option else None
        summary_data["resolution_type"] = source_event.resolution_type.value
    elif isinstance(source_event, EffectApplicationResult):
        source_event_id = metadata.get("event_id", f"eff_res_{len(career_record.events) + 1}")
        metadata = dict(source_event.metadata)
        for app in source_event.applications:
            state_changes[app.target] = app.resulting_value
    elif hasattr(source_event, "source_event_id") or hasattr(source_event, "event_id") or hasattr(source_event, "id"):
        source_event_id = getattr(source_event, "source_event_id", None) or getattr(source_event, "event_id", None) or getattr(source_event, "id", None)
        if hasattr(source_event, "event_type"):
            event_type = getattr(source_event, "event_type")
        if hasattr(source_event, "season"):
            season = str(getattr(source_event, "season"))
        if hasattr(source_event, "metadata"):
            metadata = dict(getattr(source_event, "metadata", {}))
        elif hasattr(source_event, "summary_data"):
            summary_data = dict(getattr(source_event, "summary_data", {}))
        if hasattr(source_event, "state_changes"):
            state_changes = dict(getattr(source_event, "state_changes", {}))
    elif isinstance(source_event, dict):
        source_event_id = source_event.get("id") or source_event.get("source_event_id")
        event_type = source_event.get("event_type", EventType.PLAYER)
        season = str(source_event.get("season", "1"))
        metadata = dict(source_event.get("metadata", {}))
        summary_data = dict(source_event.get("summary_data", {}))
        state_changes = dict(source_event.get("state_changes", {}))

    if not source_event_id:
        raise CareerProcessingException(
            CareerErrorCode.INVALID_EVENT,
            "Could not determine deterministic source_event_id from source_event",
        )

    # Idempotency check: if source_event_id already recorded, return unchanged record
    for ev in career_record.events:
        if ev.source_event_id == source_event_id:
            return career_record

    if context:
        if context.season is not None:
            season = str(context.season)
        if context.club_id:
            clubs.append(context.club_id)
        if context.competition_id:
            competitions.append(context.competition_id)
        if context.player_id and context.player_id != career_record.player_id:
            participants.append(context.player_id)

    if "club_id" in metadata and metadata["club_id"]:
        clubs.append(str(metadata["club_id"]))
    if "competition_id" in metadata and metadata["competition_id"]:
        competitions.append(str(metadata["competition_id"]))
    if "participant_id" in metadata and metadata["participant_id"]:
        participants.append(str(metadata["participant_id"]))

    for k, v in metadata.items():
        if k not in summary_data:
            summary_data[k] = v

    category = derive_event_category(event_type, metadata, source_event_id)
    significance = derive_event_significance(category, metadata, state_changes)

    next_seq = career_record.last_sequence + 1
    raw_key = f"{career_record.player_id}:{source_event_id}:{next_seq}"
    career_event_id = f"ce_{hashlib.sha256(raw_key.encode('utf-8')).hexdigest()[:16]}"

    new_event = CareerEvent(
        event_id=career_event_id,
        source_event_id=source_event_id,
        player_id=career_record.player_id,
        season=season,
        sequence=next_seq,
        event_type=event_type,
        category=category,
        significance=significance,
        summary_data=MappingProxyType(summary_data),
        state_changes=MappingProxyType(state_changes),
        participants=tuple(sorted(set(participants))),
        clubs=tuple(sorted(set(clubs))),
        competitions=tuple(sorted(set(competitions))),
        tags=tuple(sorted(set(tags))),
    )

    new_events = career_record.events + (new_event,)
    # Sort events deterministically by season, sequence, event_id
    sorted_events = tuple(sorted(new_events, key=lambda e: (str(e.season), e.sequence, e.event_id)))

    return CareerRecord(
        player_id=career_record.player_id,
        events=sorted_events,
        milestones=career_record.milestones,
        relationships=career_record.relationships,
        turning_points=career_record.turning_points,
        arcs=career_record.arcs,
        narrative_seeds=career_record.narrative_seeds,
        last_sequence=next_seq,
    )


UNIQUE_MILESTONES = {
    MilestoneType.FIRST_TEAM_DEBUT,
    MilestoneType.FIRST_GOAL,
    MilestoneType.FIRST_ASSIST,
    MilestoneType.FIRST_TRANSFER,
    MilestoneType.FIRST_INTERNATIONAL_APPEARANCE,
    MilestoneType.FIRST_TROPHY,
    MilestoneType.FIRST_MAJOR_AWARD,
    MilestoneType.RETIREMENT,
}


def detect_milestones(
    career_record: CareerRecord,
    simulation_state: Any = None,
) -> CareerRecord:
    if not isinstance(career_record, CareerRecord):
        raise CareerProcessingException(
            CareerErrorCode.INVALID_CAREER_RECORD,
            f"Expected CareerRecord, got {type(career_record)}",
        )

    existing_types = {m.milestone_type for m in career_record.milestones}
    existing_milestone_keys = {f"{m.milestone_type}:{m.value}" for m in career_record.milestones}
    new_milestones: list[CareerMilestone] = list(career_record.milestones)

    # Accumulate stats from all events
    total_goals = 0
    total_apps = 0

    for ev in career_record.events:
        # Check explicit milestone metadata or category
        candidate_type: MilestoneType | None = None

        if "milestone_type" in ev.summary_data:
            try:
                candidate_type = MilestoneType(str(ev.summary_data["milestone_type"]))
            except ValueError:
                pass
        elif "milestone_type" in ev.summary_data.get("metadata", {}):
            try:
                candidate_type = MilestoneType(str(ev.summary_data["metadata"]["milestone_type"]))
            except ValueError:
                pass

        if candidate_type is None:
            if ev.category == EventCategory.DEBUT:
                candidate_type = MilestoneType.FIRST_TEAM_DEBUT
            elif ev.category == EventCategory.GOAL and MilestoneType.FIRST_GOAL not in existing_types and total_goals == 0:
                candidate_type = MilestoneType.FIRST_GOAL
            elif ev.category == EventCategory.ASSIST and MilestoneType.FIRST_ASSIST not in existing_types:
                candidate_type = MilestoneType.FIRST_ASSIST
            elif ev.category == EventCategory.TRANSFER and MilestoneType.FIRST_TRANSFER not in existing_types:
                candidate_type = MilestoneType.FIRST_TRANSFER
            elif ev.category == EventCategory.INTERNATIONAL and MilestoneType.FIRST_INTERNATIONAL_APPEARANCE not in existing_types:
                candidate_type = MilestoneType.FIRST_INTERNATIONAL_APPEARANCE
            elif ev.category == EventCategory.TROPHY and MilestoneType.FIRST_TROPHY not in existing_types:
                candidate_type = MilestoneType.FIRST_TROPHY
            elif ev.category == EventCategory.AWARD and MilestoneType.FIRST_MAJOR_AWARD not in existing_types:
                candidate_type = MilestoneType.FIRST_MAJOR_AWARD
            elif ev.category == EventCategory.RETIREMENT:
                candidate_type = MilestoneType.RETIREMENT

        if ev.category == EventCategory.GOAL:
            total_goals += 1
        if ev.category in (EventCategory.APPEARANCE, EventCategory.DEBUT, EventCategory.GOAL, EventCategory.ASSIST):
            total_apps += 1

        if candidate_type is not None:
            if candidate_type in UNIQUE_MILESTONES and candidate_type in existing_types:
                continue

            ms_key = f"{candidate_type}:{ev.event_id}"
            if ms_key not in existing_milestone_keys:
                raw_key = f"{career_record.player_id}:{candidate_type.value}:{ev.event_id}"
                ms_id = f"ms_{hashlib.sha256(raw_key.encode('utf-8')).hexdigest()[:16]}"

                club_id = ev.clubs[0] if ev.clubs else None
                comp_id = ev.competitions[0] if ev.competitions else None

                ms = CareerMilestone(
                    milestone_id=ms_id,
                    milestone_type=candidate_type,
                    player_id=career_record.player_id,
                    season=ev.season,
                    sequence=ev.sequence,
                    event_id=ev.event_id,
                    club_id=club_id,
                    competition_id=comp_id,
                    value=None,
                    significance=ev.significance,
                )
                new_milestones.append(ms)
                existing_types.add(candidate_type)
                existing_milestone_keys.add(ms_key)

    # Threshold milestones checks
    latest_ev = career_record.events[-1] if career_record.events else None
    season = latest_ev.season if latest_ev else "1"
    seq = latest_ev.sequence if latest_ev else 0
    ev_id = latest_ev.event_id if latest_ev else None

    threshold_checks = [
        (total_apps >= 100, MilestoneType.APPEARANCES_100, 100),
        (total_goals >= 50, MilestoneType.GOALS_50, 50),
        (total_goals >= 100, MilestoneType.GOALS_100, 100),
    ]

    for cond, ms_type, val in threshold_checks:
        if cond and ms_type not in existing_types:
            raw_key = f"{career_record.player_id}:{ms_type.value}:{val}"
            ms_id = f"ms_{hashlib.sha256(raw_key.encode('utf-8')).hexdigest()[:16]}"
            ms = CareerMilestone(
                milestone_id=ms_id,
                milestone_type=ms_type,
                player_id=career_record.player_id,
                season=season,
                sequence=seq,
                event_id=ev_id,
                value=val,
                significance=EventSignificance.MAJOR,
            )
            new_milestones.append(ms)
            existing_types.add(ms_type)

    sorted_milestones = tuple(sorted(new_milestones, key=lambda m: (str(m.season), m.sequence, m.milestone_id)))

    return CareerRecord(
        player_id=career_record.player_id,
        events=career_record.events,
        milestones=sorted_milestones,
        relationships=career_record.relationships,
        turning_points=career_record.turning_points,
        arcs=career_record.arcs,
        narrative_seeds=career_record.narrative_seeds,
        last_sequence=career_record.last_sequence,
    )


def generate_narrative_seeds(
    career_record: CareerRecord,
    simulation_state: Any = None,
) -> CareerRecord:
    if not isinstance(career_record, CareerRecord):
        raise CareerProcessingException(
            CareerErrorCode.INVALID_CAREER_RECORD,
            f"Expected CareerRecord, got {type(career_record)}",
        )

    existing_seed_ids = {s.seed_id for s in career_record.narrative_seeds}
    seeds: list[NarrativeSeed] = list(career_record.narrative_seeds)
    active_arc = next((a for a in career_record.arcs if a.status == ArcStatus.ACTIVE), None)
    arc_id = active_arc.arc_id if active_arc else None

    # 1. Milestone-driven narrative seeds
    for ms in career_record.milestones:
        raw_key = f"seed_ms_{ms.milestone_id}"
        seed_id = f"ns_{hashlib.sha256(raw_key.encode('utf-8')).hexdigest()[:16]}"
        if seed_id not in existing_seed_ids:
            s_type = NarrativeSeedType.TRIUMPH
            priority = SeedPriority.HIGH if ms.significance in (EventSignificance.MAJOR, EventSignificance.CRITICAL, EventSignificance.LEGENDARY) else SeedPriority.MEDIUM
            if ms.milestone_type in (MilestoneType.FIRST_TEAM_DEBUT, MilestoneType.FIRST_GOAL):
                s_type = NarrativeSeedType.BREAKTHROUGH
            elif ms.milestone_type == MilestoneType.FIRST_TRANSFER:
                s_type = NarrativeSeedType.TRANSFER
            elif ms.milestone_type == MilestoneType.RETIREMENT:
                s_type = NarrativeSeedType.RETIREMENT
                priority = SeedPriority.CRITICAL

            ns = NarrativeSeed(
                seed_id=seed_id,
                seed_type=s_type,
                priority=priority,
                player_id=career_record.player_id,
                sequence=ms.sequence,
                event_ids=(ms.event_id,) if ms.event_id else (),
                milestone_ids=(ms.milestone_id,),
                relationship_ids=(),
                arc_id=arc_id,
                emotional_direction="POSITIVE" if s_type != NarrativeSeedType.FAILURE else "NEGATIVE",
                factual_context=ms.metadata,
                narrative_weight=2.0 if priority in (SeedPriority.HIGH, SeedPriority.CRITICAL) else 1.0,
            )
            seeds.append(ns)
            existing_seed_ids.add(seed_id)

    # 2. Turning-point-driven narrative seeds
    for tp in career_record.turning_points:
        raw_key = f"seed_tp_{tp.turning_point_id}"
        seed_id = f"ns_{hashlib.sha256(raw_key.encode('utf-8')).hexdigest()[:16]}"
        if seed_id not in existing_seed_ids:
            s_type = NarrativeSeedType.BREAKTHROUGH
            priority = SeedPriority.HIGH
            emo = "POSITIVE"

            if tp.turning_point_type == TurningPointType.SERIOUS_SETBACK:
                s_type = NarrativeSeedType.FAILURE
                emo = "NEGATIVE"
            elif tp.turning_point_type == TurningPointType.CAREER_RECOVERY:
                s_type = NarrativeSeedType.COMEBACK
                emo = "POSITIVE"
            elif tp.turning_point_type == TurningPointType.MAJOR_TRANSFER:
                s_type = NarrativeSeedType.TRANSFER
                priority = SeedPriority.HIGH
            elif tp.turning_point_type == TurningPointType.RETIREMENT_DECISION:
                s_type = NarrativeSeedType.LEGACY
                priority = SeedPriority.CRITICAL

            ns = NarrativeSeed(
                seed_id=seed_id,
                seed_type=s_type,
                priority=priority,
                player_id=career_record.player_id,
                sequence=tp.sequence,
                event_ids=(tp.source_event_id,) if tp.source_event_id else (),
                milestone_ids=(),
                relationship_ids=(),
                arc_id=arc_id,
                emotional_direction=emo,
                factual_context=tp.summary_data,
                narrative_weight=2.5,
            )
            seeds.append(ns)
            existing_seed_ids.add(seed_id)

    # 3. Relationship / Rivalry seeds
    for rel in career_record.relationships:
        if rel.relationship_type == RelationshipType.RIVAL or rel.strength <= -0.5:
            raw_key = f"seed_rel_{rel.relationship_id}_{rel.last_updated_sequence}"
            seed_id = f"ns_{hashlib.sha256(raw_key.encode('utf-8')).hexdigest()[:16]}"
            if seed_id not in existing_seed_ids:
                ns = NarrativeSeed(
                    seed_id=seed_id,
                    seed_type=NarrativeSeedType.RIVALRY,
                    priority=SeedPriority.HIGH if rel.strength <= -0.7 else SeedPriority.MEDIUM,
                    player_id=career_record.player_id,
                    sequence=rel.last_updated_sequence,
                    event_ids=rel.event_ids,
                    milestone_ids=(),
                    relationship_ids=(rel.relationship_id,),
                    arc_id=arc_id,
                    emotional_direction="TENSE",
                    factual_context=MappingProxyType({"target_entity": rel.target_entity, "strength": rel.strength}),
                    narrative_weight=1.5,
                )
                seeds.append(ns)
                existing_seed_ids.add(seed_id)

    PRIO_WEIGHT = {SeedPriority.CRITICAL: 4, SeedPriority.HIGH: 3, SeedPriority.MEDIUM: 2, SeedPriority.LOW: 1}
    sorted_seeds = tuple(sorted(seeds, key=lambda s: (-PRIO_WEIGHT[s.priority], -s.narrative_weight, s.sequence, s.seed_id)))

    return CareerRecord(
        player_id=career_record.player_id,
        events=career_record.events,
        milestones=career_record.milestones,
        relationships=career_record.relationships,
        turning_points=career_record.turning_points,
        arcs=career_record.arcs,
        narrative_seeds=sorted_seeds,
        last_sequence=career_record.last_sequence,
    )


def process_career_event(
    career_record: CareerRecord,
    source_event: Any,
    simulation_state: Any = None,
    context: EventContext | None = None,
) -> CareerRecord:
    """
    Pure, atomic pipeline function to process a single simulation event into history:
    1. Record event
    2. Detect milestones
    3. Update relationships
    4. Detect turning points
    5. Update career arcs
    6. Generate narrative seeds
    """
    if not isinstance(career_record, CareerRecord):
        raise CareerProcessingException(
            CareerErrorCode.INVALID_CAREER_RECORD,
            f"Expected CareerRecord, got {type(career_record)}",
        )

    # Save initial state for atomic rollback guarantee
    initial_record = career_record

    try:
        r1 = record_career_event(career_record, source_event, simulation_state, context)
        # If event was duplicate, return r1 directly
        if len(r1.events) == len(career_record.events):
            return career_record

        r2 = detect_milestones(r1, simulation_state)
        r3 = update_relationships(r2, simulation_state)
        r4 = detect_turning_points(r3, simulation_state)
        r5 = update_career_arcs(r4, simulation_state)
        r6 = generate_narrative_seeds(r5, simulation_state)
        return r6
    except Exception as exc:
        if isinstance(exc, CareerProcessingException):
            raise exc
        raise CareerProcessingException(
            CareerErrorCode.PROCESSING_ERROR,
            f"Failed to process career event atomically: {str(exc)}",
        ) from exc


def process_career_events(
    career_record: CareerRecord,
    source_events: Sequence[Any],
    simulation_state: Any = None,
    context: EventContext | None = None,
) -> CareerRecord:
    """
    Batch process an ordered sequence of events into career history atomically and deterministically.
    """
    curr = career_record
    for ev in source_events:
        curr = process_career_event(curr, ev, simulation_state, context)
    return curr


def replay_career_history(
    player_id: str,
    source_events: Sequence[Any],
    simulation_state: Any = None,
    context: EventContext | None = None,
) -> CareerRecord:
    """
    Rebuild career history deterministically from an empty record using the sequence of events.
    """
    empty_record = CareerRecord(player_id=player_id)
    return process_career_events(empty_record, source_events, simulation_state, context)


def update_career_arcs(
    career_record: CareerRecord,
    simulation_state: Any = None,
) -> CareerRecord:
    if not isinstance(career_record, CareerRecord):
        raise CareerProcessingException(
            CareerErrorCode.INVALID_CAREER_RECORD,
            f"Expected CareerRecord, got {type(career_record)}",
        )

    arcs: list[CareerArc] = list(career_record.arcs)
    active_arc = next((a for a in arcs if a.status == ArcStatus.ACTIVE), None)

    # Determine required current arc type based on history
    has_retire = any(ev.category == EventCategory.RETIREMENT for ev in career_record.events)
    has_breakthrough = any(tp.turning_point_type == TurningPointType.BREAKTHROUGH for tp in career_record.turning_points)
    has_setback = any(tp.turning_point_type == TurningPointType.SERIOUS_SETBACK for tp in career_record.turning_points)
    has_recovery = any(tp.turning_point_type == TurningPointType.CAREER_RECOVERY for tp in career_record.turning_points)
    milestone_count = len(career_record.milestones)
    event_count = len(career_record.events)

    target_type = ArcType.ACADEMY_RISE
    if has_retire:
        target_type = ArcType.RETIREMENT
    elif has_setback and not has_recovery:
        target_type = ArcType.ADVERSITY
    elif has_recovery:
        target_type = ArcType.RECOVERY
    elif milestone_count >= 5 or event_count >= 20:
        target_type = ArcType.PEAK
    elif milestone_count >= 2 or event_count >= 10:
        target_type = ArcType.ESTABLISHMENT
    elif has_breakthrough or event_count >= 3:
        target_type = ArcType.BREAKTHROUGH

    all_event_ids = tuple(ev.event_id for ev in career_record.events)
    all_ms_ids = tuple(ms.milestone_id for ms in career_record.milestones)
    all_tp_ids = tuple(tp.turning_point_id for tp in career_record.turning_points)
    curr_seq = career_record.last_sequence

    if active_arc is None:
        raw_key = f"arc_{career_record.player_id}_{target_type.value}_0"
        arc_id = f"arc_{hashlib.sha256(raw_key.encode('utf-8')).hexdigest()[:16]}"
        initial_arc = CareerArc(
            arc_id=arc_id,
            arc_type=target_type,
            player_id=career_record.player_id,
            start_sequence=0,
            end_sequence=None,
            event_ids=all_event_ids,
            milestone_ids=all_ms_ids,
            turning_point_ids=all_tp_ids,
            significance=EventSignificance.MODERATE,
            status=ArcStatus.ACTIVE,
        )
        arcs.append(initial_arc)
    elif active_arc.arc_type != target_type:
        # Complete active arc and transition to new target arc
        completed_arc = CareerArc(
            arc_id=active_arc.arc_id,
            arc_type=active_arc.arc_type,
            player_id=active_arc.player_id,
            start_sequence=active_arc.start_sequence,
            end_sequence=curr_seq,
            event_ids=active_arc.event_ids,
            milestone_ids=active_arc.milestone_ids,
            turning_point_ids=active_arc.turning_point_ids,
            significance=active_arc.significance,
            status=ArcStatus.COMPLETED,
            metadata=active_arc.metadata,
        )
        arcs = [a if a.arc_id != active_arc.arc_id else completed_arc for a in arcs]

        raw_key = f"arc_{career_record.player_id}_{target_type.value}_{curr_seq}"
        new_arc_id = f"arc_{hashlib.sha256(raw_key.encode('utf-8')).hexdigest()[:16]}"
        new_arc = CareerArc(
            arc_id=new_arc_id,
            arc_type=target_type,
            player_id=career_record.player_id,
            start_sequence=curr_seq,
            end_sequence=None,
            event_ids=all_event_ids,
            milestone_ids=all_ms_ids,
            turning_point_ids=all_tp_ids,
            significance=EventSignificance.MAJOR if target_type in (ArcType.PEAK, ArcType.RETIREMENT) else EventSignificance.MODERATE,
            status=ArcStatus.ACTIVE,
        )
        arcs.append(new_arc)
    else:
        # Update active arc event/milestone/turning_point arrays
        updated_arc = CareerArc(
            arc_id=active_arc.arc_id,
            arc_type=active_arc.arc_type,
            player_id=active_arc.player_id,
            start_sequence=active_arc.start_sequence,
            end_sequence=None,
            event_ids=all_event_ids,
            milestone_ids=all_ms_ids,
            turning_point_ids=all_tp_ids,
            significance=active_arc.significance,
            status=ArcStatus.ACTIVE,
            metadata=active_arc.metadata,
        )
        arcs = [a if a.arc_id != active_arc.arc_id else updated_arc for a in arcs]

    sorted_arcs = tuple(sorted(arcs, key=lambda a: (a.start_sequence, a.arc_id)))

    return CareerRecord(
        player_id=career_record.player_id,
        events=career_record.events,
        milestones=career_record.milestones,
        relationships=career_record.relationships,
        turning_points=career_record.turning_points,
        arcs=sorted_arcs,
        narrative_seeds=career_record.narrative_seeds,
        last_sequence=career_record.last_sequence,
    )


def detect_turning_points(
    career_record: CareerRecord,
    simulation_state: Any = None,
) -> CareerRecord:
    if not isinstance(career_record, CareerRecord):
        raise CareerProcessingException(
            CareerErrorCode.INVALID_CAREER_RECORD,
            f"Expected CareerRecord, got {type(career_record)}",
        )

    existing_tp_ids = {tp.turning_point_id for tp in career_record.turning_points}
    existing_source_events = {tp.source_event_id for tp in career_record.turning_points}
    new_turning_points: list[CareerTurningPoint] = list(career_record.turning_points)

    for ev in career_record.events:
        if ev.source_event_id in existing_source_events:
            continue

        tp_type: TurningPointType | None = None

        if "turning_point_type" in ev.summary_data:
            try:
                tp_type = TurningPointType(str(ev.summary_data["turning_point_type"]))
            except ValueError:
                pass

        if tp_type is None:
            if ev.category == EventCategory.BREAKTHROUGH:
                tp_type = TurningPointType.BREAKTHROUGH
            elif ev.category == EventCategory.TRANSFER and ev.significance in (EventSignificance.MAJOR, EventSignificance.CRITICAL, EventSignificance.LEGENDARY):
                tp_type = TurningPointType.MAJOR_TRANSFER
            elif ev.category == EventCategory.SETBACK or (ev.category == EventCategory.INJURY and ev.significance in (EventSignificance.CRITICAL, EventSignificance.LEGENDARY)):
                tp_type = TurningPointType.SERIOUS_SETBACK
            elif ev.category == EventCategory.RECOVERY and ev.significance in (EventSignificance.MAJOR, EventSignificance.CRITICAL, EventSignificance.LEGENDARY):
                tp_type = TurningPointType.CAREER_RECOVERY
            elif ev.category == EventCategory.TROPHY and ev.significance in (EventSignificance.MAJOR, EventSignificance.CRITICAL, EventSignificance.LEGENDARY):
                tp_type = TurningPointType.MAJOR_TROPHY
            elif ev.category == EventCategory.RETIREMENT:
                tp_type = TurningPointType.RETIREMENT_DECISION
            elif ev.significance in (EventSignificance.CRITICAL, EventSignificance.LEGENDARY):
                tp_type = TurningPointType.BREAKTHROUGH

        if tp_type is not None:
            raw_key = f"tp_{career_record.player_id}_{ev.event_id}_{tp_type.value}"
            tp_id = f"tp_{hashlib.sha256(raw_key.encode('utf-8')).hexdigest()[:16]}"

            if tp_id not in existing_tp_ids:
                tp = CareerTurningPoint(
                    turning_point_id=tp_id,
                    turning_point_type=tp_type,
                    player_id=career_record.player_id,
                    season=ev.season,
                    sequence=ev.sequence,
                    source_event_id=ev.source_event_id,
                    significance=ev.significance,
                    summary_data=ev.summary_data,
                )
                new_turning_points.append(tp)
                existing_tp_ids.add(tp_id)
                existing_source_events.add(ev.source_event_id)

    sorted_tps = tuple(sorted(new_turning_points, key=lambda tp: (str(tp.season), tp.sequence, tp.turning_point_id)))

    return CareerRecord(
        player_id=career_record.player_id,
        events=career_record.events,
        milestones=career_record.milestones,
        relationships=career_record.relationships,
        turning_points=sorted_tps,
        arcs=career_record.arcs,
        narrative_seeds=career_record.narrative_seeds,
        last_sequence=career_record.last_sequence,
    )


def update_relationships(
    career_record: CareerRecord,
    simulation_state: Any = None,
) -> CareerRecord:
    if not isinstance(career_record, CareerRecord):
        raise CareerProcessingException(
            CareerErrorCode.INVALID_CAREER_RECORD,
            f"Expected CareerRecord, got {type(career_record)}",
        )

    rel_map: dict[str, CareerRelationship] = {r.relationship_id: r for r in career_record.relationships}

    for ev in career_record.events:
        # Evaluate relationship updates if participants, clubs, or relationship delta present
        participants = list(ev.participants)
        clubs = list(ev.clubs)

        target_entities: list[tuple[str, RelationshipType]] = []
        for p in participants:
            if p != career_record.player_id:
                target_entities.append((p, RelationshipType.TEAMMATE))
        for c in clubs:
            target_entities.append((c, RelationshipType.CLUB))

        delta = 0.0
        if "relationship_delta" in ev.summary_data:
            delta = float(ev.summary_data["relationship_delta"])
        elif "relationship_delta" in ev.state_changes:
            delta = float(ev.state_changes["relationship_delta"])
        elif isinstance(ev.summary_data.get("metadata"), (dict, MappingProxyType)) and "relationship_delta" in ev.summary_data["metadata"]:
            delta = float(ev.summary_data["metadata"]["relationship_delta"])
        elif ev.category in (EventCategory.RELATIONSHIP, EventCategory.RIVALRY):
            delta = 0.2 if ev.significance in (EventSignificance.MAJOR, EventSignificance.CRITICAL, EventSignificance.LEGENDARY) else 0.1
        elif ev.category == EventCategory.CONTROVERSY:
            delta = -0.3

        if not target_entities or delta == 0.0:
            continue

        for target_id, rel_type in target_entities:
            rel_id = f"rel_{career_record.player_id}_{target_id}"
            existing = rel_map.get(rel_id)

            if existing:
                new_strength = max(-1.0, min(1.0, round(existing.strength + delta, 4)))
                new_event_ids = existing.event_ids if ev.event_id in existing.event_ids else existing.event_ids + (ev.event_id,)
                # Check for rivalry emergence threshold
                r_type = RelationshipType.RIVAL if (existing.relationship_type == RelationshipType.RIVAL or (new_strength <= -0.5 and delta < 0)) else existing.relationship_type
                rel_map[rel_id] = CareerRelationship(
                    relationship_id=existing.relationship_id,
                    player_id=career_record.player_id,
                    source_entity=existing.source_entity,
                    target_entity=existing.target_entity,
                    relationship_type=r_type,
                    strength=new_strength,
                    status=existing.status,
                    start_sequence=existing.start_sequence,
                    last_updated_sequence=ev.sequence,
                    event_ids=new_event_ids,
                    metadata=existing.metadata,
                )
            else:
                initial_strength = max(-1.0, min(1.0, round(delta, 4)))
                r_type = RelationshipType.RIVAL if initial_strength <= -0.5 else rel_type
                rel_map[rel_id] = CareerRelationship(
                    relationship_id=rel_id,
                    player_id=career_record.player_id,
                    source_entity=career_record.player_id,
                    target_entity=target_id,
                    relationship_type=r_type,
                    strength=initial_strength,
                    status=RelationshipStatus.ACTIVE,
                    start_sequence=ev.sequence,
                    last_updated_sequence=ev.sequence,
                    event_ids=(ev.event_id,),
                )

    sorted_rels = tuple(sorted(rel_map.values(), key=lambda r: (r.relationship_type.value, r.target_entity, r.relationship_id)))

    return CareerRecord(
        player_id=career_record.player_id,
        events=career_record.events,
        milestones=career_record.milestones,
        relationships=sorted_rels,
        turning_points=career_record.turning_points,
        arcs=career_record.arcs,
        narrative_seeds=career_record.narrative_seeds,
        last_sequence=career_record.last_sequence,
    )
