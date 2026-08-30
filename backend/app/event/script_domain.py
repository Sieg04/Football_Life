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


class ScriptSectionType(StrEnum):
    HOOK = "HOOK"
    INTRODUCTION = "INTRODUCTION"
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
    CLOSING = "CLOSING"


class ScriptSegmentType(StrEnum):
    HOOK = "HOOK"
    INTRODUCTION = "INTRODUCTION"
    NARRATION = "NARRATION"
    TRANSITION = "TRANSITION"
    CLIMAX = "CLIMAX"
    RESOLUTION = "RESOLUTION"
    CLOSING = "CLOSING"


class TransitionType(StrEnum):
    TIME_ADVANCE = "TIME_ADVANCE"
    CAUSE = "CAUSE"
    CONTRAST = "CONTRAST"
    ESCALATION = "ESCALATION"
    TURNING_POINT = "TURNING_POINT"
    RECOVERY = "RECOVERY"
    PEAK = "PEAK"
    RESOLUTION = "RESOLUTION"
    SEQUENTIAL = "SEQUENTIAL"


class HookType(StrEnum):
    ORIGIN_HOOK = "ORIGIN_HOOK"
    COLD_OPEN = "COLD_OPEN"
    MAJOR_ACHIEVEMENT = "MAJOR_ACHIEVEMENT"
    CAREER_CONTRAST = "CAREER_CONTRAST"
    CRISIS = "CRISIS"
    COMEBACK = "COMEBACK"
    RIVALRY = "RIVALRY"
    MYSTERY = "MYSTERY"
    LEGACY = "LEGACY"
    NO_HOOK = "NO_HOOK"


class ClosingType(StrEnum):
    LEGACY = "LEGACY"
    ONGOING = "ONGOING"
    RETIREMENT = "RETIREMENT"
    TRIUMPH = "TRIUMPH"
    REFLECTION = "REFLECTION"
    OPEN_ENDED = "OPEN_ENDED"


class NarrationTone(StrEnum):
    NEUTRAL = "NEUTRAL"
    DRAMATIC = "DRAMATIC"
    INSPIRATIONAL = "INSPIRATIONAL"
    DARK = "DARK"
    REFLECTIVE = "REFLECTIVE"
    TRIUMPHANT = "TRIUMPHANT"
    TENSE = "TENSE"


class NarrationPacing(StrEnum):
    SLOW = "SLOW"
    MODERATE = "MODERATE"
    FAST = "FAST"
    VERY_FAST = "VERY_FAST"
    CLIMACTIC = "CLIMACTIC"
    REFLECTIVE = "REFLECTIVE"


class ScriptDensity(StrEnum):
    COMPACT = "COMPACT"
    STANDARD = "STANDARD"
    DETAILED = "DETAILED"
    COMPLETE = "COMPLETE"


class NarrationStyle(StrEnum):
    DOCUMENTARY = "DOCUMENTARY"
    CINEMATIC = "CINEMATIC"
    DRAMATIC = "DRAMATIC"
    MINIMAL = "MINIMAL"
    FAST_PACED = "FAST_PACED"
    REFLECTIVE = "REFLECTIVE"


class ScriptErrorCode(StrEnum):
    INVALID_NARRATIVE_STORY = "INVALID_NARRATIVE_STORY"
    INVALID_SOURCE_REFERENCE = "INVALID_SOURCE_REFERENCE"
    UNSUPPORTED_FACTUAL_CLAIM = "UNSUPPORTED_FACTUAL_CLAIM"
    RETIREMENT_INCONSISTENCY = "RETIREMENT_INCONSISTENCY"
    MISSING_CLIMAX = "MISSING_CLIMAX"
    COHERENCE_VALIDATION_ERROR = "COHERENCE_VALIDATION_ERROR"
    SCRIPT_BUILD_ERROR = "SCRIPT_BUILD_ERROR"
    EMPTY_INPUT = "EMPTY_INPUT"


class ScriptProcessingException(Exception):
    """Exception raised when script generation or validation fails atomically."""

    def __init__(self, code: ScriptErrorCode, message: str) -> None:
        super().__init__(f"[{code.value}] {message}")
        self.code = code
        self.message = message


