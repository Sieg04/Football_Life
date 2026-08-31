from dataclasses import dataclass
import hashlib
import json
from pathlib import Path

from app.match.domain import PlayerMatchPerformance


def _hash_seed(seed_str: str) -> int:
    return int(hashlib.sha256(seed_str.encode("utf-8")).hexdigest(), 16)


def _load_rules(filename: str) -> dict:
    path = Path(__file__).resolve().parents[2] / "data" / "rules" / filename
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return {}


MATCH_RULES = _load_rules("matches.json")
DEFAULT_PROFILES = MATCH_RULES.get(
    "positional_profiles",
    {
        "ST": {"goal_weight": 0.45, "assist_weight": 0.15, "card_prob": 0.08},
        "LW": {"goal_weight": 0.30, "assist_weight": 0.28, "card_prob": 0.10},
        "RW": {"goal_weight": 0.30, "assist_weight": 0.28, "card_prob": 0.10},
        "AM": {"goal_weight": 0.22, "assist_weight": 0.35, "card_prob": 0.12},
        "CAM": {"goal_weight": 0.22, "assist_weight": 0.35, "card_prob": 0.12},
        "CM": {"goal_weight": 0.12, "assist_weight": 0.22, "card_prob": 0.18},
        "DM": {"goal_weight": 0.05, "assist_weight": 0.12, "card_prob": 0.25},
        "LB": {"goal_weight": 0.04, "assist_weight": 0.16, "card_prob": 0.18},
        "RB": {"goal_weight": 0.04, "assist_weight": 0.16, "card_prob": 0.18},
        "CB": {"goal_weight": 0.05, "assist_weight": 0.03, "card_prob": 0.22},
        "GK": {"goal_weight": 0.00, "assist_weight": 0.01, "card_prob": 0.03},
    },
)


@dataclass(frozen=True)
class FootballMatchOutcome:
    match_id: str
    home_club_id: str | int
    away_club_id: str | int
    home_score: int
    away_score: int
    winner_club_id: str | int | None
    protagonist_performance: PlayerMatchPerformance | None
    protagonist_injured: bool = False
    injury_severity: str | None = None


def simulate_single_match(
    match_id: str,
    home_club_id: str | int,
    away_club_id: str | int,
    home_strength: float,
    away_strength: float,
    protagonist_id: str | None = None,
    protagonist_club_id: str | int | None = None,
    protagonist_ovr: float = 75.0,
    protagonist_pos: str = "ST",
    protagonist_form: float = 1.0,
    is_injured: bool = False,
    seed: str = "MATCH_SEED",
) -> FootballMatchOutcome:
    s_hash = _hash_seed(f"{seed}_{match_id}_{home_club_id}_{away_club_id}")

    adj_home_strength = home_strength + MATCH_RULES.get("home_advantage_bonus", 3.0)
    diff = (adj_home_strength - away_strength) / 10.0

    base_l = MATCH_RULES.get("base_goal_lambda", 1.35)
    home_lambda = max(0.2, base_l + diff * 0.25)
    away_lambda = max(0.2, base_l - diff * 0.25)

    home_score = min(9, int((s_hash % 100) / 100.0 * (home_lambda * 2.2)))
    away_score = min(9, int(((s_hash // 100) % 100) / 100.0 * (away_lambda * 2.2)))

    winner_id = None
    if home_score > away_score:
        winner_id = home_club_id
    elif away_score > home_score:
        winner_id = away_club_id

    perf = None
    protagonist_injured = False
    inj_severity = None

    if protagonist_id and protagonist_club_id in (home_club_id, away_club_id):
        if not is_injured:
            part_hash = (s_hash // 1000) % 100
            start_prob = min(95, max(60, int(protagonist_ovr)))
            appeared = part_hash < start_prob

            if appeared:
                starter = part_hash < (start_prob - 10)
                minutes = 90 if starter else (15 + (part_hash % 30))

                profile = DEFAULT_PROFILES.get(protagonist_pos, DEFAULT_PROFILES["CM"])

                perf_factor = (protagonist_ovr / 75.0) * protagonist_form
                goal_hash = (s_hash // 10000) % 100
                assist_hash = (s_hash // 100000) % 100

                goals = 0
                if goal_hash < int(profile["goal_weight"] * 100 * perf_factor * (minutes / 90.0)):
                    goals = 1 + (1 if goal_hash < 10 else 0)

                assists = 0
                if assist_hash < int(profile["assist_weight"] * 100 * perf_factor * (minutes / 90.0)):
                    assists = 1

                base_r = 6.5 + (0.5 * (goals + assists)) + (0.3 if (protagonist_club_id == winner_id) else -0.2)
                rating = round(max(4.0, min(10.0, base_r + (perf_factor - 1.0) * 1.5)), 1)

                shots = goals + (1 if goals > 0 else 0) + (1 if (s_hash % 3 == 0) else 0)
                shots_on_target = goals + (1 if shots > goals else 0)

                perf = PlayerMatchPerformance(
                    player_id=protagonist_id,
                    match_id=match_id,
                    starter=starter,
                    minutes=minutes,
                    rating=rating,
                    goals=goals,
                    assists=assists,
                    shots=shots,
                    shots_on_target=shots_on_target,
                    key_passes=assists + (1 if (s_hash % 4 == 0) else 0),
                    tackles=1 if protagonist_pos in ("CB", "LB", "RB", "DM", "CM") else 0,
                    interceptions=1 if protagonist_pos in ("CB", "DM", "CM") else 0,
                    clearances=2 if protagonist_pos in ("CB", "LB", "RB") else 0,
                    saves=3 if protagonist_pos == "GK" else 0,
                    role="Standard",
                    position=protagonist_pos,
                    latent_influence=rating / 10.0,
                )

                inj_hash = (s_hash // 10000000) % 1000
                if inj_hash < 15:
                    protagonist_injured = True
                    if inj_hash < 2:
                        inj_severity = "SEASON_ENDING"
                    elif inj_hash < 5:
                        inj_severity = "MAJOR"
                    elif inj_hash < 9:
                        inj_severity = "MODERATE"
                    else:
                        inj_severity = "MINOR"

    return FootballMatchOutcome(
        match_id=match_id,
        home_club_id=home_club_id,
        away_club_id=away_club_id,
        home_score=home_score,
        away_score=away_score,
        winner_club_id=winner_id,
        protagonist_performance=perf,
        protagonist_injured=protagonist_injured,
        injury_severity=inj_severity,
    )
