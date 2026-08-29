import math
from dataclasses import dataclass, field
from enum import StrEnum
from types import MappingProxyType
from typing import Any

from app.event.domain import (
    EventType,
    _is_valid_primitive,
    _to_immutable_mapping,
    _to_immutable_primitive,
)


class EventCategory(StrEnum):
    TRANSFER = "TRANSFER"
    CONTRACT = "CONTRACT"
    DEBUT = "DEBUT"
    APPEARANCE = "APPEARANCE"
    GOAL = "GOAL"
    ASSIST = "ASSIST"
    INJURY = "INJURY"
    RECOVERY = "RECOVERY"
    FORM_CHANGE = "FORM_CHANGE"
    PERFORMANCE = "PERFORMANCE"
    AWARD = "AWARD"
    TROPHY = "TROPHY"
    PROMOTION = "PROMOTION"
    RELEGATION = "RELEGATION"
    INTERNATIONAL = "INTERNATIONAL"
    RELATIONSHIP = "RELATIONSHIP"
    RIVALRY = "RIVALRY"
    CONTROVERSY = "CONTROVERSY"
    DECISION = "DECISION"
    BREAKTHROUGH = "BREAKTHROUGH"
    SETBACK = "SETBACK"
    RETIREMENT = "RETIREMENT"
    OTHER = "OTHER"


class EventSignificance(StrEnum):
    TRIVIAL = "TRIVIAL"
    MINOR = "MINOR"
    MODERATE = "MODERATE"
    MAJOR = "MAJOR"
    CRITICAL = "CRITICAL"
    LEGENDARY = "LEGENDARY"


class MilestoneType(StrEnum):
    FIRST_TEAM_DEBUT = "FIRST_TEAM_DEBUT"
    FIRST_GOAL = "FIRST_GOAL"
    FIRST_ASSIST = "FIRST_ASSIST"
    FIRST_TRANSFER = "FIRST_TRANSFER"
    FIRST_INTERNATIONAL_APPEARANCE = "FIRST_INTERNATIONAL_APPEARANCE"
    FIRST_TROPHY = "FIRST_TROPHY"
    FIRST_MAJOR_AWARD = "FIRST_MAJOR_AWARD"
    APPEARANCES_100 = "100_APPEARANCES"
    GOALS_50 = "50_GOALS"
    GOALS_100 = "100_GOALS"
    CLUB_CAPTAINCY = "CLUB_CAPTAINCY"
    NATIONAL_TEAM_CAPTAINCY = "NATIONAL_TEAM_CAPTAINCY"
    MAJOR_TRANSFER = "MAJOR_TRANSFER"
    RECORD_BROKEN = "RECORD_BROKEN"
    CAREER_BEST_SEASON = "CAREER_BEST_SEASON"
    RETIREMENT = "RETIREMENT"


class RelationshipType(StrEnum):
    TEAMMATE = "TEAMMATE"
    MANAGER = "MANAGER"
    MENTOR = "MENTOR"
    RIVAL = "RIVAL"
    FRIEND = "FRIEND"
    COMPETITOR = "COMPETITOR"
    CLUB = "CLUB"
    NATIONAL_TEAM = "NATIONAL_TEAM"


class RelationshipStatus(StrEnum):
    ACTIVE = "ACTIVE"
    HISTORIC = "HISTORIC"
    DORMANT = "DORMANT"


class TurningPointType(StrEnum):
    BREAKTHROUGH = "BREAKTHROUGH"
    MAJOR_TRANSFER = "MAJOR_TRANSFER"
    SERIOUS_SETBACK = "SERIOUS_SETBACK"
    CAREER_RECOVERY = "CAREER_RECOVERY"
    MAJOR_TROPHY = "MAJOR_TROPHY"
    LOSS_OF_STARTING_POSITION = "LOSS_OF_STARTING_POSITION"
    MANAGER_CHANGE = "MANAGER_CHANGE"
    INTERNATIONAL_BREAKTHROUGH = "INTERNATIONAL_BREAKTHROUGH"
    CAREER_DECLINE = "CAREER_DECLINE"
    RETIREMENT_DECISION = "RETIREMENT_DECISION"


