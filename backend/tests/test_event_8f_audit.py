import json
import subprocess
import sys
import pytest
from datetime import date

from app.event import (
    Decision,
    DecisionOption,
    DecisionResolutionType,
    DecisionResult,
    EffectOperation,
    EventContext,
    EventEffect,
    EventEffectType,
    apply_decision_result,
    resolve_decision,
    to_json_bytes,
)
from app.player.domain import DevelopmentProfile, Player, PlayerAttributes, PlayerState


def create_audit_player(pid: str = "p_8f_audit") -> Player:
    attrs = PlayerAttributes(
        acceleration=70.0,
        sprint_speed=70.0,
        finishing=70.0,
        shot_power=70.0,
        long_shots=70.0,
        volleys=70.0,
        penalties=70.0,
        vision=70.0,
        short_passing=70.0,
        long_passing=70.0,
        crossing=70.0,
        curve=70.0,
        agility=70.0,
        balance=70.0,
        ball_control=70.0,
        dribbling=70.0,
        reactions=70.0,
        defensive_awareness=70.0,
        standing_tackle=70.0,
        interceptions=70.0,
        heading=70.0,
        strength=70.0,
        stamina=70.0,
        jumping=70.0,
        aggression=70.0,
        decision_making=70.0,
        composure=70.0,
        creativity=70.0,
        positioning=70.0,
        concentration=70.0,
        work_rate=70.0,
        leadership=70.0,
        diving=10.0,
        handling=10.0,
        kicking=10.0,
        reflexes=10.0,
        speed=10.0,
        goalkeeper_positioning=10.0,
    )
    pstate = PlayerState(
        confidence=50.0,
        morale=50.0,
        form=50.0,
        fitness=100.0,
        fatigue=0.0,
        happiness=50.0,
        reputation=50.0,
    )
    return Player(
        id=pid,
        name="Audit8F",
        surname="Player",
        nationality="England",
        birth_date=date(2005, 1, 1),
        height=180.0,
        weight=75.0,
        preferred_foot="Right",
        primary_position="CM",
        secondary_positions=(),
        attributes=attrs,
        current_ability=70.0,
        potential=85.0,
        development_rate=75.0,
        development_profile=DevelopmentProfile.BALANCED,
        state=pstate,
    )


def test_8f_to_8e_pipeline_integration():
    player = create_audit_player("p_pipe")

    eff_accept = EventEffect(
        id="eff_accept_morale",
        effect_type=EventEffectType.PLAYER_MORALE_CHANGE,
        target_id=player.id,
        target_type="PLAYER",
        delta_or_value=15.0,
        operation=EffectOperation.ADD,
    )
    eff_reject = EventEffect(
        id="eff_reject_morale",
        effect_type=EventEffectType.PLAYER_MORALE_CHANGE,
        target_id=player.id,
        target_type="PLAYER",
        delta_or_value=-10.0,
        operation=EffectOperation.ADD,
    )

    opt_accept = DecisionOption(id="ACCEPT", label="Accept transfer", effects=(eff_accept,))
    opt_reject = DecisionOption(id="REJECT", label="Reject transfer", effects=(eff_reject,))

    decision = Decision(
        id="dec_transfer_offer",
        prompt="Transfer offered from top club",
        options=(opt_accept, opt_reject),
    )

    context = EventContext(player_id=player.id)

    # Step 8F: Select choice (EXPLICIT)
    res_8f = resolve_decision(
        decision=decision,
        context=context,
        seed="seed_pipe_1",
        explicit_option_id="ACCEPT",
        resolution_type=DecisionResolutionType.EXPLICIT,
    )

    assert res_8f.success is True
    assert res_8f.selected_option.id == "ACCEPT"

    # Verify 8F did NOT mutate player state
    assert player.state.morale == 50.0

    # Step 8E: Apply selected option effects
    res_8e = apply_decision_result(player, res_8f, context)

    assert res_8e.success is True
    assert res_8e.resulting_state.state.morale == 65.0
    # Original player remains untouched (immutability)
    assert player.state.morale == 50.0


def test_100x_repeated_weighted_decision_determinism():
    opt1 = DecisionOption(id="ACCEPT", label="Accept", weight=60.0)
    opt2 = DecisionOption(id="REJECT", label="Reject", weight=30.0)
    opt3 = DecisionOption(id="WAIT", label="Wait", weight=10.0)

    decision = Decision(id="dec_det_100x", prompt="Deterministic choice", options=(opt1, opt2, opt3))
    context = EventContext()
    seed = "seed_det_100x_unique"

    baseline_res = resolve_decision(
        decision=decision,
        context=context,
        seed=seed,
        resolution_type=DecisionResolutionType.WEIGHTED,
    )
    baseline_bytes = to_json_bytes(baseline_res)

    for i in range(100):
        run_res = resolve_decision(
            decision=decision,
            context=context,
            seed=seed,
            resolution_type=DecisionResolutionType.WEIGHTED,
        )
        assert to_json_bytes(run_res) == baseline_bytes, f"Determinism mismatch on run {i}"


def test_cross_process_weighted_decision_determinism():
    script = """
import sys
from app.event import (
    Decision,
    DecisionOption,
    DecisionResolutionType,
    EventContext,
    resolve_decision,
    to_json_bytes,
)

opt1 = DecisionOption(id="ACCEPT", label="Accept", weight=60.0)
opt2 = DecisionOption(id="REJECT", label="Reject", weight=30.0)
opt3 = DecisionOption(id="WAIT", label="Wait", weight=10.0)

decision = Decision(id="dec_cross_proc", prompt="Cross proc choice", options=(opt1, opt2, opt3))
context = EventContext()

res = resolve_decision(
    decision=decision,
    context=context,
    seed="seed_cross_proc_999",
    resolution_type=DecisionResolutionType.WEIGHTED,
)

sys.stdout.buffer.write(to_json_bytes(res))
"""
    cmd = [sys.executable, "-c", script]
    res1 = subprocess.run(cmd, capture_output=True, check=True, env={"PYTHONPATH": "backend"})
    res2 = subprocess.run(cmd, capture_output=True, check=True, env={"PYTHONPATH": "backend"})

    assert res1.stdout == res2.stdout
    assert len(res1.stdout) > 0
