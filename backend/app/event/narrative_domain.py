import math
from dataclasses import dataclass, field
from enum import StrEnum
from types import MappingProxyType
from typing import Any

from app.event.domain import (
    _is_valid_primitive,
    _to_immutable_mapping,
    _to_immutable_primitive,
)


class StoryDensity(StrEnum):
    COMPACT = "COMPACT"
    STANDARD = "STANDARD"
    DETAILED = "DETAILED"
    COMPLETE = "COMPLETE"


class PremiseType(StrEnum):
    RISE = "RISE"
    COMEBACK = "COMEBACK"
    UNDERDOG = "UNDERDOG"
    TRIUMPH = "TRIUMPH"
    TRAGEDY = "TRAGEDY"
    REDEMPTION = "REDEMPTION"
    RIVALRY = "RIVALRY"
    LOYALTY = "LOYALTY"
    JOURNEY = "JOURNEY"
    LEGACY = "LEGACY"


class ActType(StrEnum):
    ORIGIN = "ORIGIN"
    SETUP = "SETUP"
    RISE = "RISE"
    CONFLICT = "CONFLICT"
    CRISIS = "CRISIS"
    BREAKTHROUGH = "BREAKTHROUGH"
    PEAK = "PEAK"
    FALL = "FALL"
    RECOVERY = "RECOVERY"
    RESOLUTION = "RESOLUTION"
    LEGACY = "LEGACY"


class BeatType(StrEnum):
    INTRODUCTION = "INTRODUCTION"
    ORIGIN = "ORIGIN"
    FIRST_CHANCE = "FIRST_CHANCE"
    EARLY_SUCCESS = "EARLY_SUCCESS"
    SETBACK = "SETBACK"
    CONFLICT = "CONFLICT"
    RIVAL_APPEARANCE = "RIVAL_APPEARANCE"
    BREAKTHROUGH = "BREAKTHROUGH"
    MAJOR_ACHIEVEMENT = "MAJOR_ACHIEVEMENT"
    CRISIS = "CRISIS"
    COMEBACK = "COMEBACK"
    CLIMAX = "CLIMAX"
    PEAK = "PEAK"
    DECLINE = "DECLINE"
    FINAL_CHAPTER = "FINAL_CHAPTER"
    LEGACY = "LEGACY"


class NarrativeFunction(StrEnum):
    SETUP = "SETUP"
    ESCALATION = "ESCALATION"
    CONTRAST = "CONTRAST"
    CONFLICT = "CONFLICT"
    TRANSITION = "TRANSITION"
    PAYOFF = "PAYOFF"
    CLIMAX = "CLIMAX"
    RESOLUTION = "RESOLUTION"
    REFLECTION = "REFLECTION"


class EmotionalDirection(StrEnum):
    NEUTRAL = "NEUTRAL"
    POSITIVE = "POSITIVE"
    NEGATIVE = "NEGATIVE"
    TENSION = "TENSION"
    HOPE = "HOPE"
    TRIUMPH = "TRIUMPH"
    LOSS = "LOSS"
    UNCERTAINTY = "UNCERTAINTY"
    RELIEF = "RELIEF"
    BITTERSWEET = "BITTERSWEET"


class ConflictType(StrEnum):
    SPORTING = "SPORTING"
    CAREER = "CAREER"
    TRANSFER = "TRANSFER"
    COMPETITIVE = "COMPETITIVE"
    RELATIONSHIP = "RELATIONSHIP"
    PERFORMANCE = "PERFORMANCE"
    INJURY = "INJURY"
    STATUS = "STATUS"
    INTERNATIONAL = "INTERNATIONAL"


class ConflictStatus(StrEnum):
    INTRODUCED = "INTRODUCED"
    ESCALATING = "ESCALATING"
    PEAK = "PEAK"
    RESOLVED = "RESOLVED"
    UNRESOLVED = "UNRESOLVED"
    ABANDONED = "ABANDONED"


class OpeningStrategy(StrEnum):
    CHRONOLOGICAL_ORIGIN = "CHRONOLOGICAL_ORIGIN"
    COLD_OPEN = "COLD_OPEN"
    MAJOR_ACHIEVEMENT = "MAJOR_ACHIEVEMENT"
    CAREER_CONTRAST = "CAREER_CONTRAST"
    MYSTERY = "MYSTERY"
    RIVALRY = "RIVALRY"
    CRISIS = "CRISIS"