class ArcType(StrEnum):
    ACADEMY_RISE = "ACADEMY_RISE"
    BREAKTHROUGH = "BREAKTHROUGH"
    ESTABLISHMENT = "ESTABLISHMENT"
    PEAK = "PEAK"
    ADVERSITY = "ADVERSITY"
    RECOVERY = "RECOVERY"
    DECLINE = "DECLINE"
    LATE_CAREER = "LATE_CAREER"
    RETIREMENT = "RETIREMENT"


class ArcStatus(StrEnum):
    ACTIVE = "ACTIVE"
    COMPLETED = "COMPLETED"
    SUPERSEDED = "SUPERSEDED"


class NarrativeSeedType(StrEnum):
    ORIGIN = "ORIGIN"
    BREAKTHROUGH = "BREAKTHROUGH"
    RIVALRY = "RIVALRY"
    TRIUMPH = "TRIUMPH"
    FAILURE = "FAILURE"
    COMEBACK = "COMEBACK"
    CONTROVERSY = "CONTROVERSY"
    TRANSFER = "TRANSFER"
    LOYALTY = "LOYALTY"
    BETRAYAL = "BETRAYAL"
    REDEMPTION = "REDEMPTION"
    PEAK = "PEAK"
    DECLINE = "DECLINE"
    LEGACY = "LEGACY"
    RETIREMENT = "RETIREMENT"


