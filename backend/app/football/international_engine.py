import hashlib
import json
from pathlib import Path

from app.football.international_domain import InternationalCallUp, InternationalStatus


def _hash_seed(seed_str: str) -> int:
    return int(hashlib.sha256(seed_str.encode("utf-8")).hexdigest(), 16)


def _load_rules(filename: str) -> dict:
    path = Path(__file__).resolve().parents[2] / "data" / "rules" / filename
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return {}


INT_RULES = _load_rules("international.json")


def evaluate_international_call_up(
    call_up_id: str,
    player_id: str,
    country_code: str,
    season_number: int,
    player_ovr: float,
    player_form: float = 1.0,
    position: str = "ST",
    seed: str = "INT_SEED",
) -> InternationalCallUp:
    h = _hash_seed(f"{seed}_{call_up_id}_{player_id}_{country_code}_{season_number}")
    base_thresh = INT_RULES.get("call_up_base_threshold_ovr", 74.0)

    effective_ovr = player_ovr * (0.9 + 0.2 * player_form)

    if effective_ovr < base_thresh - 5:
        status = InternationalStatus.NOT_SELECTED
        caps, goals, assists = 0, 0, 0
    elif effective_ovr < base_thresh:
        status = InternationalStatus.PRESELECTED
        caps, goals, assists = 0, 0, 0
    elif effective_ovr < base_thresh + 5:
        status = InternationalStatus.BENCH
        caps = 1 + (h % 3)
        goals = 1 if (h % 5 == 0 and position in ("ST", "LW", "RW", "AM", "CAM")) else 0
        assists = 1 if (h % 7 == 0 and position in ("LW", "RW", "AM", "CAM", "CM")) else 0
    else:
        status = InternationalStatus.STARTER
        caps = 4 + (h % 5)
        goals = (1 + (h % 3)) if position in ("ST", "LW", "RW") else ((h % 2) if position in ("AM", "CAM", "CM") else 0)
        assists = (1 + (h % 2)) if position in ("LW", "RW", "AM", "CAM", "CM") else 0

    return InternationalCallUp(
        id=call_up_id,
        player_id=player_id,
        country_code=country_code,
        season_number=season_number,
        status=status,
        caps=caps,
        goals=goals,
        assists=assists,
    )
