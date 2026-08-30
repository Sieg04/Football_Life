from dataclasses import dataclass, field
from enum import StrEnum
from types import MappingProxyType
from typing import Any

from app.event.domain import _to_immutable_mapping
from app.event.presentation_domain import CareerStatus, VisualPriority


class ReplayMomentType(StrEnum):
    CAREER_START = "CAREER_START"
    DEBUT = "DEBUT"
    GOAL_MILESTONE = "GOAL_MILESTONE"
    STAT_MILESTONE = "STAT_MILESTONE"
    TRANSFER = "TRANSFER"
    ACHIEVEMENT = "ACHIEVEMENT"
    CONFLICT = "CONFLICT"
    TURNING_POINT = "TURNING_POINT"
    BREAKTHROUGH = "BREAKTHROUGH"
    COMEBACK = "COMEBACK"
    CAREER_PEAK = "CAREER_PEAK"
    CAREER_END = "CAREER_END"
    SEASON = "SEASON"
    OTHER = "OTHER"


class SceneType(StrEnum):
    INTRO = "INTRO"
    CAREER_MOMENT = "CAREER_MOMENT"
    SEASON = "SEASON"
    TRANSFER = "TRANSFER"
    ACHIEVEMENT = "ACHIEVEMENT"
    CONFLICT = "CONFLICT"
    TURNING_POINT = "TURNING_POINT"
    CLIMAX = "CLIMAX"
    ENDING = "ENDING"
    STAT_CARD = "STAT_CARD"


class ScenePriority(StrEnum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class CapturePresetType(StrEnum):
    CINEMATIC = "CINEMATIC"
    MATCHDAY = "MATCHDAY"
    DOCUMENTARY = "DOCUMENTARY"
    PROFILE = "PROFILE"


class ReplayErrorCode(StrEnum):
    INVALID_SOURCE = "INVALID_SOURCE"
    INVALID_MOMENT = "INVALID_MOMENT"
    INVALID_SCENE = "INVALID_SCENE"
    DUPLICATE_SCENE = "DUPLICATE_SCENE"
    INVALID_ORDER = "INVALID_ORDER"
    EMPTY_CONTENT_STORY = "EMPTY_CONTENT_STORY"
    INVALID_CAPTURE_FRAME = "INVALID_CAPTURE_FRAME"
    INVALID_REFERENCE = "INVALID_REFERENCE"
    INCONSISTENT_STATE = "INCONSISTENT_STATE"


class ReplayProcessingException(Exception):
    def __init__(self, error_code: ReplayErrorCode | str, message: str) -> None:
        self.error_code = (
            ReplayErrorCode(error_code)
            if isinstance(error_code, str)
            else error_code
        )
        self.message = message
        super().__init__(f"[{self.error_code.value}] {message}")


@dataclass(frozen=True)
class ReplaySeason:
    season_id: str
    season_label: str
    season_index: int
    club_id: str
    club_name: str
    appearances: int
    goals: int
    assists: int
    trophies: tuple[str, ...]
    ovr: int
    moment_ids: tuple[str, ...]
    source_references: MappingProxyType = field(
        default_factory=lambda: MappingProxyType({})
    )

    def __post_init__(self) -> None:
        if not isinstance(self.season_id, str) or not self.season_id.strip():
            raise ValueError("season_id must be a non-empty string")
        if not isinstance(self.season_label, str) or not self.season_label.strip():
            raise ValueError("season_label must be a non-empty string")
        if not isinstance(self.season_index, int) or isinstance(self.season_index, bool):
            raise ValueError("season_index must be an integer")
        if not isinstance(self.club_id, str) or not self.club_id.strip():
            raise ValueError("club_id must be a non-empty string")
        if not isinstance(self.club_name, str) or not self.club_name.strip():
            raise ValueError("club_name must be a non-empty string")
        if not isinstance(self.appearances, int) or isinstance(self.appearances, bool) or self.appearances < 0:
            raise ValueError("appearances must be a non-negative integer")
        if not isinstance(self.goals, int) or isinstance(self.goals, bool) or self.goals < 0:
            raise ValueError("goals must be a non-negative integer")
        if not isinstance(self.assists, int) or isinstance(self.assists, bool) or self.assists < 0:
            raise ValueError("assists must be a non-negative integer")
        if not isinstance(self.trophies, tuple):
            object.__setattr__(self, "trophies", tuple(self.trophies))
        if not isinstance(self.ovr, int) or isinstance(self.ovr, bool) or self.ovr < 0:
            raise ValueError("ovr must be a non-negative integer")
        if not isinstance(self.moment_ids, tuple):
            object.__setattr__(self, "moment_ids", tuple(self.moment_ids))
        immutable_ref = _to_immutable_mapping(self.source_references)
        object.__setattr__(self, "source_references", immutable_ref)


@dataclass(frozen=True)
class ReplayMoment:
    moment_id: str
    moment_type: ReplayMomentType
    title: str
    description: str
    season_id: str
    priority: ScenePriority
    visual_priority: VisualPriority
    source_event_ids: tuple[str, ...] = ()
    source_milestone_ids: tuple[str, ...] = ()
    source_turning_point_ids: tuple[str, ...] = ()
    source_seed_ids: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not isinstance(self.moment_id, str) or not self.moment_id.strip():
            raise ValueError("moment_id must be a non-empty string")

        if isinstance(self.moment_type, str):
            object.__setattr__(self, "moment_type", ReplayMomentType(self.moment_type))
        elif not isinstance(self.moment_type, ReplayMomentType):
            raise ValueError(f"Invalid moment_type: {self.moment_type}")

        if not isinstance(self.title, str) or not self.title.strip():
            raise ValueError("title must be a non-empty string")
        if not isinstance(self.description, str):
            raise ValueError("description must be a string")
        if not isinstance(self.season_id, str) or not self.season_id.strip():
            raise ValueError("season_id must be a non-empty string")

        if isinstance(self.priority, str):
            object.__setattr__(self, "priority", ScenePriority(self.priority))
        elif not isinstance(self.priority, ScenePriority):
            raise ValueError(f"Invalid priority: {self.priority}")

        if isinstance(self.visual_priority, str):
            object.__setattr__(self, "visual_priority", VisualPriority(self.visual_priority))
        elif not isinstance(self.visual_priority, VisualPriority):
            raise ValueError(f"Invalid visual_priority: {self.visual_priority}")

        if not isinstance(self.source_event_ids, tuple):
            object.__setattr__(self, "source_event_ids", tuple(self.source_event_ids))
        if not isinstance(self.source_milestone_ids, tuple):
            object.__setattr__(self, "source_milestone_ids", tuple(self.source_milestone_ids))
        if not isinstance(self.source_turning_point_ids, tuple):
            object.__setattr__(self, "source_turning_point_ids", tuple(self.source_turning_point_ids))
        if not isinstance(self.source_seed_ids, tuple):
            object.__setattr__(self, "source_seed_ids", tuple(self.source_seed_ids))


@dataclass(frozen=True)
class CareerReplay:
    replay_id: str
    career_id: str
    player_id: str
    player_name: str
    career_status: CareerStatus
    seasons: tuple[ReplaySeason, ...]
    moments: tuple[ReplayMoment, ...]
    source_story_id: str | None = None
    source_script_id: str | None = None
    source_presentation_id: str | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.replay_id, str) or not self.replay_id.strip():
            raise ValueError("replay_id must be a non-empty string")
        if not isinstance(self.career_id, str) or not self.career_id.strip():
            raise ValueError("career_id must be a non-empty string")
        if not isinstance(self.player_id, str) or not self.player_id.strip():
            raise ValueError("player_id must be a non-empty string")
        if not isinstance(self.player_name, str) or not self.player_name.strip():
            raise ValueError("player_name must be a non-empty string")

        if isinstance(self.career_status, str):
            object.__setattr__(self, "career_status", CareerStatus(self.career_status))
        elif not isinstance(self.career_status, CareerStatus):
            raise ValueError(f"Invalid career_status: {self.career_status}")

        if not isinstance(self.seasons, tuple):
            object.__setattr__(self, "seasons", tuple(self.seasons))
        if not isinstance(self.moments, tuple):
            object.__setattr__(self, "moments", tuple(self.moments))


