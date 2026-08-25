from dataclasses import dataclass, field
import json
from pathlib import Path

from app.player.domain import Player
from app.player.engine import (
    attribute_fit,
    position_ovr,
    role_effectiveness as calc_role_effectiveness,
)


def _load_player_roles() -> dict:
    path = Path(__file__).resolve().parents[2] / "data" / "rules" / "player_roles.json"
    if path.exists():
        data = json.loads(path.read_text(encoding="utf-8"))
        return data.get("roles", {})
    return {}


_ROLE_DEFINITIONS = _load_player_roles()


@dataclass
class TacticalPreset:
    formation_name: str
    position_slots: tuple[str, ...]
    line_assignments: dict[str, str]
    role_requirements: dict[str, str] = field(default_factory=dict)


@dataclass
class LineupSlot:
    slot_position: str
    player: Player
    evaluated_role: str
    role_familiarity: float
    role_attribute_fit: float
    role_effectiveness: float


@dataclass
class Lineup:
    club_id: int
    formation: TacticalPreset
    starters: list[LineupSlot]
    bench: list[Player]
    average_ovr: float
    average_role_effectiveness: float
    tactical_fit: float


@dataclass
class EffectiveTeamStrength:
    club_id: int
    xi_quality: float
    tactical_fit: float
    form_factor: float
    fitness_factor: float
    manager_quality: float
    effective_strength: float


# Default formation presets
FORMATION_PRESETS: dict[str, TacticalPreset] = {
    "4-3-3": TacticalPreset(
        formation_name="4-3-3",
        position_slots=("GK", "CB", "CB", "LB", "RB", "CM", "CM", "CAM", "LW", "RW", "ST"),
        line_assignments={
            "GK": "GK",
            "CB": "DEF",
            "LB": "DEF",
            "RB": "DEF",
            "CM": "MID",
            "CAM": "MID",
            "LW": "ATT",
            "RW": "ATT",
            "ST": "ATT",
        },
        role_requirements={
            "GK": "TRADITIONAL_KEEPER",
            "CB": "CENTRE_BACK",
            "LB": "FULL_BACK",
            "RB": "FULL_BACK",
            "CM": "PLAYMAKER",
            "CAM": "PLAYMAKER",
            "LW": "WINGER",
            "RW": "WINGER",
            "ST": "POACHER",
        },
    ),
    "4-2-3-1": TacticalPreset(
        formation_name="4-2-3-1",
        position_slots=("GK", "CB", "CB", "LB", "RB", "DM", "DM", "CAM", "LW", "RW", "ST"),
        line_assignments={
            "GK": "GK",
            "CB": "DEF",
            "LB": "DEF",
            "RB": "DEF",
            "DM": "MID",
            "CAM": "MID",
            "LW": "ATT",
            "RW": "ATT",
            "ST": "ATT",
        },
        role_requirements={
            "GK": "TRADITIONAL_KEEPER",
            "CB": "CENTRE_BACK",
            "LB": "FULL_BACK",
            "RB": "FULL_BACK",
            "DM": "BALL_WINNER",
            "CAM": "PLAYMAKER",
            "LW": "WINGER",
            "RW": "WINGER",
            "ST": "ADVANCED_FORWARD",
        },
    ),
    "4-4-2": TacticalPreset(
        formation_name="4-4-2",
        position_slots=("GK", "CB", "CB", "LB", "RB", "CM", "CM", "LM", "RM", "ST", "ST"),
        line_assignments={
            "GK": "GK",
            "CB": "DEF",
            "LB": "DEF",
            "RB": "DEF",
            "CM": "MID",
            "LM": "MID",
            "RM": "MID",
            "ST": "ATT",
        },
        role_requirements={
            "GK": "TRADITIONAL_KEEPER",
            "CB": "CENTRE_BACK",
            "LB": "FULL_BACK",
            "RB": "FULL_BACK",
            "CM": "PLAYMAKER",
            "LM": "WINGER",
            "RM": "WINGER",
            "ST": "POACHER",
        },
    ),
    "3-5-2": TacticalPreset(
        formation_name="3-5-2",
        position_slots=("GK", "CB", "CB", "CB", "LWB", "RWB", "CM", "CM", "CAM", "ST", "ST"),
        line_assignments={
            "GK": "GK",
            "CB": "DEF",
            "LWB": "MID",
            "RWB": "MID",
            "CM": "MID",
            "CAM": "MID",
            "ST": "ATT",
        },
        role_requirements={
            "GK": "TRADITIONAL_KEEPER",
            "CB": "CENTRE_BACK",
            "LWB": "WING_BACK",
            "RWB": "WING_BACK",
            "CM": "BALL_WINNER",
            "CAM": "PLAYMAKER",
            "ST": "TARGET_FORWARD",
        },
    ),
    "3-4-3": TacticalPreset(
        formation_name="3-4-3",
        position_slots=("GK", "CB", "CB", "CB", "LM", "RM", "CM", "CM", "LW", "RW", "ST"),
        line_assignments={
            "GK": "GK",
            "CB": "DEF",
            "LM": "MID",
            "RM": "MID",
            "CM": "MID",
            "LW": "ATT",
            "RW": "ATT",
            "ST": "ATT",
        },
        role_requirements={
            "GK": "TRADITIONAL_KEEPER",
            "CB": "CENTRE_BACK",
            "LM": "WING_BACK",
            "RM": "WING_BACK",
            "CM": "PLAYMAKER",
            "LW": "WINGER",
            "RW": "WINGER",
            "ST": "POACHER",
        },
    ),
    "4-1-4-1": TacticalPreset(
        formation_name="4-1-4-1",
        position_slots=("GK", "CB", "CB", "LB", "RB", "DM", "CM", "CM", "LM", "RM", "ST"),
        line_assignments={
            "GK": "GK",
            "CB": "DEF",
            "LB": "DEF",
            "RB": "DEF",
            "DM": "MID",
            "CM": "MID",
            "LM": "MID",
            "RM": "MID",
            "ST": "ATT",
        },
        role_requirements={
            "GK": "TRADITIONAL_KEEPER",
            "CB": "CENTRE_BACK",
            "LB": "FULL_BACK",
            "RB": "FULL_BACK",
            "DM": "BALL_WINNER",
            "CM": "PLAYMAKER",
            "LM": "WINGER",
            "RM": "WINGER",
            "ST": "ADVANCED_FORWARD",
        },
    ),
}


