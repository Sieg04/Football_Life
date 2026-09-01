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


class PresentationSectionType(StrEnum):
    PLAYER = "PLAYER"
    OVERVIEW = "OVERVIEW"
    CAREER = "CAREER"
    STATISTICS = "STATISTICS"
    TIMELINE = "TIMELINE"
    HIGHLIGHTS = "HIGHLIGHTS"
    CAREER_ARC = "CAREER_ARC"
    RELATIONSHIPS = "RELATIONSHIPS"
    STORY = "STORY"
    SCRIPT = "SCRIPT"


class TimelineEntryType(StrEnum):
    EVENT = "EVENT"
    MILESTONE = "MILESTONE"
    TURNING_POINT = "TURNING_POINT"
    TRANSFER = "TRANSFER"
    TROPHY = "TROPHY"
    BREAKTHROUGH = "BREAKTHROUGH"
    SETBACK = "SETBACK"
    RECOVERY = "RECOVERY"
    CAREER_ARC_CHANGE = "CAREER_ARC_CHANGE"


class HighlightType(StrEnum):
    HIGH_SIGNIFICANCE_EVENT = "HIGH_SIGNIFICANCE_EVENT"
    FIRST_MAJOR_TROPHY = "FIRST_MAJOR_TROPHY"
    MAJOR_TROPHY = "MAJOR_TROPHY"
    MILESTONE = "MILESTONE"
    TURNING_POINT = "TURNING_POINT"
    BREAKTHROUGH = "BREAKTHROUGH"
    CAREER_ARC_TRANSITION = "CAREER_ARC_TRANSITION"
    CLIMAX = "CLIMAX"


class StatCategory(StrEnum):
    APPEARANCES = "APPEARANCES"
    GOALS = "GOALS"
    ASSISTS = "ASSISTS"
    CLEAN_SHEETS = "CLEAN_SHEETS"
    MINUTES = "MINUTES"
    AVERAGE_RATING = "AVERAGE_RATING"
    TROPHIES = "TROPHIES"
    AWARDS = "AWARDS"


class CareerStatus(StrEnum):
    ACTIVE = "ACTIVE"
    RETIRED = "RETIRED"


