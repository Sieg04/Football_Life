import hashlib
import math
from dataclasses import dataclass, field
from enum import StrEnum
from types import MappingProxyType
from typing import Any, Sequence

from app.event.conditions import (
    ConditionCompositionNode,
    EventCondition,
    evaluate_event_conditions,
)
from app.event.domain import (
    EventContext,
    EventDefinition,
    EventInstance,
    EventReason,
    EventStatus,
    _is_valid_primitive,
    _to_immutable_mapping,
)


class EventResolutionStatus(StrEnum):
    RESOLVED = "RESOLVED"
    FAILED = "FAILED"
    BLOCKED = "BLOCKED"
    CANCELLED = "CANCELLED"


class EventEffectType(StrEnum):
    PLAYER_MORALE_CHANGE = "PLAYER_MORALE_CHANGE"
    PLAYER_CONFIDENCE_CHANGE = "PLAYER_CONFIDENCE_CHANGE"
    PLAYER_FORM_CHANGE = "PLAYER_FORM_CHANGE"
    PLAYER_FITNESS_CHANGE = "PLAYER_FITNESS_CHANGE"
    PLAYER_REPUTATION_CHANGE = "PLAYER_REPUTATION_CHANGE"
    PLAYER_HAPPINESS_CHANGE = "PLAYER_HAPPINESS_CHANGE"
    PLAYER_ATTRIBUTE_CHANGE = "PLAYER_ATTRIBUTE_CHANGE"
    CLUB_MORALE_CHANGE = "CLUB_MORALE_CHANGE"
    CLUB_MOMENTUM_CHANGE = "CLUB_MOMENTUM_CHANGE"
    CAREER_FLAG = "CAREER_FLAG"
    TRANSFER_RELEVANCE = "TRANSFER_RELEVANCE"
    RELATIONSHIP_CHANGE = "RELATIONSHIP_CHANGE"


@dataclass(frozen=True)
class EventEffect:
    id: str
    effect_type: EventEffectType
    target_id: str
    target_type: str
    delta_or_value: float | int | str | bool
    min_bound: float | int | None = 0.0
    max_bound: float | int | None = 100.0
    parameters: MappingProxyType = field(default_factory=lambda: MappingProxyType({}))
    operation: Any = "ADD"

    def __post_init__(self) -> None:
        if not isinstance(self.id, str) or not self.id.strip():
            raise ValueError("EventEffect id must be a non-empty string")

        if isinstance(self.effect_type, str):
            try:
                object.__setattr__(self, "effect_type", EventEffectType(self.effect_type))
            except ValueError:
                raise ValueError(f"Invalid EventEffectType: '{self.effect_type}'")
        elif not isinstance(self.effect_type, EventEffectType):
            raise ValueError(f"Invalid EventEffectType: '{self.effect_type}'")

        if not isinstance(self.target_id, str) or not self.target_id.strip():
            raise ValueError("EventEffect target_id must be a non-empty string")

        if not isinstance(self.target_type, str) or not self.target_type.strip():
            raise ValueError("EventEffect target_type must be a non-empty string")

        if isinstance(self.delta_or_value, float):
            if math.isnan(self.delta_or_value) or math.isinf(self.delta_or_value):
                raise ValueError("EventEffect delta_or_value must not be NaN or Infinity")

        if not _is_valid_primitive(self.delta_or_value):
            raise ValueError(f"Unsupported non-primitive delta_or_value type: {type(self.delta_or_value)}")

        if self.min_bound is not None:
            if isinstance(self.min_bound, float) and (math.isnan(self.min_bound) or math.isinf(self.min_bound)):
                raise ValueError("EventEffect min_bound must not be NaN or Infinity")
            if not isinstance(self.min_bound, (int, float)) or isinstance(self.min_bound, bool):
                raise ValueError("EventEffect min_bound must be a number or None")

        if self.max_bound is not None:
            if isinstance(self.max_bound, float) and (math.isnan(self.max_bound) or math.isinf(self.max_bound)):
                raise ValueError("EventEffect max_bound must not be NaN or Infinity")
            if not isinstance(self.max_bound, (int, float)) or isinstance(self.max_bound, bool):
                raise ValueError("EventEffect max_bound must be a number or None")

        if self.min_bound is not None and self.max_bound is not None:
            if self.min_bound > self.max_bound:
                raise ValueError(f"EventEffect min_bound ({self.min_bound}) cannot exceed max_bound ({self.max_bound})")

        immutable_params = _to_immutable_mapping(self.parameters)
        object.__setattr__(self, "parameters", immutable_params)


