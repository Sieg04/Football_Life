import json
from datetime import date
from pathlib import Path

from app.player.engine import position_ovr
from app.transfer.domain import ClubNeed
from app.world.entities import Club

RULES_PATH = Path(__file__).resolve().parents[2] / "data" / "rules" / "transfers.json"

STANDARD_POSITIONS: tuple[str, ...] = (
    "GK", "CB", "LB", "RB", "DM", "CM", "CAM", "LW", "RW", "ST"
)

DEFAULT_IDEAL_DEPTH: dict[str, int] = {
    "GK": 2,
    "CB": 4,
    "LB": 2,
    "RB": 2,
    "DM": 2,
    "CM": 3,
    "CAM": 2,
    "LW": 2,
    "RW": 2,
    "ST": 3,
}


def _load_transfer_rules() -> dict:
    if RULES_PATH.exists():
        return json.loads(RULES_PATH.read_text(encoding="utf-8"))
    return {}


def evaluate_position_need(
    club: Club,
    position: str,
    evaluation_date: date = date(2025, 7, 1),
    rules: dict | None = None,
) -> ClubNeed:
    """Evaluates the squad need score (0-100) for a given position in a club."""
    if rules is None:
        rules = _load_transfer_rules()

    needs_rules = rules.get("club_needs", {})
    weights = needs_rules.get(
        "weights",
        {
            "depth_gap": 0.35,
            "quality_gap": 0.35,
            "age_risk": 0.15,
            "role_gap": 0.10,
            "squad_balance": 0.05,
        },
    )
    ideal_depth_map = needs_rules.get("ideal_depth", DEFAULT_IDEAL_DEPTH)
    ideal_depth = float(ideal_depth_map.get(position, 2))

    target_base = needs_rules.get("target_quality_base", 45.0)
    target_weight = needs_rules.get("target_quality_prestige_weight", 0.45)
    prestige = max(1.0, min(100.0, getattr(club, "prestige", 50.0)))
    target_quality = target_base + (prestige * target_weight)

    squad = list(club.squad) if club.squad else []

    # Filter players who can play this position
    position_players = []
    for p in squad:
        if p.primary_position == position or position in p.secondary_positions:
            position_players.append(p)

    # 1. Depth Gap
    actual_count = len(position_players)
    if actual_count < ideal_depth:
        depth_gap = min(100.0, ((ideal_depth - actual_count) / ideal_depth) * 100.0)
    else:
        depth_gap = 0.0

    # 2. Quality Gap
    if not position_players:
        quality_gap = 100.0
    else:
        best_ovr = max(position_ovr(p, position) for p in position_players)
        gap = target_quality - best_ovr
        if gap > 0:
            quality_gap = min(100.0, (gap / 30.0) * 100.0)
        else:
            quality_gap = 0.0

    # 3. Age Risk
    if not position_players:
        age_risk = 50.0
    else:
        # Check age of best player at position
        best_player = max(position_players, key=lambda p: position_ovr(p, position))
        bdate = best_player.birth_date
        best_age = (
            evaluation_date.year
            - bdate.year
            - ((evaluation_date.month, evaluation_date.day) < (bdate.month, bdate.day))
        )

        young_prospects = [
            p for p in position_players
            if (
                evaluation_date.year
                - p.birth_date.year
                - ((evaluation_date.month, evaluation_date.day) < (p.birth_date.month, p.birth_date.day))
            ) <= 23 and p.potential >= target_quality - 3.0
        ]

        if best_age >= 33:
            age_risk = 100.0 if not young_prospects else 50.0
        elif best_age >= 31:
            age_risk = 70.0 if not young_prospects else 30.0
        elif best_age >= 29:
            age_risk = 40.0 if not young_prospects else 15.0
        else:
            age_risk = 0.0

    # 4. Role Gap
    # If primary position depth is 0 (only secondary position players), role gap is higher
    primary_count = sum(1 for p in position_players if p.primary_position == position)
    if primary_count == 0:
        role_gap = 80.0 if position_players else 100.0
    elif primary_count < max(1, int(ideal_depth // 2)):
        role_gap = 40.0
    else:
        role_gap = 0.0

    # 5. Squad Balance
    total_squad_size = len(squad)
    target_squad_size = needs_rules.get("target_squad_size", 25)
    if total_squad_size < target_squad_size - 4:
        squad_balance = min(100.0, ((target_squad_size - total_squad_size) / target_squad_size) * 100.0)
    elif total_squad_size > target_squad_size + 6:
        squad_balance = 20.0
    else:
        squad_balance = 0.0

    # Compute overall need_score
    raw_need_score = (
        depth_gap * weights.get("depth_gap", 0.35)
        + quality_gap * weights.get("quality_gap", 0.35)
        + age_risk * weights.get("age_risk", 0.15)
        + role_gap * weights.get("role_gap", 0.10)
        + squad_balance * weights.get("squad_balance", 0.05)
    )

    need_score = round(max(0.0, min(100.0, raw_need_score)), 2)

    breakdown = {
        "depth_gap": round(depth_gap, 2),
        "quality_gap": round(quality_gap, 2),
        "age_risk": round(age_risk, 2),
        "role_gap": round(role_gap, 2),
        "squad_balance": round(squad_balance, 2),
        "target_quality": round(target_quality, 2),
        "actual_count": actual_count,
        "ideal_depth": ideal_depth,
    }

    return ClubNeed(
        position=position,
        need_score=need_score,
        depth_gap=round(depth_gap, 2),
        quality_gap=round(quality_gap, 2),
        age_risk=round(age_risk, 2),
        role_gap=round(role_gap, 2),
        squad_balance=round(squad_balance, 2),
        breakdown=breakdown,
    )


def evaluate_club_needs(
    club: Club,
    evaluation_date: date = date(2025, 7, 1),
    positions: tuple[str, ...] | None = None,
    rules: dict | None = None,
) -> dict[str, ClubNeed]:
    """Evaluates position needs for all standard or specified positions for a club."""
    if positions is None:
        positions = STANDARD_POSITIONS

    needs = {}
    for pos in positions:
        needs[pos] = evaluate_position_need(club, pos, evaluation_date=evaluation_date, rules=rules)
    return needs
