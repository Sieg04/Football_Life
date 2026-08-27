import pytest

from app.event import EventRegistry, EventType, create_event_definition


def test_registry_registration_and_lookup():
    reg = EventRegistry()
    def1 = create_event_definition(
        event_type=EventType.PLAYER,
        name="Event 1",
        description_key="desc.1",
        priority=50,
        definition_id="def_1",
    )
    def2 = create_event_definition(
        event_type=EventType.CLUB,
        name="Event 2",
        description_key="desc.2",
        priority=60,
        definition_id="def_2",
    )

    reg1 = reg.register(def1)
    reg2 = reg1.register(def2)

    assert not reg.contains("def_1")
    assert reg1.contains("def_1")
    assert not reg1.contains("def_2")
    assert reg2.contains("def_1")
    assert reg2.contains("def_2")
    assert reg2.get("def_1") == def1
    assert reg2.get("def_2") == def2
    assert reg2.get("non_existent") is None


def test_registry_duplicate_rejection():
    def1 = create_event_definition(
        event_type=EventType.PLAYER,
        name="Event 1",
        description_key="desc.1",
        priority=50,
        definition_id="def_1",
    )
    reg = EventRegistry().register(def1)

    with pytest.raises(ValueError, match="Duplicate EventDefinition ID"):
        reg.register(def1)


def test_registry_list_definitions_deterministic_sorting():
    def_c = create_event_definition(
        event_type=EventType.PLAYER,
        name="Event C",
        description_key="desc.c",
        priority=50,
        definition_id="def_c",
    )
    def_a = create_event_definition(
        event_type=EventType.PLAYER,
        name="Event A",
        description_key="desc.a",
        priority=50,
        definition_id="def_a",
        enabled=False,
    )
    def_b = create_event_definition(
        event_type=EventType.CLUB,
        name="Event B",
        description_key="desc.b",
        priority=50,
        definition_id="def_b",
    )

    reg = EventRegistry().register_many([def_c, def_a, def_b])

    # All definitions sorted by ID
    all_defs = reg.list_definitions()
    assert [d.id for d in all_defs] == ["def_a", "def_b", "def_c"]

    # Filter enabled only
    enabled_defs = reg.list_definitions(enabled_only=True)
    assert [d.id for d in enabled_defs] == ["def_b", "def_c"]

    # Filter by type
    player_defs = reg.list_definitions(event_type=EventType.PLAYER)
    assert [d.id for d in player_defs] == ["def_a", "def_c"]


def test_registry_immutability():
    def1 = create_event_definition(
        event_type=EventType.PLAYER,
        name="Event 1",
        description_key="desc.1",
        priority=50,
        definition_id="def_1",
    )
    reg = EventRegistry()
    reg.register(def1)

    # Initial registry must remain empty
    assert len(reg.list_definitions()) == 0