@dataclass(frozen=True)
class EventOutcome:
    id: str
    label: str
    weight: float
    effects: tuple[EventEffect, ...] = ()
    reasons: tuple[EventReason, ...] = ()
    conditions: Sequence[EventCondition] | ConditionCompositionNode | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.id, str) or not self.id.strip():
            raise ValueError("EventOutcome id must be a non-empty string")

        if not isinstance(self.label, str) or not self.label.strip():
            raise ValueError("EventOutcome label must be a non-empty string")

        if isinstance(self.weight, float):
            if math.isnan(self.weight) or math.isinf(self.weight):
                raise ValueError("EventOutcome weight must not be NaN or Infinity")

        if not isinstance(self.weight, (int, float)) or isinstance(self.weight, bool):
            raise ValueError("EventOutcome weight must be a number")

        if self.weight < 0.0:
            raise ValueError(f"EventOutcome weight must be non-negative, got {self.weight}")

        if not isinstance(self.effects, tuple):
            object.__setattr__(self, "effects", tuple(self.effects))
        for eff in self.effects:
            if not isinstance(eff, EventEffect):
                raise ValueError(f"Expected EventEffect, got {type(eff)}")

        if not isinstance(self.reasons, tuple):
            object.__setattr__(self, "reasons", tuple(self.reasons))
        for reas in self.reasons:
            if not isinstance(reas, EventReason):
                raise ValueError(f"Expected EventReason, got {type(reas)}")


@dataclass(frozen=True)
class EventResolution:
    event_id: str
    event_instance_id: str
    status: EventResolutionStatus
    outcome_id: str | None
    outcome_label: str | None
    effects: tuple[EventEffect, ...]
    reasons: tuple[EventReason, ...]
    resolution_score: float
    seed: str
    metadata: MappingProxyType = field(default_factory=lambda: MappingProxyType({}))

    def __post_init__(self) -> None:
        if not isinstance(self.event_id, str) or not self.event_id.strip():
            raise ValueError("EventResolution event_id must be a non-empty string")

        if not isinstance(self.event_instance_id, str) or not self.event_instance_id.strip():
            raise ValueError("EventResolution event_instance_id must be a non-empty string")

        if isinstance(self.status, str):
            try:
                object.__setattr__(self, "status", EventResolutionStatus(self.status))
            except ValueError:
                raise ValueError(f"Invalid EventResolutionStatus: '{self.status}'")
        elif not isinstance(self.status, EventResolutionStatus):
            raise ValueError(f"Invalid EventResolutionStatus: '{self.status}'")

        if self.outcome_id is not None:
            if not isinstance(self.outcome_id, str) or not self.outcome_id.strip():
                raise ValueError("EventResolution outcome_id must be a non-empty string if provided")

        if self.outcome_label is not None:
            if not isinstance(self.outcome_label, str) or not self.outcome_label.strip():
                raise ValueError("EventResolution outcome_label must be a non-empty string if provided")

        if not isinstance(self.effects, tuple):
            object.__setattr__(self, "effects", tuple(self.effects))
        for eff in self.effects:
            if not isinstance(eff, EventEffect):
                raise ValueError(f"Expected EventEffect, got {type(eff)}")

        if not isinstance(self.reasons, tuple):
            object.__setattr__(self, "reasons", tuple(self.reasons))
        for reas in self.reasons:
            if not isinstance(reas, EventReason):
                raise ValueError(f"Expected EventReason, got {type(reas)}")

        if isinstance(self.resolution_score, float):
            if math.isnan(self.resolution_score) or math.isinf(self.resolution_score):
                raise ValueError("resolution_score must not be NaN or Infinity")

        if not isinstance(self.resolution_score, (int, float)) or isinstance(self.resolution_score, bool):
            raise ValueError("resolution_score must be a number")

        if self.resolution_score < 0.0 or self.resolution_score > 1.0:
            raise ValueError(f"resolution_score must be between 0.0 and 1.0, got {self.resolution_score}")

        if not isinstance(self.seed, str) or not self.seed.strip():
            raise ValueError("EventResolution seed must be a non-empty string")

        immutable_meta = _to_immutable_mapping(self.metadata)
        object.__setattr__(self, "metadata", immutable_meta)


def derive_deterministic_outcome_roll(
    seed: str,
    instance_id: str,
    step_tag: str = "outcome",
) -> float:
    if not isinstance(seed, str) or not seed.strip():
        raise ValueError("seed must be a non-empty string")
    if not isinstance(instance_id, str) or not instance_id.strip():
        raise ValueError("instance_id must be a non-empty string")

    raw_key = f"resolution_roll:{seed}:{instance_id}:{step_tag}"
    digest = hashlib.sha256(raw_key.encode("utf-8")).digest()
    int_val = int.from_bytes(digest[:8], byteorder="big")
    return int_val / (2**64 - 1)


