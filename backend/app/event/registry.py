from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Sequence

from app.event.domain import EventDefinition, EventType


@dataclass(frozen=True)
class EventRegistry:
    _definitions: MappingProxyType[str, EventDefinition] = field(
        default_factory=lambda: MappingProxyType({})
    )

    def register(self, definition: EventDefinition) -> "EventRegistry":
        if not isinstance(definition, EventDefinition):
            raise ValueError(f"Expected EventDefinition instance, got {type(definition)}")

        if definition.id in self._definitions:
            raise ValueError(f"Duplicate EventDefinition ID: '{definition.id}'")

        new_dict = dict(self._definitions)
        new_dict[definition.id] = definition
        return EventRegistry(_definitions=MappingProxyType(new_dict))

    def get(self, definition_id: str) -> EventDefinition | None:
        if not isinstance(definition_id, str):
            return None
        return self._definitions.get(definition_id)

    def contains(self, definition_id: str) -> bool:
        if not isinstance(definition_id, str):
            return False
        return definition_id in self._definitions

    def list_definitions(
        self,
        event_type: EventType | str | None = None,
        enabled_only: bool = False,
    ) -> tuple[EventDefinition, ...]:
        filter_type: EventType | None = None
        if event_type is not None:
            filter_type = EventType(event_type) if isinstance(event_type, str) else event_type

        result: list[EventDefinition] = []
        # Sort keys deterministically by definition.id
        sorted_ids = sorted(self._definitions.keys())

        for def_id in sorted_ids:
            defn = self._definitions[def_id]
            if enabled_only and not defn.enabled:
                continue
            if filter_type is not None and defn.event_type != filter_type:
                continue
            result.append(defn)

        return tuple(result)

    def register_many(self, definitions: Sequence[EventDefinition]) -> "EventRegistry":
        current = self
        for defn in definitions:
            current = current.register(defn)
        return current
