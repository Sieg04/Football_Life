import math
from dataclasses import dataclass, field
from enum import StrEnum
from types import MappingProxyType
from typing import Any, Sequence

from app.event.domain import EventContext, _is_valid_primitive


class ConditionOperator(StrEnum):
    EQ = "EQ"
    NEQ = "NEQ"
    GT = "GT"
    GTE = "GTE"
    LT = "LT"
    LTE = "LTE"
    CONTAINS = "CONTAINS"
    IN = "IN"
    NOT_IN = "NOT_IN"


class ConditionCompositionType(StrEnum):
    ALL = "ALL"
    ANY = "ANY"
    NOT = "NOT"


@dataclass(frozen=True)
class EventCondition:
    id: str
    field_path: str
    operator: ConditionOperator
    expected_value: Any

    def __post_init__(self) -> None:
        if not isinstance(self.id, str) or not self.id.strip():
            raise ValueError("EventCondition id must be a non-empty string")
        if not isinstance(self.field_path, str) or not self.field_path.strip():
            raise ValueError("EventCondition field_path must be a non-empty string")

        if isinstance(self.operator, str):
            try:
                object.__setattr__(self, "operator", ConditionOperator(self.operator))
            except ValueError:
                raise ValueError(f"Invalid ConditionOperator: '{self.operator}'")
        elif not isinstance(self.operator, ConditionOperator):
            raise ValueError(f"Invalid ConditionOperator: '{self.operator}'")

        if isinstance(self.expected_value, float):
            if math.isnan(self.expected_value) or math.isinf(self.expected_value):
                raise ValueError("Condition expected_value must not be NaN or Infinity")

        if not _is_valid_primitive(self.expected_value):
            raise ValueError(f"Unsupported non-primitive expected_value: {type(self.expected_value)}")


@dataclass(frozen=True)
class ConditionResult:
    passed: bool
    condition_id: str
    reason: str
    observed_value: Any
    expected_value: Any

    def __post_init__(self) -> None:
        if not isinstance(self.passed, bool):
            raise ValueError("ConditionResult passed must be a boolean")
        if not isinstance(self.condition_id, str) or not self.condition_id.strip():
            raise ValueError("ConditionResult condition_id must be a non-empty string")
        if not isinstance(self.reason, str) or not self.reason.strip():
            raise ValueError("ConditionResult reason must be a non-empty string")

        if isinstance(self.observed_value, float):
            if math.isnan(self.observed_value) or math.isinf(self.observed_value):
                raise ValueError("Observed value must not be NaN or Infinity")

        if not _is_valid_primitive(self.observed_value):
            raise ValueError(f"Unsupported non-primitive observed_value: {type(self.observed_value)}")

        if isinstance(self.expected_value, float):
            if math.isnan(self.expected_value) or math.isinf(self.expected_value):
                raise ValueError("Expected value must not be NaN or Infinity")

        if not _is_valid_primitive(self.expected_value):
            raise ValueError(f"Unsupported non-primitive expected_value: {type(self.expected_value)}")


@dataclass(frozen=True)
class ConditionCompositionNode:
    composition_type: ConditionCompositionType
    conditions: tuple[EventCondition, ...] = ()
    children: tuple["ConditionCompositionNode", ...] = ()

    def __post_init__(self) -> None:
        if isinstance(self.composition_type, str):
            try:
                object.__setattr__(self, "composition_type", ConditionCompositionType(self.composition_type))
            except ValueError:
                raise ValueError(f"Invalid ConditionCompositionType: '{self.composition_type}'")
        elif not isinstance(self.composition_type, ConditionCompositionType):
            raise ValueError(f"Invalid ConditionCompositionType: '{self.composition_type}'")

        if not isinstance(self.conditions, tuple):
            object.__setattr__(self, "conditions", tuple(self.conditions))
        for cond in self.conditions:
            if not isinstance(cond, EventCondition):
                raise ValueError(f"Expected EventCondition, got {type(cond)}")

        if not isinstance(self.children, tuple):
            object.__setattr__(self, "children", tuple(self.children))
        for child in self.children:
            if not isinstance(child, ConditionCompositionNode):
                raise ValueError(f"Expected ConditionCompositionNode, got {type(child)}")

        if self.composition_type == ConditionCompositionType.NOT:
            total_elements = len(self.conditions) + len(self.children)
            if total_elements != 1:
                raise ValueError("NOT composition node must contain exactly 1 condition or 1 child node")


@dataclass(frozen=True)
class ConditionEvaluationResult:
    passed: bool
    results: tuple[ConditionResult, ...]
    node_type: ConditionCompositionType | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.passed, bool):
            raise ValueError("ConditionEvaluationResult passed must be a boolean")
        if not isinstance(self.results, tuple):
            object.__setattr__(self, "results", tuple(self.results))
        for res in self.results:
            if not isinstance(res, ConditionResult):
                raise ValueError(f"Expected ConditionResult, got {type(res)}")


