import json
import math
import pytest

from app.event import (
    ConditionCompositionNode,
    ConditionCompositionType,
    ConditionOperator,
    Decision,
    DecisionErrorCode,
    DecisionOption,
    DecisionResolutionType,
    DecisionResult,
    EffectOperation,
    EventCondition,
    EventContext,
    EventEffect,
    EventEffectType,
    is_option_available,
    resolve_decision,
    to_json_bytes,
)


def test_valid_decision_construction():
    opt1 = DecisionOption(id="ACCEPT", label="Accept offer")
    opt2 = DecisionOption(id="REJECT", label="Reject offer", weight=0.5)
    dec = Decision(
        id="dec_transfer",
        prompt="Transfer offered",
        options=(opt1, opt2),
        resolution_type=DecisionResolutionType.WEIGHTED,
        default_option_id="REJECT",
    )

    assert dec.id == "dec_transfer"
    assert len(dec.options) == 2
    assert dec.default_option_id == "REJECT"
    assert dec.resolution_type == DecisionResolutionType.WEIGHTED


def test_invalid_empty_decision():
    with pytest.raises(ValueError, match="Decision must contain at least one DecisionOption"):
        Decision(id="dec_empty", prompt="No options", options=())


def test_duplicate_option_ids():
    opt1 = DecisionOption(id="ACCEPT", label="Accept 1")
    opt2 = DecisionOption(id="ACCEPT", label="Accept 2")
    with pytest.raises(ValueError, match="Duplicate DecisionOption id found: 'ACCEPT'"):
        Decision(id="dec_dup", prompt="Dup options", options=(opt1, opt2))


def test_invalid_default_option_id():
    opt1 = DecisionOption(id="ACCEPT", label="Accept")
    with pytest.raises(ValueError, match="default_option_id 'MISSING' not found in decision options"):
        Decision(
            id="dec_bad_def",
            prompt="Bad default",
            options=(opt1,),
            default_option_id="MISSING",
        )


def test_malformed_option_weights():
    with pytest.raises(ValueError, match="DecisionOption weight must not be NaN or Infinity"):
        DecisionOption(id="OPT", label="Opt", weight=float("nan"))

    with pytest.raises(ValueError, match="DecisionOption weight must be non-negative"):
        DecisionOption(id="OPT", label="Opt", weight=-1.0)


def test_explicit_resolution_valid():
    opt1 = DecisionOption(id="ACCEPT", label="Accept")
    opt2 = DecisionOption(id="REJECT", label="Reject")
    dec = Decision(id="d1", prompt="Choose", options=(opt1, opt2))
    ctx = EventContext()

    res = resolve_decision(
        decision=dec,
        context=ctx,
        seed="seed123",
        explicit_option_id="REJECT",
        resolution_type=DecisionResolutionType.EXPLICIT,
    )

    assert res.success is True
    assert res.selected_option is not None
    assert res.selected_option.id == "REJECT"
    assert res.resolution_type == DecisionResolutionType.EXPLICIT


def test_explicit_resolution_invalid_option():
    opt1 = DecisionOption(id="ACCEPT", label="Accept")
    dec = Decision(id="d1", prompt="Choose", options=(opt1,))
    ctx = EventContext()

    res = resolve_decision(
        decision=dec,
        context=ctx,
        seed="seed123",
        explicit_option_id="INVALID",
        resolution_type=DecisionResolutionType.EXPLICIT,
    )

    assert res.success is False
    assert res.error_code == DecisionErrorCode.INVALID_OPTION
    assert res.selected_option is None


def test_explicit_resolution_unavailable_option():
    opt1 = DecisionOption(id="ACCEPT", label="Accept", available=False)
    opt2 = DecisionOption(id="REJECT", label="Reject", available=True)
    dec = Decision(id="d1", prompt="Choose", options=(opt1, opt2))
    ctx = EventContext()

    res = resolve_decision(
        decision=dec,
        context=ctx,
        seed="seed123",
        explicit_option_id="ACCEPT",
        resolution_type=DecisionResolutionType.EXPLICIT,
    )

    assert res.success is False
    assert res.error_code == DecisionErrorCode.OPTION_UNAVAILABLE