def _get_default_role_for_position(position: str) -> str:
    defaults = {
        "GK": "TRADITIONAL_KEEPER",
        "CB": "CENTRE_BACK",
        "LB": "FULL_BACK",
        "RB": "FULL_BACK",
        "LWB": "WING_BACK",
        "RWB": "WING_BACK",
        "DM": "BALL_WINNER",
        "CM": "PLAYMAKER",
        "CAM": "PLAYMAKER",
        "AM": "PLAYMAKER",
        "LM": "WINGER",
        "RM": "WINGER",
        "LW": "WINGER",
        "RW": "WINGER",
        "ST": "POACHER",
    }
    return defaults.get(position, "PLAYMAKER")


def evaluate_player_for_slot(
    player: Player,
    slot_position: str,
    target_role: str | None = None,
    manager_pref: float = 50.0,
) -> tuple[float, LineupSlot]:
    if not target_role or target_role not in _ROLE_DEFINITIONS:
        target_role = _get_default_role_for_position(slot_position)

    raw_ovr = position_ovr(player, slot_position)
    role_def = _ROLE_DEFINITIONS.get(target_role)

    # Positional suitability factor
    if player.primary_position == slot_position:
        pos_factor = 1.00
    elif slot_position in player.secondary_positions:
        pos_factor = 0.85
    else:
        pos_factor = 0.50

    eval_ovr = raw_ovr * pos_factor

    if role_def:
        role_eff = calc_role_effectiveness(player, target_role, _ROLE_DEFINITIONS) * pos_factor
        attr_fit = attribute_fit(player, role_def["attribute_weights"])
    else:
        role_eff = eval_ovr
        attr_fit = raw_ovr

    familiarity = player.role_familiarity.get(target_role, 50.0)
    form = player.state.form
    fitness = player.state.fitness

    selection_score = (
        eval_ovr * 0.50
        + role_eff * 0.20
        + form * 0.10
        + fitness * 0.10
        + manager_pref * 0.10
    )

    slot = LineupSlot(
        slot_position=slot_position,
        player=player,
        evaluated_role=target_role,
        role_familiarity=familiarity,
        role_attribute_fit=attr_fit,
        role_effectiveness=role_eff,
    )
    return selection_score, slot


def calculate_tactical_fit(starters: list[LineupSlot], manager_style: str = "BALANCED") -> float:
    if not starters:
        return 0.0

    position_fit_scores = []
    for slot in starters:
        p = slot.player
        pos = slot.slot_position
        if p.primary_position == pos:
            pos_score = 100.0
        elif pos in p.secondary_positions:
            pos_score = 75.0
        else:
            pos_score = 25.0

        slot_fit = (pos_score * 0.6) + (slot.role_effectiveness * 0.4)
        position_fit_scores.append(slot_fit)

    avg_fit = sum(position_fit_scores) / len(position_fit_scores)
    return max(0.0, min(100.0, avg_fit))


