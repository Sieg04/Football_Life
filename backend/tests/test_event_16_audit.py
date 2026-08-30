import hashlib
import json
import os
import re
import subprocess
import sys
from pathlib import Path
import pytest

from app.event.domain import to_json_bytes
from app.event.presentation_engine import build_career_presentation
from app.event.replay_engine import build_career_replay, build_content_story


def test_determinism_100x_builds() -> None:
    pres = build_career_presentation()

    first_bytes = None
    for _ in range(100):
        res = build_career_replay(
            presentation=pres,
            career_id="car_audit_100x",
            player_id="P_AUDIT",
            player_name="Audit Player",
        )
        assert res.success is True
        assert res.replay is not None

        json_bytes = to_json_bytes(res.replay)
        if first_bytes is None:
            first_bytes = json_bytes
        else:
            assert json_bytes == first_bytes, "Replay build output must be byte-identical across 100 runs"


def test_cross_process_determinism() -> None:
    code = """
import hashlib, json, sys
from app.event.presentation_engine import build_career_presentation
from app.event.replay_engine import build_career_replay
from app.event.domain import to_json_bytes

pres = build_career_presentation()
replay = build_career_replay(presentation=pres, career_id="car_cross_proc", player_id="P_CROSS", player_name="Cross Proc").replay
print(hashlib.sha256(to_json_bytes(replay)).hexdigest())
"""
    env = os.environ.copy()
    env["PYTHONPATH"] = "backend"

    cmd = [sys.executable, "-c", code]
    out1 = subprocess.check_output(cmd, text=True, env=env).strip()
    out2 = subprocess.check_output(cmd, text=True, env=env).strip()

    assert out1 == out2
    assert len(out1) == 64


def test_immutability_input_snapshots_unmodified() -> None:
    pres = build_career_presentation()
    before_bytes = to_json_bytes(pres)

    _ = build_career_replay(
        presentation=pres,
        career_id="car_immut",
    )

    after_bytes = to_json_bytes(pres)
    assert before_bytes == after_bytes, "CareerPresentation must not be mutated during replay building"


def test_security_audit_phase16_files() -> None:
    forbidden = ["eval(", "exec(", "compile(", "new Function", "uuid4", "random.", "datetime.now", "time.time("]
    phase16_files = [
        Path("backend/app/event/replay_domain.py"),
        Path("backend/app/event/replay_engine.py"),
        Path("backend/app/api/replay.py"),
    ]

    for filepath in phase16_files:
        if not filepath.exists():
            continue
        content = filepath.read_text(encoding="utf-8")
        for term in forbidden:
            assert term not in content, f"Forbidden term '{term}' found in {filepath}"
