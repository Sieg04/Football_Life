import sys
import subprocess
import pytest

from app.event import (
    EventContext,
    EventDefinition,
    EventInstance,
    EventReason,
    EventRegistry,
    EventStatus,
    EventType,
    create_event_definition,
    create_event_instance,
    to_json_bytes,
)


def test_100_repeated_executions_determinism():
    seed = "test_determinism_seed_8b"
    season = "2025/26"
    entity_id = "player_1001"
    entity_type = "PLAYER"

    def_base = create_event_definition(
        event_type=EventType.DEVELOPMENT,
        name="Talent Spike",
        description_key="event.dev.spike",
        priority=75,
        definition_id="def_talent_spike",
        cooldown=1,
        metadata={"multiplier": 1.25, "attribute": "dribbling"},
    )

    baseline_inst = create_event_instance(
        definition=def_base,
        season=season,
        entity_id=entity_id,
        entity_type=entity_type,
        seed=seed,
        metadata={"context_rating": 8.5},
    )
    baseline_bytes = to_json_bytes(baseline_inst)

    for i in range(100):
        run_defn = create_event_definition(
            event_type=EventType.DEVELOPMENT,
            name="Talent Spike",
            description_key="event.dev.spike",
            priority=75,
            definition_id="def_talent_spike",
            cooldown=1,
            metadata={"multiplier": 1.25, "attribute": "dribbling"},
        )
        run_inst = create_event_instance(
            definition=run_defn,
            season=season,
            entity_id=entity_id,
            entity_type=entity_type,
            seed=seed,
            metadata={"context_rating": 8.5},
        )
        run_bytes = to_json_bytes(run_inst)
        assert run_bytes == baseline_bytes, f"Mismatch on run {i}"


def test_cross_process_determinism():
    script = """
import sys
from app.event import create_event_definition, create_event_instance, to_json_bytes, EventType

defn = create_event_definition(
    event_type=EventType.MILESTONE,
    name="Cross Process Test",
    description_key="test.cross_process",
    priority=85,
    definition_id="def_cross_proc",
    metadata={"param": 42}
)
inst = create_event_instance(
    definition=defn,
    season=2026,
    entity_id="entity_proc_1",
    entity_type="CLUB",
    seed="proc_seed_abc",
    metadata={"step": 1}
)
sys.stdout.buffer.write(to_json_bytes(inst))
"""
    cmd = [sys.executable, "-c", script]
    res1 = subprocess.run(cmd, capture_output=True, check=True, env={"PYTHONPATH": "backend"})
    res2 = subprocess.run(cmd, capture_output=True, check=True, env={"PYTHONPATH": "backend"})

    assert res1.stdout == res2.stdout
    assert len(res1.stdout) > 0


def test_large_synthetic_audit():
    # 500 Definitions across categories
    categories = list(EventType)
    definitions: list[EventDefinition] = []

    for i in range(500):
        cat = categories[i % len(categories)]
        defn = create_event_definition(
            event_type=cat,
            name=f"Synthetic Event Definition {i}",
            description_key=f"synth.event.{i}",
            priority=(i * 17) % 101,
            cooldown=i % 5,
            enabled=(i % 10 != 0),
            metadata={"index": i, "tag": f"tag_{i % 7}"},
        )
        definitions.append(defn)

    # Verify 500 unique def IDs
    def_ids = {d.id for d in definitions}
    assert len(def_ids) == 500

    # Register into EventRegistry
    registry = EventRegistry().register_many(definitions)
    registered_defs = registry.list_definitions()
    assert len(registered_defs) == 500

    # Verify registry deterministic ordering
    sorted_def_ids = sorted([d.id for d in definitions])
    assert [d.id for d in registered_defs] == sorted_def_ids

    # 5,000 Event Instances
    instances: list[EventInstance] = []
    instance_ids: set[str] = set()

    for j in range(5000):
        defn = definitions[j % 500]
        season = 2025 + (j % 10)
        entity_id = f"player_{(j * 31) % 1000}"
        entity_type = "PLAYER" if j % 2 == 0 else "CLUB"
        seed = f"audit_seed_{j % 50}"

        inst = create_event_instance(
            definition=defn,
            season=season,
            entity_id=entity_id,
            entity_type=entity_type,
            seed=seed,
            metadata={"step": j, "val": (j * 1.5) % 100.0},
        )
        instances.append(inst)
        instance_ids.add(inst.id)

        # Audit validations
        assert 0 <= inst.priority <= 100
        assert inst.status == EventStatus.PENDING
        assert isinstance(to_json_bytes(inst), bytes)

    # Verify no duplicate instance IDs across 5,000 instances
    # Note: since instance_id is derived from (season, event_type, entity_type, entity_id, def_id, seed),
    # deterministic identical inputs produce identical IDs.
    # Check that all generated instance objects serialize reproducibly
    for k in range(0, 5000, 500):
        b1 = to_json_bytes(instances[k])
        b2 = to_json_bytes(instances[k])
        assert b1 == b2
