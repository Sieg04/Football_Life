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
        # Import lazily to avoid circular imports
        from app.event.resolution import EventEffect, EventOutcome, EventResolution

        if isinstance(obj, EventEffect):
            payload = {
                "delta_or_value": obj.delta_or_value,
                "effect_type": obj.effect_type.value,
                "id": obj.id,
                "max_bound": obj.max_bound,
                "min_bound": obj.min_bound,
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
            raise ValueError(f"Unserializable object type: {type(obj)}")

    return json.dumps(payload, sort_keys=True, ensure_ascii=True).encode("utf-8")