def select_event_outcome(
    outcomes: Sequence[EventOutcome],
    context: EventContext,
    seed: str,
    instance_id: str,
) -> tuple[EventOutcome | None, tuple[EventReason, ...], float]:
    if not isinstance(context, EventContext):
        raise ValueError(f"Expected EventContext, got {type(context)}")
    if not isinstance(seed, str) or not seed.strip():
        raise ValueError("seed must be a non-empty string")
    if not isinstance(instance_id, str) or not instance_id.strip():
        raise ValueError("instance_id must be a non-empty string")

    outcome_list = list(outcomes)
    for o in outcome_list:
        if not isinstance(o, EventOutcome):
            raise ValueError(f"Expected EventOutcome, got {type(o)}")

    if not outcome_list:
        reason = EventReason(code="NO_OUTCOMES_CONFIGURED", value="empty_outcome_set", weight=1.0)
        return (None, (reason,), 0.0)

    # Filter eligible outcomes based on outcome conditions
    eligible_outcomes: list[EventOutcome] = []
    reasons: list[EventReason] = []

    for o in outcome_list:
        if o.conditions is not None:
            cond_res = evaluate_event_conditions(o.conditions, context)
            if not cond_res.passed:
                reasons.append(
                    EventReason(code="OUTCOME_CONDITION_FAILED", value=o.id, weight=1.0)
                )
                continue
        eligible_outcomes.append(o)

    if not eligible_outcomes:
        reasons.append(
            EventReason(code="NO_ELIGIBLE_OUTCOMES", value="all_conditions_failed", weight=1.0)
        )
        return (None, tuple(reasons), 0.0)

    total_weight = sum(o.weight for o in eligible_outcomes)
    if total_weight <= 0.0:
        reasons.append(
            EventReason(code="ALL_ZERO_WEIGHTS", value="total_weight_zero", weight=1.0)
        )
        return (None, tuple(reasons), 0.0)

    # Sort outcomes deterministically by ID
    sorted_eligible = sorted(eligible_outcomes, key=lambda o: o.id)

    # Derive deterministic roll value
    roll_val = derive_deterministic_outcome_roll(seed=seed, instance_id=instance_id)

    target_accum = roll_val * total_weight
    current_accum = 0.0
    selected: EventOutcome | None = None

    for o in sorted_eligible:
        current_accum += o.weight
        if current_accum >= target_accum:
            selected = o
            break

    if selected is None:
        selected = sorted_eligible[-1]

    # Deterministically order reasons if present
    out_reasons = sorted(selected.reasons, key=lambda r: (r.code, str(r.value)))

    return (selected, tuple(out_reasons), roll_val)


def resolve_event(
    definition: EventDefinition | str,
    instance: EventInstance,
    context: EventContext,
    outcomes: Sequence[EventOutcome],
    seed: str | None = None,
) -> EventResolution:
    if not isinstance(instance, EventInstance):
        raise ValueError(f"Expected EventInstance, got {type(instance)}")
    if not isinstance(context, EventContext):
        raise ValueError(f"Expected EventContext, got {type(context)}")

    def_id = definition.id if isinstance(definition, EventDefinition) else str(definition)
    def_enabled = definition.enabled if isinstance(definition, EventDefinition) else True

    eff_seed = seed if seed is not None else instance.seed

    if instance.status == EventStatus.CANCELLED or instance.status == EventStatus.EXPIRED:
        return EventResolution(
            event_id=def_id,
            event_instance_id=instance.id,
            status=EventResolutionStatus.CANCELLED,
            outcome_id=None,
            outcome_label=None,
            effects=(),
            reasons=(EventReason(code="INSTANCE_CANCELLED_OR_EXPIRED", value=instance.status.value, weight=1.0),),
            resolution_score=0.0,
            seed=eff_seed,
            metadata=instance.metadata,
        )

    if not def_enabled:
        return EventResolution(
            event_id=def_id,
            event_instance_id=instance.id,
            status=EventResolutionStatus.BLOCKED,
            outcome_id=None,
            outcome_label=None,
            effects=(),
            reasons=(EventReason(code="EVENT_DEFINITION_DISABLED", value=def_id, weight=1.0),),
            resolution_score=0.0,
            seed=eff_seed,
            metadata=instance.metadata,
        )

    selected_outcome, outcome_reasons, roll_val = select_event_outcome(
        outcomes=outcomes,
        context=context,
        seed=eff_seed,
        instance_id=instance.id,
    )

    if selected_outcome is None:
        return EventResolution(
            event_id=def_id,
            event_instance_id=instance.id,
            status=EventResolutionStatus.BLOCKED,
            outcome_id=None,
            outcome_label=None,
            effects=(),
            reasons=outcome_reasons,
            resolution_score=roll_val,
            seed=eff_seed,
            metadata=instance.metadata,
        )

    # Sort effects deterministically by id
    sorted_effects = tuple(sorted(selected_outcome.effects, key=lambda e: e.id))

    return EventResolution(
        event_id=def_id,
        event_instance_id=instance.id,
        status=EventResolutionStatus.RESOLVED,
        outcome_id=selected_outcome.id,
        outcome_label=selected_outcome.label,
        effects=sorted_effects,
        reasons=outcome_reasons,
        resolution_score=roll_val,
        seed=eff_seed,
        metadata=instance.metadata,
    )


def resolve_event_outcome(
    outcomes: Sequence[EventOutcome],
    context: EventContext,
    seed: str,
    instance_id: str,
) -> tuple[EventOutcome | None, tuple[EventReason, ...], float]:
    return select_event_outcome(outcomes=outcomes, context=context, seed=seed, instance_id=instance_id)