class ResolutionType(StrEnum):
    TRIUMPH = "TRIUMPH"
    LEGACY = "LEGACY"
    RETIREMENT = "RETIREMENT"
    DECLINE = "DECLINE"
    UNRESOLVED = "UNRESOLVED"
    ONGOING = "ONGOING"
    COMEBACK = "COMEBACK"


class NarrativeTheme(StrEnum):
    PERSEVERANCE = "PERSEVERANCE"
    AMBITION = "AMBITION"
    LOYALTY = "LOYALTY"
    RIVALRY = "RIVALRY"
    RECOVERY = "RECOVERY"
    ADVERSITY = "ADVERSITY"
    SUCCESS = "SUCCESS"
    SACRIFICE = "SACRIFICE"
    CHANGE = "CHANGE"
    LEGACY = "LEGACY"


class NarrativePacing(StrEnum):
    SLOW = "SLOW"
    MODERATE = "MODERATE"
    FAST = "FAST"
    CLIMACTIC = "CLIMACTIC"
    REFLECTIVE = "REFLECTIVE"


class NarrativeThreadType(StrEnum):
    CAREER_RISE = "CAREER_RISE"
    RIVALRY = "RIVALRY"
    CLUB_LOYALTY = "CLUB_LOYALTY"
    INTERNATIONAL_CAREER = "INTERNATIONAL_CAREER"
    RECOVERY = "RECOVERY"
    PERFORMANCE = "PERFORMANCE"
    TRANSFER_JOURNEY = "TRANSFER_JOURNEY"


class NarrativeErrorCode(StrEnum):
    INVALID_CAREER_RECORD = "INVALID_CAREER_RECORD"
    INVALID_EVENT_REFERENCE = "INVALID_EVENT_REFERENCE"
    INVALID_MILESTONE_REFERENCE = "INVALID_MILESTONE_REFERENCE"
    INVALID_TURNING_POINT_REFERENCE = "INVALID_TURNING_POINT_REFERENCE"
    INVALID_ARC_REFERENCE = "INVALID_ARC_REFERENCE"
    INVALID_RELATIONSHIP_REFERENCE = "INVALID_RELATIONSHIP_REFERENCE"
    INVALID_SEED_REFERENCE = "INVALID_SEED_REFERENCE"
    INVALID_CONFIGURATION = "INVALID_CONFIGURATION"
    EMPTY_INPUT = "EMPTY_INPUT"
    NARRATIVE_VALIDATION_ERROR = "NARRATIVE_VALIDATION_ERROR"
    NARRATIVE_BUILD_ERROR = "NARRATIVE_BUILD_ERROR"


@dataclass(frozen=True)
class StoryPremise:
    premise_type: PremiseType
    primary_arc_id: str | None = None
    central_conflict_id: str | None = None
    protagonist_goal: str = ""
    resolution_type: ResolutionType = ResolutionType.ONGOING
    supporting_facts: MappingProxyType = field(default_factory=lambda: MappingProxyType({}))

    def __post_init__(self) -> None:
        if isinstance(self.premise_type, str):
            try:
                object.__setattr__(self, "premise_type", PremiseType(self.premise_type))
            except ValueError:
                raise ValueError(f"Invalid PremiseType: '{self.premise_type}'")
        elif not isinstance(self.premise_type, PremiseType):
            raise ValueError(f"Invalid PremiseType: '{self.premise_type}'")

        if self.primary_arc_id is not None:
            if not isinstance(self.primary_arc_id, str) or not self.primary_arc_id.strip():
                raise ValueError("primary_arc_id must be non-empty string if provided")

        if self.central_conflict_id is not None:
            if not isinstance(self.central_conflict_id, str) or not self.central_conflict_id.strip():
                raise ValueError("central_conflict_id must be non-empty string if provided")

        if not isinstance(self.protagonist_goal, str):
            raise ValueError("protagonist_goal must be a string")

        if isinstance(self.resolution_type, str):
            try:
                object.__setattr__(self, "resolution_type", ResolutionType(self.resolution_type))
            except ValueError:
                raise ValueError(f"Invalid ResolutionType: '{self.resolution_type}'")
        elif not isinstance(self.resolution_type, ResolutionType):
            raise ValueError(f"Invalid ResolutionType: '{self.resolution_type}'")

        object.__setattr__(self, "supporting_facts", _to_immutable_mapping(self.supporting_facts))