class SeedPriority(StrEnum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class CareerErrorCode(StrEnum):
    INVALID_CAREER_RECORD = "INVALID_CAREER_RECORD"
    INVALID_EVENT = "INVALID_EVENT"
    INVALID_PLAYER = "INVALID_PLAYER"
    INVALID_SEQUENCE = "INVALID_SEQUENCE"
    DUPLICATE_EVENT = "DUPLICATE_EVENT"
    INVALID_CONTEXT = "INVALID_CONTEXT"
    INVALID_RELATIONSHIP = "INVALID_RELATIONSHIP"
    INVALID_MILESTONE = "INVALID_MILESTONE"
    PROCESSING_ERROR = "PROCESSING_ERROR"


@dataclass(frozen=True)
class CareerEvent:
    event_id: str
    source_event_id: str
    player_id: str
    season: int | str
    sequence: int
    event_type: EventType
    category: EventCategory
    significance: EventSignificance
    summary_data: MappingProxyType = field(default_factory=lambda: MappingProxyType({}))
    state_changes: MappingProxyType = field(default_factory=lambda: MappingProxyType({}))
    participants: tuple[str, ...] = ()
    clubs: tuple[str, ...] = ()
    competitions: tuple[str, ...] = ()
    tags: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not isinstance(self.event_id, str) or not self.event_id.strip():
            raise ValueError("CareerEvent event_id must be a non-empty string")

        if not isinstance(self.source_event_id, str) or not self.source_event_id.strip():
            raise ValueError("CareerEvent source_event_id must be a non-empty string")

        if not isinstance(self.player_id, str) or not self.player_id.strip():
            raise ValueError("CareerEvent player_id must be a non-empty string")

        if isinstance(self.season, int):
            if self.season <= 0:
                raise ValueError(f"Season year must be positive, got {self.season}")
        elif isinstance(self.season, str):
            if not self.season.strip():
                raise ValueError("Season string cannot be empty")
        else:
            raise ValueError(f"Invalid season format: {type(self.season)}")

        if not isinstance(self.sequence, int) or isinstance(self.sequence, bool):
            raise ValueError("CareerEvent sequence must be an integer")
        if self.sequence < 0:
            raise ValueError("CareerEvent sequence must be non-negative")

        if isinstance(self.event_type, str):
            try:
                object.__setattr__(self, "event_type", EventType(self.event_type))
            except ValueError:
                raise ValueError(f"Invalid EventType: '{self.event_type}'")
        elif not isinstance(self.event_type, EventType):
            raise ValueError(f"Invalid EventType: '{self.event_type}'")

        if isinstance(self.category, str):
            try:
                object.__setattr__(self, "category", EventCategory(self.category))
            except ValueError:
                raise ValueError(f"Invalid EventCategory: '{self.category}'")
        elif not isinstance(self.category, EventCategory):
            raise ValueError(f"Invalid EventCategory: '{self.category}'")

        if isinstance(self.significance, str):
            try:
                object.__setattr__(self, "significance", EventSignificance(self.significance))
            except ValueError:
                raise ValueError(f"Invalid EventSignificance: '{self.significance}'")
        elif not isinstance(self.significance, EventSignificance):
            raise ValueError(f"Invalid EventSignificance: '{self.significance}'")

        object.__setattr__(self, "summary_data", _to_immutable_mapping(self.summary_data))
        object.__setattr__(self, "state_changes", _to_immutable_mapping(self.state_changes))

        if not isinstance(self.participants, tuple):
            object.__setattr__(self, "participants", tuple(self.participants))
        for p in self.participants:
            if not isinstance(p, str) or not p.strip():
                raise ValueError("participants must be non-empty strings")

        if not isinstance(self.clubs, tuple):
            object.__setattr__(self, "clubs", tuple(self.clubs))
        for c in self.clubs:
            if not isinstance(c, str) or not c.strip():
                raise ValueError("clubs must be non-empty strings")

        if not isinstance(self.competitions, tuple):
            object.__setattr__(self, "competitions", tuple(self.competitions))
        for comp in self.competitions:
            if not isinstance(comp, str) or not comp.strip():
                raise ValueError("competitions must be non-empty strings")

        if not isinstance(self.tags, tuple):
            object.__setattr__(self, "tags", tuple(self.tags))
        for t in self.tags:
            if not isinstance(t, str) or not t.strip():
                raise ValueError("tags must be non-empty strings")


@dataclass(frozen=True)
class CareerMilestone:
    milestone_id: str
    milestone_type: MilestoneType
    player_id: str
    season: int | str
    sequence: int
    event_id: str | None = None
    club_id: str | None = None
    competition_id: str | None = None
    value: float | int | str | None = None
    significance: EventSignificance = EventSignificance.MODERATE
    metadata: MappingProxyType = field(default_factory=lambda: MappingProxyType({}))

    def __post_init__(self) -> None:
        if not isinstance(self.milestone_id, str) or not self.milestone_id.strip():
            raise ValueError("CareerMilestone milestone_id must be a non-empty string")

        if isinstance(self.milestone_type, str):
            try:
                object.__setattr__(self, "milestone_type", MilestoneType(self.milestone_type))
            except ValueError:
                raise ValueError(f"Invalid MilestoneType: '{self.milestone_type}'")
        elif not isinstance(self.milestone_type, MilestoneType):
            raise ValueError(f"Invalid MilestoneType: '{self.milestone_type}'")

        if not isinstance(self.player_id, str) or not self.player_id.strip():
            raise ValueError("CareerMilestone player_id must be a non-empty string")

        if isinstance(self.season, int):
            if self.season <= 0:
                raise ValueError(f"Season year must be positive, got {self.season}")
        elif isinstance(self.season, str):
            if not self.season.strip():
                raise ValueError("Season string cannot be empty")
        else:
            raise ValueError(f"Invalid season format: {type(self.season)}")

        if not isinstance(self.sequence, int) or isinstance(self.sequence, bool):
            raise ValueError("CareerMilestone sequence must be an integer")
        if self.sequence < 0:
            raise ValueError("CareerMilestone sequence must be non-negative")

        if self.event_id is not None:
            if not isinstance(self.event_id, str) or not self.event_id.strip():
                raise ValueError("event_id must be non-empty string if provided")

        if self.club_id is not None:
            if not isinstance(self.club_id, str) or not self.club_id.strip():
                raise ValueError("club_id must be non-empty string if provided")

        if self.competition_id is not None:
            if not isinstance(self.competition_id, str) or not self.competition_id.strip():
                raise ValueError("competition_id must be non-empty string if provided")

        if self.value is not None:
            if isinstance(self.value, float) and (math.isnan(self.value) or math.isinf(self.value)):
                raise ValueError("Milestone value float cannot be NaN or Infinity")

        if isinstance(self.significance, str):
            try:
                object.__setattr__(self, "significance", EventSignificance(self.significance))
            except ValueError:
                raise ValueError(f"Invalid EventSignificance: '{self.significance}'")
        elif not isinstance(self.significance, EventSignificance):
            raise ValueError(f"Invalid EventSignificance: '{self.significance}'")

        object.__setattr__(self, "metadata", _to_immutable_mapping(self.metadata))


@dataclass(frozen=True)
class CareerRelationship:
    relationship_id: str
    player_id: str
    source_entity: str
    target_entity: str
    relationship_type: RelationshipType
    strength: float
    status: RelationshipStatus = RelationshipStatus.ACTIVE
    start_sequence: int = 0
    last_updated_sequence: int = 0
    event_ids: tuple[str, ...] = ()
    metadata: MappingProxyType = field(default_factory=lambda: MappingProxyType({}))

    def __post_init__(self) -> None:
        if not isinstance(self.relationship_id, str) or not self.relationship_id.strip():
            raise ValueError("CareerRelationship relationship_id must be a non-empty string")

        if not isinstance(self.player_id, str) or not self.player_id.strip():
            raise ValueError("CareerRelationship player_id must be a non-empty string")

        if not isinstance(self.source_entity, str) or not self.source_entity.strip():
            raise ValueError("CareerRelationship source_entity must be a non-empty string")

        if not isinstance(self.target_entity, str) or not self.target_entity.strip():
            raise ValueError("CareerRelationship target_entity must be a non-empty string")

        if isinstance(self.relationship_type, str):
            try:
                object.__setattr__(self, "relationship_type", RelationshipType(self.relationship_type))
            except ValueError:
                raise ValueError(f"Invalid RelationshipType: '{self.relationship_type}'")
        elif not isinstance(self.relationship_type, RelationshipType):
            raise ValueError(f"Invalid RelationshipType: '{self.relationship_type}'")

        if isinstance(self.strength, float):
            if math.isnan(self.strength) or math.isinf(self.strength):
                raise ValueError("Relationship strength cannot be NaN or Infinity")
        if not isinstance(self.strength, (int, float)) or isinstance(self.strength, bool):
            raise ValueError("Relationship strength must be a number")
        if self.strength < -1.0 or self.strength > 1.0:
            raise ValueError(f"Relationship strength must be between -1.0 and 1.0, got {self.strength}")

        if isinstance(self.status, str):
            try:
                object.__setattr__(self, "status", RelationshipStatus(self.status))
            except ValueError:
                raise ValueError(f"Invalid RelationshipStatus: '{self.status}'")
        elif not isinstance(self.status, RelationshipStatus):
            raise ValueError(f"Invalid RelationshipStatus: '{self.status}'")

        if not isinstance(self.start_sequence, int) or isinstance(self.start_sequence, bool) or self.start_sequence < 0:
            raise ValueError("start_sequence must be a non-negative integer")

        if not isinstance(self.last_updated_sequence, int) or isinstance(self.last_updated_sequence, bool) or self.last_updated_sequence < 0:
            raise ValueError("last_updated_sequence must be a non-negative integer")

        if not isinstance(self.event_ids, tuple):
            object.__setattr__(self, "event_ids", tuple(self.event_ids))
        for eid in self.event_ids:
            if not isinstance(eid, str) or not eid.strip():
                raise ValueError("event_ids must be non-empty strings")

        object.__setattr__(self, "metadata", _to_immutable_mapping(self.metadata))


@dataclass(frozen=True)
class CareerTurningPoint:
    turning_point_id: str
    turning_point_type: TurningPointType
    player_id: str
    season: int | str
    sequence: int
    source_event_id: str
    significance: EventSignificance
    summary_data: MappingProxyType = field(default_factory=lambda: MappingProxyType({}))
    metadata: MappingProxyType = field(default_factory=lambda: MappingProxyType({}))

    def __post_init__(self) -> None:
        if not isinstance(self.turning_point_id, str) or not self.turning_point_id.strip():
            raise ValueError("CareerTurningPoint turning_point_id must be a non-empty string")

        if isinstance(self.turning_point_type, str):
            try:
                object.__setattr__(self, "turning_point_type", TurningPointType(self.turning_point_type))
            except ValueError:
                raise ValueError(f"Invalid TurningPointType: '{self.turning_point_type}'")
        elif not isinstance(self.turning_point_type, TurningPointType):
            raise ValueError(f"Invalid TurningPointType: '{self.turning_point_type}'")

        if not isinstance(self.player_id, str) or not self.player_id.strip():
            raise ValueError("CareerTurningPoint player_id must be a non-empty string")

        if isinstance(self.season, int):
            if self.season <= 0:
                raise ValueError(f"Season year must be positive, got {self.season}")
        elif isinstance(self.season, str):
            if not self.season.strip():
                raise ValueError("Season string cannot be empty")
        else:
            raise ValueError(f"Invalid season format: {type(self.season)}")

        if not isinstance(self.sequence, int) or isinstance(self.sequence, bool) or self.sequence < 0:
            raise ValueError("CareerTurningPoint sequence must be non-negative integer")

        if not isinstance(self.source_event_id, str) or not self.source_event_id.strip():
            raise ValueError("CareerTurningPoint source_event_id must be non-empty string")

        if isinstance(self.significance, str):
            try:
                object.__setattr__(self, "significance", EventSignificance(self.significance))
            except ValueError:
                raise ValueError(f"Invalid EventSignificance: '{self.significance}'")
        elif not isinstance(self.significance, EventSignificance):
            raise ValueError(f"Invalid EventSignificance: '{self.significance}'")

        object.__setattr__(self, "summary_data", _to_immutable_mapping(self.summary_data))
        object.__setattr__(self, "metadata", _to_immutable_mapping(self.metadata))


@dataclass(frozen=True)
class CareerArc:
    arc_id: str
    arc_type: ArcType
    player_id: str
    start_sequence: int
    end_sequence: int | None = None
    event_ids: tuple[str, ...] = ()
    milestone_ids: tuple[str, ...] = ()
    turning_point_ids: tuple[str, ...] = ()
    significance: EventSignificance = EventSignificance.MODERATE
    status: ArcStatus = ArcStatus.ACTIVE
    metadata: MappingProxyType = field(default_factory=lambda: MappingProxyType({}))

    def __post_init__(self) -> None:
        if not isinstance(self.arc_id, str) or not self.arc_id.strip():
            raise ValueError("CareerArc arc_id must be a non-empty string")

        if isinstance(self.arc_type, str):
            try:
                object.__setattr__(self, "arc_type", ArcType(self.arc_type))
            except ValueError:
                raise ValueError(f"Invalid ArcType: '{self.arc_type}'")
        elif not isinstance(self.arc_type, ArcType):
            raise ValueError(f"Invalid ArcType: '{self.arc_type}'")

        if not isinstance(self.player_id, str) or not self.player_id.strip():
            raise ValueError("CareerArc player_id must be a non-empty string")

        if not isinstance(self.start_sequence, int) or isinstance(self.start_sequence, bool) or self.start_sequence < 0:
            raise ValueError("start_sequence must be a non-negative integer")

        if self.end_sequence is not None:
            if not isinstance(self.end_sequence, int) or isinstance(self.end_sequence, bool) or self.end_sequence < self.start_sequence:
                raise ValueError("end_sequence must be an integer >= start_sequence")

        if not isinstance(self.event_ids, tuple):
            object.__setattr__(self, "event_ids", tuple(self.event_ids))
        for eid in self.event_ids:
            if not isinstance(eid, str) or not eid.strip():
                raise ValueError("event_ids must be non-empty strings")

        if not isinstance(self.milestone_ids, tuple):
            object.__setattr__(self, "milestone_ids", tuple(self.milestone_ids))
        for mid in self.milestone_ids:
            if not isinstance(mid, str) or not mid.strip():
                raise ValueError("milestone_ids must be non-empty strings")

        if not isinstance(self.turning_point_ids, tuple):
            object.__setattr__(self, "turning_point_ids", tuple(self.turning_point_ids))
        for tpid in self.turning_point_ids:
            if not isinstance(tpid, str) or not tpid.strip():
                raise ValueError("turning_point_ids must be non-empty strings")

        if isinstance(self.significance, str):
            try:
                object.__setattr__(self, "significance", EventSignificance(self.significance))
            except ValueError:
                raise ValueError(f"Invalid EventSignificance: '{self.significance}'")
        elif not isinstance(self.significance, EventSignificance):
            raise ValueError(f"Invalid EventSignificance: '{self.significance}'")

        if isinstance(self.status, str):
            try:
                object.__setattr__(self, "status", ArcStatus(self.status))
            except ValueError:
                raise ValueError(f"Invalid ArcStatus: '{self.status}'")
        elif not isinstance(self.status, ArcStatus):
            raise ValueError(f"Invalid ArcStatus: '{self.status}'")

        object.__setattr__(self, "metadata", _to_immutable_mapping(self.metadata))


@dataclass(frozen=True)
class NarrativeSeed:
    seed_id: str
    seed_type: NarrativeSeedType
    priority: SeedPriority
    player_id: str
    sequence: int
    event_ids: tuple[str, ...] = ()
    milestone_ids: tuple[str, ...] = ()
    relationship_ids: tuple[str, ...] = ()
    arc_id: str | None = None
    emotional_direction: str = "NEUTRAL"
    factual_context: MappingProxyType = field(default_factory=lambda: MappingProxyType({}))
    narrative_weight: float = 1.0

    def __post_init__(self) -> None:
        if not isinstance(self.seed_id, str) or not self.seed_id.strip():
            raise ValueError("NarrativeSeed seed_id must be a non-empty string")

        if isinstance(self.seed_type, str):
            try:
                object.__setattr__(self, "seed_type", NarrativeSeedType(self.seed_type))
            except ValueError:
                raise ValueError(f"Invalid NarrativeSeedType: '{self.seed_type}'")
        elif not isinstance(self.seed_type, NarrativeSeedType):
            raise ValueError(f"Invalid NarrativeSeedType: '{self.seed_type}'")

        if isinstance(self.priority, str):
            try:
                object.__setattr__(self, "priority", SeedPriority(self.priority))
            except ValueError:
                raise ValueError(f"Invalid SeedPriority: '{self.priority}'")
        elif not isinstance(self.priority, SeedPriority):
            raise ValueError(f"Invalid SeedPriority: '{self.priority}'")

        if not isinstance(self.player_id, str) or not self.player_id.strip():
            raise ValueError("NarrativeSeed player_id must be non-empty string")

        if not isinstance(self.sequence, int) or isinstance(self.sequence, bool) or self.sequence < 0:
            raise ValueError("sequence must be non-negative integer")

        if not isinstance(self.event_ids, tuple):
            object.__setattr__(self, "event_ids", tuple(self.event_ids))
        for eid in self.event_ids:
            if not isinstance(eid, str) or not eid.strip():
                raise ValueError("event_ids must be non-empty strings")

        if not isinstance(self.milestone_ids, tuple):
            object.__setattr__(self, "milestone_ids", tuple(self.milestone_ids))
        for mid in self.milestone_ids:
            if not isinstance(mid, str) or not mid.strip():
                raise ValueError("milestone_ids must be non-empty strings")

        if not isinstance(self.relationship_ids, tuple):
            object.__setattr__(self, "relationship_ids", tuple(self.relationship_ids))
        for rid in self.relationship_ids:
            if not isinstance(rid, str) or not rid.strip():
                raise ValueError("relationship_ids must be non-empty strings")

        if self.arc_id is not None:
            if not isinstance(self.arc_id, str) or not self.arc_id.strip():
                raise ValueError("arc_id must be non-empty string if provided")

        if not isinstance(self.emotional_direction, str) or not self.emotional_direction.strip():
            raise ValueError("emotional_direction must be non-empty string")

        if isinstance(self.narrative_weight, float) and (math.isnan(self.narrative_weight) or math.isinf(self.narrative_weight)):
            raise ValueError("narrative_weight float cannot be NaN or Infinity")
        if not isinstance(self.narrative_weight, (int, float)) or isinstance(self.narrative_weight, bool):
            raise ValueError("narrative_weight must be a number")

        object.__setattr__(self, "factual_context", _to_immutable_mapping(self.factual_context))


@dataclass(frozen=True)
class CareerRecord:
    player_id: str
    events: tuple[CareerEvent, ...] = ()
    milestones: tuple[CareerMilestone, ...] = ()
    relationships: tuple[CareerRelationship, ...] = ()
    turning_points: tuple[CareerTurningPoint, ...] = ()
    arcs: tuple[CareerArc, ...] = ()
    narrative_seeds: tuple[NarrativeSeed, ...] = ()
    last_sequence: int = 0

    def __post_init__(self) -> None:
        if not isinstance(self.player_id, str) or not self.player_id.strip():
            raise ValueError("CareerRecord player_id must be a non-empty string")

        if not isinstance(self.events, tuple):
            object.__setattr__(self, "events", tuple(self.events))
        for ev in self.events:
            if not isinstance(ev, CareerEvent):
                raise ValueError(f"Expected CareerEvent, got {type(ev)}")

        if not isinstance(self.milestones, tuple):
            object.__setattr__(self, "milestones", tuple(self.milestones))
        for ms in self.milestones:
            if not isinstance(ms, CareerMilestone):
                raise ValueError(f"Expected CareerMilestone, got {type(ms)}")

        if not isinstance(self.relationships, tuple):
            object.__setattr__(self, "relationships", tuple(self.relationships))
        for rel in self.relationships:
            if not isinstance(rel, CareerRelationship):
                raise ValueError(f"Expected CareerRelationship, got {type(rel)}")

        if not isinstance(self.turning_points, tuple):
            object.__setattr__(self, "turning_points", tuple(self.turning_points))
        for tp in self.turning_points:
            if not isinstance(tp, CareerTurningPoint):
                raise ValueError(f"Expected CareerTurningPoint, got {type(tp)}")

        if not isinstance(self.arcs, tuple):
            object.__setattr__(self, "arcs", tuple(self.arcs))
        for arc in self.arcs:
            if not isinstance(arc, CareerArc):
                raise ValueError(f"Expected CareerArc, got {type(arc)}")

        if not isinstance(self.narrative_seeds, tuple):
            object.__setattr__(self, "narrative_seeds", tuple(self.narrative_seeds))
        for ns in self.narrative_seeds:
            if not isinstance(ns, NarrativeSeed):
                raise ValueError(f"Expected NarrativeSeed, got {type(ns)}")

        if not isinstance(self.last_sequence, int) or isinstance(self.last_sequence, bool) or self.last_sequence < 0:
            raise ValueError("last_sequence must be a non-negative integer")
