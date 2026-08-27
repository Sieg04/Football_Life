import hashlib
import math
from dataclasses import dataclass, field
from enum import StrEnum
from types import MappingProxyType
from typing import Any, Sequence

from app.event.conditions import (
    ConditionCompositionNode,
    ConditionEvaluationResult,
    EventCondition,
    evaluate_event_conditions,
)
from app.event.domain import EventContext, EventDefinition, EventInstance, EventStatus, EventType, _is_valid_primitive


class ProbabilityModifierType(StrEnum):
    ADDITIVE = "ADDITIVE"
    MULTIPLICATIVE = "MULTIPLICATIVE"
    OVERRIDE = "OVERRIDE"


@dataclass(frozen=True)
class ProbabilityModifier:
    id: str
    modifier_type: ProbabilityModifierType
    value: float
    description: str = ""

    def __post_init__(self) -> None:
        if not isinstance(self.id, str) or not self.id.strip():
            raise ValueError("ProbabilityModifier id must be a non-empty string")

        if isinstance(self.modifier_type, str):
            try:
                object.__setattr__(self, "modifier_type", ProbabilityModifierType(self.modifier_type))
            except ValueError:
                raise ValueError(f"Invalid ProbabilityModifierType: '{self.modifier_type}'")
        elif not isinstance(self.modifier_type, ProbabilityModifierType):
            raise ValueError(f"Invalid ProbabilityModifierType: '{self.modifier_type}'")

        if isinstance(self.value, float):
            if math.isnan(self.value) or math.isinf(self.value):
                raise ValueError("ProbabilityModifier value must not be NaN or Infinity")

        if not isinstance(self.value, (int, float)) or isinstance(self.value, bool):
            raise ValueError("ProbabilityModifier value must be a number")


@dataclass(frozen=True)
class ProbabilityCalculationResult:
    base_probability: float
    final_probability: float
    modifiers: tuple[ProbabilityModifier, ...] = ()

    def __post_init__(self) -> None:
        if isinstance(self.base_probability, float):
            if math.isnan(self.base_probability) or math.isinf(self.base_probability):
                raise ValueError("base_probability must not be NaN or Infinity")
        if self.base_probability < 0.0 or self.base_probability > 1.0:
            raise ValueError(f"base_probability must be between 0.0 and 1.0, got {self.base_probability}")

        if isinstance(self.final_probability, float):
            if math.isnan(self.final_probability) or math.isinf(self.final_probability):
                raise ValueError("final_probability must not be NaN or Infinity")
        if self.final_probability < 0.0 or self.final_probability > 1.0:
            raise ValueError(f"final_probability must be between 0.0 and 1.0, got {self.final_probability}")

        if not isinstance(self.modifiers, tuple):
            object.__setattr__(self, "modifiers", tuple(self.modifiers))
        for mod in self.modifiers:
            if not isinstance(mod, ProbabilityModifier):
                raise ValueError(f"Expected ProbabilityModifier, got {type(mod)}")


@dataclass(frozen=True)
class EventCandidate:
    definition: EventDefinition
    context: EventContext
    eligible: bool
    probability: float
    roll_value: float
    triggered: bool
    condition_evaluation: ConditionEvaluationResult
    probability_calculation: ProbabilityCalculationResult
    instance: EventInstance | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.definition, EventDefinition):
            raise ValueError(f"Expected EventDefinition, got {type(self.definition)}")
        if not isinstance(self.context, EventContext):
            raise ValueError(f"Expected EventContext, got {type(self.context)}")
        if not isinstance(self.eligible, bool):
            raise ValueError("eligible must be a boolean")
        if not isinstance(self.triggered, bool):
            raise ValueError("triggered must be a boolean")

        if isinstance(self.probability, float):
            if math.isnan(self.probability) or math.isinf(self.probability):
                raise ValueError("probability must not be NaN or Infinity")
        if self.probability < 0.0 or self.probability > 1.0:
            raise ValueError(f"probability must be between 0.0 and 1.0, got {self.probability}")

        if isinstance(self.roll_value, float):
            if math.isnan(self.roll_value) or math.isinf(self.roll_value):
                raise ValueError("roll_value must not be NaN or Infinity")
        if self.roll_value < 0.0 or self.roll_value > 1.0:
            raise ValueError(f"roll_value must be between 0.0 and 1.0, got {self.roll_value}")

        if not isinstance(self.condition_evaluation, ConditionEvaluationResult):
            raise ValueError(f"Expected ConditionEvaluationResult, got {type(self.condition_evaluation)}")
        if not isinstance(self.probability_calculation, ProbabilityCalculationResult):
            raise ValueError(f"Expected ProbabilityCalculationResult, got {type(self.probability_calculation)}")
        if self.instance is not None and not isinstance(self.instance, EventInstance):
            raise ValueError(f"Expected EventInstance or None, got {type(self.instance)}")