@dataclass(frozen=True)
class NarrativeProtagonist:
    player_id: str
    position: str = ""
    origin: str = ""
    career_stage: str = ""
    key_traits: tuple[str, ...] = ()
    important_clubs: tuple[str, ...] = ()
    important_relationships: tuple[str, ...] = ()
    defining_events: tuple[str, ...] = ()
    metadata: MappingProxyType = field(default_factory=lambda: MappingProxyType({}))

    def __post_init__(self) -> None:
        if not isinstance(self.player_id, str) or not self.player_id.strip():
            raise ValueError("NarrativeProtagonist player_id must be a non-empty string")

        if not isinstance(self.position, str):
            raise ValueError("position must be a string")
        if not isinstance(self.origin, str):
            raise ValueError("origin must be a string")
        if not isinstance(self.career_stage, str):
            raise ValueError("career_stage must be a string")

        if not isinstance(self.key_traits, tuple):
            object.__setattr__(self, "key_traits", tuple(self.key_traits))
        for item in self.key_traits:
            if not isinstance(item, str) or not item.strip():
                raise ValueError("key_traits must contain non-empty strings")

        if not isinstance(self.important_clubs, tuple):
            object.__setattr__(self, "important_clubs", tuple(self.important_clubs))
        for item in self.important_clubs:
            if not isinstance(item, str) or not item.strip():
                raise ValueError("important_clubs must contain non-empty strings")

        if not isinstance(self.important_relationships, tuple):
            object.__setattr__(self, "important_relationships", tuple(self.important_relationships))
        for item in self.important_relationships:
            if not isinstance(item, str) or not item.strip():
                raise ValueError("important_relationships must contain non-empty strings")

        if not isinstance(self.defining_events, tuple):
            object.__setattr__(self, "defining_events", tuple(self.defining_events))
        for item in self.defining_events:
            if not isinstance(item, str) or not item.strip():
                raise ValueError("defining_events must contain non-empty strings")

        object.__setattr__(self, "metadata", _to_immutable_mapping(self.metadata))


@dataclass(frozen=True)
class NarrativeAct:
    act_id: str
    act_type: ActType
    sequence: int
    title: str
    description: str
    start_sequence: int = 0
    end_sequence: int = 0
    beat_ids: tuple[str, ...] = ()
    pacing: NarrativePacing = NarrativePacing.MODERATE
    metadata: MappingProxyType = field(default_factory=lambda: MappingProxyType({}))

    def __post_init__(self) -> None:
        if not isinstance(self.act_id, str) or not self.act_id.strip():
            raise ValueError("NarrativeAct act_id must be a non-empty string")

        if isinstance(self.act_type, str):
            try:
                object.__setattr__(self, "act_type", ActType(self.act_type))
            except ValueError:
                raise ValueError(f"Invalid ActType: '{self.act_type}'")
        elif not isinstance(self.act_type, ActType):
            raise ValueError(f"Invalid ActType: '{self.act_type}'")

        if not isinstance(self.sequence, int) or isinstance(self.sequence, bool) or self.sequence < 0:
            raise ValueError("sequence must be a non-negative integer")

        if not isinstance(self.title, str):
            raise ValueError("title must be a string")
        if not isinstance(self.description, str):
            raise ValueError("description must be a string")

        if not isinstance(self.start_sequence, int) or isinstance(self.start_sequence, bool) or self.start_sequence < 0:
            raise ValueError("start_sequence must be a non-negative integer")

        if not isinstance(self.end_sequence, int) or isinstance(self.end_sequence, bool) or self.end_sequence < self.start_sequence:
            raise ValueError("end_sequence must be an integer >= start_sequence")

        if not isinstance(self.beat_ids, tuple):
            object.__setattr__(self, "beat_ids", tuple(self.beat_ids))
        for item in self.beat_ids:
            if not isinstance(item, str) or not item.strip():
                raise ValueError("beat_ids must contain non-empty strings")

        if isinstance(self.pacing, str):
            try:
                object.__setattr__(self, "pacing", NarrativePacing(self.pacing))
            except ValueError:
                raise ValueError(f"Invalid NarrativePacing: '{self.pacing}'")
        elif not isinstance(self.pacing, NarrativePacing):
            raise ValueError(f"Invalid NarrativePacing: '{self.pacing}'")

        object.__setattr__(self, "metadata", _to_immutable_mapping(self.metadata))