@dataclass(frozen=True)
class ScriptSourceReference:
    story_id: str | None = None
    act_ids: tuple[str, ...] = ()
    beat_ids: tuple[str, ...] = ()
    thread_ids: tuple[str, ...] = ()
    conflict_ids: tuple[str, ...] = ()
    event_ids: tuple[str, ...] = ()
    milestone_ids: tuple[str, ...] = ()
    turning_point_ids: tuple[str, ...] = ()
    seed_ids: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if self.story_id is not None and (not isinstance(self.story_id, str) or not self.story_id.strip()):
            raise ValueError("story_id must be a non-empty string if provided")

        for name, field_val in [
            ("act_ids", self.act_ids),
            ("beat_ids", self.beat_ids),
            ("thread_ids", self.thread_ids),
            ("conflict_ids", self.conflict_ids),
            ("event_ids", self.event_ids),
            ("milestone_ids", self.milestone_ids),
            ("turning_point_ids", self.turning_point_ids),
            ("seed_ids", self.seed_ids),
        ]:
            if not isinstance(field_val, tuple):
                object.__setattr__(self, name, tuple(field_val))
            for item in getattr(self, name):
                if not isinstance(item, str) or not item.strip():
                    raise ValueError(f"{name} must contain non-empty strings")


@dataclass(frozen=True)
class ScriptSegment:
    segment_id: str
    sequence: int
    segment_type: ScriptSegmentType
    text: str
    word_count: int
    estimated_duration_seconds: float
    pacing: NarrationPacing = NarrationPacing.MODERATE
    importance: float = 1.0
    source_reference: ScriptSourceReference = field(default_factory=ScriptSourceReference)
    metadata: MappingProxyType = field(default_factory=lambda: MappingProxyType({}))

    def __post_init__(self) -> None:
        if not isinstance(self.segment_id, str) or not self.segment_id.strip():
            raise ValueError("segment_id must be a non-empty string")

        if not isinstance(self.sequence, int) or isinstance(self.sequence, bool) or self.sequence < 0:
            raise ValueError("sequence must be a non-negative integer")

        if isinstance(self.segment_type, str):
            try:
                object.__setattr__(self, "segment_type", ScriptSegmentType(self.segment_type))
            except ValueError:
                raise ValueError(f"Invalid ScriptSegmentType: '{self.segment_type}'")
        elif not isinstance(self.segment_type, ScriptSegmentType):
            raise ValueError(f"Invalid ScriptSegmentType: '{self.segment_type}'")

        if not isinstance(self.text, str):
            raise ValueError("text must be a string")

        if not isinstance(self.word_count, int) or isinstance(self.word_count, bool) or self.word_count < 0:
            raise ValueError("word_count must be a non-negative integer")

        if isinstance(self.estimated_duration_seconds, float) and (
            math.isnan(self.estimated_duration_seconds) or math.isinf(self.estimated_duration_seconds)
        ):
            raise ValueError("estimated_duration_seconds cannot be NaN or Infinity")
        if not isinstance(self.estimated_duration_seconds, (int, float)) or isinstance(self.estimated_duration_seconds, bool) or self.estimated_duration_seconds < 0:
            raise ValueError("estimated_duration_seconds must be a non-negative number")

        if isinstance(self.pacing, str):
            try:
                object.__setattr__(self, "pacing", NarrationPacing(self.pacing))
            except ValueError:
                raise ValueError(f"Invalid NarrationPacing: '{self.pacing}'")
        elif not isinstance(self.pacing, NarrationPacing):
            raise ValueError(f"Invalid NarrationPacing: '{self.pacing}'")

        if isinstance(self.importance, float) and (math.isnan(self.importance) or math.isinf(self.importance)):
            raise ValueError("importance cannot be NaN or Infinity")
        if not isinstance(self.importance, (int, float)) or isinstance(self.importance, bool):
            raise ValueError("importance must be a number")

        if not isinstance(self.source_reference, ScriptSourceReference):
            raise ValueError(f"Expected ScriptSourceReference, got {type(self.source_reference)}")

        object.__setattr__(self, "metadata", _to_immutable_mapping(self.metadata))


