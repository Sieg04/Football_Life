import math
import pytest

from app.event import (
    EventCondition,
    EventContext,
    EventEffect,
    EventEffectType,
    EventOutcome,
    EventReason,
    EventResolutionStatus,
    EventType,
    create_event_definition,
    create_event_instance,
    resolve_event,
)


def test_large_scale_event_resolution_audit():
    # Evaluate 750 event resolutions across varied players, ages, states, clubs, event types, seeds, outcomes
    categories = list(EventType)
    resolutions = []

    for i in range(750):
        cat = categories[i % len(categories)]
        defn = create_event_definition(
            event_type=cat,
            name=f"Audit Event {i}",
            description_key=f"audit.event.{i}",
            priority=(i * 13) % 101,
            cooldown=i % 4,
            enabled=(i % 15 != 0),  # Occasionally disabled
            metadata={"index": i},
        )

        season = 2025 + (i % 8)
        player_id = f"p_audit_{(i * 17) % 200}"
        club_id = f"club_{(i * 7) % 30}"
        seed = f"audit_8d_seed_{i}"

        context = EventContext(
            season=season,
            player_id=player_id,
            club_id=club_id,
            event_type=cat,
            attributes={"morale": (i * 7.5) % 100.0, "form": 5.0 + (i % 5)},
        )

        inst = create_event_instance(
            definition=defn,
            season=season,
            entity_id=player_id,
            entity_type="PLAYER",
            seed=seed,
            metadata={"step": i},
        )

        # Create outcomes for event
        eff1 = EventEffect(
            id=f"eff_{i}_morale",
            effect_type=EventEffectType.PLAYER_MORALE_CHANGE,
            target_id=player_id,
            target_type="PLAYER",
            delta_or_value=((i % 10) - 5) * 1.5,
        )
        eff2 = EventEffect(
            id=f"eff_{i}_form",
            effect_type=EventEffectType.PLAYER_FORM_CHANGE,
            target_id=player_id,
            target_type="PLAYER",
            delta_or_value=1.0,
        )

        # Condition for high morale outcome
        cond = EventCondition(
            id=f"cond_morale_{i}",
            field_path="attributes.morale",
            operator="GTE",
            expected_value=40.0,
        )

        out_a = EventOutcome(
            id=f"out_{i}_a",
            label="High Morale Outcome",
            weight=40.0,
            effects=(eff1,),
            conditions=(cond,),
        )
        out_b = EventOutcome(
            id=f"out_{i}_b",
            label="General Outcome",
            weight=60.0,
            effects=(eff2,),
        )

        res = resolve_event(
            definition=defn,
            instance=inst,
            context=context,
            outcomes=(out_a, out_b),
        )

        resolutions.append(res)

        # Basic invariant assertions
        assert res.event_id == defn.id
        assert res.event_instance_id == inst.id
        assert isinstance(res.status, EventResolutionStatus)
        assert 0.0 <= res.resolution_score <= 1.0

        if not defn.enabled:
            assert res.status == EventResolutionStatus.BLOCKED

    # Statistics
    resolved_count = sum(1 for r in resolutions if r.status == EventResolutionStatus.RESOLVED)
    blocked_count = sum(1 for r in resolutions if r.status == EventResolutionStatus.BLOCKED)

    assert len(resolutions) == 750
    assert resolved_count > 0
    assert blocked_count > 0
    assert resolved_count + blocked_count == 750


def test_distribution_audit():
    # Verify that sampling multiple seeds for a weighted multi-outcome event produces expected probabilities
    out_a = EventOutcome(
        id="out_a",
        label="Option A (20%)",
        weight=20.0,
    )
    out_b = EventOutcome(
        id="out_b",
        label="Option B (80%)",
        weight=80.0,
    )

    counts = {"out_a": 0, "out_b": 0}
    num_samples = 1000

    defn = create_event_definition(
        event_type=EventType.CAREER,
        name="Distribution Event",
        description_key="evt.dist",
        priority=50,
        definition_id="def_dist",
    )

    for s in range(num_samples):
        seed = f"dist_sampling_seed_{s}"
        context = EventContext(player_id="p_dist", season=2026)
        inst = create_event_instance(
            definition=defn,
            season=2026,
            entity_id="p_dist",
            entity_type="PLAYER",
            seed=seed,
        )

        res = resolve_event(
            definition=defn,
            instance=inst,
            context=context,
            outcomes=(out_a, out_b),
        )

        assert res.status == EventResolutionStatus.RESOLVED
        counts[res.outcome_id] += 1

    pct_a = counts["out_a"] / num_samples
    pct_b = counts["out_b"] / num_samples

    # Configured ratio is 20% / 80%
    # Allow a reasonable tolerance for 1,000 samples (e.g. 15% - 25% for A)
    assert 0.15 <= pct_a <= 0.25, f"Outcome A frequency {pct_a:.3f} outside expected range around 0.20"
    assert 0.75 <= pct_b <= 0.85, f"Outcome B frequency {pct_b:.3f} outside expected range around 0.80"
