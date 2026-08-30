import hashlib
import json
import math
from dataclasses import dataclass, field
from enum import StrEnum
from types import MappingProxyType
from typing import Any


class EventType(StrEnum):
    PLAYER = "PLAYER"
    CAREER = "CAREER"
    CLUB = "CLUB"
    COMPETITION = "COMPETITION"
    TRANSFER = "TRANSFER"
    DEVELOPMENT = "DEVELOPMENT"
    MILESTONE = "MILESTONE"
    CONTEXTUAL = "CONTEXTUAL"


class EventStatus(StrEnum):
    PENDING = "PENDING"
    TRIGGERED = "TRIGGERED"
    RESOLVED = "RESOLVED"
    CANCELLED = "CANCELLED"
    EXPIRED = "EXPIRED"


def _is_valid_primitive(val: Any) -> bool:
    if val is None or isinstance(val, (str, int, bool)):
        return True
    if isinstance(val, float):
        return not (math.isnan(val) or math.isinf(val))
    if isinstance(val, tuple):
        return all(_is_valid_primitive(item) for item in val)
    if isinstance(val, MappingProxyType):
        return all(isinstance(k, str) and _is_valid_primitive(v) for k, v in val.items())
    return False


def _to_immutable_mapping(data: Any) -> MappingProxyType:
    if data is None:
        return MappingProxyType({})
    if isinstance(data, MappingProxyType):
        dict_data = dict(data)
    elif isinstance(data, dict):
        dict_data = dict(data)
    else:
        raise ValueError(f"Metadata or attributes must be a dict or MappingProxyType, got {type(data)}")

    converted: dict[str, Any] = {}
    for k, v in dict_data.items():
        if not isinstance(k, str) or not k.strip():
            raise ValueError("Mapping keys must be non-empty strings")
        converted[k] = _to_immutable_primitive(v)

    return MappingProxyType(converted)


def _to_immutable_primitive(val: Any) -> Any:
    if val is None or isinstance(val, (str, int, bool)):
        return val
    if isinstance(val, float):
        if math.isnan(val) or math.isinf(val):
            raise ValueError("Float values must not be NaN or Infinity")
        return val
    if isinstance(val, (list, tuple)):
        return tuple(_to_immutable_primitive(item) for item in val)
    if isinstance(val, (dict, MappingProxyType)):
        return _to_immutable_mapping(val)
    raise ValueError(f"Unsupported non-primitive value in metadata/attributes: {type(val)}")


@dataclass(frozen=True)
class EventReason:
    code: str
    value: float | int | str | bool | None = None
    weight: float = 1.0

    def __post_init__(self) -> None:
        if not isinstance(self.code, str) or not self.code.strip():
            raise ValueError("EventReason code must be a non-empty string")
        if isinstance(self.weight, float):
            if math.isnan(self.weight) or math.isinf(self.weight):
                raise ValueError("EventReason weight must not be NaN or Infinity")
        if self.weight < 0:
            raise ValueError("EventReason weight must be non-negative")
        if self.value is not None:
            if not _is_valid_primitive(self.value):
                raise ValueError("EventReason value must be a primitive type (str, int, float, bool, None)")


@dataclass(frozen=True)
class EventDefinition:
    id: str
    event_type: EventType
    name: str
    description_key: str
    priority: int
    cooldown: int = 0
    enabled: bool = True
    metadata: MappingProxyType = field(default_factory=lambda: MappingProxyType({}))

    def __post_init__(self) -> None:
        if not isinstance(self.id, str) or not self.id.strip():
            raise ValueError("EventDefinition id must be a non-empty string")

        if isinstance(self.event_type, str):
            try:
                object.__setattr__(self, "event_type", EventType(self.event_type))
            except ValueError:
                raise ValueError(f"Invalid event_type: '{self.event_type}'")
        elif not isinstance(self.event_type, EventType):
            raise ValueError(f"Invalid event_type: '{self.event_type}'")

        if not isinstance(self.name, str) or not self.name.strip():
            raise ValueError("EventDefinition name must be a non-empty string")

        if not isinstance(self.description_key, str) or not self.description_key.strip():
            raise ValueError("EventDefinition description_key must be a non-empty string")

        if isinstance(self.priority, float):
            if math.isnan(self.priority) or math.isinf(self.priority):
                raise ValueError("EventDefinition priority must not be NaN or Infinity")
            if not self.priority.is_integer():
                raise ValueError("EventDefinition priority must be an integer")
            object.__setattr__(self, "priority", int(self.priority))

        if not isinstance(self.priority, int) or isinstance(self.priority, bool):
            raise ValueError("EventDefinition priority must be an integer")

        if self.priority < 0 or self.priority > 100:
            raise ValueError(f"EventDefinition priority must be between 0 and 100, got {self.priority}")

        if isinstance(self.cooldown, float):
            if math.isnan(self.cooldown) or math.isinf(self.cooldown):
                raise ValueError("EventDefinition cooldown must not be NaN or Infinity")
            if not self.cooldown.is_integer():
                raise ValueError("EventDefinition cooldown must be an integer")
            object.__setattr__(self, "cooldown", int(self.cooldown))

        if not isinstance(self.cooldown, int) or isinstance(self.cooldown, bool):
            raise ValueError("EventDefinition cooldown must be an integer")

        if self.cooldown < 0:
            raise ValueError("EventDefinition cooldown must be non-negative")

        if not isinstance(self.enabled, bool):
            raise ValueError("EventDefinition enabled must be a boolean")

        immutable_meta = _to_immutable_mapping(self.metadata)
        object.__setattr__(self, "metadata", immutable_meta)