@dataclass(frozen=True)
class ScriptTransition:
    transition_id: str
    transition_type: TransitionType
    from_section_id: str
    to_section_id: str
    text: str
    word_count: int
    estimated_duration_seconds: float
    source_reference: ScriptSourceReference = field(default_factory=ScriptSourceReference)
    metadata: MappingProxyType = field(default_factory=lambda: MappingProxyType({}))

    def __post_init__(self) -> None:
        if not isinstance(self.transition_id, str) or not self.transition_id.strip():
            raise ValueError("transition_id must be a non-empty string")

        if isinstance(self.transition_type, str):
            try:
                object.__setattr__(self, "transition_type", TransitionType(self.transition_type))
            except ValueError:
                raise ValueError(f"Invalid TransitionType: '{self.transition_type}'")
        elif not isinstance(self.transition_type, TransitionType):
            raise ValueError(f"Invalid TransitionType: '{self.transition_type}'")

        if not isinstance(self.from_section_id, str) or not self.from_section_id.strip():
            raise ValueError("from_section_id must be a non-empty string")

        if not isinstance(self.to_section_id, str) or not self.to_section_id.strip():
            raise ValueError("to_section_id must be a non-empty string")

        if not isinstance(self.text, str):
            raise ValueError("text must be a string")

        if not isinstance(self.word_count, int) or isinstance(self.word_count, bool) or self.word_count < 0:
            raise ValueError("word_count must be a non-negative integer")

        if isinstance(self.estimated_duration_seconds, float) and (
            math.isnan(self.estimated_duration_seconds) or math.isinf(self.estimated_duration_seconds)
        ):
            raise ValueError("estimated_duration_seconds cannot be NaN or Infinity")
        if not isinstance(self.estimated_duration_seconds, (int, float)) or isinstance(self.estimated_duration_seconds, bool) or self.estimated_duration_seconds < 0:
            raise ValueError("estimated_duration_seconds must be a non-negative number")

        if not isinstance(self.source_reference, ScriptSourceReference):
            raise ValueError(f"Expected ScriptSourceReference, got {type(self.source_reference)}")

        object.__setattr__(self, "metadata", _to_immutable_mapping(self.metadata))


@dataclass(frozen=True)
class ScriptHook:
    hook_id: str
    hook_type: HookType
    text: str
    segment: ScriptSegment
    source_reference: ScriptSourceReference = field(default_factory=ScriptSourceReference)
    metadata: MappingProxyType = field(default_factory=lambda: MappingProxyType({}))

    def __post_init__(self) -> None:
        if not isinstance(self.hook_id, str) or not self.hook_id.strip():
            raise ValueError("hook_id must be a non-empty string")

        if isinstance(self.hook_type, str):
            try:
                object.__setattr__(self, "hook_type", HookType(self.hook_type))
            except ValueError:
                raise ValueError(f"Invalid HookType: '{self.hook_type}'")
        elif not isinstance(self.hook_type, HookType):
            raise ValueError(f"Invalid HookType: '{self.hook_type}'")

        if not isinstance(self.text, str):
            raise ValueError("text must be a string")

        if not isinstance(self.segment, ScriptSegment):
            raise ValueError(f"Expected ScriptSegment, got {type(self.segment)}")

        if not isinstance(self.source_reference, ScriptSourceReference):
            raise ValueError(f"Expected ScriptSourceReference, got {type(self.source_reference)}")

        object.__setattr__(self, "metadata", _to_immutable_mapping(self.metadata))


@dataclass(frozen=True)
class ScriptClosing:
    closing_id: str
    closing_type: ClosingType
    text: str
    segment: ScriptSegment
    source_reference: ScriptSourceReference = field(default_factory=ScriptSourceReference)
    metadata: MappingProxyType = field(default_factory=lambda: MappingProxyType({}))

    def __post_init__(self) -> None:
        if not isinstance(self.closing_id, str) or not self.closing_id.strip():
            raise ValueError("closing_id must be a non-empty string")

        if isinstance(self.closing_type, str):
            try:
                object.__setattr__(self, "closing_type", ClosingType(self.closing_type))
            except ValueError:
                raise ValueError(f"Invalid ClosingType: '{self.closing_type}'")
        elif not isinstance(self.closing_type, ClosingType):
            raise ValueError(f"Invalid ClosingType: '{self.closing_type}'")

        if not isinstance(self.text, str):
            raise ValueError("text must be a string")

        if not isinstance(self.segment, ScriptSegment):
            raise ValueError(f"Expected ScriptSegment, got {type(self.segment)}")

        if not isinstance(self.source_reference, ScriptSourceReference):
            raise ValueError(f"Expected ScriptSourceReference, got {type(self.source_reference)}")

        object.__setattr__(self, "metadata", _to_immutable_mapping(self.metadata))