def _resolve_field_value(context: EventContext, field_path: str) -> Any:
    if not isinstance(field_path, str) or not field_path.strip():
        return None

    parts = field_path.strip().split(".")
    root_field = parts[0]

    if root_field == "season":
        val = context.season
    elif root_field == "player_id":
        val = context.player_id
    elif root_field == "club_id":
        val = context.club_id
    elif root_field == "competition_id":
        val = context.competition_id
    elif root_field == "event_type":
        val = context.event_type.value if context.event_type else None
    elif root_field == "attributes":
        val = context.attributes
    else:
        val = context.attributes.get(root_field)
        if len(parts) == 1:
            return val

    if len(parts) > 1:
        curr = val
        for part in parts[1:]:
            if isinstance(curr, (dict, MappingProxyType)):
                curr = curr.get(part)
            else:
                return None
        return curr

    return val


def evaluate_condition(condition: EventCondition, context: EventContext) -> ConditionResult:
    if not isinstance(condition, EventCondition):
        raise ValueError(f"Expected EventCondition, got {type(condition)}")
    if not isinstance(context, EventContext):
        raise ValueError(f"Expected EventContext, got {type(context)}")

    observed = _resolve_field_value(context, condition.field_path)
    expected = condition.expected_value
    op = condition.operator

    if observed is None:
        return ConditionResult(
            passed=False,
            condition_id=condition.id,
            reason="MISSING_ATTRIBUTE",
            observed_value=None,
            expected_value=expected,
        )

    passed = False
    reason = "COMPARISON_FAILED"

    try:
        if op == ConditionOperator.EQ:
            passed = (observed == expected)
        elif op == ConditionOperator.NEQ:
            passed = (observed != expected)
        elif op == ConditionOperator.GT:
            passed = (observed > expected)
        elif op == ConditionOperator.GTE:
            passed = (observed >= expected)
        elif op == ConditionOperator.LT:
            passed = (observed < expected)
        elif op == ConditionOperator.LTE:
            passed = (observed <= expected)
        elif op == ConditionOperator.CONTAINS:
            if isinstance(observed, (tuple, list, str, MappingProxyType, dict)):
                passed = (expected in observed)
            else:
                passed = False
                reason = "INVALID_CONTAINS_TYPE"
        elif op == ConditionOperator.IN:
            if isinstance(expected, (tuple, list)):
                passed = (observed in expected)
            else:
                passed = False
                reason = "INVALID_IN_TYPE"
        elif op == ConditionOperator.NOT_IN:
            if isinstance(expected, (tuple, list)):
                passed = (observed not in expected)
            else:
                passed = False
                reason = "INVALID_NOT_IN_TYPE"
    except TypeError:
        passed = False
        reason = "TYPE_MISMATCH"

    if passed:
        reason = "CONDITION_MET"

    return ConditionResult(
        passed=passed,
        condition_id=condition.id,
        reason=reason,
        observed_value=observed,
        expected_value=expected,
    )


def evaluate_composition(
    node: ConditionCompositionNode,
    context: EventContext,
) -> ConditionEvaluationResult:
    if not isinstance(node, ConditionCompositionNode):
        raise ValueError(f"Expected ConditionCompositionNode, got {type(node)}")
    if not isinstance(context, EventContext):
        raise ValueError(f"Expected EventContext, got {type(context)}")

    sub_results: list[ConditionResult] = []
    boolean_evals: list[bool] = []

    # Evaluate direct conditions
    for cond in node.conditions:
        res = evaluate_condition(cond, context)
        sub_results.append(res)
        boolean_evals.append(res.passed)

    # Evaluate child nodes
    for child in node.children:
        child_eval = evaluate_composition(child, context)
        sub_results.extend(child_eval.results)
        boolean_evals.append(child_eval.passed)

    comp_type = node.composition_type

    if comp_type == ConditionCompositionType.ALL:
        passed = all(boolean_evals) if boolean_evals else True
    elif comp_type == ConditionCompositionType.ANY:
        passed = any(boolean_evals) if boolean_evals else True
    elif comp_type == ConditionCompositionType.NOT:
        if len(boolean_evals) == 1:
            passed = not boolean_evals[0]
        else:
            passed = False

    return ConditionEvaluationResult(
        passed=passed,
        results=tuple(sub_results),
        node_type=comp_type,
    )


def evaluate_event_conditions(
    conditions: Sequence[EventCondition] | ConditionCompositionNode | None,
    context: EventContext,
) -> ConditionEvaluationResult:
    if not isinstance(context, EventContext):
        raise ValueError(f"Expected EventContext, got {type(context)}")

    if conditions is None:
        return ConditionEvaluationResult(passed=True, results=(), node_type=ConditionCompositionType.ALL)

    if isinstance(conditions, ConditionCompositionNode):
        return evaluate_composition(conditions, context)

    cond_tuple = tuple(conditions)
    for c in cond_tuple:
        if not isinstance(c, EventCondition):
            raise ValueError(f"Expected EventCondition instance, got {type(c)}")

    node = ConditionCompositionNode(
        composition_type=ConditionCompositionType.ALL,
        conditions=cond_tuple,
    )
    return evaluate_composition(node, context)
