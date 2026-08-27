import pytest
from app.event import (
    ConditionCompositionNode,
    ConditionCompositionType,
    ConditionEvaluationResult,
    ConditionOperator,
    ConditionResult,
    EventCondition,
    EventContext,
    EventType,
    evaluate_composition,
    evaluate_condition,
    evaluate_event_conditions,
)


def test_event_condition_valid():
    cond = EventCondition(
        id="cond_age_18",
        field_path="attributes.age",
        operator=ConditionOperator.GTE,
        expected_value=18,
    )
    assert cond.id == "cond_age_18"
    assert cond.field_path == "attributes.age"
    assert cond.operator == ConditionOperator.GTE
    assert cond.expected_value == 18


def test_event_condition_validation():
    with pytest.raises(ValueError, match="id must be a non-empty string"):
        EventCondition(id="", field_path="age", operator=ConditionOperator.EQ, expected_value=20)

    with pytest.raises(ValueError, match="field_path must be a non-empty string"):
        EventCondition(id="c1", field_path="  ", operator=ConditionOperator.EQ, expected_value=20)

    with pytest.raises(ValueError, match="Invalid ConditionOperator"):
        EventCondition(id="c1", field_path="age", operator="BAD_OP", expected_value=20)  # type: ignore

    with pytest.raises(ValueError, match="expected_value must not be NaN or Infinity"):
        EventCondition(id="c1", field_path="age", operator=ConditionOperator.GT, expected_value=float("nan"))


def test_evaluate_condition_operators():
    ctx = EventContext(
        season=2025,
        player_id="p10",
        attributes={"age": 22, "ovr": 80, "roles": ("ST", "LW"), "name": "Alex"},
    )

    # EQ
    c_eq = EventCondition(id="c1", field_path="attributes.age", operator=ConditionOperator.EQ, expected_value=22)
    res_eq = evaluate_condition(c_eq, ctx)
    assert res_eq.passed is True
    assert res_eq.observed_value == 22

    # NEQ
    c_neq = EventCondition(id="c2", field_path="attributes.age", operator=ConditionOperator.NEQ, expected_value=20)
    assert evaluate_condition(c_neq, ctx).passed is True

    # GT / GTE
    c_gt = EventCondition(id="c3", field_path="attributes.ovr", operator=ConditionOperator.GT, expected_value=79)
    assert evaluate_condition(c_gt, ctx).passed is True
    c_gte = EventCondition(id="c4", field_path="attributes.ovr", operator=ConditionOperator.GTE, expected_value=80)
    assert evaluate_condition(c_gte, ctx).passed is True

    # LT / LTE
    c_lt = EventCondition(id="c5", field_path="attributes.ovr", operator=ConditionOperator.LT, expected_value=85)
    assert evaluate_condition(c_lt, ctx).passed is True
    c_lte = EventCondition(id="c6", field_path="attributes.ovr", operator=ConditionOperator.LTE, expected_value=80)
    assert evaluate_condition(c_lte, ctx).passed is True

    # CONTAINS
    c_contains = EventCondition(id="c7", field_path="attributes.roles", operator=ConditionOperator.CONTAINS, expected_value="ST")
    assert evaluate_condition(c_contains, ctx).passed is True

    # IN
    c_in = EventCondition(id="c8", field_path="attributes.age", operator=ConditionOperator.IN, expected_value=(20, 21, 22))
    assert evaluate_condition(c_in, ctx).passed is True

    # NOT_IN
    c_notin = EventCondition(id="c9", field_path="attributes.age", operator=ConditionOperator.NOT_IN, expected_value=(30, 31))
    assert evaluate_condition(c_notin, ctx).passed is True


def test_evaluate_condition_missing_attribute():
    ctx = EventContext(season=2025, attributes={"ovr": 75})
    c_missing = EventCondition(id="c_missing", field_path="attributes.form", operator=ConditionOperator.GT, expected_value=6.0)
    res = evaluate_condition(c_missing, ctx)
    assert res.passed is False
    assert res.reason == "MISSING_ATTRIBUTE"
    assert res.observed_value is None


def test_composition_all_any_not():
    ctx = EventContext(season=2025, attributes={"age": 20, "ovr": 75})

    c_age = EventCondition(id="c_age", field_path="attributes.age", operator=ConditionOperator.GTE, expected_value=18)
    c_ovr = EventCondition(id="c_ovr", field_path="attributes.ovr", operator=ConditionOperator.GTE, expected_value=80)

    # ALL (age GTE 18 AND ovr GTE 80) -> False
    node_all = ConditionCompositionNode(
        composition_type=ConditionCompositionType.ALL,
        conditions=(c_age, c_ovr),
    )
    res_all = evaluate_composition(node_all, ctx)
    assert res_all.passed is False

    # ANY (age GTE 18 OR ovr GTE 80) -> True
    node_any = ConditionCompositionNode(
        composition_type=ConditionCompositionType.ANY,
        conditions=(c_age, c_ovr),
    )
    res_any = evaluate_composition(node_any, ctx)
    assert res_any.passed is True

    # NOT (ovr GTE 80) -> True because ovr is 75 < 80
    node_not = ConditionCompositionNode(
        composition_type=ConditionCompositionType.NOT,
        conditions=(c_ovr,),
    )
    res_not = evaluate_composition(node_not, ctx)
    assert res_not.passed is True


def test_nested_composition():
    ctx = EventContext(season=2025, attributes={"age": 21, "ovr": 78, "morale": 85})

    # ALL (age >= 18, ovr >= 75, ANY(morale >= 90, ovr >= 75))
    c1 = EventCondition(id="c1", field_path="attributes.age", operator=ConditionOperator.GTE, expected_value=18)
    c2 = EventCondition(id="c2", field_path="attributes.ovr", operator=ConditionOperator.GTE, expected_value=75)
    c3 = EventCondition(id="c3", field_path="attributes.morale", operator=ConditionOperator.GTE, expected_value=90)

    any_child = ConditionCompositionNode(
        composition_type=ConditionCompositionType.ANY,
        conditions=(c3, c2),
    )
    root_all = ConditionCompositionNode(
        composition_type=ConditionCompositionType.ALL,
        conditions=(c1,),
        children=(any_child,),
    )

    res = evaluate_event_conditions(root_all, ctx)
    assert res.passed is True


def test_condition_result_immutability():
    ctx = EventContext(season=2025, attributes={"age": 20})
    c = EventCondition(id="c1", field_path="attributes.age", operator=ConditionOperator.EQ, expected_value=20)
    res = evaluate_condition(c, ctx)

    with pytest.raises(AttributeError):
        res.passed = False  # type: ignore