@dataclass(frozen=True)
class EventContext:
    season: int | str | None = None
    player_id: str | None = None
    club_id: str | None = None
    competition_id: str | None = None
    event_type: EventType | None = None
    attributes: MappingProxyType = field(default_factory=lambda: MappingProxyType({}))

    def __post_init__(self) -> None:
        if self.season is not None:
            if isinstance(self.season, int):
                if self.season <= 0:
                    raise ValueError(f"Season year must be positive, got {self.season}")
            elif isinstance(self.season, str):
                if not self.season.strip():
                    raise ValueError("Season string cannot be empty")
            else:
                raise ValueError(f"Invalid season format: {type(self.season)}")

        if self.player_id is not None:
            if not isinstance(self.player_id, str) or not self.player_id.strip():
                raise ValueError("player_id must be a non-empty string if provided")

        if self.club_id is not None:
            if not isinstance(self.club_id, str) or not self.club_id.strip():
                raise ValueError("club_id must be a non-empty string if provided")

        if self.competition_id is not None:
            if not isinstance(self.competition_id, str) or not self.competition_id.strip():
                raise ValueError("competition_id must be a non-empty string if provided")

        if self.event_type is not None:
            if isinstance(self.event_type, str):
                try:
                    object.__setattr__(self, "event_type", EventType(self.event_type))
                except ValueError:
                    raise ValueError(f"Invalid event_type: '{self.event_type}'")
            elif not isinstance(self.event_type, EventType):
                raise ValueError(f"Invalid event_type: '{self.event_type}'")

        immutable_attrs = _to_immutable_mapping(self.attributes)
        object.__setattr__(self, "attributes", immutable_attrs)


@dataclass(frozen=True)
class EventInstance:
    id: str
    definition_id: str
    event_type: EventType
    season: int | str
    entity_id: str
    entity_type: str
    seed: str
    priority: int
    status: EventStatus = EventStatus.PENDING
    metadata: MappingProxyType = field(default_factory=lambda: MappingProxyType({}))

    def __post_init__(self) -> None:
        if not isinstance(self.id, str) or not self.id.strip():
            raise ValueError("EventInstance id must be a non-empty string")

        if not isinstance(self.definition_id, str) or not self.definition_id.strip():
            raise ValueError("EventInstance definition_id must be a non-empty string")

        if isinstance(self.event_type, str):
            try:
                object.__setattr__(self, "event_type", EventType(self.event_type))
            except ValueError:
                raise ValueError(f"Invalid event_type: '{self.event_type}'")
        elif not isinstance(self.event_type, EventType):
            raise ValueError(f"Invalid event_type: '{self.event_type}'")

        if isinstance(self.season, int):
            if self.season <= 0:
                raise ValueError(f"Season year must be positive, got {self.season}")
        elif isinstance(self.season, str):
            if not self.season.strip():
                raise ValueError("Season string cannot be empty")
        else:
            raise ValueError(f"Invalid season format: {type(self.season)}")

        if not isinstance(self.entity_id, str) or not self.entity_id.strip():
            raise ValueError("EventInstance entity_id must be a non-empty string")

        if not isinstance(self.entity_type, str) or not self.entity_type.strip():
            raise ValueError("EventInstance entity_type must be a non-empty string")

        if not isinstance(self.seed, str) or not self.seed.strip():
            raise ValueError("EventInstance seed must be a non-empty string")

        if isinstance(self.priority, float):
            if math.isnan(self.priority) or math.isinf(self.priority):
                raise ValueError("EventInstance priority must not be NaN or Infinity")
            if not self.priority.is_integer():
                raise ValueError("EventInstance priority must be an integer")
            object.__setattr__(self, "priority", int(self.priority))

        if not isinstance(self.priority, int) or isinstance(self.priority, bool):
            raise ValueError("EventInstance priority must be an integer")

        if self.priority < 0 or self.priority > 100:
            raise ValueError(f"EventInstance priority must be between 0 and 100, got {self.priority}")

        if isinstance(self.status, str):
            try:
                object.__setattr__(self, "status", EventStatus(self.status))
            except ValueError:
                raise ValueError(f"Invalid status: '{self.status}'")
        elif not isinstance(self.status, EventStatus):
            raise ValueError(f"Invalid status: '{self.status}'")

        immutable_meta = _to_immutable_mapping(self.metadata)
        object.__setattr__(self, "metadata", immutable_meta)


def create_event_definition(
    event_type: EventType | str,
    name: str,
    description_key: str,
    priority: int,
    definition_id: str | None = None,
    cooldown: int = 0,
    enabled: bool = True,
    metadata: dict[str, Any] | MappingProxyType | None = None,
) -> EventDefinition:
    type_enum = EventType(event_type) if isinstance(event_type, str) else event_type

    if definition_id is None:
        raw_key = f"{type_enum.value}:{name}:{description_key}"
        definition_id = f"evt_def_{hashlib.sha256(raw_key.encode('utf-8')).hexdigest()[:16]}"

    meta_proxy = _to_immutable_mapping(metadata)

    return EventDefinition(
        id=definition_id,
        event_type=type_enum,
        name=name,
        description_key=description_key,
        priority=priority,
        cooldown=cooldown,
        enabled=enabled,
        metadata=meta_proxy,
    )


def create_event_instance(
    definition: EventDefinition | str,
    season: int | str,
    entity_id: str,
    entity_type: str,
    seed: str,
    instance_id: str | None = None,
    event_type: EventType | str | None = None,
    priority: int | None = None,
    status: EventStatus | str = EventStatus.PENDING,
    metadata: dict[str, Any] | MappingProxyType | None = None,
) -> EventInstance:
    if isinstance(definition, EventDefinition):
        def_id = definition.id
        def_type = definition.event_type
        def_prio = definition.priority
    else:
        def_id = str(definition)
        if event_type is None:
            raise ValueError("event_type must be provided when definition is a string ID")
        def_type = EventType(event_type) if isinstance(event_type, str) else event_type
        if priority is None:
            raise ValueError("priority must be provided when definition is a string ID")
        def_prio = priority

    if priority is not None and isinstance(definition, EventDefinition):
        def_prio = priority
    if event_type is not None and isinstance(definition, EventDefinition):
        def_type = EventType(event_type) if isinstance(event_type, str) else event_type

    status_enum = EventStatus(status) if isinstance(status, str) else status

    if instance_id is None:
        raw_key = f"{season}:{def_type.value}:{entity_type}:{entity_id}:{def_id}:{seed}"
        instance_id = f"evt_inst_{hashlib.sha256(raw_key.encode('utf-8')).hexdigest()[:16]}"

    meta_proxy = _to_immutable_mapping(metadata)

    return EventInstance(
        id=instance_id,
        definition_id=def_id,
        event_type=def_type,
        season=season,
        entity_id=entity_id,
        entity_type=entity_type,
        seed=seed,
        priority=def_prio,
        status=status_enum,
        metadata=meta_proxy,
    )


