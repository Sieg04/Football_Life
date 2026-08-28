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
    EventReason,
    _is_valid_primitive,
    _to_immutable_mapping,
)
from app.event.effects import (
    EffectApplicationResult,
    apply_effects,
)
from app.event.resolution import EventEffect


class DecisionResolutionType(StrEnum):
    EXPLICIT = "EXPLICIT"
    DEFAULT = "DEFAULT"
    WEIGHTED = "WEIGHTED"


class DecisionErrorCode(StrEnum):
    INVALID_DECISION = "INVALID_DECISION"
    INVALID_OPTION = "INVALID_OPTION"
    DUPLICATE_OPTION = "DUPLICATE_OPTION"
    OPTION_UNAVAILABLE = "OPTION_UNAVAILABLE"
    NO_OPTIONS = "NO_OPTIONS"
    NO_SELECTABLE_OPTION = "NO_SELECTABLE_OPTION"
    INVALID_WEIGHT = "INVALID_WEIGHT"
    INVALID_RESOLUTION_TYPE = "INVALID_RESOLUTION_TYPE"
    INVALID_DEFAULT_OPTION = "INVALID_DEFAULT_OPTION"


@dataclass(frozen=True)
class DecisionOption:
    id: str
    label: str
    description: str = ""
    weight: float = 1.0
    available: bool = True
    effects: tuple[EventEffect, ...] = ()
    conditions: Sequence[EventCondition] | ConditionCompositionNode | None = None
    metadata: MappingProxyType = field(default_factory=lambda: MappingProxyType({}))

    def __post_init__(self) -> None:
        if not isinstance(self.id, str) or not self.id.strip():
            raise ValueError("DecisionOption id must be a non-empty string")

        if not isinstance(self.label, str) or not self.label.strip():
            raise ValueError("DecisionOption label must be a non-empty string")

        if not isinstance(self.description, str):
            raise ValueError("DecisionOption description must be a string")

        if isinstance(self.weight, float):
            if math.isnan(self.weight) or math.isinf(self.weight):
                raise ValueError("DecisionOption weight must not be NaN or Infinity")

        if not isinstance(self.weight, (int, float)) or isinstance(self.weight, bool):
            raise ValueError("DecisionOption weight must be a number")

        if self.weight < 0.0:
            raise ValueError(f"DecisionOption weight must be non-negative, got {self.weight}")

        if not isinstance(self.available, bool):
            raise ValueError("DecisionOption available must be a boolean")

        if not isinstance(self.effects, tuple):
            object.__setattr__(self, "effects", tuple(self.effects))
        for eff in self.effects:
            if not isinstance(eff, EventEffect):
                raise ValueError(f"Expected EventEffect in effects, got {type(eff)}")

        immutable_meta = _to_immutable_mapping(self.metadata)
        object.__setattr__(self, "metadata", immutable_meta)


@dataclass(frozen=True)
class Decision:
    id: str
    prompt: str
    options: tuple[DecisionOption, ...]
    resolution_type: DecisionResolutionType = DecisionResolutionType.WEIGHTED
    default_option_id: str | None = None
    metadata: MappingProxyType = field(default_factory=lambda: MappingProxyType({}))

    def __post_init__(self) -> None:
        if not isinstance(self.id, str) or not self.id.strip():
            raise ValueError("Decision id must be a non-empty string")

        if not isinstance(self.prompt, str) or not self.prompt.strip():
            raise ValueError("Decision prompt must be a non-empty string")

        if isinstance(self.resolution_type, str):
            try:
                object.__setattr__(self, "resolution_type", DecisionResolutionType(self.resolution_type))
            except ValueError:
                raise ValueError(f"Invalid DecisionResolutionType: '{self.resolution_type}'")
        elif not isinstance(self.resolution_type, DecisionResolutionType):
            raise ValueError(f"Invalid DecisionResolutionType: '{self.resolution_type}'")

        if not isinstance(self.options, tuple):
            object.__setattr__(self, "options", tuple(self.options))

        if len(self.options) == 0:
            raise ValueError("Decision must contain at least one DecisionOption")

        seen_ids: set[str] = set()
        for opt in self.options:
            if not isinstance(opt, DecisionOption):
                raise ValueError(f"Expected DecisionOption, got {type(opt)}")
            if opt.id in seen_ids:
                raise ValueError(f"Duplicate DecisionOption id found: '{opt.id}'")
            seen_ids.add(opt.id)

        if self.default_option_id is not None:
            if not isinstance(self.default_option_id, str) or not self.default_option_id.strip():
                raise ValueError("Decision default_option_id must be a non-empty string if provided")
            if self.default_option_id not in seen_ids:
                raise ValueError(f"default_option_id '{self.default_option_id}' not found in decision options")

        immutable_meta = _to_immutable_mapping(self.metadata)
        object.__setattr__(self, "metadata", immutable_meta)


