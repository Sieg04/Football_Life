import pytest
from types import MappingProxyType

from app.event import (
    EventContext,
    EventDefinition,
    EventInstance,
    EventReason,
    EventStatus,
    EventType,
    create_event_definition,
    create_event_instance,
    to_json_bytes,
)


def test_event_type_enum():
    expected = {"PLAYER", "CAREER", "CLUB", "COMPETITION", "TRANSFER", "DEVELOPMENT", "MILESTONE", "CONTEXTUAL"}
    actual = {t.value for t in EventType}
    assert actual == expected


def test_event_status_enum():
    expected = {"PENDING", "TRIGGERED", "RESOLVED", "CANCELLED", "EXPIRED"}
    actual = {s.value for s in EventStatus}
    assert actual == expected


def test_event_reason_valid():
    reason = EventReason(code="LOW_PLAYING_TIME", value=15, weight=1.5)
    assert reason.code == "LOW_PLAYING_TIME"
    assert reason.value == 15
    assert reason.weight == 1.5

    # Test frozen immutability
    with pytest.raises(AttributeError):
        reason.weight = 2.0  # type: ignore


def test_event_reason_validation():
    with pytest.raises(ValueError, match="code must be a non-empty string"):
        EventReason(code="")

    with pytest.raises(ValueError, match="weight must be non-negative"):
        EventReason(code="TEST", weight=-0.5)

    with pytest.raises(ValueError, match="weight must not be NaN or Infinity"):
        EventReason(code="TEST", weight=float("nan"))

    with pytest.raises(ValueError, match="value must be a primitive type"):
        EventReason(code="TEST", value=object())  # type: ignore


def test_event_definition_valid():
    defn = EventDefinition(
        id="def_001",
        event_type=EventType.CAREER,
        name="Breakthrough Season",
        description_key="event.career.breakthrough",
        priority=80,
        cooldown=2,
        enabled=True,
        metadata=MappingProxyType({"category": "major"}),
    )
    assert defn.id == "def_001"
    assert defn.event_type == EventType.CAREER
    assert defn.priority == 80
    assert defn.cooldown == 2
    assert defn.metadata["category"] == "major"


def test_event_definition_validation():
    with pytest.raises(ValueError, match="id must be a non-empty string"):
        EventDefinition(
            id="",
            event_type=EventType.PLAYER,
            name="Test",
            description_key="key",
            priority=50,
        )

    with pytest.raises(ValueError, match="Invalid event_type"):
        EventDefinition(
            id="def_1",
            event_type="INVALID_TYPE",  # type: ignore
            name="Test",
            description_key="key",
            priority=50,
        )

    with pytest.raises(ValueError, match="priority must be between 0 and 100"):
        EventDefinition(
            id="def_1",
            event_type=EventType.PLAYER,
            name="Test",
            description_key="key",
            priority=101,
        )

    with pytest.raises(ValueError, match="priority must be between 0 and 100"):
        EventDefinition(
            id="def_1",
            event_type=EventType.PLAYER,
            name="Test",
            description_key="key",
            priority=-1,
        )

    with pytest.raises(ValueError, match="cooldown must be non-negative"):
        EventDefinition(
            id="def_1",
            event_type=EventType.PLAYER,
            name="Test",
            description_key="key",
            priority=50,
            cooldown=-1,
        )

    with pytest.raises(ValueError, match="Float values must not be NaN or Infinity"):
        EventDefinition(
            id="def_1",
            event_type=EventType.PLAYER,
            name="Test",
            description_key="key",
            priority=50,
            metadata={"bad": float("nan")},
        )


def test_event_definition_metadata_immutability():
    meta = {"key1": "val1", "nested": {"key2": 100}}
    defn = EventDefinition(
        id="def_meta",
        event_type=EventType.PLAYER,
        name="Meta Test",
        description_key="meta.key",
        priority=50,
        metadata=meta,
    )
    meta["key1"] = "mutated"
    meta["nested"]["key2"] = 999
    assert defn.metadata["key1"] == "val1"
    assert defn.metadata["nested"]["key2"] == 100

    with pytest.raises(TypeError):
        defn.metadata["key1"] = "new_val"  # type: ignore


