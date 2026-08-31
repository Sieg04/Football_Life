import hashlib
import json
from pathlib import Path

from app.football.injury_domain import Injury, InjuryCategory


def _hash_seed(seed_str: str) -> int:
    return int(hashlib.sha256(seed_str.encode("utf-8")).hexdigest(), 16)


def _load_rules(filename: str) -> dict:
    path = Path(__file__).resolve().parents[2] / "data" / "rules" / filename
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return {}


INJURY_RULES = _load_rules("injuries.json")

INJURY_SPECS = {
    InjuryCategory.MINOR: {
        "names": ["Ankle Sprain", "Muscle Strain", "Knock"],
        "weeks": (1, 2),
        "matches": (1, 3),
    },
    InjuryCategory.MODERATE: {
        "names": ["Hamstring Pull", "Groin Strain", "Calf Tear"],
        "weeks": (3, 6),
        "matches": (3, 7),
    },
    InjuryCategory.MAJOR: {
        "names": ["Knee Ligament Sprain", "Fractured Bone"],
        "weeks": (7, 14),
        "matches": (8, 16),
    },
    InjuryCategory.SEASON_ENDING: {
        "names": ["ACL Tear", "Achilles Rupture"],
        "weeks": (24, 36),
        "matches": (20, 35),
    },
}


def create_injury(
    injury_id: str,
    player_id: str,
    category: InjuryCategory | str,
    start_season: int,
    start_matchday: int,
    seed: str = "INJURY_SEED",
) -> Injury:
    if isinstance(category, str):
        category = InjuryCategory(category)

    spec = INJURY_SPECS.get(category, INJURY_SPECS[InjuryCategory.MINOR])
    h = _hash_seed(f"{seed}_{injury_id}_{player_id}_{category}")

    names = spec["names"]
    name = names[h % len(names)]

    w_min, w_max = spec["weeks"]
    duration_weeks = w_min + ((h // 10) % (w_max - w_min + 1))

    m_min, m_max = spec["matches"]
    matches_missed = m_min + ((h // 100) % (m_max - m_min + 1))

    return Injury(
        id=injury_id,
        player_id=player_id,
        category=category,
        name=name,
        duration_weeks=duration_weeks,
        matches_missed=matches_missed,
        start_season=start_season,
        start_matchday=start_matchday,
    )