@dataclass(frozen=True)
class DecisionResult:
    success: bool
    decision_id: str
    selected_option: DecisionOption | None
    resolution_type: DecisionResolutionType
    effects: tuple[EventEffect, ...]
    reasons: tuple[EventReason, ...]
    seed: str
    metadata: MappingProxyType = field(default_factory=lambda: MappingProxyType({}))
    error_code: DecisionErrorCode | None = None
    error_message: str | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.success, bool):
            raise ValueError("DecisionResult success must be a boolean")

        if not isinstance(self.decision_id, str) or not self.decision_id.strip():
            raise ValueError("DecisionResult decision_id must be a non-empty string")

        if self.selected_option is not None and not isinstance(self.selected_option, DecisionOption):
            raise ValueError(f"Expected DecisionOption or None, got {type(self.selected_option)}")

        if isinstance(self.resolution_type, str):
            try:
                object.__setattr__(self, "resolution_type", DecisionResolutionType(self.resolution_type))
            except ValueError:
                raise ValueError(f"Invalid DecisionResolutionType: '{self.resolution_type}'")
        elif not isinstance(self.resolution_type, DecisionResolutionType):
            raise ValueError(f"Invalid DecisionResolutionType: '{self.resolution_type}'")

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

        if not isinstance(self.seed, str) or not self.seed.strip():
            raise ValueError("DecisionResult seed must be a non-empty string")

        if self.error_code is not None:
            if isinstance(self.error_code, str):
                try:
                    object.__setattr__(self, "error_code", DecisionErrorCode(self.error_code))
                except ValueError:
                    raise ValueError(f"Invalid DecisionErrorCode: '{self.error_code}'")
            elif not isinstance(self.error_code, DecisionErrorCode):
                raise ValueError(f"Invalid DecisionErrorCode: '{self.error_code}'")

        immutable_meta = _to_immutable_mapping(self.metadata)
        object.__setattr__(self, "metadata", immutable_meta)


def derive_deterministic_decision_roll(
    seed: str,
    decision_id: str,
    step_tag: str = "decision",
) -> float:
    if not isinstance(seed, str) or not seed.strip():
        raise ValueError("seed must be a non-empty string")
    if not isinstance(decision_id, str) or not decision_id.strip():
        raise ValueError("decision_id must be a non-empty string")

    raw_key = f"decision_roll:{seed}:{decision_id}:{step_tag}"
    digest = hashlib.sha256(raw_key.encode("utf-8")).digest()
    int_val = int.from_bytes(digest[:8], byteorder="big")
    return int_val / (2**64 - 1)


def is_option_available(option: DecisionOption, context: EventContext) -> bool:
    if not option.available:
        return False
    if option.conditions is not None:
        eval_res = evaluate_event_conditions(option.conditions, context)
        if not eval_res.passed:
            return False
    return True