class VisualPriority(StrEnum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class PresentationDensity(StrEnum):
    COMPACT = "COMPACT"
    STANDARD = "STANDARD"
    DETAILED = "DETAILED"
    COMPLETE = "COMPLETE"


class PresentationErrorCode(StrEnum):
    INVALID_INPUT = "INVALID_INPUT"
    MISSING_SOURCE = "MISSING_SOURCE"
    INVALID_REFERENCE = "INVALID_REFERENCE"
    INVALID_CONFIGURATION = "INVALID_CONFIGURATION"
    INCONSISTENT_DATA = "INCONSISTENT_DATA"
    IMMUTABILITY_VIOLATION = "IMMUTABILITY_VIOLATION"
    INVALID_DENSITY = "INVALID_DENSITY"
    INVALID_PRESENTATION = "INVALID_PRESENTATION"
    PRESENTATION_BUILD_ERROR = "PRESENTATION_BUILD_ERROR"


class PresentationProcessingException(Exception):
    """Exception raised when presentation generation or validation fails atomically."""

    def __init__(self, code: PresentationErrorCode, message: str) -> None:
        super().__init__(f"[{code.value}] {message}")
        self.code = code
        self.message = message


@dataclass(frozen=True)
class PresentationSourceReference:
    career_record_id: str | None = None
    event_ids: tuple[str, ...] = ()
    milestone_ids: tuple[str, ...] = ()
    turning_point_ids: tuple[str, ...] = ()
    relationship_ids: tuple[str, ...] = ()
    arc_ids: tuple[str, ...] = ()
    story_id: str | None = None
    act_ids: tuple[str, ...] = ()
    beat_ids: tuple[str, ...] = ()
    thread_ids: tuple[str, ...] = ()
    conflict_ids: tuple[str, ...] = ()
    seed_ids: tuple[str, ...] = ()
    script_id: str | None = None
    segment_ids: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        for str_field, val in [
            ("career_record_id", self.career_record_id),
            ("story_id", self.story_id),
            ("script_id", self.script_id),
        ]:
            if val is not None and (not isinstance(val, str) or not val.strip()):
                raise ValueError(f"{str_field} must be a non-empty string if provided")

        tuple_fields = [
            ("event_ids", self.event_ids),
            ("milestone_ids", self.milestone_ids),
            ("turning_point_ids", self.turning_point_ids),
            ("relationship_ids", self.relationship_ids),
            ("arc_ids", self.arc_ids),
            ("act_ids", self.act_ids),
            ("beat_ids", self.beat_ids),
            ("thread_ids", self.thread_ids),
            ("conflict_ids", self.conflict_ids),
            ("seed_ids", self.seed_ids),
            ("segment_ids", self.segment_ids),
        ]
        for name, field_val in tuple_fields:
            if not isinstance(field_val, tuple):
                object.__setattr__(self, name, tuple(field_val))
            for item in getattr(self, name):
                if not isinstance(item, str) or not item.strip():
                    raise ValueError(f"{name} must contain non-empty strings")


@dataclass(frozen=True)
class PlayerPresentation:
    player_id: str
    name: str
    first_name: str | None = None
    last_name: str | None = None
    age: int | None = None
    nationality: str | None = None
    position: str | None = None
    overall_rating: int | None = None
    potential: int | None = None
    current_club: str | None = None
    career_status: CareerStatus = CareerStatus.ACTIVE

    def __post_init__(self) -> None:
        if not isinstance(self.player_id, str) or not self.player_id.strip():
            raise ValueError("player_id must be a non-empty string")
        if not isinstance(self.name, str) or not self.name.strip():
            raise ValueError("name must be a non-empty string")

        if self.first_name is not None and not isinstance(self.first_name, str):
            raise ValueError("first_name must be a string if provided")
        if self.last_name is not None and not isinstance(self.last_name, str):
            raise ValueError("last_name must be a string if provided")

        if self.age is not None and (not isinstance(self.age, int) or isinstance(self.age, bool) or self.age < 0):
            raise ValueError("age must be a non-negative integer if provided")

        if self.nationality is not None and not isinstance(self.nationality, str):
            raise ValueError("nationality must be a string if provided")
        if self.position is not None and not isinstance(self.position, str):
            raise ValueError("position must be a string if provided")

        if self.overall_rating is not None and (
            not isinstance(self.overall_rating, int) or isinstance(self.overall_rating, bool) or self.overall_rating < 0
        ):
            raise ValueError("overall_rating must be a non-negative integer if provided")

        if self.potential is not None and (
            not isinstance(self.potential, int) or isinstance(self.potential, bool) or self.potential < 0
        ):
            raise ValueError("potential must be a non-negative integer if provided")

        if self.current_club is not None and not isinstance(self.current_club, str):
            raise ValueError("current_club must be a string if provided")

        if isinstance(self.career_status, str):
            try:
                object.__setattr__(self, "career_status", CareerStatus(self.career_status))
            except ValueError:
                raise ValueError(f"Invalid CareerStatus: '{self.career_status}'")
        elif not isinstance(self.career_status, CareerStatus):
            raise ValueError(f"Invalid CareerStatus: '{self.career_status}'")


@dataclass(frozen=True)
class CareerOverview:
    career_start: str | int | None = None
    career_end: str | int | None = None
    years_active: int = 0
    clubs_count: int = 0
    matches: int = 0
    goals: int = 0
    assists: int = 0
    trophies: int = 0
    milestones: int = 0
    turning_points: int = 0
    peak_rating: int | None = None
    peak_club: str | None = None
    career_arc: str | None = None

    def __post_init__(self) -> None:
        for name in ["years_active", "clubs_count", "matches", "goals", "assists", "trophies", "milestones", "turning_points"]:
            val = getattr(self, name)
            if not isinstance(val, int) or isinstance(val, bool) or val < 0:
                raise ValueError(f"{name} must be a non-negative integer")

        if self.peak_rating is not None and (
            not isinstance(self.peak_rating, int) or isinstance(self.peak_rating, bool) or self.peak_rating < 0
        ):
            raise ValueError("peak_rating must be a non-negative integer if provided")

        if self.peak_club is not None and not isinstance(self.peak_club, str):
            raise ValueError("peak_club must be a string if provided")

        if self.career_arc is not None and not isinstance(self.career_arc, str):
            raise ValueError("career_arc must be a string if provided")


@dataclass(frozen=True)
class CareerStatistics:
    appearances: int = 0
    goals: int = 0
    assists: int = 0
    clean_sheets: int = 0
    minutes: int = 0
    average_rating: float | None = None
    trophies: tuple[str, ...] = ()
    awards: tuple[str, ...] = ()
    international_caps: int = 0
    international_goals: int = 0
    international_assists: int = 0
    extra_stats: MappingProxyType = field(default_factory=lambda: MappingProxyType({}))

    def __post_init__(self) -> None:
        for name in ["appearances", "goals", "assists", "clean_sheets", "minutes"]:
            val = getattr(self, name)
            if not isinstance(val, int) or isinstance(val, bool) or val < 0:
                raise ValueError(f"{name} must be a non-negative integer")

        if self.average_rating is not None:
            if isinstance(self.average_rating, float) and (
                math.isnan(self.average_rating) or math.isinf(self.average_rating)
            ):
                raise ValueError("average_rating cannot be NaN or Infinity")
            if not isinstance(self.average_rating, (int, float)) or isinstance(self.average_rating, bool) or self.average_rating < 0:
                raise ValueError("average_rating must be a non-negative number if provided")

        for name, tuple_val in [("trophies", self.trophies), ("awards", self.awards)]:
            if not isinstance(tuple_val, tuple):
                object.__setattr__(self, name, tuple(tuple_val))
            for item in getattr(self, name):
                if not isinstance(item, str) or not item.strip():
                    raise ValueError(f"{name} must contain non-empty strings")

        object.__setattr__(self, "extra_stats", _to_immutable_mapping(self.extra_stats))


@dataclass(frozen=True)
class ClubPresentation:
    club_id: str
    club_name: str
    country: str | None = None
    start_date: str | None = None
    end_date: str | None = None
    season_count: int = 0
    appearances: int = 0
    goals: int = 0
    assists: int = 0
    trophies: tuple[str, ...] = ()
    role: str | None = None
    importance: float = 1.0

    def __post_init__(self) -> None:
        if not isinstance(self.club_id, str) or not self.club_id.strip():
            raise ValueError("club_id must be a non-empty string")
        if not isinstance(self.club_name, str) or not self.club_name.strip():
            raise ValueError("club_name must be a non-empty string")

        for name in ["season_count", "appearances", "goals", "assists"]:
            val = getattr(self, name)
            if not isinstance(val, int) or isinstance(val, bool) or val < 0:
                raise ValueError(f"{name} must be a non-negative integer")

        if not isinstance(self.trophies, tuple):
            object.__setattr__(self, "trophies", tuple(self.trophies))
        for item in self.trophies:
            if not isinstance(item, str) or not item.strip():
                raise ValueError("trophies must contain non-empty strings")

        if isinstance(self.importance, float) and (math.isnan(self.importance) or math.isinf(self.importance)):
            raise ValueError("importance cannot be NaN or Infinity")
        if not isinstance(self.importance, (int, float)) or isinstance(self.importance, bool):
            raise ValueError("importance must be a number")


@dataclass(frozen=True)
class SeasonPresentation:
    season_id: str
    season_label: str
    club_id: str | None = None
    club_name: str | None = None
    appearances: int = 0
    goals: int = 0
    assists: int = 0
    average_rating: float | None = None
    league_position: int | None = None
    league_name: str | None = None
    domestic_cup_result: str | None = None
    continental_result: str | None = None
    international_caps: int = 0
    international_goals: int = 0
    trophies: tuple[str, ...] = ()
    important_events: tuple[str, ...] = ()
    milestones: tuple[str, ...] = ()
    turning_points: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not isinstance(self.season_id, str) or not self.season_id.strip():
            raise ValueError("season_id must be a non-empty string")
        if not isinstance(self.season_label, str) or not self.season_label.strip():
            raise ValueError("season_label must be a non-empty string")

        for name in ["appearances", "goals", "assists"]:
            val = getattr(self, name)
            if not isinstance(val, int) or isinstance(val, bool) or val < 0:
                raise ValueError(f"{name} must be a non-negative integer")

        if self.average_rating is not None:
            if isinstance(self.average_rating, float) and (
                math.isnan(self.average_rating) or math.isinf(self.average_rating)
            ):
                raise ValueError("average_rating cannot be NaN or Infinity")
            if not isinstance(self.average_rating, (int, float)) or isinstance(self.average_rating, bool) or self.average_rating < 0:
                raise ValueError("average_rating must be a non-negative number if provided")

        for name, tuple_val in [
            ("trophies", self.trophies),
            ("important_events", self.important_events),
            ("milestones", self.milestones),
            ("turning_points", self.turning_points),
        ]:
            if not isinstance(tuple_val, tuple):
                object.__setattr__(self, name, tuple(tuple_val))
            for item in getattr(self, name):
                if not isinstance(item, str) or not item.strip():
                    raise ValueError(f"{name} must contain non-empty strings")


@dataclass(frozen=True)
class TimelineEntry:
    timeline_id: str
    date_or_season: str
    entry_type: TimelineEntryType
    title: str
    summary: str
    importance: float = 1.0
    priority: VisualPriority = VisualPriority.MEDIUM
    source_reference: PresentationSourceReference = field(default_factory=PresentationSourceReference)

    def __post_init__(self) -> None:
        if not isinstance(self.timeline_id, str) or not self.timeline_id.strip():
            raise ValueError("timeline_id must be a non-empty string")
        if not isinstance(self.date_or_season, str) or not self.date_or_season.strip():
            raise ValueError("date_or_season must be a non-empty string")

        if isinstance(self.entry_type, str):
            try:
                object.__setattr__(self, "entry_type", TimelineEntryType(self.entry_type))
            except ValueError:
                raise ValueError(f"Invalid TimelineEntryType: '{self.entry_type}'")
        elif not isinstance(self.entry_type, TimelineEntryType):
            raise ValueError(f"Invalid TimelineEntryType: '{self.entry_type}'")

        if not isinstance(self.title, str):
            raise ValueError("title must be a string")
        if not isinstance(self.summary, str):
            raise ValueError("summary must be a string")

        if isinstance(self.importance, float) and (math.isnan(self.importance) or math.isinf(self.importance)):
            raise ValueError("importance cannot be NaN or Infinity")
        if not isinstance(self.importance, (int, float)) or isinstance(self.importance, bool):
            raise ValueError("importance must be a number")

        if isinstance(self.priority, str):
            try:
                object.__setattr__(self, "priority", VisualPriority(self.priority))
            except ValueError:
                raise ValueError(f"Invalid VisualPriority: '{self.priority}'")
        elif not isinstance(self.priority, VisualPriority):
            raise ValueError(f"Invalid VisualPriority: '{self.priority}'")

        if not isinstance(self.source_reference, PresentationSourceReference):
            raise ValueError(f"Expected PresentationSourceReference, got {type(self.source_reference)}")


@dataclass(frozen=True)
class CareerHighlight:
    highlight_id: str
    highlight_type: HighlightType
    title: str
    description: str
    priority: VisualPriority = VisualPriority.HIGH
    source_reference: PresentationSourceReference = field(default_factory=PresentationSourceReference)

    def __post_init__(self) -> None:
        if not isinstance(self.highlight_id, str) or not self.highlight_id.strip():
            raise ValueError("highlight_id must be a non-empty string")

        if isinstance(self.highlight_type, str):
            try:
                object.__setattr__(self, "highlight_type", HighlightType(self.highlight_type))
            except ValueError:
                raise ValueError(f"Invalid HighlightType: '{self.highlight_type}'")
        elif not isinstance(self.highlight_type, HighlightType):
            raise ValueError(f"Invalid HighlightType: '{self.highlight_type}'")

        if not isinstance(self.title, str):
            raise ValueError("title must be a string")
        if not isinstance(self.description, str):
            raise ValueError("description must be a string")

        if isinstance(self.priority, str):
            try:
                object.__setattr__(self, "priority", VisualPriority(self.priority))
            except ValueError:
                raise ValueError(f"Invalid VisualPriority: '{self.priority}'")
        elif not isinstance(self.priority, VisualPriority):
            raise ValueError(f"Invalid VisualPriority: '{self.priority}'")

        if not isinstance(self.source_reference, PresentationSourceReference):
            raise ValueError(f"Expected PresentationSourceReference, got {type(self.source_reference)}")


@dataclass(frozen=True)
class CareerArcPresentation:
    arc_id: str
    arc_type: str
    status: str
    start_reference: str | None = None
    end_reference: str | None = None
    phases: tuple[str, ...] = ()
    current_phase: str | None = None
    history: tuple[str, ...] = ()
    source_reference: PresentationSourceReference = field(default_factory=PresentationSourceReference)

    def __post_init__(self) -> None:
        if not isinstance(self.arc_id, str) or not self.arc_id.strip():
            raise ValueError("arc_id must be a non-empty string")
        if not isinstance(self.arc_type, str) or not self.arc_type.strip():
            raise ValueError("arc_type must be a non-empty string")
        if not isinstance(self.status, str) or not self.status.strip():
            raise ValueError("status must be a non-empty string")

        for name, tuple_val in [("phases", self.phases), ("history", self.history)]:
            if not isinstance(tuple_val, tuple):
                object.__setattr__(self, name, tuple(tuple_val))
            for item in getattr(self, name):
                if not isinstance(item, str) or not item.strip():
                    raise ValueError(f"{name} must contain non-empty strings")

        if not isinstance(self.source_reference, PresentationSourceReference):
            raise ValueError(f"Expected PresentationSourceReference, got {type(self.source_reference)}")


@dataclass(frozen=True)
class RelationshipPresentation:
    relationship_id: str
    target_entity_id: str
    target_entity_name: str
    relationship_type: str
    status: str
    strength: float = 1.0
    start_reference: str | None = None
    end_reference: str | None = None
    source_reference: PresentationSourceReference = field(default_factory=PresentationSourceReference)

    def __post_init__(self) -> None:
        if not isinstance(self.relationship_id, str) or not self.relationship_id.strip():
            raise ValueError("relationship_id must be a non-empty string")
        if not isinstance(self.target_entity_id, str) or not self.target_entity_id.strip():
            raise ValueError("target_entity_id must be a non-empty string")
        if not isinstance(self.target_entity_name, str) or not self.target_entity_name.strip():
            raise ValueError("target_entity_name must be a non-empty string")
        if not isinstance(self.relationship_type, str) or not self.relationship_type.strip():
            raise ValueError("relationship_type must be a non-empty string")
        if not isinstance(self.status, str) or not self.status.strip():
            raise ValueError("status must be a non-empty string")

        if isinstance(self.strength, float) and (math.isnan(self.strength) or math.isinf(self.strength)):
            raise ValueError("strength cannot be NaN or Infinity")
        if not isinstance(self.strength, (int, float)) or isinstance(self.strength, bool):
            raise ValueError("strength must be a number")

        if not isinstance(self.source_reference, PresentationSourceReference):
            raise ValueError(f"Expected PresentationSourceReference, got {type(self.source_reference)}")


@dataclass(frozen=True)
class NarrativePresentation:
    story_id: str
    premise: str
    theme: tuple[str, ...] = ()
    acts: tuple[MappingProxyType, ...] = ()
    beats: tuple[MappingProxyType, ...] = ()
    threads: tuple[MappingProxyType, ...] = ()
    conflicts: tuple[MappingProxyType, ...] = ()
    opening: str | None = None
    climax: str | None = None
    resolution: str | None = None
    source_reference: PresentationSourceReference = field(default_factory=PresentationSourceReference)

    def __post_init__(self) -> None:
        if not isinstance(self.story_id, str) or not self.story_id.strip():
            raise ValueError("story_id must be a non-empty string")
        if not isinstance(self.premise, str):
            raise ValueError("premise must be a string")

        if not isinstance(self.theme, tuple):
            object.__setattr__(self, "theme", tuple(self.theme))

        for name in ["acts", "beats", "threads", "conflicts"]:
            val = getattr(self, name)
            if not isinstance(val, tuple):
                converted = tuple(_to_immutable_mapping(item) if isinstance(item, (dict, MappingProxyType)) else item for item in val)
                object.__setattr__(self, name, converted)

        if not isinstance(self.source_reference, PresentationSourceReference):
            raise ValueError(f"Expected PresentationSourceReference, got {type(self.source_reference)}")


@dataclass(frozen=True)
class ScriptPresentation:
    script_id: str
    hook: str | None = None
    introduction: str | None = None
    sections: tuple[MappingProxyType, ...] = ()
    segments: tuple[MappingProxyType, ...] = ()
    transitions: tuple[MappingProxyType, ...] = ()
    climax: str | None = None
    resolution: str | None = None
    closing: str | None = None
    word_count: int = 0
    estimated_duration: float = 0.0
    source_reference: PresentationSourceReference = field(default_factory=PresentationSourceReference)

    def __post_init__(self) -> None:
        if not isinstance(self.script_id, str) or not self.script_id.strip():
            raise ValueError("script_id must be a non-empty string")

        for name in ["sections", "segments", "transitions"]:
            val = getattr(self, name)
            if not isinstance(val, tuple):
                converted = tuple(_to_immutable_mapping(item) if isinstance(item, (dict, MappingProxyType)) else item for item in val)
                object.__setattr__(self, name, converted)

        if not isinstance(self.word_count, int) or isinstance(self.word_count, bool) or self.word_count < 0:
            raise ValueError("word_count must be a non-negative integer")

        if isinstance(self.estimated_duration, float) and (
            math.isnan(self.estimated_duration) or math.isinf(self.estimated_duration)
        ):
            raise ValueError("estimated_duration cannot be NaN or Infinity")
        if not isinstance(self.estimated_duration, (int, float)) or isinstance(self.estimated_duration, bool) or self.estimated_duration < 0:
            raise ValueError("estimated_duration must be a non-negative number")

        if not isinstance(self.source_reference, PresentationSourceReference):
            raise ValueError(f"Expected PresentationSourceReference, got {type(self.source_reference)}")


@dataclass(frozen=True)
class PresentationMetadata:
    presentation_id: str
    player_id: str
    created_from_story_id: str | None = None
    created_from_script_id: str | None = None
    density: PresentationDensity = PresentationDensity.STANDARD
    section_order: tuple[PresentationSectionType, ...] = ()
    version: str = "1.0"
    extra: MappingProxyType = field(default_factory=lambda: MappingProxyType({}))

    def __post_init__(self) -> None:
        if not isinstance(self.presentation_id, str) or not self.presentation_id.strip():
            raise ValueError("presentation_id must be a non-empty string")
        if not isinstance(self.player_id, str) or not self.player_id.strip():
            raise ValueError("player_id must be a non-empty string")

        if isinstance(self.density, str):
            try:
                object.__setattr__(self, "density", PresentationDensity(self.density))
            except ValueError:
                raise ValueError(f"Invalid PresentationDensity: '{self.density}'")
        elif not isinstance(self.density, PresentationDensity):
            raise ValueError(f"Invalid PresentationDensity: '{self.density}'")

        if not isinstance(self.section_order, tuple):
            converted_sections = []
            for sec in self.section_order:
                if isinstance(sec, str):
                    converted_sections.append(PresentationSectionType(sec))
                else:
                    converted_sections.append(sec)
            object.__setattr__(self, "section_order", tuple(converted_sections))
        for sec in self.section_order:
            if not isinstance(sec, PresentationSectionType):
                raise ValueError(f"Expected PresentationSectionType, got {type(sec)}")

        if not isinstance(self.version, str):
            raise ValueError("version must be a string")

        object.__setattr__(self, "extra", _to_immutable_mapping(self.extra))


@dataclass(frozen=True)
class CareerPresentation:
    presentation_id: str
    player: PlayerPresentation
    overview: CareerOverview
    statistics: CareerStatistics
    clubs: tuple[ClubPresentation, ...] = ()
    seasons: tuple[SeasonPresentation, ...] = ()
    timeline: tuple[TimelineEntry, ...] = ()
    highlights: tuple[CareerHighlight, ...] = ()
    career_arcs: tuple[CareerArcPresentation, ...] = ()
    relationships: tuple[RelationshipPresentation, ...] = ()
    narrative: NarrativePresentation | None = None
    script: ScriptPresentation | None = None
    metadata: PresentationMetadata = field(
        default_factory=lambda: PresentationMetadata(presentation_id="default", player_id="default")
    )
    source_reference: PresentationSourceReference = field(default_factory=PresentationSourceReference)

    def __post_init__(self) -> None:
        if not isinstance(self.presentation_id, str) or not self.presentation_id.strip():
            raise ValueError("presentation_id must be a non-empty string")

        if not isinstance(self.player, PlayerPresentation):
            raise ValueError(f"Expected PlayerPresentation, got {type(self.player)}")
        if not isinstance(self.overview, CareerOverview):
            raise ValueError(f"Expected CareerOverview, got {type(self.overview)}")
        if not isinstance(self.statistics, CareerStatistics):
            raise ValueError(f"Expected CareerStatistics, got {type(self.statistics)}")

        tuple_checks = [
            ("clubs", self.clubs, ClubPresentation),
            ("seasons", self.seasons, SeasonPresentation),
            ("timeline", self.timeline, TimelineEntry),
            ("highlights", self.highlights, CareerHighlight),
            ("career_arcs", self.career_arcs, CareerArcPresentation),
            ("relationships", self.relationships, RelationshipPresentation),
        ]
        for name, field_val, expected_cls in tuple_checks:
            if not isinstance(field_val, tuple):
                object.__setattr__(self, name, tuple(field_val))
            for item in getattr(self, name):
                if not isinstance(item, expected_cls):
                    raise ValueError(f"Expected {expected_cls.__name__} in {name}, got {type(item)}")

        if self.narrative is not None and not isinstance(self.narrative, NarrativePresentation):
            raise ValueError(f"Expected NarrativePresentation, got {type(self.narrative)}")

        if self.script is not None and not isinstance(self.script, ScriptPresentation):
            raise ValueError(f"Expected ScriptPresentation, got {type(self.script)}")

        if not isinstance(self.metadata, PresentationMetadata):
            raise ValueError(f"Expected PresentationMetadata, got {type(self.metadata)}")

        if not isinstance(self.source_reference, PresentationSourceReference):
            raise ValueError(f"Expected PresentationSourceReference, got {type(self.source_reference)}")


@dataclass(frozen=True)
class PresentationBuildResult:
    success: bool
    presentation: CareerPresentation | None = None
    error_code: PresentationErrorCode | None = None
    error_message: str | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.success, bool):
            raise ValueError("success must be a boolean")

        if self.success:
            if not isinstance(self.presentation, CareerPresentation):
                raise ValueError("presentation must be CareerPresentation when success=True")
        else:
            if self.error_code is not None:
                if isinstance(self.error_code, str):
                    try:
                        object.__setattr__(self, "error_code", PresentationErrorCode(self.error_code))
                    except ValueError:
                        raise ValueError(f"Invalid PresentationErrorCode: '{self.error_code}'")
                elif not isinstance(self.error_code, PresentationErrorCode):
                    raise ValueError(f"Invalid PresentationErrorCode: '{self.error_code}'")