def calculate_event_probability(
    base_probability: float,
    modifiers: Sequence[ProbabilityModifier] | None = None,
) -> ProbabilityCalculationResult:
    if isinstance(base_probability, float):
        if math.isnan(base_probability) or math.isinf(base_probability):
            raise ValueError("base_probability must not be NaN or Infinity")
    if not isinstance(base_probability, (int, float)) or isinstance(base_probability, bool):
        raise ValueError("base_probability must be a number")

    clamped_base = max(0.0, min(1.0, float(base_probability)))
    mod_tuple = tuple(modifiers) if modifiers is not None else ()

    for m in mod_tuple:
        if not isinstance(m, ProbabilityModifier):
            raise ValueError(f"Expected ProbabilityModifier, got {type(m)}")

    current_prob = clamped_base
    for mod in mod_tuple:
        if mod.modifier_type == ProbabilityModifierType.ADDITIVE:
            current_prob += mod.value
        elif mod.modifier_type == ProbabilityModifierType.MULTIPLICATIVE:
            current_prob *= mod.value
        elif mod.modifier_type == ProbabilityModifierType.OVERRIDE:
            current_prob = mod.value

    final_prob = max(0.0, min(1.0, current_prob))

    return ProbabilityCalculationResult(
        base_probability=clamped_base,
        final_probability=final_prob,
        modifiers=mod_tuple,
    )


def derive_deterministic_roll(
    seed: str,
    season: int | str,
    entity_type: str,
    entity_id: str,
    definition_id: str,
) -> float:
    raw_key = f"roll:{seed}:{season}:{entity_type}:{entity_id}:{definition_id}"
    digest = hashlib.sha256(raw_key.encode("utf-8")).digest()
    int_val = int.from_bytes(digest[:8], byteorder="big")
    return int_val / (2**64 - 1)


def evaluate_event_candidate(
    definition: EventDefinition,
    context: EventContext,
    seed: str,
    entity_id: str,
    entity_type: str,
    base_probability: float = 0.05,
    conditions: Sequence[EventCondition] | ConditionCompositionNode | None = None,
    modifiers: Sequence[ProbabilityModifier] | None = None,
) -> EventCandidate:
    if not isinstance(definition, EventDefinition):
        raise ValueError(f"Expected EventDefinition, got {type(definition)}")
    if not isinstance(context, EventContext):
        raise ValueError(f"Expected EventContext, got {type(context)}")
    if not isinstance(seed, str) or not seed.strip():
        raise ValueError("seed must be a non-empty string")
    if not isinstance(entity_id, str) or not entity_id.strip():
        raise ValueError("entity_id must be a non-empty string")
    if not isinstance(entity_type, str) or not entity_type.strip():
        raise ValueError("entity_type must be a non-empty string")

    # Evaluate eligibility
    cond_eval = evaluate_event_conditions(conditions, context)
    eligible = cond_eval.passed and definition.enabled

    # Calculate probability
    prob_calc = calculate_event_probability(base_probability, modifiers)
    final_prob = prob_calc.final_probability if eligible else 0.0

    # Derive deterministic SHA-256 roll value
    season_val = context.season if context.season is not None else "0"
    roll_val = derive_deterministic_roll(
        seed=seed,
        season=season_val,
        entity_type=entity_type,
        entity_id=entity_id,
        definition_id=definition.id,
    )

    triggered = eligible and (roll_val < final_prob)

    inst: EventInstance | None = None
    if triggered:
        raw_key = f"{season_val}:{definition.event_type.value}:{entity_type}:{entity_id}:{definition.id}:{seed}"
        inst_id = f"evt_inst_{hashlib.sha256(raw_key.encode('utf-8')).hexdigest()[:16]}"
        inst = EventInstance(
            id=inst_id,
            definition_id=definition.id,
            event_type=definition.event_type,
            season=season_val,
            entity_id=entity_id,
            entity_type=entity_type,
            seed=seed,
            priority=definition.priority,
            status=EventStatus.TRIGGERED,
            metadata=definition.metadata,
        )

    return EventCandidate(
        definition=definition,
        context=context,
        eligible=eligible,
        probability=final_prob,
        roll_value=roll_val,
        triggered=triggered,
        condition_evaluation=cond_eval,
        probability_calculation=prob_calc,
        instance=inst,
    )


def evaluate_event_candidates(
    candidates: Sequence[EventCandidate],
) -> tuple[EventCandidate, ...]:
    cand_list = list(candidates)
    for c in cand_list:
        if not isinstance(c, EventCandidate):
            raise ValueError(f"Expected EventCandidate, got {type(c)}")

    # Deterministic sorting: priority DESC, probability DESC, definition.id ASC
    sorted_candidates = sorted(
        cand_list,
        key=lambda c: (-c.definition.priority, -c.probability, c.definition.id),
    )
    return tuple(sorted_candidates)