def test_event_context_valid():
    ctx = EventContext(
        season=2025,
        player_id="p_123",
        club_id="c_456",
        event_type=EventType.TRANSFER,
        attributes={"form": 7.5, "morale": 90},
    )
    assert ctx.season == 2025
    assert ctx.player_id == "p_123"
    assert ctx.club_id == "c_456"
    assert ctx.event_type == EventType.TRANSFER
    assert ctx.attributes["form"] == 7.5


def test_event_context_validation():
    with pytest.raises(ValueError, match="Season year must be positive"):
        EventContext(season=-1)

    with pytest.raises(ValueError, match="player_id must be a non-empty string"):
        EventContext(player_id="   ")

    with pytest.raises(ValueError, match="Unsupported non-primitive value"):
        EventContext(attributes={"bad_obj": object()})


def test_event_instance_valid():
    inst = EventInstance(
        id="inst_001",
        definition_id="def_001",
        event_type=EventType.DEVELOPMENT,
        season="2025/26",
        entity_id="p_100",
        entity_type="PLAYER",
        seed="seed_abc_123",
        priority=75,
        status=EventStatus.PENDING,
        metadata=MappingProxyType({"detail": "boost"}),
    )
    assert inst.id == "inst_001"
    assert inst.definition_id == "def_001"
    assert inst.event_type == EventType.DEVELOPMENT
    assert inst.season == "2025/26"
    assert inst.entity_id == "p_100"
    assert inst.entity_type == "PLAYER"
    assert inst.seed == "seed_abc_123"
    assert inst.priority == 75
    assert inst.status == EventStatus.PENDING


def test_event_instance_validation():
    with pytest.raises(ValueError, match="EventInstance id must be a non-empty string"):
        EventInstance(
            id="",
            definition_id="def_1",
            event_type=EventType.PLAYER,
            season=2025,
            entity_id="p1",
            entity_type="PLAYER",
            seed="seed",
            priority=50,
        )

    with pytest.raises(ValueError, match="seed must be a non-empty string"):
        EventInstance(
            id="inst_1",
            definition_id="def_1",
            event_type=EventType.PLAYER,
            season=2025,
            entity_id="p1",
            entity_type="PLAYER",
            seed="  ",
            priority=50,
        )


def test_factories_determinism():
    defn1 = create_event_definition(
        event_type=EventType.MILESTONE,
        name="100 Goals Scored",
        description_key="milestone.goals.100",
        priority=90,
    )
    defn2 = create_event_definition(
        event_type=EventType.MILESTONE,
        name="100 Goals Scored",
        description_key="milestone.goals.100",
        priority=90,
    )
    assert defn1.id == defn2.id
    assert defn1.id.startswith("evt_def_")

    inst1 = create_event_instance(
        definition=defn1,
        season=2025,
        entity_id="player_99",
        entity_type="PLAYER",
        seed="master_seed_2025",
    )
    inst2 = create_event_instance(
        definition=defn1,
        season=2025,
        entity_id="player_99",
        entity_type="PLAYER",
        seed="master_seed_2025",
    )
    assert inst1.id == inst2.id
    assert inst1.id.startswith("evt_inst_")


def test_serialization():
    defn = create_event_definition(
        event_type=EventType.CLUB,
        name="Stadium Upgrade",
        description_key="club.stadium.upgrade",
        priority=40,
        metadata={"cost": 5000000, "capacity": 45000},
    )
    json_bytes1 = to_json_bytes(defn)
    json_bytes2 = to_json_bytes(defn)
    assert json_bytes1 == json_bytes2
    assert b"Stadium Upgrade" in json_bytes1