@dataclass(frozen=True)
class ScriptSection:
    section_id: str
    section_type: ScriptSectionType
    sequence: int
    title: str
    segments: tuple[ScriptSegment, ...] = ()
    act_id: str | None = None
    source_reference: ScriptSourceReference = field(default_factory=ScriptSourceReference)
    metadata: MappingProxyType = field(default_factory=lambda: MappingProxyType({}))

    def __post_init__(self) -> None:
        if not isinstance(self.section_id, str) or not self.section_id.strip():
            raise ValueError("section_id must be a non-empty string")

        if isinstance(self.section_type, str):
            try:
                object.__setattr__(self, "section_type", ScriptSectionType(self.section_type))
            except ValueError:
                raise ValueError(f"Invalid ScriptSectionType: '{self.section_type}'")
        elif not isinstance(self.section_type, ScriptSectionType):
            raise ValueError(f"Invalid ScriptSectionType: '{self.section_type}'")

        if not isinstance(self.sequence, int) or isinstance(self.sequence, bool) or self.sequence < 0:
            raise ValueError("sequence must be a non-negative integer")

        if not isinstance(self.title, str):
            raise ValueError("title must be a string")

        if self.act_id is not None and (not isinstance(self.act_id, str) or not self.act_id.strip()):
            raise ValueError("act_id must be non-empty string if provided")

        if not isinstance(self.segments, tuple):
            object.__setattr__(self, "segments", tuple(self.segments))
        for item in self.segments:
            if not isinstance(item, ScriptSegment):
                raise ValueError(f"Expected ScriptSegment, got {type(item)}")

        if not isinstance(self.source_reference, ScriptSourceReference):
            raise ValueError(f"Expected ScriptSourceReference, got {type(self.source_reference)}")

        object.__setattr__(self, "metadata", _to_immutable_mapping(self.metadata))


@dataclass(frozen=True)
class ScriptMetadata:
    story_id: str
    player_id: str
    density: ScriptDensity
    style: NarrationStyle
    tone: NarrationTone
    target_duration_seconds: float | None = None
    words_per_minute: int = 150
    created_version: str = "1.0"
    extra: MappingProxyType = field(default_factory=lambda: MappingProxyType({}))

    def __post_init__(self) -> None:
        if not isinstance(self.story_id, str) or not self.story_id.strip():
            raise ValueError("story_id must be a non-empty string")

        if not isinstance(self.player_id, str) or not self.player_id.strip():
            raise ValueError("player_id must be a non-empty string")

        if isinstance(self.density, str):
            try:
                object.__setattr__(self, "density", ScriptDensity(self.density))
            except ValueError:
                raise ValueError(f"Invalid ScriptDensity: '{self.density}'")
        elif not isinstance(self.density, ScriptDensity):
            raise ValueError(f"Invalid ScriptDensity: '{self.density}'")

        if isinstance(self.style, str):
            try:
                object.__setattr__(self, "style", NarrationStyle(self.style))
            except ValueError:
                raise ValueError(f"Invalid NarrationStyle: '{self.style}'")
        elif not isinstance(self.style, NarrationStyle):
            raise ValueError(f"Invalid NarrationStyle: '{self.style}'")

        if isinstance(self.tone, str):
            try:
                object.__setattr__(self, "tone", NarrationTone(self.tone))
            except ValueError:
                raise ValueError(f"Invalid NarrationTone: '{self.tone}'")
        elif not isinstance(self.tone, NarrationTone):
            raise ValueError(f"Invalid NarrationTone: '{self.tone}'")

        if self.target_duration_seconds is not None:
            if isinstance(self.target_duration_seconds, float) and (
                math.isnan(self.target_duration_seconds) or math.isinf(self.target_duration_seconds)
            ):
                raise ValueError("target_duration_seconds cannot be NaN or Infinity")
            if not isinstance(self.target_duration_seconds, (int, float)) or isinstance(self.target_duration_seconds, bool) or self.target_duration_seconds < 0:
                raise ValueError("target_duration_seconds must be a non-negative number")

        if not isinstance(self.words_per_minute, int) or isinstance(self.words_per_minute, bool) or self.words_per_minute <= 0:
            raise ValueError("words_per_minute must be a positive integer")

        if not isinstance(self.created_version, str):
            raise ValueError("created_version must be a string")

        object.__setattr__(self, "extra", _to_immutable_mapping(self.extra))