@dataclass(frozen=True)
class NarrativeBeat:
    beat_id: str
    beat_type: BeatType
    sequence: int
    importance: float = 1.0
    source_event_ids: tuple[str, ...] = ()
    source_milestone_ids: tuple[str, ...] = ()
    source_turning_point_ids: tuple[str, ...] = ()
    source_seed_ids: tuple[str, ...] = ()
    emotional_direction: EmotionalDirection = EmotionalDirection.NEUTRAL
    narrative_function: NarrativeFunction = NarrativeFunction.SETUP
    pacing: NarrativePacing = NarrativePacing.MODERATE
    factual_context: MappingProxyType = field(default_factory=lambda: MappingProxyType({}))

    def __post_init__(self) -> None:
        if not isinstance(self.beat_id, str) or not self.beat_id.strip():
            raise ValueError("NarrativeBeat beat_id must be a non-empty string")

        if isinstance(self.beat_type, str):
            try:
                object.__setattr__(self, "beat_type", BeatType(self.beat_type))
            except ValueError:
                raise ValueError(f"Invalid BeatType: '{self.beat_type}'")
        elif not isinstance(self.beat_type, BeatType):
            raise ValueError(f"Invalid BeatType: '{self.beat_type}'")

        if not isinstance(self.sequence, int) or isinstance(self.sequence, bool) or self.sequence < 0:
            raise ValueError("sequence must be a non-negative integer")

        if isinstance(self.importance, float):
            if math.isnan(self.importance) or math.isinf(self.importance):
                raise ValueError("importance float cannot be NaN or Infinity")
        if not isinstance(self.importance, (int, float)) or isinstance(self.importance, bool):
            raise ValueError("importance must be a number")

        if not isinstance(self.source_event_ids, tuple):
            object.__setattr__(self, "source_event_ids", tuple(self.source_event_ids))
        for item in self.source_event_ids:
            if not isinstance(item, str) or not item.strip():
                raise ValueError("source_event_ids must contain non-empty strings")

        if not isinstance(self.source_milestone_ids, tuple):
            object.__setattr__(self, "source_milestone_ids", tuple(self.source_milestone_ids))
        for item in self.source_milestone_ids:
            if not isinstance(item, str) or not item.strip():
                raise ValueError("source_milestone_ids must contain non-empty strings")

        if not isinstance(self.source_turning_point_ids, tuple):
            object.__setattr__(self, "source_turning_point_ids", tuple(self.source_turning_point_ids))
        for item in self.source_turning_point_ids:
            if not isinstance(item, str) or not item.strip():
                raise ValueError("source_turning_point_ids must contain non-empty strings")

        if not isinstance(self.source_seed_ids, tuple):
            object.__setattr__(self, "source_seed_ids", tuple(self.source_seed_ids))
        for item in self.source_seed_ids:
            if not isinstance(item, str) or not item.strip():
                raise ValueError("source_seed_ids must contain non-empty strings")

        if isinstance(self.emotional_direction, str):
            try:
                object.__setattr__(self, "emotional_direction", EmotionalDirection(self.emotional_direction))
            except ValueError:
                raise ValueError(f"Invalid EmotionalDirection: '{self.emotional_direction}'")
        elif not isinstance(self.emotional_direction, EmotionalDirection):
            raise ValueError(f"Invalid EmotionalDirection: '{self.emotional_direction}'")

        if isinstance(self.narrative_function, str):
            try:
                object.__setattr__(self, "narrative_function", NarrativeFunction(self.narrative_function))
            except ValueError:
                raise ValueError(f"Invalid NarrativeFunction: '{self.narrative_function}'")
        elif not isinstance(self.narrative_function, NarrativeFunction):
            raise ValueError(f"Invalid NarrativeFunction: '{self.narrative_function}'")

        if isinstance(self.pacing, str):
            try:
                object.__setattr__(self, "pacing", NarrativePacing(self.pacing))
            except ValueError:
                raise ValueError(f"Invalid NarrativePacing: '{self.pacing}'")
        elif not isinstance(self.pacing, NarrativePacing):
            raise ValueError(f"Invalid NarrativePacing: '{self.pacing}'")

        object.__setattr__(self, "factual_context", _to_immutable_mapping(self.factual_context))


