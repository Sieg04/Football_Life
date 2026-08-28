import dataclasses
import copy
import math
from dataclasses import dataclass, field
from enum import StrEnum
from types import MappingProxyType
from typing import Any, Sequence

from app.event.domain import EventContext, _is_valid_primitive, _to_immutable_mapping
from app.event.resolution import (
    EventEffect,
    EventEffectType,
    EventOutcome,
    EventResolution,
    EventResolutionStatus,
)


class EffectOperation(StrEnum):
    ADD = "ADD"
    SET = "SET"
    MULTIPLY = "MULTIPLY"


class EffectErrorCode(StrEnum):
    INVALID_EFFECT = "INVALID_EFFECT"
    UNKNOWN_TARGET = "UNKNOWN_TARGET"
    INVALID_OPERATION = "INVALID_OPERATION"
    TYPE_MISMATCH = "TYPE_MISMATCH"
    INVALID_VALUE = "INVALID_VALUE"
    OUT_OF_RANGE = "OUT_OF_RANGE"
    INVALID_STATE = "INVALID_STATE"


@dataclass(frozen=True)
class EffectTarget:
    target_id: str
    target_type: str
    attribute: str
    scope: str = "player"

    def __post_init__(self) -> None:
        if not isinstance(self.target_id, str) or not self.target_id.strip():
            raise ValueError("EffectTarget target_id must be a non-empty string")
        if not isinstance(self.target_type, str) or not self.target_type.strip():
            raise ValueError("EffectTarget target_type must be a non-empty string")
        if not isinstance(self.attribute, str) or not self.attribute.strip():
            raise ValueError("EffectTarget attribute must be a non-empty string")
        if not isinstance(self.scope, str) or not self.scope.strip():
            raise ValueError("EffectTarget scope must be a non-empty string")


@dataclass(frozen=True)
class EffectApplicationError:
    code: EffectErrorCode
    message: str
    effect_id: str | None = None
    effect_index: int | None = None
    target: str | None = None
    details: MappingProxyType = field(default_factory=lambda: MappingProxyType({}))

    def __post_init__(self) -> None:
        if isinstance(self.code, str):
            try:
                object.__setattr__(self, "code", EffectErrorCode(self.code))
            except ValueError:
                raise ValueError(f"Invalid EffectErrorCode: '{self.code}'")
        elif not isinstance(self.code, EffectErrorCode):
            raise ValueError(f"Invalid EffectErrorCode: '{self.code}'")

        if not isinstance(self.message, str) or not self.message.strip():
            raise ValueError("EffectApplicationError message must be a non-empty string")

        immutable_details = _to_immutable_mapping(self.details)
        object.__setattr__(self, "details", immutable_details)


@dataclass(frozen=True)
class EffectApplication:
    target: str
    operation: EffectOperation
    requested_value: float | int | str | bool
    previous_value: float | int | str | bool | None
    resulting_value: float | int | str | bool | None
    applied: bool
    event_id: str | None = None
    effect_id: str | None = None
    effect_index: int | None = None
    metadata: MappingProxyType = field(default_factory=lambda: MappingProxyType({}))

    def __post_init__(self) -> None:
        if not isinstance(self.target, str) or not self.target.strip():
            raise ValueError("EffectApplication target must be a non-empty string")

        if isinstance(self.operation, str):
            try:
                object.__setattr__(self, "operation", EffectOperation(self.operation))
            except ValueError:
                raise ValueError(f"Invalid EffectOperation: '{self.operation}'")
        elif not isinstance(self.operation, EffectOperation):
            raise ValueError(f"Invalid EffectOperation: '{self.operation}'")

        if self.requested_value is not None:
            if isinstance(self.requested_value, float) and (
                math.isnan(self.requested_value) or math.isinf(self.requested_value)
            ):
                raise ValueError("EffectApplication requested_value must not be NaN or Infinity")
            if not _is_valid_primitive(self.requested_value):
                raise ValueError(f"Unsupported non-primitive requested_value: {type(self.requested_value)}")

        if self.previous_value is not None:
            if isinstance(self.previous_value, float) and (
                math.isnan(self.previous_value) or math.isinf(self.previous_value)
            ):
                raise ValueError("EffectApplication previous_value must not be NaN or Infinity")

        if self.resulting_value is not None:
            if isinstance(self.resulting_value, float) and (
                math.isnan(self.resulting_value) or math.isinf(self.resulting_value)
            ):
                raise ValueError("EffectApplication resulting_value must not be NaN or Infinity")

        if not isinstance(self.applied, bool):
            raise ValueError("EffectApplication applied must be a boolean")

        immutable_meta = _to_immutable_mapping(self.metadata)
        object.__setattr__(self, "metadata", immutable_meta)