def serialize_mapping(mapping: MappingProxyType | dict) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for k in sorted(mapping.keys()):
        v = mapping[k]
        if isinstance(v, MappingProxyType):
            result[k] = serialize_mapping(v)
        elif isinstance(v, tuple):
            result[k] = [serialize_mapping(item) if isinstance(item, MappingProxyType) else item for item in v]
        else:
            result[k] = v
    return result


def to_json_bytes(obj: Any) -> bytes:
    if obj is None:
        return json.dumps(None).encode("utf-8")

    if isinstance(obj, EventDefinition):
        payload = {
            "cooldown": obj.cooldown,
            "description_key": obj.description_key,
            "enabled": obj.enabled,
            "event_type": obj.event_type.value,
            "id": obj.id,
            "metadata": serialize_mapping(obj.metadata),
            "name": obj.name,
            "priority": obj.priority,
        }
    elif isinstance(obj, EventInstance):
        payload = {
            "definition_id": obj.definition_id,
            "entity_id": obj.entity_id,
            "entity_type": obj.entity_type,
            "event_type": obj.event_type.value,
            "id": obj.id,
            "metadata": serialize_mapping(obj.metadata),
            "priority": obj.priority,
            "season": str(obj.season),
            "seed": obj.seed,
            "status": obj.status.value,
        }
    elif isinstance(obj, EventContext):
        payload = {
            "attributes": serialize_mapping(obj.attributes),
            "club_id": obj.club_id,
            "competition_id": obj.competition_id,
            "event_type": obj.event_type.value if obj.event_type else None,
            "player_id": obj.player_id,
            "season": str(obj.season) if obj.season is not None else None,
        }
    elif isinstance(obj, EventReason):
        payload = {
            "code": obj.code,
            "value": obj.value,
            "weight": obj.weight,
        }
    else:
        # Check Phase 16 models first
        try:
            from app.event.replay_domain import (
                CaptureFrame,
                CapturePreset,
                CareerReplay,
                ContentScene,
                ContentStory,
                ContentStoryBuildResult,
                ReplayBuildResult,
                ReplayMoment,
                ReplaySeason,
            )

            if isinstance(obj, ReplaySeason):
                payload = {
                    "appearances": obj.appearances,
                    "assists": obj.assists,
                    "club_id": obj.club_id,
                    "club_name": obj.club_name,
                    "goals": obj.goals,
                    "moment_ids": list(obj.moment_ids),
                    "ovr": obj.ovr,
                    "season_id": obj.season_id,
                    "season_index": obj.season_index,
                    "season_label": obj.season_label,
                    "source_references": serialize_mapping(obj.source_references),
                    "trophies": list(obj.trophies),
                }
            elif isinstance(obj, ReplayMoment):
                payload = {
                    "description": obj.description,
                    "moment_id": obj.moment_id,
                    "moment_type": obj.moment_type.value,
                    "priority": obj.priority.value,
                    "season_id": obj.season_id,
                    "source_event_ids": list(obj.source_event_ids),
                    "source_milestone_ids": list(obj.source_milestone_ids),
                    "source_seed_ids": list(obj.source_seed_ids),
                    "source_turning_point_ids": list(obj.source_turning_point_ids),
                    "title": obj.title,
                    "visual_priority": obj.visual_priority.value,
                }
            elif isinstance(obj, CareerReplay):
                payload = {
                    "career_id": obj.career_id,
                    "career_status": obj.career_status.value,
                    "moments": [json.loads(to_json_bytes(m).decode("utf-8")) for m in obj.moments],
                    "player_id": obj.player_id,
                    "player_name": obj.player_name,
                    "replay_id": obj.replay_id,
                    "seasons": [json.loads(to_json_bytes(s).decode("utf-8")) for s in obj.seasons],
                    "source_presentation_id": obj.source_presentation_id,
                    "source_script_id": obj.source_script_id,
                    "source_story_id": obj.source_story_id,
                }
            elif isinstance(obj, ContentScene):
                payload = {
                    "description": obj.description,
                    "moment_id": obj.moment_id,
                    "order_index": obj.order_index,
                    "presentation_references": serialize_mapping(obj.presentation_references),
                    "priority": obj.priority.value,
                    "scene_id": obj.scene_id,
                    "scene_type": obj.scene_type.value,
                    "script_segment_ids": list(obj.script_segment_ids),
                    "season_id": obj.season_id,
                    "source_references": serialize_mapping(obj.source_references),
                    "subtitle": obj.subtitle,
                    "title": obj.title,
                }
            elif isinstance(obj, ContentStory):
                payload = {
                    "career_id": obj.career_id,
                    "content_story_id": obj.content_story_id,
                    "estimated_duration_seconds": obj.estimated_duration_seconds,
                    "scenes": [json.loads(to_json_bytes(sc).decode("utf-8")) for sc in obj.scenes],
                    "source_script_id": obj.source_script_id,
                    "source_story_id": obj.source_story_id,
                    "title": obj.title,
                    "total_scenes": obj.total_scenes,
                }
            elif isinstance(obj, CapturePreset):
                payload = {
                    "height": obj.height,
                    "preset_id": obj.preset_id,
                    "preset_type": obj.preset_type.value,
                    "show_branding": obj.show_branding,
                    "show_controls": obj.show_controls,
                    "show_navigation": obj.show_navigation,
                    "show_player_identity": obj.show_player_identity,
                    "show_season": obj.show_season,
                    "show_statistics": obj.show_statistics,
                    "width": obj.width,
                }
            elif isinstance(obj, CaptureFrame):
                payload = {
                    "club_name": obj.club_name,
                    "frame_id": obj.frame_id,
                    "headline": obj.headline,
                    "metadata": serialize_mapping(obj.metadata),
                    "player_name": obj.player_name,
                    "preset": json.loads(to_json_bytes(obj.preset).decode("utf-8")),
                    "scene_id": obj.scene_id,
                    "script_text": obj.script_text,
                    "season": obj.season,
                    "statistics": serialize_mapping(obj.statistics),
                    "subheadline": obj.subheadline,
                    "visual_priority": obj.visual_priority.value,
                }
            elif isinstance(obj, ReplayBuildResult):
                payload = {
                    "errors": list(obj.errors),
                    "replay": json.loads(to_json_bytes(obj.replay).decode("utf-8")) if obj.replay else None,
                    "success": obj.success,
                    "warnings": list(obj.warnings),
                }
            elif isinstance(obj, ContentStoryBuildResult):
                payload = {
                    "content_story": json.loads(to_json_bytes(obj.content_story).decode("utf-8")) if obj.content_story else None,
                    "errors": list(obj.errors),
                    "success": obj.success,
                    "warnings": list(obj.warnings),
                }
            else:
                payload = None
        except ImportError:
            payload = None

        if payload is None:
            from app.event.resolution import EventEffect, EventOutcome, EventResolution
            from app.event.effects import (
                EffectApplication,
                EffectApplicationError,
                EffectApplicationResult,
                EffectTarget,
            )
            from app.event.decisions import (
                Decision,
                DecisionOption,
                DecisionResult,
            )

            if isinstance(obj, DecisionOption):
                payload = {
                    "available": obj.available,
                    "description": obj.description,
                    "effects": [json.loads(to_json_bytes(e).decode("utf-8")) for e in obj.effects],
                    "id": obj.id,
                    "label": obj.label,
                    "metadata": serialize_mapping(obj.metadata),
                    "weight": obj.weight,
                }
            elif isinstance(obj, Decision):
                payload = {
                    "default_option_id": obj.default_option_id,
                    "id": obj.id,
                    "metadata": serialize_mapping(obj.metadata),
                    "options": [json.loads(to_json_bytes(o).decode("utf-8")) for o in obj.options],
                    "prompt": obj.prompt,
                    "resolution_type": obj.resolution_type.value,
                }
            elif isinstance(obj, DecisionResult):
                payload = {
                    "decision_id": obj.decision_id,
                    "effects": [json.loads(to_json_bytes(e).decode("utf-8")) for e in obj.effects],
                    "error_code": obj.error_code.value if obj.error_code else None,
                    "error_message": obj.error_message,
                    "metadata": serialize_mapping(obj.metadata),
                    "reasons": [json.loads(to_json_bytes(r).decode("utf-8")) for r in obj.reasons],
                    "resolution_type": obj.resolution_type.value,
                    "seed": obj.seed,
                    "selected_option": json.loads(to_json_bytes(obj.selected_option).decode("utf-8")) if obj.selected_option else None,
                    "success": obj.success,
                }
            elif isinstance(obj, EffectApplication):
                payload = {
                    "applied": obj.applied,
                    "effect_id": obj.effect_id,
                    "effect_index": obj.effect_index,
                    "event_id": obj.event_id,
                    "metadata": serialize_mapping(obj.metadata),
                    "operation": obj.operation.value,
                    "previous_value": obj.previous_value,
                    "requested_value": obj.requested_value,
                    "resulting_value": obj.resulting_value,
                    "target": obj.target,
                }
            elif isinstance(obj, EffectApplicationError):
                payload = {
                    "code": obj.code.value,
                    "details": serialize_mapping(obj.details),
                    "effect_id": obj.effect_id,
                    "effect_index": obj.effect_index,
                    "message": obj.message,
                    "target": obj.target,
                }
            elif isinstance(obj, EffectApplicationResult):
                payload = {
                    "applications": [json.loads(to_json_bytes(a).decode("utf-8")) for a in obj.applications],
                    "errors": [json.loads(to_json_bytes(e).decode("utf-8")) for e in obj.errors],
                    "metadata": serialize_mapping(obj.metadata),
                    "success": obj.success,
                }
            elif isinstance(obj, EffectTarget):
                payload = {
                    "attribute": obj.attribute,
                    "scope": obj.scope,
                    "target_id": obj.target_id,
                    "target_type": obj.target_type,
                }
            elif isinstance(obj, EventEffect):
                payload = {
                    "delta_or_value": obj.delta_or_value,
                    "effect_type": obj.effect_type.value,
                    "id": obj.id,
                    "max_bound": obj.max_bound,
                    "min_bound": obj.min_bound,
                    "operation": str(obj.operation),
                    "parameters": serialize_mapping(obj.parameters),
                    "target_id": obj.target_id,
                    "target_type": obj.target_type,
                }
            elif isinstance(obj, EventOutcome):
                payload = {
                    "effects": [json.loads(to_json_bytes(e).decode("utf-8")) for e in obj.effects],
                    "id": obj.id,
                    "label": obj.label,
                    "reasons": [json.loads(to_json_bytes(r).decode("utf-8")) for r in obj.reasons],
                    "weight": obj.weight,
                }
            elif isinstance(obj, EventResolution):
                payload = {
                    "effects": [json.loads(to_json_bytes(e).decode("utf-8")) for e in obj.effects],
                    "event_id": obj.event_id,
                    "event_instance_id": obj.event_instance_id,
                    "metadata": serialize_mapping(obj.metadata),
                    "outcome_id": obj.outcome_id,
                    "outcome_label": obj.outcome_label,
                    "reasons": [json.loads(to_json_bytes(r).decode("utf-8")) for r in obj.reasons],
                    "resolution_score": obj.resolution_score,
                    "seed": obj.seed,
                    "status": obj.status.value,
                }
            else:
                try:
                    from app.event.career_domain import (
                        CareerArc,
                        CareerEvent,
                        CareerMilestone,
                        CareerRecord,
                        CareerRelationship,
                        CareerTurningPoint,
                        NarrativeSeed,
                    )

                    if isinstance(obj, CareerEvent):
                        payload = {
                            "category": obj.category.value,
                            "clubs": list(obj.clubs),
                            "competitions": list(obj.competitions),
                            "event_id": obj.event_id,
                            "event_type": obj.event_type.value,
                            "participants": list(obj.participants),
                            "player_id": obj.player_id,
                            "season": str(obj.season),
                            "sequence": obj.sequence,
                            "significance": obj.significance.value,
                            "source_event_id": obj.source_event_id,
                            "state_changes": serialize_mapping(obj.state_changes),
                            "summary_data": serialize_mapping(obj.summary_data),
                            "tags": list(obj.tags),
                        }
                    elif isinstance(obj, CareerMilestone):
                        payload = {
                            "club_id": obj.club_id,
                            "competition_id": obj.competition_id,
                            "event_id": obj.event_id,
                            "metadata": serialize_mapping(obj.metadata),
                            "milestone_id": obj.milestone_id,
                            "milestone_type": obj.milestone_type.value,
                            "player_id": obj.player_id,
                            "season": str(obj.season),
                            "sequence": obj.sequence,
                            "significance": obj.significance.value,
                            "value": obj.value,
                        }
                    elif isinstance(obj, CareerRelationship):
                        payload = {
                            "event_ids": list(obj.event_ids),
                            "last_updated_sequence": obj.last_updated_sequence,
                            "metadata": serialize_mapping(obj.metadata),
                            "player_id": obj.player_id,
                            "relationship_id": obj.relationship_id,
                            "relationship_type": obj.relationship_type.value,
                            "source_entity": obj.source_entity,
                            "start_sequence": obj.start_sequence,
                            "status": obj.status.value,
                            "strength": obj.strength,
                            "target_entity": obj.target_entity,
                        }
                    elif isinstance(obj, CareerTurningPoint):
                        payload = {
                            "metadata": serialize_mapping(obj.metadata),
                            "player_id": obj.player_id,
                            "season": str(obj.season),
                            "sequence": obj.sequence,
                            "significance": obj.significance.value,
                            "source_event_id": obj.source_event_id,
                            "summary_data": serialize_mapping(obj.summary_data),
                            "turning_point_id": obj.turning_point_id,
                            "turning_point_type": obj.turning_point_type.value,
                        }
                    elif isinstance(obj, CareerArc):
                        payload = {
                            "arc_id": obj.arc_id,
                            "arc_type": obj.arc_type.value,
                            "end_sequence": obj.end_sequence,
                            "event_ids": list(obj.event_ids),
                            "metadata": serialize_mapping(obj.metadata),
                            "milestone_ids": list(obj.milestone_ids),
                            "player_id": obj.player_id,
                            "significance": obj.significance.value,
                            "start_sequence": obj.start_sequence,
                            "status": obj.status.value,
                            "turning_point_ids": list(obj.turning_point_ids),
                        }
                    elif isinstance(obj, NarrativeSeed):
                        payload = {
                            "arc_id": obj.arc_id,
                            "emotional_direction": obj.emotional_direction,
                            "event_ids": list(obj.event_ids),
                            "factual_context": serialize_mapping(obj.factual_context),
                            "milestone_ids": list(obj.milestone_ids),
                            "narrative_weight": obj.narrative_weight,
                            "player_id": obj.player_id,
                            "priority": obj.priority.value,
                            "relationship_ids": list(obj.relationship_ids),
                            "seed_id": obj.seed_id,
                            "seed_type": obj.seed_type.value,
                            "sequence": obj.sequence,
                        }
                    elif isinstance(obj, CareerRecord):
                        payload = {
                            "arcs": [json.loads(to_json_bytes(a).decode("utf-8")) for a in obj.arcs],
                            "events": [json.loads(to_json_bytes(e).decode("utf-8")) for e in obj.events],
                            "last_sequence": obj.last_sequence,
                            "milestones": [json.loads(to_json_bytes(m).decode("utf-8")) for m in obj.milestones],
                            "narrative_seeds": [json.loads(to_json_bytes(ns).decode("utf-8")) for ns in obj.narrative_seeds],
                            "player_id": obj.player_id,
                            "relationships": [json.loads(to_json_bytes(r).decode("utf-8")) for r in obj.relationships],
                            "turning_points": [json.loads(to_json_bytes(tp).decode("utf-8")) for tp in obj.turning_points],
                        }
                    else:
                        try:
                            from app.event.narrative_domain import (
                                NarrativeAct,
                                NarrativeBeat,
                                NarrativeBuildResult,
                                NarrativeConflict,
                                NarrativeProtagonist,
                                NarrativeStory,
                                NarrativeThread,
                                StoryPremise,
                            )

                            if isinstance(obj, StoryPremise):
                                payload = {
                                    "central_conflict_id": obj.central_conflict_id,
                                    "premise_type": obj.premise_type.value,
                                    "primary_arc_id": obj.primary_arc_id,
                                    "protagonist_goal": obj.protagonist_goal,
                                    "resolution_type": obj.resolution_type.value,
                                    "supporting_facts": serialize_mapping(obj.supporting_facts),
                                }
                            elif isinstance(obj, NarrativeProtagonist):
                                payload = {
                                    "career_stage": obj.career_stage,
                                    "defining_events": list(obj.defining_events),
                                    "important_clubs": list(obj.important_clubs),
                                    "important_relationships": list(obj.important_relationships),
                                    "key_traits": list(obj.key_traits),
                                    "metadata": serialize_mapping(obj.metadata),
                                    "origin": obj.origin,
                                    "player_id": obj.player_id,
                                    "position": obj.position,
                                }
                            elif isinstance(obj, NarrativeAct):
                                payload = {
                                    "act_id": obj.act_id,
                                    "act_type": obj.act_type.value,
                                    "beat_ids": list(obj.beat_ids),
                                    "description": obj.description,
                                    "end_sequence": obj.end_sequence,
                                    "metadata": serialize_mapping(obj.metadata),
                                    "pacing": obj.pacing.value,
                                    "sequence": obj.sequence,
                                    "start_sequence": obj.start_sequence,
                                    "title": obj.title,
                                }
                            elif isinstance(obj, NarrativeBeat):
                                payload = {
                                    "beat_id": obj.beat_id,
                                    "beat_type": obj.beat_type.value,
                                    "emotional_direction": obj.emotional_direction.value,
                                    "factual_context": serialize_mapping(obj.factual_context),
                                    "importance": obj.importance,
                                    "narrative_function": obj.narrative_function.value,
                                    "pacing": obj.pacing.value,
                                    "sequence": obj.sequence,
                                    "source_event_ids": list(obj.source_event_ids),
                                    "source_milestone_ids": list(obj.source_milestone_ids),
                                    "source_seed_ids": list(obj.source_seed_ids),
                                    "source_turning_point_ids": list(obj.source_turning_point_ids),
                                }
                            elif isinstance(obj, NarrativeConflict):
                                payload = {
                                    "conflict_id": obj.conflict_id,
                                    "conflict_type": obj.conflict_type.value,
                                    "end_sequence": obj.end_sequence,
                                    "intensity": obj.intensity,
                                    "metadata": serialize_mapping(obj.metadata),
                                    "resolution_status": obj.resolution_status.value,
                                    "source_events": list(obj.source_events),
                                    "start_sequence": obj.start_sequence,
                                }
                            elif isinstance(obj, NarrativeThread):
                                payload = {
                                    "beat_ids": list(obj.beat_ids),
                                    "end_sequence": obj.end_sequence,
                                    "importance": obj.importance,
                                    "metadata": serialize_mapping(obj.metadata),
                                    "start_sequence": obj.start_sequence,
                                    "status": obj.status,
                                    "thread_id": obj.thread_id,
                                    "thread_type": obj.thread_type.value,
                                }
                            elif isinstance(obj, NarrativeStory):
                                payload = {
                                    "acts": [json.loads(to_json_bytes(a).decode("utf-8")) for a in obj.acts],
                                    "climax_beat_id": obj.climax_beat_id,
                                    "conflicts": [json.loads(to_json_bytes(c).decode("utf-8")) for c in obj.conflicts],
                                    "density": obj.density.value,
                                    "featured_arcs": list(obj.featured_arcs),
                                    "featured_events": list(obj.featured_events),
                                    "featured_milestones": list(obj.featured_milestones),
                                    "featured_relationships": list(obj.featured_relationships),
                                    "featured_turning_points": list(obj.featured_turning_points),
                                    "metadata": serialize_mapping(obj.metadata),
                                    "narrative_beats": [json.loads(to_json_bytes(nb).decode("utf-8")) for nb in obj.narrative_beats],
                                    "opening_beat_id": obj.opening_beat_id,
                                    "opening_strategy": obj.opening_strategy.value,
                                    "player_id": obj.player_id,
                                    "premise": json.loads(to_json_bytes(obj.premise).decode("utf-8")),
                                    "protagonist": json.loads(to_json_bytes(obj.protagonist).decode("utf-8")),
                                    "resolution_type": obj.resolution_type.value,
                                    "story_id": obj.story_id,
                                    "target_duration_seconds": obj.target_duration_seconds,
                                    "themes": [t.value if hasattr(t, "value") else str(t) for t in obj.themes],
                                    "threads": [json.loads(to_json_bytes(th).decode("utf-8")) for th in obj.threads],
                                    "title_context": obj.title_context,
                                }
                            elif isinstance(obj, NarrativeBuildResult):
                                payload = {
                                    "error_code": obj.error_code.value if obj.error_code else None,
                                    "error_message": obj.error_message,
                                    "story": json.loads(to_json_bytes(obj.story).decode("utf-8")) if obj.story else None,
                                    "success": obj.success,
                                }
                            else:
                                try:
                                    from app.event.script_domain import (
                                        ScriptBuildResult,
                                        ScriptClosing,
                                        ScriptHook,
                                        ScriptMetadata,
                                        ScriptSection,
                                        ScriptSegment,
                                        ScriptSourceReference,
                                        ScriptTransition,
                                        StoryScript,
                                    )

                                    if isinstance(obj, ScriptSourceReference):
                                        payload = {
                                            "act_ids": list(obj.act_ids),
                                            "beat_ids": list(obj.beat_ids),
                                            "conflict_ids": list(obj.conflict_ids),
                                            "event_ids": list(obj.event_ids),
                                            "milestone_ids": list(obj.milestone_ids),
                                            "seed_ids": list(obj.seed_ids),
                                            "story_id": obj.story_id,
                                            "thread_ids": list(obj.thread_ids),
                                            "turning_point_ids": list(obj.turning_point_ids),
                                        }
                                    elif isinstance(obj, ScriptSegment):
                                        payload = {
                                            "estimated_duration_seconds": obj.estimated_duration_seconds,
                                            "importance": obj.importance,
                                            "metadata": serialize_mapping(obj.metadata),
                                            "pacing": obj.pacing.value,
                                            "segment_id": obj.segment_id,
                                            "segment_type": obj.segment_type.value,
                                            "sequence": obj.sequence,
                                            "source_reference": json.loads(to_json_bytes(obj.source_reference).decode("utf-8")),
                                            "text": obj.text,
                                            "word_count": obj.word_count,
                                        }
                                    elif isinstance(obj, ScriptTransition):
                                        payload = {
                                            "estimated_duration_seconds": obj.estimated_duration_seconds,
                                            "from_section_id": obj.from_section_id,
                                            "metadata": serialize_mapping(obj.metadata),
                                            "source_reference": json.loads(to_json_bytes(obj.source_reference).decode("utf-8")),
                                            "text": obj.text,
                                            "to_section_id": obj.to_section_id,
                                            "transition_id": obj.transition_id,
                                            "transition_type": obj.transition_type.value,
                                            "word_count": obj.word_count,
                                        }
                                    elif isinstance(obj, ScriptHook):
                                        payload = {
                                            "hook_id": obj.hook_id,
                                            "hook_type": obj.hook_type.value,
                                            "metadata": serialize_mapping(obj.metadata),
                                            "segment": json.loads(to_json_bytes(obj.segment).decode("utf-8")),
                                            "source_reference": json.loads(to_json_bytes(obj.source_reference).decode("utf-8")),
                                            "text": obj.text,
                                        }
                                    elif isinstance(obj, ScriptClosing):
                                        payload = {
                                            "closing_id": obj.closing_id,
                                            "closing_type": obj.closing_type.value,
                                            "metadata": serialize_mapping(obj.metadata),
                                            "segment": json.loads(to_json_bytes(obj.segment).decode("utf-8")),
                                            "source_reference": json.loads(to_json_bytes(obj.source_reference).decode("utf-8")),
                                            "text": obj.text,
                                        }
                                    elif isinstance(obj, ScriptSection):
                                        payload = {
                                            "act_id": obj.act_id,
                                            "metadata": serialize_mapping(obj.metadata),
                                            "section_id": obj.section_id,
                                            "section_type": obj.section_type.value,
                                            "segments": [json.loads(to_json_bytes(s).decode("utf-8")) for s in obj.segments],
                                            "sequence": obj.sequence,
                                            "source_reference": json.loads(to_json_bytes(obj.source_reference).decode("utf-8")),
                                            "title": obj.title,
                                        }
                                    elif isinstance(obj, ScriptMetadata):
                                        payload = {
                                            "created_version": obj.created_version,
                                            "density": obj.density.value,
                                            "extra": serialize_mapping(obj.extra),
                                            "player_id": obj.player_id,
                                            "story_id": obj.story_id,
                                            "style": obj.style.value,
                                            "target_duration_seconds": obj.target_duration_seconds,
                                            "tone": obj.tone.value,
                                            "words_per_minute": obj.words_per_minute,
                                        }
                                    elif isinstance(obj, StoryScript):
                                        payload = {
                                            "climax": json.loads(to_json_bytes(obj.climax).decode("utf-8")) if obj.climax else None,
                                            "closing": json.loads(to_json_bytes(obj.closing).decode("utf-8")) if obj.closing else None,
                                            "estimated_duration_seconds": obj.estimated_duration_seconds,
                                            "hook": json.loads(to_json_bytes(obj.hook).decode("utf-8")) if obj.hook else None,
                                            "introduction": json.loads(to_json_bytes(obj.introduction).decode("utf-8")) if obj.introduction else None,
                                            "metadata": json.loads(to_json_bytes(obj.metadata).decode("utf-8")),
                                            "resolution": json.loads(to_json_bytes(obj.resolution).decode("utf-8")) if obj.resolution else None,
                                            "script_id": obj.script_id,
                                            "sections": [json.loads(to_json_bytes(s).decode("utf-8")) for s in obj.sections],
                                            "source_reference": json.loads(to_json_bytes(obj.source_reference).decode("utf-8")),
                                            "title": obj.title,
                                            "transitions": [json.loads(to_json_bytes(tr).decode("utf-8")) for tr in obj.transitions],
                                            "word_count": obj.word_count,
                                        }
                                    elif isinstance(obj, ScriptBuildResult):
                                        payload = {
                                            "error_code": obj.error_code.value if obj.error_code else None,
                                            "error_message": obj.error_message,
                                            "script": json.loads(to_json_bytes(obj.script).decode("utf-8")) if obj.script else None,
                                            "success": obj.success,
                                        }
                                    else:
                                        try:
                                            from app.event.presentation_domain import (
                                                CareerArcPresentation,
                                                CareerHighlight,
                                                CareerOverview,
                                                CareerPresentation,
                                                CareerStatistics,
                                                ClubPresentation,
                                                NarrativePresentation,
                                                PlayerPresentation,
                                                PresentationBuildResult,
                                                PresentationMetadata,
                                                PresentationSourceReference,
                                                RelationshipPresentation,
                                                ScriptPresentation,
                                                SeasonPresentation,
                                                TimelineEntry,
                                            )

                                            if isinstance(obj, PresentationSourceReference):
                                                payload = {
                                                    "act_ids": list(obj.act_ids),
                                                    "arc_ids": list(obj.arc_ids),
                                                    "beat_ids": list(obj.beat_ids),
                                                    "career_record_id": obj.career_record_id,
                                                    "conflict_ids": list(obj.conflict_ids),
                                                    "event_ids": list(obj.event_ids),
                                                    "milestone_ids": list(obj.milestone_ids),
                                                    "script_id": obj.script_id,
                                                    "segment_ids": list(obj.segment_ids),
                                                    "seed_ids": list(obj.seed_ids),
                                                    "story_id": obj.story_id,
                                                    "thread_ids": list(obj.thread_ids),
                                                    "turning_point_ids": list(obj.turning_point_ids),
                                                }
                                            elif isinstance(obj, PlayerPresentation):
                                                payload = {
                                                    "age": obj.age,
                                                    "career_status": obj.career_status.value,
                                                    "current_club": obj.current_club,
                                                    "first_name": obj.first_name,
                                                    "last_name": obj.last_name,
                                                    "name": obj.name,
                                                    "nationality": obj.nationality,
                                                    "overall_rating": obj.overall_rating,
                                                    "player_id": obj.player_id,
                                                    "position": obj.position,
                                                    "potential": obj.potential,
                                                }
                                            elif isinstance(obj, CareerOverview):
                                                payload = {
                                                    "assists": obj.assists,
                                                    "career_arc": obj.career_arc,
                                                    "career_end": str(obj.career_end) if obj.career_end is not None else None,
                                                    "career_start": str(obj.career_start) if obj.career_start is not None else None,
                                                    "clubs_count": obj.clubs_count,
                                                    "goals": obj.goals,
                                                    "matches": obj.matches,
                                                    "milestones": obj.milestones,
                                                    "peak_club": obj.peak_club,
                                                    "peak_rating": obj.peak_rating,
                                                    "trophies": obj.trophies,
                                                    "turning_points": obj.turning_points,
                                                    "years_active": obj.years_active,
                                                }
                                            elif isinstance(obj, CareerStatistics):
                                                payload = {
                                                    "appearances": obj.appearances,
                                                    "assists": obj.assists,
                                                    "average_rating": obj.average_rating,
                                                    "awards": list(obj.awards),
                                                    "clean_sheets": obj.clean_sheets,
                                                    "extra_stats": serialize_mapping(obj.extra_stats),
                                                    "goals": obj.goals,
                                                    "minutes": obj.minutes,
                                                    "trophies": list(obj.trophies),
                                                }
                                            elif isinstance(obj, ClubPresentation):
                                                payload = {
                                                    "appearances": obj.appearances,
                                                    "assists": obj.assists,
                                                    "club_id": obj.club_id,
                                                    "club_name": obj.club_name,
                                                    "country": obj.country,
                                                    "end_date": obj.end_date,
                                                    "goals": obj.goals,
                                                    "importance": obj.importance,
                                                    "role": obj.role,
                                                    "season_count": obj.season_count,
                                                    "start_date": obj.start_date,
                                                    "trophies": list(obj.trophies),
                                                }
                                            elif isinstance(obj, SeasonPresentation):
                                                payload = {
                                                    "appearances": obj.appearances,
                                                    "assists": obj.assists,
                                                    "average_rating": obj.average_rating,
                                                    "club_id": obj.club_id,
                                                    "club_name": obj.club_name,
                                                    "goals": obj.goals,
                                                    "important_events": list(obj.important_events),
                                                    "milestones": list(obj.milestones),
                                                    "season_id": obj.season_id,
                                                    "season_label": obj.season_label,
                                                    "trophies": list(obj.trophies),
                                                    "turning_points": list(obj.turning_points),
                                                }
                                            elif isinstance(obj, TimelineEntry):
                                                payload = {
                                                    "date_or_season": obj.date_or_season,
                                                    "entry_type": obj.entry_type.value,
                                                    "importance": obj.importance,
                                                    "priority": obj.priority.value,
                                                    "source_reference": json.loads(to_json_bytes(obj.source_reference).decode("utf-8")),
                                                    "summary": obj.summary,
                                                    "timeline_id": obj.timeline_id,
                                                    "title": obj.title,
                                                }
                                            elif isinstance(obj, CareerHighlight):
                                                payload = {
                                                    "description": obj.description,
                                                    "highlight_id": obj.highlight_id,
                                                    "highlight_type": obj.highlight_type.value,
                                                    "priority": obj.priority.value,
                                                    "source_reference": json.loads(to_json_bytes(obj.source_reference).decode("utf-8")),
                                                    "title": obj.title,
                                                }
                                            elif isinstance(obj, CareerArcPresentation):
                                                payload = {
                                                    "arc_id": obj.arc_id,
                                                    "arc_type": obj.arc_type,
                                                    "current_phase": obj.current_phase,
                                                    "end_reference": obj.end_reference,
                                                    "history": list(obj.history),
                                                    "phases": list(obj.phases),
                                                    "source_reference": json.loads(to_json_bytes(obj.source_reference).decode("utf-8")),
                                                    "start_reference": obj.start_reference,
                                                    "status": obj.status,
                                                }
                                            elif isinstance(obj, RelationshipPresentation):
                                                payload = {
                                                    "end_reference": obj.end_reference,
                                                    "relationship_id": obj.relationship_id,
                                                    "relationship_type": obj.relationship_type,
                                                    "source_reference": json.loads(to_json_bytes(obj.source_reference).decode("utf-8")),
                                                    "start_reference": obj.start_reference,
                                                    "status": obj.status,
                                                    "strength": obj.strength,
                                                    "target_entity_id": obj.target_entity_id,
                                                    "target_entity_name": obj.target_entity_name,
                                                }
                                            elif isinstance(obj, NarrativePresentation):
                                                payload = {
                                                    "acts": [serialize_mapping(a) for a in obj.acts],
                                                    "beats": [serialize_mapping(b) for b in obj.beats],
                                                    "climax": obj.climax,
                                                    "conflicts": [serialize_mapping(c) for c in obj.conflicts],
                                                    "opening": obj.opening,
                                                    "premise": obj.premise,
                                                    "resolution": obj.resolution,
                                                    "source_reference": json.loads(to_json_bytes(obj.source_reference).decode("utf-8")),
                                                    "story_id": obj.story_id,
                                                    "theme": list(obj.theme),
                                                    "threads": [serialize_mapping(th) for th in obj.threads],
                                                }
                                            elif isinstance(obj, ScriptPresentation):
                                                payload = {
                                                    "climax": obj.climax,
                                                    "closing": obj.closing,
                                                    "estimated_duration": obj.estimated_duration,
                                                    "hook": obj.hook,
                                                    "introduction": obj.introduction,
                                                    "resolution": obj.resolution,
                                                    "script_id": obj.script_id,
                                                    "sections": [serialize_mapping(sec) for sec in obj.sections],
                                                    "segments": [serialize_mapping(seg) for seg in obj.segments],
                                                    "source_reference": json.loads(to_json_bytes(obj.source_reference).decode("utf-8")),
                                                    "transitions": [serialize_mapping(tr) for tr in obj.transitions],
                                                    "word_count": obj.word_count,
                                                }
                                            elif isinstance(obj, PresentationMetadata):
                                                payload = {
                                                    "created_from_script_id": obj.created_from_script_id,
                                                    "created_from_story_id": obj.created_from_story_id,
                                                    "density": obj.density.value,
                                                    "extra": serialize_mapping(obj.extra),
                                                    "player_id": obj.player_id,
                                                    "presentation_id": obj.presentation_id,
                                                    "section_order": [s.value for s in obj.section_order],
                                                    "version": obj.version,
                                                }
                                            elif isinstance(obj, CareerPresentation):
                                                payload = {
                                                    "career_arcs": [json.loads(to_json_bytes(ca).decode("utf-8")) for ca in obj.career_arcs],
                                                    "clubs": [json.loads(to_json_bytes(c).decode("utf-8")) for c in obj.clubs],
                                                    "highlights": [json.loads(to_json_bytes(h).decode("utf-8")) for h in obj.highlights],
                                                    "metadata": json.loads(to_json_bytes(obj.metadata).decode("utf-8")),
                                                    "narrative": json.loads(to_json_bytes(obj.narrative).decode("utf-8")) if obj.narrative else None,
                                                    "overview": json.loads(to_json_bytes(obj.overview).decode("utf-8")),
                                                    "player": json.loads(to_json_bytes(obj.player).decode("utf-8")),
                                                    "presentation_id": obj.presentation_id,
                                                    "relationships": [json.loads(to_json_bytes(r).decode("utf-8")) for r in obj.relationships],
                                                    "script": json.loads(to_json_bytes(obj.script).decode("utf-8")) if obj.script else None,
                                                    "seasons": [json.loads(to_json_bytes(s).decode("utf-8")) for s in obj.seasons],
                                                    "source_reference": json.loads(to_json_bytes(obj.source_reference).decode("utf-8")),
                                                    "statistics": json.loads(to_json_bytes(obj.statistics).decode("utf-8")),
                                                    "timeline": [json.loads(to_json_bytes(t).decode("utf-8")) for t in obj.timeline],
                                                }
                                            elif isinstance(obj, PresentationBuildResult):
                                                payload = {
                                                    "error_code": obj.error_code.value if obj.error_code else None,
                                                    "error_message": obj.error_message,
                                                    "presentation": json.loads(to_json_bytes(obj.presentation).decode("utf-8")) if obj.presentation else None,
                                                    "success": obj.success,
                                                }
                                            else:
                                                raise ValueError(f"Unserializable object type: {type(obj)}")
                                        except ImportError:
                                            raise ValueError(f"Unserializable object type: {type(obj)}")
                                except ImportError:
                                    raise ValueError(f"Unserializable object type: {type(obj)}")
                        except ImportError:
                            raise ValueError(f"Unserializable object type: {type(obj)}")
                except ImportError:
                    raise ValueError(f"Unserializable object type: {type(obj)}")

    return json.dumps(payload, sort_keys=True, ensure_ascii=True).encode("utf-8")
