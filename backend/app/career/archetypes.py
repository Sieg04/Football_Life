import json
from dataclasses import dataclass, field
from enum import StrEnum
from pathlib import Path

from app.career.domain import Career


class CareerArchetypeTag(StrEnum):
    WONDERKID = "WONDERKID"
    FAILED_WONDERKID = "FAILED_WONDERKID"
    SUPERSTAR = "SUPERSTAR"
    LATE_BLOOMER = "LATE_BLOOMER"
    EARLY_DECLINER = "EARLY_DECLINER"
    LONG_PRIME = "LONG_PRIME"
    SOLID_PRO = "SOLID_PRO"


@dataclass
class CareerArchetypeResult:
    tags: list[CareerArchetypeTag]
    evidence: dict[str, dict] = field(default_factory=dict)


def _load_archetype_rules() -> dict:
    path = Path(__file__).resolve().parents[2] / "data" / "rules" / "career_archetypes.json"
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return {}


def classify_career(career: Career, rules: dict | None = None) -> CareerArchetypeResult:
    if rules is None:
        rules = _load_archetype_rules()

    tags: list[CareerArchetypeTag] = []
    evidence: dict[str, dict] = {}

    start_snapshot = career.snapshots[0] if career.snapshots else None
    start_age = start_snapshot.starting_age if start_snapshot else (career.seasons[0].starting_age if career.seasons else 18)
    start_ca = start_snapshot.starting_ability if start_snapshot else (career.seasons[0].starting_ability if career.seasons else career.player.current_ability)
    potential = career.player.potential

    peak_ca = career.peak_ability
    peak_ovr = career.peak_ovr
    peak_age = career.peak_age
    final_ca = career.snapshots[-1].ending_ability if career.snapshots else career.player.current_ability

    snapshots = career.snapshots if career.snapshots else []
    ca_by_age = {sn.ending_age: sn.ending_ability for sn in snapshots}
    if start_snapshot:
        ca_by_age[start_snapshot.starting_age] = start_snapshot.starting_ability

    # 1. SUPERSTAR
    sup_rules = rules.get("superstar", {})
    min_peak_ovr = sup_rules.get("min_peak_ovr", 88.0)
    if peak_ovr >= min_peak_ovr:
        tags.append(CareerArchetypeTag.SUPERSTAR)
        evidence[CareerArchetypeTag.SUPERSTAR] = {
            "peak_ovr": peak_ovr,
            "threshold": min_peak_ovr,
        }

    # 2. LONG_PRIME
    lp_rules = rules.get("long_prime", {})
    min_lp_peak_age = lp_rules.get("min_peak_age", 27)
    min_lp_seasons = lp_rules.get("min_seasons_within_98_pct", 19)
    seasons_within_98 = sum(1 for sn in snapshots if sn.ending_ability >= 0.98 * peak_ca) if snapshots else 0
    if peak_age >= min_lp_peak_age and seasons_within_98 >= min_lp_seasons:
        tags.append(CareerArchetypeTag.LONG_PRIME)
        evidence[CareerArchetypeTag.LONG_PRIME] = {
            "peak_age": peak_age,
            "min_peak_age_threshold": min_lp_peak_age,
            "seasons_within_98_percent": seasons_within_98,
            "threshold": min_lp_seasons,
        }

    # 3. LATE_BLOOMER
    lb_rules = rules.get("late_bloomer", {})
    min_lb_peak_age = lb_rules.get("min_peak_age", 28)
    min_post_24_growth = lb_rules.get("min_ca_growth_post_24", 1.5)
    ca_at_24 = ca_by_age.get(24, ca_by_age.get(23, start_ca))
    ca_growth_post_24 = peak_ca - ca_at_24

    if peak_age >= min_lb_peak_age and ca_growth_post_24 >= min_post_24_growth:
        tags.append(CareerArchetypeTag.LATE_BLOOMER)
        evidence[CareerArchetypeTag.LATE_BLOOMER] = {
            "peak_age": peak_age,
            "min_peak_age_threshold": min_lb_peak_age,
            "ca_growth_post_24": ca_growth_post_24,
            "min_post_24_growth_threshold": min_post_24_growth,
        }

    # 4. WONDERKID
    wk_rules = rules.get("wonderkid", {})
    max_wk_start_age = wk_rules.get("max_starting_age", 17)
    min_wk_start_ca = wk_rules.get("min_starting_ca", 78.36)
    min_wk_pot = wk_rules.get("min_potential", 87.23)

    if start_age <= max_wk_start_age and start_ca >= min_wk_start_ca and potential >= min_wk_pot:
        tags.append(CareerArchetypeTag.WONDERKID)
        evidence[CareerArchetypeTag.WONDERKID] = {
            "start_age": start_age,
            "max_starting_age_threshold": max_wk_start_age,
            "start_ca": start_ca,
            "min_starting_ca_threshold": min_wk_start_ca,
            "potential": potential,
            "min_potential_threshold": min_wk_pot,
        }

    # 5. FAILED_WONDERKID
    fw_rules = rules.get("failed_wonderkid", {})
    max_fw_start_age = fw_rules.get("max_starting_age", 17)
    min_fw_pot = fw_rules.get("min_potential", 87.23)
    max_pot_realization = fw_rules.get("max_potential_realization_pct", 82.0)
    pot_realization_pct = (peak_ca / potential * 100.0) if potential > 0 else 0.0

    if start_age <= max_fw_start_age and potential >= min_fw_pot and pot_realization_pct <= max_pot_realization:
        tags.append(CareerArchetypeTag.FAILED_WONDERKID)
        evidence[CareerArchetypeTag.FAILED_WONDERKID] = {
            "start_age": start_age,
            "potential": potential,
            "min_potential_threshold": min_fw_pot,
            "potential_realization_pct": pot_realization_pct,
            "max_potential_realization_pct_threshold": max_pot_realization,
        }

    # 6. EARLY_DECLINER
    ed_rules = rules.get("early_decliner", {})
    max_ed_peak_age = ed_rules.get("max_peak_age", 29)
    min_ed_ca_decline = ed_rules.get("min_ca_decline", 3.0)
    ca_decline_from_peak = peak_ca - final_ca

    if peak_age <= max_ed_peak_age and ca_decline_from_peak >= min_ed_ca_decline:
        tags.append(CareerArchetypeTag.EARLY_DECLINER)
        evidence[CareerArchetypeTag.EARLY_DECLINER] = {
            "peak_age": peak_age,
            "max_peak_age_threshold": max_ed_peak_age,
            "ca_decline_from_peak": ca_decline_from_peak,
            "min_ca_decline_threshold": min_ed_ca_decline,
        }

    # Fallback to SOLID_PRO if no major tags match
    if not tags:
        tags.append(CareerArchetypeTag.SOLID_PRO)
        evidence[CareerArchetypeTag.SOLID_PRO] = {
            "reason": "No major career archetype conditions met."
        }

    return CareerArchetypeResult(tags=tags, evidence=evidence)