@dataclass(frozen=True)
class EffectApplicationResult:
    success: bool
    applications: tuple[EffectApplication, ...]
    errors: tuple[EffectApplicationError, ...]
    resulting_state: Any
    metadata: MappingProxyType = field(default_factory=lambda: MappingProxyType({}))

    def __post_init__(self) -> None:
        if not isinstance(self.success, bool):
            raise ValueError("EffectApplicationResult success must be a boolean")

        if not isinstance(self.applications, tuple):
            object.__setattr__(self, "applications", tuple(self.applications))
        for app in self.applications:
            if not isinstance(app, EffectApplication):
                raise ValueError(f"Expected EffectApplication, got {type(app)}")

        if not isinstance(self.errors, tuple):
            object.__setattr__(self, "errors", tuple(self.errors))
        for err in self.errors:
            if not isinstance(err, EffectApplicationError):
                raise ValueError(f"Expected EffectApplicationError, got {type(err)}")

        immutable_meta = _to_immutable_mapping(self.metadata)
        object.__setattr__(self, "metadata", immutable_meta)


class EffectApplicationException(Exception):

    def __init__(self, error: EffectApplicationError) -> None:
        super().__init__(error.message)
        self.error = error


EFFECT_TYPE_ATTRIBUTE_MAP: dict[EventEffectType, str] = {
    EventEffectType.PLAYER_MORALE_CHANGE: "morale",
    EventEffectType.PLAYER_CONFIDENCE_CHANGE: "confidence",
    EventEffectType.PLAYER_FORM_CHANGE: "form",
    EventEffectType.PLAYER_FITNESS_CHANGE: "fitness",
    EventEffectType.PLAYER_REPUTATION_CHANGE: "reputation",
    EventEffectType.PLAYER_HAPPINESS_CHANGE: "happiness",
    EventEffectType.CLUB_MORALE_CHANGE: "morale",
    EventEffectType.CLUB_MOMENTUM_CHANGE: "momentum",
}


def resolve_effect_target(effect: EventEffect) -> EffectTarget:
    attr = (
        effect.parameters.get("attribute")
        or effect.parameters.get("field_path")
        or effect.parameters.get("target")
    )
    if not attr:
        attr = EFFECT_TYPE_ATTRIBUTE_MAP.get(effect.effect_type)
    if not attr:
        attr = str(effect.effect_type).lower()

    scope = str(effect.target_type).lower()
    return EffectTarget(
        target_id=effect.target_id,
        target_type=effect.target_type,
        attribute=str(attr),
        scope=scope,
    )


def _resolve_target_value(
    state: Any,
    target: EffectTarget,
    effect_id: str | None = None,
    effect_index: int | None = None,
) -> tuple[Any, str, Any, Any]:
    attr_name = target.attribute
    target_str = f"{target.scope}.{attr_name}" if target.scope else attr_name

    if state is None:
        raise EffectApplicationException(
            EffectApplicationError(
                code=EffectErrorCode.INVALID_STATE,
                message="Simulation state is None",
                effect_id=effect_id,
                effect_index=effect_index,
                target=target_str,
            )
        )

    # 1. State is a dict
    if isinstance(state, dict):
        if attr_name in state:
            return (state, attr_name, state[attr_name], "dict")
        if target.scope in state and isinstance(state[target.scope], dict):
            if attr_name in state[target.scope]:
                return (state[target.scope], attr_name, state[target.scope][attr_name], "nested_dict")
        if "." in attr_name:
            parts = attr_name.split(".")
            curr = state
            for p in parts[:-1]:
                if isinstance(curr, dict) and p in curr:
                    curr = curr[p]
                elif hasattr(curr, p):
                    curr = getattr(curr, p)
                else:
                    curr = None
                    break
            if curr is not None and isinstance(curr, dict) and parts[-1] in curr:
                return (curr, parts[-1], curr[parts[-1]], "nested_dict")
            if curr is not None and hasattr(curr, parts[-1]):
                return (curr, parts[-1], getattr(curr, parts[-1]), "nested_attr")

    # 2. State is Player or object with sub-dataclasses
    if hasattr(state, "state") and getattr(state, "state") is not None:
        player_state = getattr(state, "state")
        if hasattr(player_state, attr_name):
            return (player_state, attr_name, getattr(player_state, attr_name), "sub_dataclass_state")

    if hasattr(state, "attributes") and getattr(state, "attributes") is not None:
        player_attrs = getattr(state, "attributes")
        if hasattr(player_attrs, attr_name):
            return (player_attrs, attr_name, getattr(player_attrs, attr_name), "sub_dataclass_attributes")

    if hasattr(state, attr_name):
        return (state, attr_name, getattr(state, attr_name), "direct_attr")

    if "." in attr_name:
        parts = attr_name.split(".")
        curr = state
        for p in parts[:-1]:
            if hasattr(curr, p):
                curr = getattr(curr, p)
            elif isinstance(curr, dict) and p in curr:
                curr = curr[p]
            else:
                curr = None
                break
        if curr is not None and hasattr(curr, parts[-1]):
            return (curr, parts[-1], getattr(curr, parts[-1]), "nested_attr")
        if curr is not None and isinstance(curr, dict) and parts[-1] in curr:
            return (curr, parts[-1], curr[parts[-1]], "nested_dict")

    raise EffectApplicationException(
        EffectApplicationError(
            code=EffectErrorCode.UNKNOWN_TARGET,
            message=f"Target attribute '{attr_name}' not found on state model ({type(state).__name__})",
            effect_id=effect_id,
            effect_index=effect_index,
            target=target_str,
        )
    )


