import os
import re
import pytest
from app.event import build_narrative_story, build_story_script, CareerRecord, CareerEvent, EventType, EventCategory, EventSignificance


def test_audit_no_forbidden_nondeterminism_or_unsafe_code():
    forbidden_terms = [
        r"\beval\(",
        r"\bexec\(",
        r"\bcompile\(",
        r"\brandom\.",
        r"\bhash\(",
        r"\buuid\.uuid4\b",
        r"\bdatetime\.now\b",
        r"\btime\.time\b",
    ]

    target_files = [
        "backend/app/event/script_domain.py",
        "backend/app/event/script_engine.py",
    ]

    for filepath in target_files:
        if not os.path.exists(filepath):
            continue
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
            for pattern in forbidden_terms:
                matches = re.findall(pattern, content)
                assert len(matches) == 0, f"Forbidden non-deterministic/unsafe code pattern '{pattern}' found in {filepath}"


def test_audit_no_forbidden_imports():
    forbidden_imports = [
        "requests",
        "httpx",
        "urllib",
        "FastAPI",
        "SQLAlchemy",
        "openai",
    ]

    target_files = [
        "backend/app/event/script_domain.py",
        "backend/app/event/script_engine.py",
    ]

    for filepath in target_files:
        if not os.path.exists(filepath):
            continue
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
            for imp in forbidden_imports:
                pattern = rf"\bimport\s+{imp}\b|\bfrom\s+{imp}\b"
                matches = re.findall(pattern, content, re.IGNORECASE)
                assert len(matches) == 0, f"Forbidden import '{imp}' found in {filepath}"


def test_audit_active_career_never_retires():
    ev = CareerEvent(
        event_id="ce_audit", source_event_id="se_audit", player_id="p_audit", season=1, sequence=1,
        event_type=EventType.PLAYER, category=EventCategory.APPEARANCE, significance=EventSignificance.MINOR,
    )
    rec = CareerRecord(player_id="p_audit", events=(ev,))
    story = build_narrative_story(rec)
    script = build_story_script(story, rec)

    script_text = " ".join([
        script.hook.text if script.hook else "",
        " ".join(s.text for s in script.introduction.segments) if script.introduction else "",
        " ".join(seg.text for sec in script.sections for seg in sec.segments),
        script.resolution.segments[0].text if script.resolution else "",
        script.closing.text if script.closing else "",
    ]).lower()

    assert "retired" not in script_text
    assert "career ended" not in script_text
    assert "final season" not in script_text
