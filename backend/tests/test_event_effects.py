from datetime import date
import pytest

from app.event import (
    EffectApplication,
    EffectApplicationError,
    EffectApplicationResult,
    EffectErrorCode,
    EffectOperation,
    EffectTarget,
    EventContext,
    EventEffect,
    EventEffectType,
    EventInstance,
    EventOutcome,
    EventReason,
    EventResolution,
    EventResolutionStatus,
    EventType,
    apply_effect,
    apply_effects,
    apply_event_outcome,
    apply_event_resolution,
    create_event_definition,
    create_event_instance,
)
from app.player.domain import DevelopmentProfile, Player, PlayerAttributes, PlayerState


def create_sample_player(player_id: str = "p100") -> Player:
    attrs = PlayerAttributes(
        acceleration=70.0,
        sprint_speed=72.0,
        finishing=65.0,
        shot_power=68.0,
        long_shots=60.0,
        volleys=55.0,
        penalties=60.0,
        vision=70.0,
        short_passing=75.0,
        long_passing=70.0,
        crossing=65.0,
        curve=60.0,
        agility=72.0,
        balance=70.0,
        ball_control=74.0,
        dribbling=72.0,
        reactions=70.0,
        defensive_awareness=50.0,
        standing_tackle=52.0,
        interceptions=48.0,
        heading=55.0,
        strength=68.0,
        stamina=75.0,
        jumping=65.0,
        aggression=60.0,
        decision_making=70.0,
        composure=68.0,
        creativity=72.0,
        positioning=65.0,
        concentration=68.0,
        work_rate=70.0,
        leadership=60.0,
        diving=10.0,
        handling=10.0,
        kicking=10.0,
        reflexes=10.0,
        speed=10.0,
        goalkeeper_positioning=10.0,
    )
    pstate = PlayerState(
        confidence=60.0,
        morale=60.0,
        form=50.0,
        fitness=100.0,
        fatigue=0.0,
        happiness=60.0,
        reputation=50.0,
    )
    return Player(
        id=player_id,
        name="Alex",
        surname="Hunter",
        nationality="England",
        birth_date=date(2005, 1, 1),
        height=180.0,
        weight=75.0,
        preferred_foot="Right",
        primary_position="CAM",
        secondary_positions=("CM", "LW"),
        attributes=attrs,
        current_ability=70.0,
        potential=85.0,
        development_rate=75.0,
        development_profile=DevelopmentProfile.BALANCED,
        state=pstate,
    )


# --- 1. DOMAIN CONSTRUCTION TESTS ---


def test_effect_operation_enum():
    assert EffectOperation.ADD == "ADD"
    assert EffectOperation.SET == "SET"
    assert EffectOperation.MULTIPLY == "MULTIPLY"


def test_effect_target_validation():
    # Valid construction
    target = EffectTarget(target_id="p1", target_type="PLAYER", attribute="confidence", scope="player")
    assert target.target_id == "p1"
    assert target.attribute == "confidence"

    # Empty target_id
    with pytest.raises(ValueError, match="target_id must be a non-empty string"):
        EffectTarget(target_id="", target_type="PLAYER", attribute="confidence")

    # Empty attribute
    with pytest.raises(ValueError, match="attribute must be a non-empty string"):
        EffectTarget(target_id="p1", target_type="PLAYER", attribute=" ")


def test_effect_application_error_validation():
    # Valid construction
    err = EffectApplicationError(code=EffectErrorCode.UNKNOWN_TARGET, message="Target missing")
    assert err.code == EffectErrorCode.UNKNOWN_TARGET

    # Invalid code
    with pytest.raises(ValueError, match="Invalid EffectErrorCode"):
        EffectApplicationError(code="NONEXISTENT_CODE", message="msg")

    # Empty message
    with pytest.raises(ValueError, match="message must be a non-empty string"):
        EffectApplicationError(code=EffectErrorCode.INVALID_EFFECT, message="")


def test_effect_application_validation():
    app = EffectApplication(
        target="player.confidence",
        operation=EffectOperation.ADD,
        requested_value=5.0,
        previous_value=60.0,
        resulting_value=65.0,
        applied=True,
    )
    assert app.applied is True
    assert app.resulting_value == 65.0

    # NaN requested_value
    with pytest.raises(ValueError, match="NaN or Infinity"):
        EffectApplication(
            target="player.confidence",
            operation=EffectOperation.ADD,
            requested_value=float("nan"),
            previous_value=60.0,
            resulting_value=65.0,
            applied=True,
        )


def test_effect_application_result_validation():
    app = EffectApplication(
        target="player.confidence",
        operation=EffectOperation.ADD,
        requested_value=5.0,
        previous_value=60.0,
        resulting_value=65.0,
        applied=True,
    )
    res = EffectApplicationResult(success=True, applications=(app,), errors=(), resulting_state={})
    assert res.success is True
    assert len(res.applications) == 1


# --- 2. OPERATION TESTS (ADD, SET, MULTIPLY) ---