def _update_state_tree(
    root_state: Any,
    sub_container: Any,
    attr_name: str,
    new_value: Any,
    loc_type: str,
    target: EffectTarget | None = None,
) -> Any:
    if loc_type == "dict":
        new_dict = dict(root_state)
        new_dict[attr_name] = new_value
        return new_dict

    if loc_type == "nested_dict":
        new_root = copy.deepcopy(root_state)
        if target and target.scope in new_root and isinstance(new_root[target.scope], dict):
            new_root[target.scope][attr_name] = new_value
        elif "." in attr_name:
            parts = attr_name.split(".")
            curr = new_root
            for p in parts[:-1]:
                if isinstance(curr, dict) and p in curr:
                    curr = curr[p]
            if isinstance(curr, dict):
                curr[parts[-1]] = new_value
        return new_root

    if loc_type == "sub_dataclass_state":
        new_sub = dataclasses.replace(sub_container, **{attr_name: new_value})
        return dataclasses.replace(root_state, state=new_sub)

    if loc_type == "sub_dataclass_attributes":
        new_sub = dataclasses.replace(sub_container, **{attr_name: new_value})
        return dataclasses.replace(root_state, attributes=new_sub)

    if loc_type == "direct_attr":
        if dataclasses.is_dataclass(root_state):
            return dataclasses.replace(root_state, **{attr_name: new_value})
        new_root = copy.deepcopy(root_state)
        setattr(new_root, attr_name, new_value)
        return new_root

    new_root = copy.deepcopy(root_state)
    if hasattr(new_root, attr_name):
        setattr(new_root, attr_name, new_value)
    elif isinstance(new_root, dict):
        new_root[attr_name] = new_value
    return new_root


def _execute_operation(
    operation: EffectOperation,
    current_value: Any,
    requested_value: Any,
    min_bound: float | int | None,
    max_bound: float | int | None,
    effect_id: str | None = None,
    effect_index: int | None = None,
    target_str: str = "",
) -> Any:
    if not isinstance(operation, EffectOperation):
        try:
            operation = EffectOperation(str(operation))
        except ValueError:
            raise EffectApplicationException(
                EffectApplicationError(
                    code=EffectErrorCode.INVALID_OPERATION,
                    message=f"Unsupported operation: '{operation}'",
                    effect_id=effect_id,
                    effect_index=effect_index,
                    target=target_str,
                )
            )

    if current_value is None:
        raise EffectApplicationException(
            EffectApplicationError(
                code=EffectErrorCode.INVALID_STATE,
                message=f"Current value for target '{target_str}' is None",
                effect_id=effect_id,
                effect_index=effect_index,
                target=target_str,
            )
        )

    is_curr_bool = isinstance(current_value, bool)
    is_req_bool = isinstance(requested_value, bool)
    is_curr_num = isinstance(current_value, (int, float)) and not is_curr_bool
    is_req_num = isinstance(requested_value, (int, float)) and not is_req_bool

    if operation in (EffectOperation.ADD, EffectOperation.MULTIPLY):
        if not is_curr_num or not is_req_num:
            raise EffectApplicationException(
                EffectApplicationError(
                    code=EffectErrorCode.TYPE_MISMATCH,
                    message=(
                        f"Operation '{operation.value}' requires numeric current and requested values, "
                        f"got current={type(current_value).__name__}, requested={type(requested_value).__name__}"
                    ),
                    effect_id=effect_id,
                    effect_index=effect_index,
                    target=target_str,
                )
            )

        if operation == EffectOperation.ADD:
            raw_val = current_value + requested_value
        else:
            raw_val = current_value * requested_value

    elif operation == EffectOperation.SET:
        if is_curr_num:
            if not is_req_num:
                raise EffectApplicationException(
                    EffectApplicationError(
                        code=EffectErrorCode.TYPE_MISMATCH,
                        message=(
                            f"SET operation on numeric target '{target_str}' requires numeric value, "
                            f"got {type(requested_value).__name__}"
                        ),
                        effect_id=effect_id,
                        effect_index=effect_index,
                        target=target_str,
                    )
                )
            raw_val = requested_value
        else:
            raw_val = requested_value

    else:
        raise EffectApplicationException(
            EffectApplicationError(
                code=EffectErrorCode.INVALID_OPERATION,
                message=f"Unknown operation: '{operation}'",
                effect_id=effect_id,
                effect_index=effect_index,
                target=target_str,
            )
        )

    if isinstance(raw_val, (int, float)) and not isinstance(raw_val, bool):
        final_val = raw_val
        if min_bound is not None:
            final_val = max(min_bound, final_val)
        if max_bound is not None:
            final_val = min(max_bound, final_val)

        if isinstance(final_val, float):
            final_val = round(final_val, 4)

        if isinstance(current_value, int) and isinstance(requested_value, int) and not isinstance(final_val, int):
            if final_val.is_integer():
                final_val = int(final_val)

        return final_val

    return raw_val