def test_default_resolution_valid():
    opt1 = DecisionOption(id="ACCEPT", label="Accept")
    opt2 = DecisionOption(id="REJECT", label="Reject")
    dec = Decision(
        id="d1",
        prompt="Choose",
        options=(opt1, opt2),
        default_option_id="REJECT",
    )
    ctx = EventContext()

    res = resolve_decision(
        decision=dec,
        context=ctx,
        seed="seed123",
        resolution_type=DecisionResolutionType.DEFAULT,
    )

    assert res.success is True
    assert res.selected_option is not None
    assert res.selected_option.id == "REJECT"
    assert res.resolution_type == DecisionResolutionType.DEFAULT


def test_default_resolution_missing_default():
    opt1 = DecisionOption(id="ACCEPT", label="Accept")
    dec = Decision(id="d1", prompt="Choose", options=(opt1,))
    ctx = EventContext()

    res = resolve_decision(
        decision=dec,
        context=ctx,
        seed="seed123",
        resolution_type=DecisionResolutionType.DEFAULT,
    )

    assert res.success is False
    assert res.error_code == DecisionErrorCode.INVALID_DEFAULT_OPTION


def test_default_resolution_unavailable_default():
    opt1 = DecisionOption(id="ACCEPT", label="Accept", available=False)
    dec = Decision(
        id="d1",
        prompt="Choose",
        options=(opt1,),
        default_option_id="ACCEPT",
    )
    ctx = EventContext()

    res = resolve_decision(
        decision=dec,
        context=ctx,
        seed="seed123",
        resolution_type=DecisionResolutionType.DEFAULT,
    )

    assert res.success is False
    assert res.error_code == DecisionErrorCode.OPTION_UNAVAILABLE


def test_weighted_resolution_deterministic_selection():
    opt1 = DecisionOption(id="ACCEPT", label="Accept", weight=70.0)
    opt2 = DecisionOption(id="REJECT", label="Reject", weight=30.0)
    dec = Decision(id="d1", prompt="Choose", options=(opt1, opt2))
    ctx = EventContext()

    res1 = resolve_decision(
        decision=dec,
        context=ctx,
        seed="seed_test_1",
        resolution_type=DecisionResolutionType.WEIGHTED,
    )
    res2 = resolve_decision(
        decision=dec,
        context=ctx,
        seed="seed_test_1",
        resolution_type=DecisionResolutionType.WEIGHTED,
    )

    assert res1.success is True
    assert res2.success is True
    assert res1.selected_option.id == res2.selected_option.id


def test_weighted_resolution_single_available_option():
    opt1 = DecisionOption(id="ACCEPT", label="Accept", available=False)
    opt2 = DecisionOption(id="REJECT", label="Reject", available=True)
    dec = Decision(id="d1", prompt="Choose", options=(opt1, opt2))
    ctx = EventContext()

    res = resolve_decision(
        decision=dec,
        context=ctx,
        seed="any_seed",
        resolution_type=DecisionResolutionType.WEIGHTED,
    )

    assert res.success is True
    assert res.selected_option.id == "REJECT"


def test_weighted_resolution_single_available_zero_weight():
    opt1 = DecisionOption(id="ACCEPT", label="Accept", weight=0.0)
    dec = Decision(id="d1", prompt="Choose", options=(opt1,))
    ctx = EventContext()

    res = resolve_decision(
        decision=dec,
        context=ctx,
        seed="any_seed",
        resolution_type=DecisionResolutionType.WEIGHTED,
    )

    assert res.success is False
    assert res.error_code == DecisionErrorCode.NO_SELECTABLE_OPTION


def test_weighted_resolution_zero_weights():
    opt1 = DecisionOption(id="ACCEPT", label="Accept", weight=0.0)
    opt2 = DecisionOption(id="REJECT", label="Reject", weight=10.0)
    dec = Decision(id="d1", prompt="Choose", options=(opt1, opt2))
    ctx = EventContext()

    # Repeat with multiple seeds to verify zero weight is never selected
    for seed in ["s1", "s2", "s3", "s4", "s5"]:
        res = resolve_decision(
            decision=dec,
            context=ctx,
            seed=seed,
            resolution_type=DecisionResolutionType.WEIGHTED,
        )
        assert res.success is True
        assert res.selected_option.id == "REJECT"