def test_operation_add():
    player = create_sample_player()
    assert player.state.confidence == 60.0

    eff = EventEffect(
        id="eff_add",
        effect_type=EventEffectType.PLAYER_CONFIDENCE_CHANGE,
        target_id=player.id,
        target_type="PLAYER",
        delta_or_value=5.0,
        operation=EffectOperation.ADD,
    )

    res = apply_effects(player, [eff])
    assert res.success is True
    assert res.resulting_state.state.confidence == 65.0
    assert len(res.applications) == 1
    assert res.applications[0].previous_value == 60.0
    assert res.applications[0].resulting_value == 65.0


def test_operation_set():
    player = create_sample_player()
    assert player.state.morale == 60.0

    eff = EventEffect(
        id="eff_set",
        effect_type=EventEffectType.PLAYER_MORALE_CHANGE,
        target_id=player.id,
        target_type="PLAYER",
        delta_or_value=80.0,
        operation=EffectOperation.SET,
    )

    res = apply_effects(player, [eff])
    assert res.success is True
    assert res.resulting_state.state.morale == 80.0
    assert res.applications[0].previous_value == 60.0
    assert res.applications[0].resulting_value == 80.0


def test_operation_multiply():
    player = create_sample_player()
    assert player.state.form == 50.0

    eff = EventEffect(
        id="eff_mul",
        effect_type=EventEffectType.PLAYER_FORM_CHANGE,
        target_id=player.id,
        target_type="PLAYER",
        delta_or_value=1.10,
        operation=EffectOperation.MULTIPLY,
    )

    res = apply_effects(player, [eff])
    assert res.success is True
    assert res.resulting_state.state.form == 55.0
    assert res.applications[0].previous_value == 50.0
    assert res.applications[0].resulting_value == 55.0


# --- 3. SEQUENTIAL SEMANTICS TESTS ---


def test_sequential_semantics_a_b_c():
    # confidence = 60
    # ADD 5 -> 65
    # SET 20 -> 20
    # ADD 3 -> 23
    player = create_sample_player()
    assert player.state.confidence == 60.0

    eff1 = EventEffect(
        id="eff_1",
        effect_type=EventEffectType.PLAYER_CONFIDENCE_CHANGE,
        target_id=player.id,
        target_type="PLAYER",
        delta_or_value=5.0,
        operation=EffectOperation.ADD,
    )
    eff2 = EventEffect(
        id="eff_2",
        effect_type=EventEffectType.PLAYER_CONFIDENCE_CHANGE,
        target_id=player.id,
        target_type="PLAYER",
        delta_or_value=20.0,
        operation=EffectOperation.SET,
    )
    eff3 = EventEffect(
        id="eff_3",
        effect_type=EventEffectType.PLAYER_CONFIDENCE_CHANGE,
        target_id=player.id,
        target_type="PLAYER",
        delta_or_value=3.0,
        operation=EffectOperation.ADD,
    )

    res = apply_effects(player, [eff1, eff2, eff3])
    assert res.success is True
    assert res.resulting_state.state.confidence == 23.0
    assert len(res.applications) == 3

    # Check intermediate records
    assert res.applications[0].previous_value == 60.0
    assert res.applications[0].resulting_value == 65.0

    assert res.applications[1].previous_value == 65.0
    assert res.applications[1].resulting_value == 20.0

    assert res.applications[2].previous_value == 20.0
    assert res.applications[2].resulting_value == 23.0


# --- 4. BOUNDS TESTS ---


def test_bounds_maximum_clamping():
    player = create_sample_player()
    # Set confidence close to 100
    player_high = apply_effects(
        player,
        [
            EventEffect(
                id="e_init",
                effect_type=EventEffectType.PLAYER_CONFIDENCE_CHANGE,
                target_id=player.id,
                target_type="PLAYER",
                delta_or_value=98.0,
                operation=EffectOperation.SET,
            )
        ],
    ).resulting_state

    assert player_high.state.confidence == 98.0

    # ADD 10 with max_bound = 100
    eff_overflow = EventEffect(
        id="e_over",
        effect_type=EventEffectType.PLAYER_CONFIDENCE_CHANGE,
        target_id=player.id,
        target_type="PLAYER",
        delta_or_value=10.0,
        min_bound=0.0,
        max_bound=100.0,
        operation=EffectOperation.ADD,
    )

    res = apply_effects(player_high, [eff_overflow])
    assert res.success is True
    assert res.resulting_state.state.confidence == 100.0


def test_bounds_minimum_clamping():
    player = create_sample_player()
    eff_underflow = EventEffect(
        id="e_under",
        effect_type=EventEffectType.PLAYER_CONFIDENCE_CHANGE,
        target_id=player.id,
        target_type="PLAYER",
        delta_or_value=-100.0,
        min_bound=0.0,
        max_bound=100.0,
        operation=EffectOperation.ADD,
    )

    res = apply_effects(player, [eff_underflow])
    assert res.success is True
    assert res.resulting_state.state.confidence == 0.0


# --- 5. UNKNOWN TARGET TESTS ---