@dataclass(frozen=True)
class ContentScene:
    scene_id: str
    scene_type: SceneType
    title: str
    subtitle: str
    description: str
    order_index: int
    priority: ScenePriority
    moment_id: str | None = None
    season_id: str | None = None
    source_references: MappingProxyType = field(
        default_factory=lambda: MappingProxyType({})
    )
    script_segment_ids: tuple[str, ...] = ()
    presentation_references: MappingProxyType = field(
        default_factory=lambda: MappingProxyType({})
    )

    def __post_init__(self) -> None:
        if not isinstance(self.scene_id, str) or not self.scene_id.strip():
            raise ValueError("scene_id must be a non-empty string")

        if isinstance(self.scene_type, str):
            object.__setattr__(self, "scene_type", SceneType(self.scene_type))
        elif not isinstance(self.scene_type, SceneType):
            raise ValueError(f"Invalid scene_type: {self.scene_type}")

        if not isinstance(self.title, str):
            raise ValueError("title must be a string")
        if not isinstance(self.subtitle, str):
            raise ValueError("subtitle must be a string")
        if not isinstance(self.description, str):
            raise ValueError("description must be a string")
        if not isinstance(self.order_index, int) or isinstance(self.order_index, bool) or self.order_index < 0:
            raise ValueError("order_index must be a non-negative integer")

        if isinstance(self.priority, str):
            object.__setattr__(self, "priority", ScenePriority(self.priority))
        elif not isinstance(self.priority, ScenePriority):
            raise ValueError(f"Invalid priority: {self.priority}")

        if not isinstance(self.script_segment_ids, tuple):
            object.__setattr__(self, "script_segment_ids", tuple(self.script_segment_ids))

        immutable_src = _to_immutable_mapping(self.source_references)
        object.__setattr__(self, "source_references", immutable_src)

        immutable_pres = _to_immutable_mapping(self.presentation_references)
        object.__setattr__(self, "presentation_references", immutable_pres)


