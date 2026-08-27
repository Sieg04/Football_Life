import json
from datetime import date
from pathlib import Path

from app.player.domain import Player
from app.player.engine import position_ovr
from app.transfer.domain import ClubNeed, PlayerFit
from app.transfer.needs import evaluate_position_need
from app.world.entities import Club, Manager

RULES_PATH = Path(__file__).resolve().parents[2] / "data" / "rules" / "transfers.json"


def _load_transfer_rules() -> dict:
    if RULES_PATH.exists():
        return json.loads(RULES_PATH.read_text(encoding="utf-8"))
    return {}


def _calc_manager_quality(manager: Manager | None) -> float:
    if manager is None:
        return 50.0
    mq = (
        manager.tactical_quality * 0.30
        + manager.player_development * 0.25
        + manager.game_management * 0.20
        + manager.rotation * 0.10
        + manager.adaptability * 0.15
    )
    return max(1.0, min(100.0, mq))


def calculate_club_attractiveness(
    club: Club,
    league_strength: float = 50.0,
    rules: dict | None = None,
) -> float:
    """Calculates pure club attractiveness score (0-100) using existing club world data."""
    if rules is None:
        rules = _load_transfer_rules()

    attr_rules = rules.get("club_attractiveness", {})
    weights = attr_rules.get(
        "weights",
        {
            "prestige": 0.30,
            "league_strength": 0.25,
            "financial_power": 0.20,
            "manager_quality": 0.10,
            "facilities": 0.10,
            "squad_quality": 0.05,
        },
    )

    prestige = max(1.0, min(100.0, getattr(club, "prestige", 50.0)))
    financial_power = max(1.0, min(100.0, getattr(club, "financial_power", 50.0)))
    facilities = max(1.0, min(100.0, getattr(club, "facilities", 50.0)))
    mgr_quality = _calc_manager_quality(getattr(club, "manager", None))
    lg_strength = max(1.0, min(100.0, league_strength))

    # Calculate average squad quality (top 11 OVRs or baseline)
    squad = list(club.squad) if club.squad else []
    if squad:
        ovrs = sorted([position_ovr(p, p.primary_position) for p in squad], reverse=True)
        top_11 = ovrs[:11]
        squad_quality = sum(top_11) / len(top_11)
    else:
        squad_quality = 50.0
    squad_quality = max(1.0, min(100.0, squad_quality))

    attractiveness = (
        prestige * weights.get("prestige", 0.30)
        + lg_strength * weights.get("league_strength", 0.25)
        + financial_power * weights.get("financial_power", 0.20)
        + mgr_quality * weights.get("manager_quality", 0.10)
        + facilities * weights.get("facilities", 0.10)
        + squad_quality * weights.get("squad_quality", 0.05)
    )

    return round(max(0.0, min(100.0, attractiveness)), 2)


def evaluate_player_fit(
    player: Player,
    club: Club,
    squad_needs: dict[str, ClubNeed] | None = None,
    evaluation_date: date = date(2025, 7, 1),
    rules: dict | None = None,
) -> PlayerFit:
    """Evaluates player fit score (0-100) for a given player and club."""
    if rules is None:
        rules = _load_transfer_rules()

    fit_rules = rules.get("player_fit", {})
    weights = fit_rules.get(
        "weights",
        {
            "squad_need_fit": 0.35,
            "quality_fit": 0.30,
            "role_fit": 0.15,
            "tactical_fit": 0.10,
            "age_fit": 0.10,
        },
    )

    # Player position OVR
    pos = player.primary_position
    p_ovr = position_ovr(player, pos)

    # 1. Squad Need Fit
    if squad_needs and pos in squad_needs:
        cn = squad_needs[pos]
    else:
        cn = evaluate_position_need(club, pos, evaluation_date=evaluation_date, rules=rules)
    squad_need_fit = cn.need_score

    # 2. Quality Fit
    # Target quality based on club prestige
    prestige = max(1.0, min(100.0, getattr(club, "prestige", 50.0)))
    target_quality = 45.0 + (prestige * 0.45)

    diff = p_ovr - target_quality
    if diff >= 0:
        # Player is at or above target quality for club level
        quality_fit = max(60.0, 100.0 - (diff * 1.5))
    else:
        # Player is below target quality
        quality_fit = max(0.0, 100.0 + (diff * 4.0))

    # 3. Role / Positional Fit
    if player.primary_position == pos:
        role_fit = 100.0
    elif pos in player.secondary_positions:
        role_fit = 75.0
    else:
        role_fit = 40.0

    # 4. Age / Potential Fit
    birth_date = player.birth_date
    age = evaluation_date.year - birth_date.year - ((evaluation_date.month, evaluation_date.day) < (birth_date.month, birth_date.day))

    manager = getattr(club, "manager", None)
    youth_pref = manager.youth_preference if manager else 50.0

    if age <= 21:
        # High potential young player
        pot_gap = player.potential - p_ovr
        age_fit = min(100.0, 60.0 + (youth_pref * 0.2) + (pot_gap * 1.5))
    elif age <= 28:
        # Prime age player
        age_fit = 90.0
    elif age <= 31:
        # Late prime
        age_fit = 70.0
    else:
        # Veteran decline
        age_fit = max(20.0, 70.0 - ((age - 31) * 12.0))

    # 5. Tactical Fit
    # Influenced by manager style, youth preference compatibility, and player personality/traits
    tactical_fit = 75.0
    if manager:
        if age <= 22:
            tactical_fit += (manager.youth_preference - 50.0) * 0.3
        if player.personality.get("professionalism", 50.0) >= 70:
            tactical_fit += (manager.discipline - 50.0) * 0.2
    tactical_fit = max(0.0, min(100.0, tactical_fit))

    # Combined fit score
    raw_fit_score = (
        squad_need_fit * weights.get("squad_need_fit", 0.35)
        + quality_fit * weights.get("quality_fit", 0.30)
        + role_fit * weights.get("role_fit", 0.15)
        + tactical_fit * weights.get("tactical_fit", 0.10)
        + age_fit * weights.get("age_fit", 0.10)
    )

    fit_score = round(max(0.0, min(100.0, raw_fit_score)), 2)

    club_id = getattr(club, "id", getattr(club, "name", "unknown_club"))

    breakdown = {
        "squad_need_fit": round(squad_need_fit, 2),
        "quality_fit": round(quality_fit, 2),
        "role_fit": round(role_fit, 2),
        "tactical_fit": round(tactical_fit, 2),
        "age_fit": round(age_fit, 2),
        "player_ovr": round(p_ovr, 2),
        "target_quality": round(target_quality, 2),
    }

    return PlayerFit(
        player_id=player.id,
        club_id=club_id,
        fit_score=fit_score,
        quality_fit=round(quality_fit, 2),
        role_fit=round(role_fit, 2),
        tactical_fit=round(tactical_fit, 2),
        age_fit=round(age_fit, 2),
        squad_need_fit=round(squad_need_fit, 2),
        breakdown=breakdown,
    )