def apply_effect(
    state: Any,
    effect: EventEffect,
    context: EventContext | None = None,
    effect_index: int | None = None,
    event_id: str | None = None,
) -> tuple[Any, EffectApplication]:
    if not isinstance(effect, EventEffect):
        raise ValueError(f"Expected EventEffect, got {type(effect)}")

    target = resolve_effect_target(effect)
    target_str = f"{target.scope}.{target.attribute}" if target.scope else target.attribute

    sub_container, attr_name, current_val, loc_type = _resolve_target_value(
        state=state,
        target=target,
        effect_id=effect.id,
        effect_index=effect_index,
    )

    operation = getattr(effect, "operation", EffectOperation.ADD)
    if "operation" in effect.parameters:
        try:
            operation = EffectOperation(str(effect.parameters["operation"]))
        except ValueError:
            raise EffectApplicationException(
                EffectApplicationError(
                    code=EffectErrorCode.INVALID_OPERATION,
                    message=f"Invalid EffectOperation parameter: '{effect.parameters['operation']}'",
                    effect_id=effect.id,
                    effect_index=effect_index,
                    target=target_str,
                )
            )

    new_val = _execute_operation(
        operation=operation,
        current_value=current_val,
        requested_value=effect.delta_or_value,
        min_bound=effect.min_bound,
        max_bound=effect.max_bound,
        effect_id=effect.id,
        effect_index=effect_index,
        target_str=target_str,
    )

    new_state = _update_state_tree(
        root_state=state,
        sub_container=sub_container,
        attr_name=attr_name,
        new_value=new_val,
        loc_type=loc_type,
        target=target,
    )

    app_record = EffectApplication(
        target=target_str,
        operation=operation,
        requested_value=effect.delta_or_value,
        previous_value=current_val,
        resulting_value=new_val,
        applied=True,
        event_id=event_id,
        effect_id=effect.id,
        effect_index=effect_index,
        metadata=effect.parameters,
    )

    return (new_state, app_record)


def apply_effects(
    state: Any,
    effects: Sequence[EventEffect],
    context: EventContext | None = None,
    event_id: str | None = None,
) -> EffectApplicationResult:
    effect_list = list(effects)
    for eff in effect_list:
        if not isinstance(eff, EventEffect):
            raise ValueError(f"Expected EventEffect, got {type(eff)}")

    curr_state = state
    applications: list[EffectApplication] = []

    for idx, eff in enumerate(effect_list):
        try:
            next_state, app_record = apply_effect(
                state=curr_state,
                effect=eff,
                context=context,
                effect_index=idx,
                event_id=event_id,
            )
            curr_state = next_state
            applications.append(app_record)
        except EffectApplicationException as exc:
            return EffectApplicationResult(
                success=False,
                applications=tuple(applications),
                errors=(exc.error,),
                resulting_state=state,
            )

    return EffectApplicationResult(
        success=True,
        applications=tuple(applications),
        errors=(),
        resulting_state=curr_state,
    )


def apply_event_outcome(
    state: Any,
    outcome: EventOutcome,
    context: EventContext | None = None,
    event_id: str | None = None,
) -> EffectApplicationResult:
    if not isinstance(outcome, EventOutcome):
        raise ValueError(f"Expected EventOutcome, got {type(outcome)}")

    return apply_effects(
        state=state,
        effects=outcome.effects,
        context=context,
        event_id=event_id,
    )


def apply_event_resolution(
    state: Any,
    resolution: EventResolution,
    context: EventContext | None = None,
) -> EffectApplicationResult:
    if not isinstance(resolution, EventResolution):
        raise ValueError(f"Expected EventResolution, got {type(resolution)}")

    if resolution.status != EventResolutionStatus.RESOLVED:
        return EffectApplicationResult(
            success=True,
            applications=(),
            errors=(),
            resulting_state=state,
            metadata=resolution.metadata,
        )

    return apply_effects(
        state=state,
        effects=resolution.effects,
        context=context,
        event_id=resolution.event_id,
    )