@dataclass(frozen=True)
class StoryScript:
    script_id: str
    metadata: ScriptMetadata
    title: str
    hook: ScriptHook | None = None
    introduction: ScriptSection | None = None
    sections: tuple[ScriptSection, ...] = ()
    transitions: tuple[ScriptTransition, ...] = ()
    climax: ScriptSegment | None = None
    resolution: ScriptSection | None = None
    closing: ScriptClosing | None = None
    word_count: int = 0
    estimated_duration_seconds: float = 0.0
    source_reference: ScriptSourceReference = field(default_factory=ScriptSourceReference)

    def __post_init__(self) -> None:
        if not isinstance(self.script_id, str) or not self.script_id.strip():
            raise ValueError("script_id must be a non-empty string")

        if not isinstance(self.metadata, ScriptMetadata):
            raise ValueError(f"Expected ScriptMetadata, got {type(self.metadata)}")

        if not isinstance(self.title, str):
            raise ValueError("title must be a string")

        if self.hook is not None and not isinstance(self.hook, ScriptHook):
            raise ValueError(f"Expected ScriptHook, got {type(self.hook)}")

        if self.introduction is not None and not isinstance(self.introduction, ScriptSection):
            raise ValueError(f"Expected ScriptSection for introduction, got {type(self.introduction)}")

        if not isinstance(self.sections, tuple):
            object.__setattr__(self, "sections", tuple(self.sections))
        for item in self.sections:
            if not isinstance(item, ScriptSection):
                raise ValueError(f"Expected ScriptSection, got {type(item)}")

        if not isinstance(self.transitions, tuple):
            object.__setattr__(self, "transitions", tuple(self.transitions))
        for item in self.transitions:
            if not isinstance(item, ScriptTransition):
                raise ValueError(f"Expected ScriptTransition, got {type(item)}")

        if self.climax is not None and not isinstance(self.climax, ScriptSegment):
            raise ValueError(f"Expected ScriptSegment for climax, got {type(self.climax)}")

        if self.resolution is not None and not isinstance(self.resolution, ScriptSection):
            raise ValueError(f"Expected ScriptSection for resolution, got {type(self.resolution)}")

        if self.closing is not None and not isinstance(self.closing, ScriptClosing):
            raise ValueError(f"Expected ScriptClosing, got {type(self.closing)}")

        if not isinstance(self.word_count, int) or isinstance(self.word_count, bool) or self.word_count < 0:
            raise ValueError("word_count must be a non-negative integer")

        if isinstance(self.estimated_duration_seconds, float) and (
            math.isnan(self.estimated_duration_seconds) or math.isinf(self.estimated_duration_seconds)
        ):
            raise ValueError("estimated_duration_seconds cannot be NaN or Infinity")
        if not isinstance(self.estimated_duration_seconds, (int, float)) or isinstance(self.estimated_duration_seconds, bool) or self.estimated_duration_seconds < 0:
            raise ValueError("estimated_duration_seconds must be a non-negative number")

        if not isinstance(self.source_reference, ScriptSourceReference):
            raise ValueError(f"Expected ScriptSourceReference, got {type(self.source_reference)}")


@dataclass(frozen=True)
class ScriptBuildResult:
    success: bool
    script: StoryScript | None = None
    error_code: ScriptErrorCode | None = None
    error_message: str | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.success, bool):
            raise ValueError("success must be a boolean")

        if self.success:
            if not isinstance(self.script, StoryScript):
                raise ValueError("script must be StoryScript when success=True")
        else:
            if self.error_code is not None:
                if isinstance(self.error_code, str):
                    try:
                        object.__setattr__(self, "error_code", ScriptErrorCode(self.error_code))
                    except ValueError:
                        raise ValueError(f"Invalid ScriptErrorCode: '{self.error_code}'")
                elif not isinstance(self.error_code, ScriptErrorCode):
                    raise ValueError(f"Invalid ScriptErrorCode: '{self.error_code}'")