@dataclass(frozen=True)
class NarrativeConflict:
    conflict_id: str
    conflict_type: ConflictType
    source_events: tuple[str, ...] = ()
    start_sequence: int = 0
    end_sequence: int | None = None
    intensity: float = 1.0
    resolution_status: ConflictStatus = ConflictStatus.INTRODUCED
    metadata: MappingProxyType = field(default_factory=lambda: MappingProxyType({}))

    def __post_init__(self) -> None:
        if not isinstance(self.conflict_id, str) or not self.conflict_id.strip():
            raise ValueError("NarrativeConflict conflict_id must be a non-empty string")

        if isinstance(self.conflict_type, str):
            try:
                object.__setattr__(self, "conflict_type", ConflictType(self.conflict_type))
            except ValueError:
                raise ValueError(f"Invalid ConflictType: '{self.conflict_type}'")
        elif not isinstance(self.conflict_type, ConflictType):
            raise ValueError(f"Invalid ConflictType: '{self.conflict_type}'")

        if not isinstance(self.source_events, tuple):
            object.__setattr__(self, "source_events", tuple(self.source_events))
        for item in self.source_events:
            if not isinstance(item, str) or not item.strip():
                raise ValueError("source_events must contain non-empty strings")

        if not isinstance(self.start_sequence, int) or isinstance(self.start_sequence, bool) or self.start_sequence < 0:
            raise ValueError("start_sequence must be a non-negative integer")

        if self.end_sequence is not None:
            if not isinstance(self.end_sequence, int) or isinstance(self.end_sequence, bool) or self.end_sequence < self.start_sequence:
                raise ValueError("end_sequence must be an integer >= start_sequence")

        if isinstance(self.intensity, float):
            if math.isnan(self.intensity) or math.isinf(self.intensity):
                raise ValueError("intensity float cannot be NaN or Infinity")
        if not isinstance(self.intensity, (int, float)) or isinstance(self.intensity, bool):
            raise ValueError("intensity must be a number")

        if isinstance(self.resolution_status, str):
            try:
                object.__setattr__(self, "resolution_status", ConflictStatus(self.resolution_status))
            except ValueError:
                raise ValueError(f"Invalid ConflictStatus: '{self.resolution_status}'")
        elif not isinstance(self.resolution_status, ConflictStatus):
            raise ValueError(f"Invalid ConflictStatus: '{self.resolution_status}'")

        object.__setattr__(self, "metadata", _to_immutable_mapping(self.metadata))


@dataclass(frozen=True)
class NarrativeThread:
    thread_id: str
    thread_type: NarrativeThreadType
    beat_ids: tuple[str, ...] = ()
    start_sequence: int = 0
    end_sequence: int | None = None
    importance: float = 1.0
    status: str = "ACTIVE"
    metadata: MappingProxyType = field(default_factory=lambda: MappingProxyType({}))

    def __post_init__(self) -> None:
        if not isinstance(self.thread_id, str) or not self.thread_id.strip():
            raise ValueError("NarrativeThread thread_id must be a non-empty string")

        if isinstance(self.thread_type, str):
            try:
                object.__setattr__(self, "thread_type", NarrativeThreadType(self.thread_type))
            except ValueError:
                raise ValueError(f"Invalid NarrativeThreadType: '{self.thread_type}'")
        elif not isinstance(self.thread_type, NarrativeThreadType):
            raise ValueError(f"Invalid NarrativeThreadType: '{self.thread_type}'")

        if not isinstance(self.beat_ids, tuple):
            object.__setattr__(self, "beat_ids", tuple(self.beat_ids))
        for item in self.beat_ids:
            if not isinstance(item, str) or not item.strip():
                raise ValueError("beat_ids must contain non-empty strings")

        if not isinstance(self.start_sequence, int) or isinstance(self.start_sequence, bool) or self.start_sequence < 0:
            raise ValueError("start_sequence must be a non-negative integer")

        if self.end_sequence is not None:
            if not isinstance(self.end_sequence, int) or isinstance(self.end_sequence, bool) or self.end_sequence < self.start_sequence:
                raise ValueError("end_sequence must be an integer >= start_sequence")

        if isinstance(self.importance, float):
            if math.isnan(self.importance) or math.isinf(self.importance):
                raise ValueError("importance float cannot be NaN or Infinity")
        if not isinstance(self.importance, (int, float)) or isinstance(self.importance, bool):
            raise ValueError("importance must be a number")

        if not isinstance(self.status, str):
            raise ValueError("status must be a string")

        object.__setattr__(self, "metadata", _to_immutable_mapping(self.metadata))