def calculate_xi_quality(starters: list[LineupSlot], formation: TacticalPreset) -> float:
    line_ovrs: dict[str, list[float]] = {"GK": [], "DEF": [], "MID": [], "ATT": []}

    for slot in starters:
        pos = slot.slot_position
        ovr = position_ovr(slot.player, pos)
        line_type = formation.line_assignments.get(pos, "MID")
        line_ovrs[line_type].append(ovr)

    gk_avg = sum(line_ovrs["GK"]) / len(line_ovrs["GK"]) if line_ovrs["GK"] else 50.0
    def_avg = sum(line_ovrs["DEF"]) / len(line_ovrs["DEF"]) if line_ovrs["DEF"] else 50.0
    mid_avg = sum(line_ovrs["MID"]) / len(line_ovrs["MID"]) if line_ovrs["MID"] else 50.0
    att_avg = sum(line_ovrs["ATT"]) / len(line_ovrs["ATT"]) if line_ovrs["ATT"] else 50.0

    xi_quality = (gk_avg * 0.10) + (def_avg * 0.30) + (mid_avg * 0.30) + (att_avg * 0.30)
    return max(1.0, min(100.0, xi_quality))


def calculate_effective_team_strength(
    xi_quality: float,
    club_strength: float,
    manager_quality: float,
    tactical_fit: float,
    form_factor: float,
    fitness_factor: float,
    club_id: int = 1,
) -> EffectiveTeamStrength:
    eff_strength = (
        (xi_quality * 0.65)
        + (club_strength * 0.15)
        + (manager_quality * 0.05)
        + (tactical_fit * 0.05)
        + (form_factor * 0.05)
        + (fitness_factor * 0.05)
    )
    eff_strength = max(1.0, min(100.0, eff_strength))

    return EffectiveTeamStrength(
        club_id=club_id,
        xi_quality=xi_quality,
        tactical_fit=tactical_fit,
        form_factor=form_factor,
        fitness_factor=fitness_factor,
        manager_quality=manager_quality,
        effective_strength=eff_strength,
    )


def select_lineup(
    squad: list[Player],
    club_id: int,
    formation: TacticalPreset | None = None,
    manager_pref_map: dict[str, float] | None = None,
) -> Lineup:
    if formation is None:
        formation = FORMATION_PRESETS["4-3-3"]
    if manager_pref_map is None:
        manager_pref_map = {}

    available_players = list(squad)
    starters: list[LineupSlot] = []
    selected_player_ids = set()

    for slot_pos in formation.position_slots:
        target_role = formation.role_requirements.get(slot_pos)
        candidates = []

        for p in available_players:
            if p.id in selected_player_ids:
                continue

            # Specialized constraint for GK slot
            if slot_pos == "GK" and p.primary_position != "GK":
                gk_available = any(
                    other.primary_position == "GK" and other.id not in selected_player_ids
                    for other in available_players
                )
                if gk_available:
                    continue

            pref = manager_pref_map.get(p.id, 50.0)
            score, slot = evaluate_player_for_slot(p, slot_pos, target_role, pref)
            # Deterministic tie-breaker: (-score, player.id)
            candidates.append((score, p.id, slot))

        if candidates:
            candidates.sort(key=lambda x: (-x[0], x[1]))
            chosen_score, chosen_id, chosen_slot = candidates[0]
            starters.append(chosen_slot)
            selected_player_ids.add(chosen_id)

    # Remaining players go to bench
    bench = [p for p in squad if p.id not in selected_player_ids]
    # Sort bench deterministically by position_ovr
    bench.sort(key=lambda p: (-position_ovr(p, p.primary_position), p.id))

    if starters:
        avg_ovr = sum(position_ovr(slot.player, slot.slot_position) for slot in starters) / len(starters)
        avg_role_eff = sum(slot.role_effectiveness for slot in starters) / len(starters)
    else:
        avg_ovr = 50.0
        avg_role_eff = 50.0

    tac_fit = calculate_tactical_fit(starters)

    return Lineup(
        club_id=club_id,
        formation=formation,
        starters=starters,
        bench=bench,
        average_ovr=avg_ovr,
        average_role_effectiveness=avg_role_eff,
        tactical_fit=tac_fit,
    )
