import os
import subprocess
import sys
import pytest

from app.event.domain import to_json_bytes
from app.event.presentation_engine import build_career_presentation
from tests.test_event_phase12 import (
    create_sample_career_record,
    create_sample_narrative_story,
    create_sample_script,
)


def test_presentation_100x_determinism():
    rec = create_sample_career_record()
    story = create_sample_narrative_story()
    script = create_sample_script()

    base_pres = build_career_presentation(career_record=rec, story=story, script=script)
    base_bytes = to_json_bytes(base_pres)

    for _ in range(100):
        iteration_pres = build_career_presentation(career_record=rec, story=story, script=script)
        iteration_bytes = to_json_bytes(iteration_pres)
        assert iteration_bytes == base_bytes


def test_presentation_cross_process_determinism():
    code = """
from app.event.presentation_engine import build_career_presentation
from app.event.domain import to_json_bytes
from tests.test_event_phase12 import (
    create_sample_career_record,
    create_sample_narrative_story,
    create_sample_script,
)
rec = create_sample_career_record()
story = create_sample_narrative_story()
script = create_sample_script()
pres = build_career_presentation(career_record=rec, story=story, script=script)
print(to_json_bytes(pres).decode("utf-8"))
"""
    cmd = [sys.executable, "-c", code]
    env = dict(os.environ)
    env["PYTHONPATH"] = "backend"

    res1 = subprocess.check_output(cmd, env=env, text=True).strip()
    res2 = subprocess.check_output(cmd, env=env, text=True).strip()

    assert res1 == res2


def test_presentation_security_audit():
    import app.event.presentation_domain as p_dom
    import app.event.presentation_engine as p_eng

    forbidden_terms = [
        "random.random",
        "uuid.uuid4",
        "datetime.now",
        "datetime.utcnow",
        "time.time",
        "eval(",
        "exec(",
        "compile(",
    ]

    for mod in [p_dom, p_eng]:
        src = os.path.abspath(mod.__file__)
        with open(src, "r", encoding="utf-8") as f:
            content = f.read()

        for term in forbidden_terms:
            assert term not in content, f"Forbidden term '{term}' found in {src}"