@dataclass(frozen=True)
class NarrativeStory:
    story_id: str
    player_id: str
    title_context: str
    premise: StoryPremise
    protagonist: NarrativeProtagonist
    density: StoryDensity = StoryDensity.STANDARD
    target_duration_seconds: float | None = None
    opening_strategy: OpeningStrategy = OpeningStrategy.CHRONOLOGICAL_ORIGIN
    opening_beat_id: str | None = None
    climax_beat_id: str | None = None
    resolution_type: ResolutionType = ResolutionType.ONGOING
    acts: tuple[NarrativeAct, ...] = ()
    narrative_beats: tuple[NarrativeBeat, ...] = ()
    threads: tuple[NarrativeThread, ...] = ()
    conflicts: tuple[NarrativeConflict, ...] = ()
    featured_events: tuple[str, ...] = ()
    featured_relationships: tuple[str, ...] = ()
    featured_milestones: tuple[str, ...] = ()
    featured_turning_points: tuple[str, ...] = ()
    featured_arcs: tuple[str, ...] = ()
    themes: tuple[NarrativeTheme, ...] = ()
    metadata: MappingProxyType = field(default_factory=lambda: MappingProxyType({}))

    def __post_init__(self) -> None:
        if not isinstance(self.story_id, str) or not self.story_id.strip():
            raise ValueError("NarrativeStory story_id must be a non-empty string")

        if not isinstance(self.player_id, str) or not self.player_id.strip():
            raise ValueError("NarrativeStory player_id must be a non-empty string")

        if not isinstance(self.title_context, str):
            raise ValueError("title_context must be a string")

        if not isinstance(self.premise, StoryPremise):
            raise ValueError(f"Expected StoryPremise, got {type(self.premise)}")

        if not isinstance(self.protagonist, NarrativeProtagonist):
            raise ValueError(f"Expected NarrativeProtagonist, got {type(self.protagonist)}")

        if isinstance(self.density, str):
            try:
                object.__setattr__(self, "density", StoryDensity(self.density))
            except ValueError:
                raise ValueError(f"Invalid StoryDensity: '{self.density}'")
        elif not isinstance(self.density, StoryDensity):
            raise ValueError(f"Invalid StoryDensity: '{self.density}'")

        if self.target_duration_seconds is not None:
            if isinstance(self.target_duration_seconds, float) and (math.isnan(self.target_duration_seconds) or math.isinf(self.target_duration_seconds)):
                raise ValueError("target_duration_seconds cannot be NaN or Infinity")
            if not isinstance(self.target_duration_seconds, (int, float)) or isinstance(self.target_duration_seconds, bool) or self.target_duration_seconds < 0:
                raise ValueError("target_duration_seconds must be a non-negative number")

        if isinstance(self.opening_strategy, str):
            try:
                object.__setattr__(self, "opening_strategy", OpeningStrategy(self.opening_strategy))
            except ValueError:
                raise ValueError(f"Invalid OpeningStrategy: '{self.opening_strategy}'")
        elif not isinstance(self.opening_strategy, OpeningStrategy):
            raise ValueError(f"Invalid OpeningStrategy: '{self.opening_strategy}'")

        if self.opening_beat_id is not None:
            if not isinstance(self.opening_beat_id, str) or not self.opening_beat_id.strip():
                raise ValueError("opening_beat_id must be non-empty string if provided")

        if self.climax_beat_id is not None:
            if not isinstance(self.climax_beat_id, str) or not self.climax_beat_id.strip():
                raise ValueError("climax_beat_id must be non-empty string if provided")

        if isinstance(self.resolution_type, str):
            try:
                object.__setattr__(self, "resolution_type", ResolutionType(self.resolution_type))
            except ValueError:
                raise ValueError(f"Invalid ResolutionType: '{self.resolution_type}'")
        elif not isinstance(self.resolution_type, ResolutionType):
            raise ValueError(f"Invalid ResolutionType: '{self.resolution_type}'")

        if not isinstance(self.acts, tuple):
            object.__setattr__(self, "acts", tuple(self.acts))
        for item in self.acts:
            if not isinstance(item, NarrativeAct):
                raise ValueError(f"Expected NarrativeAct, got {type(item)}")

        if not isinstance(self.narrative_beats, tuple):
            object.__setattr__(self, "narrative_beats", tuple(self.narrative_beats))
        for item in self.narrative_beats:
            if not isinstance(item, NarrativeBeat):
                raise ValueError(f"Expected NarrativeBeat, got {type(item)}")

        if not isinstance(self.threads, tuple):
            object.__setattr__(self, "threads", tuple(self.threads))
        for item in self.threads:
            if not isinstance(item, NarrativeThread):
                raise ValueError(f"Expected NarrativeThread, got {type(item)}")

        if not isinstance(self.conflicts, tuple):
            object.__setattr__(self, "conflicts", tuple(self.conflicts))
        for item in self.conflicts:
            if not isinstance(item, NarrativeConflict):
                raise ValueError(f"Expected NarrativeConflict, got {type(item)}")

        if not isinstance(self.featured_events, tuple):
            object.__setattr__(self, "featured_events", tuple(self.featured_events))
        for item in self.featured_events:
            if not isinstance(item, str) or not item.strip():
                raise ValueError("featured_events must contain non-empty strings")

        if not isinstance(self.featured_relationships, tuple):
            object.__setattr__(self, "featured_relationships", tuple(self.featured_relationships))
        for item in self.featured_relationships:
            if not isinstance(item, str) or not item.strip():
                raise ValueError("featured_relationships must contain non-empty strings")

        if not isinstance(self.featured_milestones, tuple):
            object.__setattr__(self, "featured_milestones", tuple(self.featured_milestones))
        for item in self.featured_milestones:
            if not isinstance(item, str) or not item.strip():
                raise ValueError("featured_milestones must contain non-empty strings")

        if not isinstance(self.featured_turning_points, tuple):
            object.__setattr__(self, "featured_turning_points", tuple(self.featured_turning_points))
        for item in self.featured_turning_points:
            if not isinstance(item, str) or not item.strip():
                raise ValueError("featured_turning_points must contain non-empty strings")

        if not isinstance(self.featured_arcs, tuple):
            object.__setattr__(self, "featured_arcs", tuple(self.featured_arcs))
        for item in self.featured_arcs:
            if not isinstance(item, str) or not item.strip():
                raise ValueError("featured_arcs must contain non-empty strings")

        if not isinstance(self.themes, tuple):
            object.__setattr__(self, "themes", tuple(self.themes))
        validated_themes: list[NarrativeTheme] = []
        for item in self.themes:
            if isinstance(item, str):
                try:
                    validated_themes.append(NarrativeTheme(item))
                except ValueError:
                    raise ValueError(f"Invalid NarrativeTheme: '{item}'")
            elif isinstance(item, NarrativeTheme):
                validated_themes.append(item)
            else:
                raise ValueError(f"Expected NarrativeTheme, got {type(item)}")
        object.__setattr__(self, "themes", tuple(validated_themes))

        object.__setattr__(self, "metadata", _to_immutable_mapping(self.metadata))


@dataclass(frozen=True)
class NarrativeBuildResult:
    success: bool
    story: NarrativeStory | None = None
    error_code: NarrativeErrorCode | None = None
    error_message: str | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.success, bool):
            raise ValueError("success must be a boolean")

        if self.success:
            if not isinstance(self.story, NarrativeStory):
                raise ValueError("story must be NarrativeStory when success=True")
        else:
            if self.error_code is not None:
                if isinstance(self.error_code, str):
                    try:
                        object.__setattr__(self, "error_code", NarrativeErrorCode(self.error_code))
                    except ValueError:
                        raise ValueError(f"Invalid NarrativeErrorCode: '{self.error_code}'")
                elif not isinstance(self.error_code, NarrativeErrorCode):
                    raise ValueError(f"Invalid NarrativeErrorCode: '{self.error_code}'")