def resolve_decision(
    decision: Decision,
    context: EventContext,
    seed: str,
    explicit_option_id: str | None = None,
    resolution_type: DecisionResolutionType | str | None = None,
) -> DecisionResult:
    if not isinstance(decision, Decision):
        raise ValueError(f"Expected Decision, got {type(decision)}")
    if not isinstance(context, EventContext):
        raise ValueError(f"Expected EventContext, got {type(context)}")
    if not isinstance(seed, str) or not seed.strip():
        raise ValueError("seed must be a non-empty string")

    res_type = resolution_type if resolution_type is not None else decision.resolution_type
    if isinstance(res_type, str):
        try:
            res_type = DecisionResolutionType(res_type)
        except ValueError:
            return DecisionResult(
                success=False,
                decision_id=decision.id,
                selected_option=None,
                resolution_type=decision.resolution_type,
                effects=(),
                reasons=(EventReason(code="INVALID_RESOLUTION_TYPE", value=str(res_type)),),
                seed=seed,
                metadata=decision.metadata,
                error_code=DecisionErrorCode.INVALID_RESOLUTION_TYPE,
                error_message=f"Invalid resolution type: '{res_type}'",
            )

    if res_type == DecisionResolutionType.EXPLICIT:
        if explicit_option_id is None or not isinstance(explicit_option_id, str) or not explicit_option_id.strip():
            return DecisionResult(
                success=False,
                decision_id=decision.id,
                selected_option=None,
                resolution_type=res_type,
                effects=(),
                reasons=(EventReason(code="EXPLICIT_OPTION_MISSING", value=str(explicit_option_id)),),
                seed=seed,
                metadata=decision.metadata,
                error_code=DecisionErrorCode.INVALID_OPTION,
                error_message="Explicit option ID must be provided for EXPLICIT resolution mode",
            )

        matched_option = next((opt for opt in decision.options if opt.id == explicit_option_id), None)
        if matched_option is None:
            return DecisionResult(
                success=False,
                decision_id=decision.id,
                selected_option=None,
                resolution_type=res_type,
                effects=(),
                reasons=(EventReason(code="OPTION_NOT_FOUND", value=explicit_option_id),),
                seed=seed,
                metadata=decision.metadata,
                error_code=DecisionErrorCode.INVALID_OPTION,
                error_message=f"Option '{explicit_option_id}' does not exist in decision '{decision.id}'",
            )

        if not is_option_available(matched_option, context):
            return DecisionResult(
                success=False,
                decision_id=decision.id,
                selected_option=None,
                resolution_type=res_type,
                effects=(),
                reasons=(EventReason(code="OPTION_UNAVAILABLE", value=explicit_option_id),),
                seed=seed,
                metadata=decision.metadata,
                error_code=DecisionErrorCode.OPTION_UNAVAILABLE,
                error_message=f"Option '{explicit_option_id}' is unavailable",
            )

        sorted_effects = tuple(sorted(matched_option.effects, key=lambda e: e.id))
        return DecisionResult(
            success=True,
            decision_id=decision.id,
            selected_option=matched_option,
            resolution_type=res_type,
            effects=sorted_effects,
            reasons=(EventReason(code="EXPLICIT_SELECTION", value=explicit_option_id),),
            seed=seed,
            metadata=decision.metadata,
        )

    elif res_type == DecisionResolutionType.DEFAULT:
        if decision.default_option_id is None:
            return DecisionResult(
                success=False,
                decision_id=decision.id,
                selected_option=None,
                resolution_type=res_type,
                effects=(),
                reasons=(EventReason(code="DEFAULT_OPTION_NOT_CONFIGURED", value=decision.id),),
                seed=seed,
                metadata=decision.metadata,
                error_code=DecisionErrorCode.INVALID_DEFAULT_OPTION,
                error_message=f"Decision '{decision.id}' has no default_option_id configured",
            )

        default_opt = next((opt for opt in decision.options if opt.id == decision.default_option_id), None)
        if default_opt is None:
            return DecisionResult(
                success=False,
                decision_id=decision.id,
                selected_option=None,
                resolution_type=res_type,
                effects=(),
                reasons=(EventReason(code="DEFAULT_OPTION_NOT_FOUND", value=decision.default_option_id),),
                seed=seed,
                metadata=decision.metadata,
                error_code=DecisionErrorCode.INVALID_DEFAULT_OPTION,
                error_message=f"Default option '{decision.default_option_id}' not found in decision",
            )

        if not is_option_available(default_opt, context):
            return DecisionResult(
                success=False,
                decision_id=decision.id,
                selected_option=None,
                resolution_type=res_type,
                effects=(),
                reasons=(EventReason(code="DEFAULT_OPTION_UNAVAILABLE", value=decision.default_option_id),),
                seed=seed,
                metadata=decision.metadata,
                error_code=DecisionErrorCode.OPTION_UNAVAILABLE,
                error_message=f"Default option '{decision.default_option_id}' is unavailable",
            )

        sorted_effects = tuple(sorted(default_opt.effects, key=lambda e: e.id))
        return DecisionResult(
            success=True,
            decision_id=decision.id,
            selected_option=default_opt,
            resolution_type=res_type,
            effects=sorted_effects,
            reasons=(EventReason(code="DEFAULT_SELECTION", value=decision.default_option_id),),
            seed=seed,
            metadata=decision.metadata,
        )

    elif res_type == DecisionResolutionType.WEIGHTED:
        available_options = [opt for opt in decision.options if is_option_available(opt, context)]
        if not available_options:
            return DecisionResult(
                success=False,
                decision_id=decision.id,
                selected_option=None,
                resolution_type=res_type,
                effects=(),
                reasons=(EventReason(code="NO_AVAILABLE_OPTIONS", value=decision.id),),
                seed=seed,
                metadata=decision.metadata,
                error_code=DecisionErrorCode.OPTION_UNAVAILABLE,
                error_message="No options are available for decision",
            )

        # Validate weights of available options
        for opt in available_options:
            if math.isnan(opt.weight) or math.isinf(opt.weight) or opt.weight < 0:
                return DecisionResult(
                    success=False,
                    decision_id=decision.id,
                    selected_option=None,
                    resolution_type=res_type,
                    effects=(),
                    reasons=(EventReason(code="INVALID_OPTION_WEIGHT", value=opt.id),),
                    seed=seed,
                    metadata=decision.metadata,
                    error_code=DecisionErrorCode.INVALID_WEIGHT,
                    error_message=f"Option '{opt.id}' has invalid weight: {opt.weight}",
                )

        total_weight = sum(opt.weight for opt in available_options)
        if total_weight <= 0.0:
            return DecisionResult(
                success=False,
                decision_id=decision.id,
                selected_option=None,
                resolution_type=res_type,
                effects=(),
                reasons=(EventReason(code="ALL_ZERO_WEIGHTS", value=decision.id),),
                seed=seed,
                metadata=decision.metadata,
                error_code=DecisionErrorCode.NO_SELECTABLE_OPTION,
                error_message="All available options have zero weight",
            )

        positive_weight_options = [opt for opt in available_options if opt.weight > 0.0]

        if len(positive_weight_options) == 1:
            selected_opt = positive_weight_options[0]
            sorted_effects = tuple(sorted(selected_opt.effects, key=lambda e: e.id))
            return DecisionResult(
                success=True,
                decision_id=decision.id,
                selected_option=selected_opt,
                resolution_type=res_type,
                effects=sorted_effects,
                reasons=(EventReason(code="SINGLE_AVAILABLE_OPTION", value=selected_opt.id),),
                seed=seed,
                metadata=decision.metadata,
            )

        roll_val = derive_deterministic_decision_roll(seed=seed, decision_id=decision.id)
        target_accum = roll_val * total_weight
        cursor = 0.0
        selected_opt: DecisionOption | None = None

        for opt in positive_weight_options:
            cursor += opt.weight
            if cursor >= target_accum:
                selected_opt = opt
                break

        if selected_opt is None:
            selected_opt = positive_weight_options[-1]

        sorted_effects = tuple(sorted(selected_opt.effects, key=lambda e: e.id))
        meta_dict = dict(decision.metadata)
        meta_dict.update({
            "roll_val": roll_val,
            "total_weight": total_weight,
            "selected_weight": selected_opt.weight,
        })
        meta_proxy = _to_immutable_mapping(meta_dict)

        return DecisionResult(
            success=True,
            decision_id=decision.id,
            selected_option=selected_opt,
            resolution_type=res_type,
            effects=sorted_effects,
            reasons=(EventReason(code="WEIGHTED_SELECTION", value=selected_opt.id, weight=selected_opt.weight),),
            seed=seed,
            metadata=meta_proxy,
        )

    else:
        return DecisionResult(
            success=False,
            decision_id=decision.id,
            selected_option=None,
            resolution_type=res_type,
            effects=(),
            reasons=(EventReason(code="UNSUPPORTED_RESOLUTION_TYPE", value=str(res_type)),),
            seed=seed,
            metadata=decision.metadata,
            error_code=DecisionErrorCode.INVALID_RESOLUTION_TYPE,
            error_message=f"Unsupported resolution type: '{res_type}'",
        )


def apply_decision_result(
    state: Any,
    result: DecisionResult,
    context: EventContext | None = None,
) -> EffectApplicationResult:
    if not isinstance(result, DecisionResult):
        raise ValueError(f"Expected DecisionResult, got {type(result)}")

    if not result.success or result.selected_option is None or len(result.effects) == 0:
        return EffectApplicationResult(
            success=result.success,
            applications=(),
            errors=(),
            resulting_state=state,
            metadata=result.metadata,
        )

    return apply_effects(
        state=state,
        effects=result.effects,
        context=context,
        event_id=result.decision_id,
    )