def test_unknown_target_fails_explicitly():
    player = create_sample_player()

    eff_unknown = EventEffect(
        id="eff_unk",
        effect_type=EventEffectType.PLAYER_ATTRIBUTE_CHANGE,
        target_id=player.id,
        target_type="PLAYER",
        delta_or_value=10.0,
        parameters={"attribute": "nonexistent_stat"},
    )

    res = apply_effects(player, [eff_unknown])
    assert res.success is False
    assert len(res.errors) == 1
    assert res.errors[0].code == EffectErrorCode.UNKNOWN_TARGET
    assert "nonexistent_stat" in res.errors[0].message
    assert res.resulting_state == player  # Unchanged state


# --- 6. TYPE MISMATCH TESTS ---


def test_type_mismatch_fails_explicitly():
    player = create_sample_player()

    eff_bad_type = EventEffect(
        id="eff_bad",
        effect_type=EventEffectType.PLAYER_CONFIDENCE_CHANGE,
        target_id=player.id,
        target_type="PLAYER",
        delta_or_value="high",  # string where number expected
        operation=EffectOperation.ADD,
    )

    res = apply_effects(player, [eff_bad_type])
    assert res.success is False
    assert len(res.errors) == 1
    assert res.errors[0].code == EffectErrorCode.TYPE_MISMATCH
    assert res.resulting_state == player  # Unchanged state


# --- 7. ATOMICITY TESTS ---


def test_atomic_batch_rollback():
    player = create_sample_player()
    initial_confidence = player.state.confidence

    eff_valid_1 = EventEffect(
        id="eff_v1",
        effect_type=EventEffectType.PLAYER_CONFIDENCE_CHANGE,
        target_id=player.id,
        target_type="PLAYER",
        delta_or_value=10.0,
        operation=EffectOperation.ADD,
    )
    eff_valid_2 = EventEffect(
        id="eff_v2",
        effect_type=EventEffectType.PLAYER_MORALE_CHANGE,
        target_id=player.id,
        target_type="PLAYER",
        delta_or_value=15.0,
        operation=EffectOperation.ADD,
    )
    eff_invalid_3 = EventEffect(
        id="eff_inv3",
        effect_type=EventEffectType.PLAYER_ATTRIBUTE_CHANGE,
        target_id=player.id,
        target_type="PLAYER",
        delta_or_value=5.0,
        parameters={"attribute": "invalid_attribute_xyz"},
    )

    res = apply_effects(player, [eff_valid_1, eff_valid_2, eff_invalid_3])

    assert res.success is False
    assert len(res.errors) == 1
    assert res.errors[0].code == EffectErrorCode.UNKNOWN_TARGET
    # Original state preserved entirely
    assert res.resulting_state.state.confidence == initial_confidence
    assert res.resulting_state.state.morale == player.state.morale


# --- 8. IMMUTABILITY TESTS ---


def test_input_state_immutability():
    player = create_sample_player()
    orig_confidence = player.state.confidence
    orig_morale = player.state.morale

    eff = EventEffect(
        id="eff_immut",
        effect_type=EventEffectType.PLAYER_CONFIDENCE_CHANGE,
        target_id=player.id,
        target_type="PLAYER",
        delta_or_value=20.0,
        operation=EffectOperation.ADD,
    )

    res = apply_effects(player, [eff])

    # Caller-owned input object remains completely unchanged
    assert player.state.confidence == orig_confidence
    assert player.state.morale == orig_morale
    # Resulting state has updated value
    assert res.resulting_state.state.confidence == orig_confidence + 20.0


# --- 9. OUTCOME INTEGRATION & NOT TRIGGERED INVARIANT TESTS ---


def test_outcome_resolved_status_applies_effects():
    player = create_sample_player()
    eff = EventEffect(
        id="eff_res",
        effect_type=EventEffectType.PLAYER_CONFIDENCE_CHANGE,
        target_id=player.id,
        target_type="PLAYER",
        delta_or_value=10.0,
    )

    resolution = EventResolution(
        event_id="def_1",
        event_instance_id="inst_1",
        status=EventResolutionStatus.RESOLVED,
        outcome_id="out_success",
        outcome_label="Success",
        effects=(eff,),
        reasons=(),
        resolution_score=0.8,
        seed="seed1",
    )

    res = apply_event_resolution(player, resolution)
    assert res.success is True
    assert res.resulting_state.state.confidence == 70.0
    assert len(res.applications) == 1


def test_not_triggered_invariant_preserves_state():
    player = create_sample_player()
    eff = EventEffect(
        id="eff_blocked",
        effect_type=EventEffectType.PLAYER_CONFIDENCE_CHANGE,
        target_id=player.id,
        target_type="PLAYER",
        delta_or_value=10.0,
    )

    for status in (
        EventResolutionStatus.BLOCKED,
        EventResolutionStatus.CANCELLED,
        EventResolutionStatus.FAILED,
    ):
        resolution = EventResolution(
            event_id="def_1",
            event_instance_id="inst_1",
            status=status,
            outcome_id=None,
            outcome_label=None,
            effects=(eff,),
            reasons=(),
            resolution_score=0.0,
            seed="seed1",
        )

        res = apply_event_resolution(player, resolution)
        assert res.success is True
        assert len(res.applications) == 0
        assert res.resulting_state == player