@dataclass(frozen=True)
class ContentStory:
    content_story_id: str
    career_id: str
    title: str
    scenes: tuple[ContentScene, ...]
    total_scenes: int
    estimated_duration_seconds: float
    source_story_id: str | None = None
    source_script_id: str | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.content_story_id, str) or not self.content_story_id.strip():
            raise ValueError("content_story_id must be a non-empty string")
        if not isinstance(self.career_id, str) or not self.career_id.strip():
            raise ValueError("career_id must be a non-empty string")
        if not isinstance(self.title, str):
            raise ValueError("title must be a string")

        if not isinstance(self.scenes, tuple):
            object.__setattr__(self, "scenes", tuple(self.scenes))

        if not isinstance(self.total_scenes, int) or isinstance(self.total_scenes, bool) or self.total_scenes < 0:
            raise ValueError("total_scenes must be a non-negative integer")

        if not isinstance(self.estimated_duration_seconds, (int, float)) or self.estimated_duration_seconds < 0:
            raise ValueError("estimated_duration_seconds must be a non-negative number")


@dataclass(frozen=True)
class CapturePreset:
    preset_id: str
    preset_type: CapturePresetType
    width: int = 1920
    height: int = 1080
    show_navigation: bool = False
    show_controls: bool = False
    show_branding: bool = True
    show_statistics: bool = True
    show_player_identity: bool = True
    show_season: bool = True

    def __post_init__(self) -> None:
        if not isinstance(self.preset_id, str) or not self.preset_id.strip():
            raise ValueError("preset_id must be a non-empty string")

        if isinstance(self.preset_type, str):
            object.__setattr__(self, "preset_type", CapturePresetType(self.preset_type))
        elif not isinstance(self.preset_type, CapturePresetType):
            raise ValueError(f"Invalid preset_type: {self.preset_type}")

        if not isinstance(self.width, int) or isinstance(self.width, bool) or self.width <= 0:
            raise ValueError("width must be a positive integer")
        if not isinstance(self.height, int) or isinstance(self.height, bool) or self.height <= 0:
            raise ValueError("height must be a positive integer")


@dataclass(frozen=True)
class CaptureFrame:
    frame_id: str
    scene_id: str
    preset: CapturePreset
    player_name: str
    club_name: str
    season: str
    headline: str
    subheadline: str
    statistics: MappingProxyType
    visual_priority: ScenePriority
    script_text: str | None = None
    metadata: MappingProxyType = field(
        default_factory=lambda: MappingProxyType({})
    )

    def __post_init__(self) -> None:
        if not isinstance(self.frame_id, str) or not self.frame_id.strip():
            raise ValueError("frame_id must be a non-empty string")
        if not isinstance(self.scene_id, str) or not self.scene_id.strip():
            raise ValueError("scene_id must be a non-empty string")
        if not isinstance(self.preset, CapturePreset):
            raise ValueError("preset must be a CapturePreset instance")
        if not isinstance(self.player_name, str):
            raise ValueError("player_name must be a string")
        if not isinstance(self.club_name, str):
            raise ValueError("club_name must be a string")
        if not isinstance(self.season, str):
            raise ValueError("season must be a string")
        if not isinstance(self.headline, str):
            raise ValueError("headline must be a string")
        if not isinstance(self.subheadline, str):
            raise ValueError("subheadline must be a string")

        if isinstance(self.visual_priority, str):
            object.__setattr__(self, "visual_priority", ScenePriority(self.visual_priority))
        elif not isinstance(self.visual_priority, ScenePriority):
            raise ValueError(f"Invalid visual_priority: {self.visual_priority}")

        immutable_stats = _to_immutable_mapping(self.statistics)
        object.__setattr__(self, "statistics", immutable_stats)

        immutable_meta = _to_immutable_mapping(self.metadata)
        object.__setattr__(self, "metadata", immutable_meta)


@dataclass(frozen=True)
class ReplayBuildResult:
    success: bool
    replay: CareerReplay | None = None
    errors: tuple[str, ...] = ()
    warnings: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not isinstance(self.success, bool):
            raise ValueError("success must be a boolean")
        if not isinstance(self.errors, tuple):
            object.__setattr__(self, "errors", tuple(self.errors))
        if not isinstance(self.warnings, tuple):
            object.__setattr__(self, "warnings", tuple(self.warnings))


@dataclass(frozen=True)
class ContentStoryBuildResult:
    success: bool
    content_story: ContentStory | None = None
    errors: tuple[str, ...] = ()
    warnings: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not isinstance(self.success, bool):
            raise ValueError("success must be a boolean")
        if not isinstance(self.errors, tuple):
            object.__setattr__(self, "errors", tuple(self.errors))
        if not isinstance(self.warnings, tuple):
            object.__setattr__(self, "warnings", tuple(self.warnings))
