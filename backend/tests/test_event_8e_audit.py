import json
import subprocess
import sys
import pytest
from datetime import date

from app.event import (
    EffectApplicationResult,
    EffectErrorCode,
    EffectOperation,
    EventContext,
    EventEffect,
    EventEffectType,
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
    resolve_event,
    to_json_bytes,
)
from app.player.domain import DevelopmentProfile, Player, PlayerAttributes, PlayerState


def create_audit_player(pid: str = "p_audit") -> Player:
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
        name="Audit",
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


def test_100x_repeated_effects_determinism():
    player = create_audit_player("p_det_100x")
    eff1 = EventEffect(
        id="eff_a",
        effect_type=EventEffectType.PLAYER_MORALE_CHANGE,
        target_id=player.id,
        target_type="PLAYER",
        delta_or_value=12.5,
        operation=EffectOperation.ADD,
    )
    eff2 = EventEffect(
        id="eff_b",
        effect_type=EventEffectType.PLAYER_CONFIDENCE_CHANGE,
        target_id=player.id,
        target_type="PLAYER",
        delta_or_value=0.90,
        operation=EffectOperation.MULTIPLY,
    )

    baseline_res = apply_effects(player, [eff1, eff2])
    baseline_bytes = to_json_bytes(baseline_res)

    for i in range(100):
        run_res = apply_effects(player, [eff1, eff2])
        assert to_json_bytes(run_res) == baseline_bytes, f"Determinism mismatch on run {i}"


def test_cross_process_effects_determinism():
    script = """
import sys
from datetime import date
from app.event import (
    EventEffect,
    EventEffectType,
    EffectOperation,
    apply_effects,
    to_json_bytes,
)
from app.player.domain import Player, PlayerAttributes, PlayerState, DevelopmentProfile

attrs = PlayerAttributes(
    acceleration=70.0, sprint_speed=70.0, finishing=70.0, shot_power=70.0, long_shots=70.0,
    volleys=70.0, penalties=70.0, vision=70.0, short_passing=70.0, long_passing=70.0,
    crossing=70.0, curve=70.0, agility=70.0, balance=70.0, ball_control=70.0, dribbling=70.0,
    reactions=70.0, defensive_awareness=70.0, standing_tackle=70.0, interceptions=70.0, heading=70.0,
    strength=70.0, stamina=70.0, jumping=70.0, aggression=70.0, decision_making=70.0, composure=70.0,
    creativity=70.0, positioning=70.0, concentration=70.0, work_rate=70.0, leadership=70.0,
    diving=10.0, handling=10.0, kicking=10.0, reflexes=10.0, speed=10.0, goalkeeper_positioning=10.0
)
pstate = PlayerState(confidence=50.0, morale=50.0, form=50.0, fitness=100.0, fatigue=0.0, happiness=50.0, reputation=50.0)
player = Player(
    id="p_proc", name="P", surname="Proc", nationality="E", birth_date=date(2005, 1, 1),
    height=180.0, weight=75.0, preferred_foot="Right", primary_position="CM", secondary_positions=(),
    attributes=attrs, current_ability=70.0, potential=85.0, development_rate=75.0,
    development_profile=DevelopmentProfile.BALANCED, state=pstate
)

eff = EventEffect(
    id="eff_proc",
    effect_type=EventEffectType.PLAYER_MORALE_CHANGE,
    target_id="p_proc",
    target_type="PLAYER",
    delta_or_value=15.0,
    operation=EffectOperation.ADD,
)

res = apply_effects(player, [eff])
sys.stdout.buffer.write(to_json_bytes(res))
"""
    cmd = [sys.executable, "-c", script]
    res1 = subprocess.run(cmd, capture_output=True, check=True, env={"PYTHONPATH": "backend"})
    res2 = subprocess.run(cmd, capture_output=True, check=True, env={"PYTHONPATH": "backend"})

    assert res1.stdout == res2.stdout
    assert len(res1.stdout) > 0


def test_large_scale_8e_application_audit():
    # Execute 500 varied effect applications across multi-effect sequences
    players = [create_audit_player(f"p_{i}") for i in range(10)]

    for i in range(500):
        player = players[i % len(players)]
        eff_type = [
            EventEffectType.PLAYER_MORALE_CHANGE,
            EventEffectType.PLAYER_CONFIDENCE_CHANGE,
            EventEffectType.PLAYER_FORM_CHANGE,
            EventEffectType.PLAYER_FITNESS_CHANGE,
        ][i % 4]

        op = [EffectOperation.ADD, EffectOperation.SET, EffectOperation.MULTIPLY][i % 3]
        val = 5.0 if op == EffectOperation.ADD else (75.0 if op == EffectOperation.SET else 1.05)

        eff = EventEffect(
            id=f"eff_audit_{i}",
            effect_type=eff_type,
            target_id=player.id,
            target_type="PLAYER",
            delta_or_value=val,
            min_bound=0.0,
            max_bound=100.0,
            operation=op,
        )

        res = apply_effects(player, [eff])
        assert res.success is True
        assert len(res.applications) == 1
        assert res.applications[0].applied is True
        assert 0.0 <= res.applications[0].resulting_value <= 100.0


def test_dict_based_simulation_state_support():
    # 8E must also support dictionary-based simulation state
    state = {
        "player": {
            "confidence": 60.0,
            "morale": 50.0,
        },
        "global_morale": 70.0,
    }

    eff1 = EventEffect(
        id="eff_dict_1",
        effect_type=EventEffectType.PLAYER_CONFIDENCE_CHANGE,
        target_id="p1",
        target_type="PLAYER",
        delta_or_value=10.0,
        operation=EffectOperation.ADD,
        parameters={"attribute": "confidence"},
    )
    eff2 = EventEffect(
        id="eff_dict_2",
        effect_type=EventEffectType.CLUB_MORALE_CHANGE,
        target_id="c1",
        target_type="CLUB",
        delta_or_value=5.0,
        operation=EffectOperation.ADD,
        parameters={"attribute": "global_morale"},
    )

    res = apply_effects(state, [eff1, eff2])
    assert res.success is True
    assert res.resulting_state["player"]["confidence"] == 70.0
    assert res.resulting_state["global_morale"] == 75.0
    # Original dict unchanged
    assert state["player"]["confidence"] == 60.0
    assert state["global_morale"] == 70.0