def test_weighted_resolution_all_zero_weights():
    opt1 = DecisionOption(id="ACCEPT", label="Accept", weight=0.0)
    opt2 = DecisionOption(id="REJECT", label="Reject", weight=0.0)
    dec = Decision(id="d1", prompt="Choose", options=(opt1, opt2))
    ctx = EventContext()

    res = resolve_decision(
        decision=dec,
        context=ctx,
        seed="seed123",
        resolution_type=DecisionResolutionType.WEIGHTED,
    )

    assert res.success is False
    assert res.error_code == DecisionErrorCode.NO_SELECTABLE_OPTION


def test_weighted_resolution_all_unavailable():
    opt1 = DecisionOption(id="ACCEPT", label="Accept", available=False)
    opt2 = DecisionOption(id="REJECT", label="Reject", available=False)
    dec = Decision(id="d1", prompt="Choose", options=(opt1, opt2))
    ctx = EventContext()

    res = resolve_decision(
        decision=dec,
        context=ctx,
        seed="seed123",
        resolution_type=DecisionResolutionType.WEIGHTED,
    )

    assert res.success is False
    assert res.error_code == DecisionErrorCode.OPTION_UNAVAILABLE


def test_option_ordering_preserved():
    opts = tuple(DecisionOption(id=f"OPT_{i}", label=f"Option {i}") for i in range(10))
    dec = Decision(id="d_order", prompt="Preserve order", options=opts)

    assert tuple(opt.id for opt in dec.options) == tuple(f"OPT_{i}" for i in range(10))


def test_immutability_during_resolution():
    eff = EventEffect(
        id="eff1",
        effect_type=EventEffectType.PLAYER_MORALE_CHANGE,
        target_id="p1",
        target_type="PLAYER",
        delta_or_value=10.0,
    )
    opt1 = DecisionOption(id="ACCEPT", label="Accept", effects=(eff,))
    opt2 = DecisionOption(id="REJECT", label="Reject")
    dec = Decision(id="d1", prompt="Prompt", options=(opt1, opt2))
    ctx = EventContext(player_id="p1")

    res = resolve_decision(
        decision=dec,
        context=ctx,
        seed="seed123",
        explicit_option_id="ACCEPT",
        resolution_type=DecisionResolutionType.EXPLICIT,
    )

    assert res.success is True
    # Verify input decision and option were not mutated
    assert dec.options[0].id == "ACCEPT"
    assert len(dec.options[0].effects) == 1
    assert dec.options[0].effects[0].id == "eff1"


def test_8f_domain_serialization():
    eff = EventEffect(
        id="eff_opt",
        effect_type=EventEffectType.PLAYER_CONFIDENCE_CHANGE,
        target_id="p1",
        target_type="PLAYER",
        delta_or_value=5.0,
    )
    opt1 = DecisionOption(id="ACCEPT", label="Accept", effects=(eff,))
    opt2 = DecisionOption(id="REJECT", label="Reject")
    dec = Decision(id="dec_ser", prompt="Serialize me", options=(opt1, opt2), default_option_id="REJECT")
    ctx = EventContext()

    res = resolve_decision(
        decision=dec,
        context=ctx,
        seed="seed_ser",
        explicit_option_id="ACCEPT",
        resolution_type=DecisionResolutionType.EXPLICIT,
    )

    dec_bytes = to_json_bytes(dec)
    opt_bytes = to_json_bytes(opt1)
    res_bytes = to_json_bytes(res)

    dec_json = json.loads(dec_bytes.decode("utf-8"))
    opt_json = json.loads(opt_bytes.decode("utf-8"))
    res_json = json.loads(res_bytes.decode("utf-8"))

    assert dec_json["id"] == "dec_ser"
    assert dec_json["default_option_id"] == "REJECT"
    assert len(dec_json["options"]) == 2

    assert opt_json["id"] == "ACCEPT"
    assert opt_json["effects"][0]["id"] == "eff_opt"

    assert res_json["decision_id"] == "dec_ser"
    assert res_json["selected_option"]["id"] == "ACCEPT"
    assert res_json["success"] is True
