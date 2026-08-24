import hashlib
import json
import random
from datetime import date
from pathlib import Path

from app.career.domain import (
    Career,
    CareerPhase,
    Season,
    SeasonalEnvironmentInput,
    SeasonalPerformanceInput,
    SeasonalPlayingTimeInput,
    SeasonSnapshot,
)
from app.player.domain import Player
from app.player.engine import current_ability, position_ovr


def _load_rules(filename: str) -> dict:
    path = Path(__file__).resolve().parents[2] / "data" / "rules" / filename
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return {}


_development_rules = _load_rules("player_development.json")
_attribute_rules = _load_rules("player_attributes.json")

BASE_RATE = _development_rules.get("base_rate", 2.0)
POTENTIAL_GAP_MAX = _development_rules.get("potential_gap_max", 30.0)
PROFILES = _development_rules.get("profiles", {})
AGE_FACTORS = _development_rules.get("age_factors", {})
PLAYING_TIME_FACTORS = _development_rules.get("playing_time_factors", [])
SOFT_CAPS = _development_rules.get("soft_caps", [])
DECLINE_RULES = _development_rules.get("decline", {})
ATTRIBUTE_GROUPS = _attribute_rules.get("groups", {})


def calculate_age(birth_date: date, as_of: date) -> int:
    return as_of.year - birth_date.year - ((as_of.month, as_of.day) < (birth_date.month, birth_date.day))


def calculate_career_phase(age: int) -> CareerPhase:
    if age < 18:
        return CareerPhase.YOUTH
    elif 18 <= age <= 20:
        return CareerPhase.EARLY_PRO
    elif 21 <= age <= 23:
        return CareerPhase.DEVELOPMENT
    elif 24 <= age <= 28:
        return CareerPhase.PRIME
    elif 29 <= age <= 31:
        return CareerPhase.LATE_PRIME
    elif 32 <= age <= 34:
        return CareerPhase.DECLINE
    else:
        return CareerPhase.VETERAN


def get_sha256_rng(seed: str, player_id: str, season_number: int) -> random.Random:
    seed_material = f"{seed}:{player_id}:{season_number}"
    seed_hash = hashlib.sha256(seed_material.encode("utf-8")).hexdigest()
    seed_int = int(seed_hash[:16], 16)
    return random.Random(seed_int)


def get_age_factor(age: int) -> float:
    if age <= 18:
        return AGE_FACTORS.get("16-18", 1.4)
    elif age <= 21:
        return AGE_FACTORS.get("19-21", 1.25)
    elif age <= 24:
        return AGE_FACTORS.get("22-24", 1.1)
    elif age <= 27:
        return AGE_FACTORS.get("25-27", 0.85)
    elif age <= 30:
        return AGE_FACTORS.get("28-30", 0.6)
    elif age <= 33:
        return AGE_FACTORS.get("31-33", 0.35)
    else:
        return AGE_FACTORS.get("34+", 0.1)


def get_playing_time_factor(minutes_played: int) -> float:
    for rule in PLAYING_TIME_FACTORS:
        if minutes_played <= rule["max_minutes"]:
            return rule["factor"]
    return 1.0


def calculate_development_budget(
    player: Player,
    starting_age: int,
    playing_time: SeasonalPlayingTimeInput,
    performance: SeasonalPerformanceInput,
    environment: SeasonalEnvironmentInput,
    rng: random.Random,
) -> float:
    potential_gap = max(0.0, player.potential - player.current_ability)
    potential_factor = min(1.0, max(0.0, potential_gap / POTENTIAL_GAP_MAX))

    age_factor_val = get_age_factor(starting_age)
    development_rate_factor = 0.5 + (player.development_rate / 100.0)
    playing_time_factor = get_playing_time_factor(playing_time.minutes_played)

    facilities_mod = 1.0 + ((environment.facilities - 50.0) / 500.0)
    manager_mod = 1.0 + ((environment.manager_player_development - 50.0) / 500.0)
    environment_factor = facilities_mod * manager_mod

    prof = player.personality.get("professionalism", 50.0)
    professionalism_factor = 1.0 + ((prof - 50.0) / 625.0)

    performance_factor = 1.0 + ((performance.average_rating - 6.8) / 10.0)

    state_avg = (player.state.confidence + player.state.morale + player.state.fitness + player.state.happiness) / 4.0
    player_state_factor = 1.0 + ((state_avg - 70.0) / 300.0)

    random_factor = rng.uniform(0.85, 1.15)

    budget = (
        BASE_RATE
        * potential_factor
        * age_factor_val
        * development_rate_factor
        * playing_time_factor
        * environment_factor
        * professionalism_factor
        * performance_factor
        * player_state_factor
        * random_factor
    )
    return max(0.0, budget)


def get_soft_cap_multiplier(current_val: float) -> float:
    for rule in SOFT_CAPS:
        if current_val <= rule["max_val"]:
            return rule["multiplier"]
    return 0.10


def allocate_two_stage_development(
    player: Player,
    development_budget: float,
) -> tuple[dict[str, float], dict[str, float]]:
    profile_name = player.development_profile.value if hasattr(player.development_profile, "value") else str(player.development_profile)
    profile_weights = PROFILES.get(profile_name, PROFILES.get("BALANCED", {}))
    total_profile_weight = sum(profile_weights.values()) or 1.0

    stage1_group_budget: dict[str, float] = {}
    for group, weight in profile_weights.items():
        stage1_group_budget[group] = development_budget * (weight / total_profile_weight)

    stage2_attribute_changes: dict[str, float] = {}
    for group, group_budget in stage1_group_budget.items():
        attr_subweights = ATTRIBUTE_GROUPS.get(group, {})
        group_sub_total = sum(attr_subweights.values()) or 1.0
        for attr_name, subweight in attr_subweights.items():
            if not hasattr(player.attributes, attr_name):
                continue
            allocated_delta = group_budget * (subweight / group_sub_total)
            current_val = getattr(player.attributes, attr_name)
            soft_cap_mult = get_soft_cap_multiplier(current_val)
            net_delta = allocated_delta * soft_cap_mult
            stage2_attribute_changes[attr_name] = stage2_attribute_changes.get(attr_name, 0.0) + net_delta

    return stage1_group_budget, stage2_attribute_changes


def apply_decline_effects(player: Player, age: int, attribute_changes: dict[str, float]) -> None:
    start_age = DECLINE_RULES.get("start_age", 29)
    if age < start_age:
        return

    years_over = age - start_age + 1
    physical_attrs = set(DECLINE_RULES.get("physical_attributes", ["acceleration", "sprint_speed", "agility", "stamina"]))
    base_phys_rate = DECLINE_RULES.get("physical_rate", 0.15)
    base_other_rate = DECLINE_RULES.get("other_rate", 0.03)

    phys_decline = base_phys_rate * (1.0 + 0.1 * years_over)
    other_decline = base_other_rate * (1.0 + 0.05 * years_over)

    for attr_name in vars(player.attributes):
        if attr_name in physical_attrs:
            loss = phys_decline
        else:
            loss = other_decline
        attribute_changes[attr_name] = attribute_changes.get(attr_name, 0.0) - loss


def apply_attribute_changes(player: Player, attribute_changes: dict[str, float]) -> None:
    for attr_name, delta in attribute_changes.items():
        if hasattr(player.attributes, attr_name):
            old_val = getattr(player.attributes, attr_name)
            new_val = max(1.0, min(100.0, old_val + delta))
            setattr(player.attributes, attr_name, new_val)


def create_career(
    career_id: str,
    player: Player,
    club_id: int,
    start_date: date,
    seed: str = "FL-0000-0000",
) -> Career:
    starting_age = calculate_age(player.birth_date, start_date)
    starting_phase = calculate_career_phase(starting_age)

    ca = current_ability(player)
    player.current_ability = ca
    ovr = position_ovr(player, player.primary_position)

    career = Career(
        id=career_id,
        player=player,
        start_date=start_date,
        end_date=None,
        current_season_number=1,
        current_season_label=f"{start_date.year}/{str(start_date.year + 1)[-2:]}",
        current_club_id=club_id,
        career_phase=starting_phase,
        peak_ability=ca,
        peak_ovr=ovr,
        peak_age=starting_age,
        peak_position=player.primary_position,
        peak_club_id=club_id,
        seed=seed,
    )

    initial_snapshot = SeasonSnapshot(
        season_number=0,
        season_label="INITIAL",
        starting_age=starting_age,
        ending_age=starting_age,
        club_id=club_id,
        starting_position=player.primary_position,
        ending_position=player.primary_position,
        starting_ability=ca,
        ending_ability=ca,
        starting_ovr=ovr,
        ending_ovr=ovr,
        career_phase_at_start=starting_phase,
        career_phase_at_end=starting_phase,
        playing_time_input=SeasonalPlayingTimeInput(0),
        performance_input=SeasonalPerformanceInput(6.8),
        environment_input=SeasonalEnvironmentInput(),
        development_budget=0.0,
        development_summary={},
        attribute_changes={},
        season_seed=f"{seed}:{player.id}:0",
    )
    career.snapshots.append(initial_snapshot)

    return career


def simulate_season(
    career: Career,
    playing_time: SeasonalPlayingTimeInput | None = None,
    performance: SeasonalPerformanceInput | None = None,
    environment: SeasonalEnvironmentInput | None = None,
) -> Season:
    if playing_time is None:
        playing_time = SeasonalPlayingTimeInput()
    if performance is None:
        performance = SeasonalPerformanceInput()
    if environment is None:
        environment = SeasonalEnvironmentInput()

    player = career.player
    season_number = career.current_season_number

    start_year = career.start_date.year + (season_number - 1)
    season_start_date = date(start_year, 7, 1)
    season_end_date = date(start_year + 1, 6, 30)

    starting_age = calculate_age(player.birth_date, season_start_date)
    ending_age = starting_age + 1

    starting_phase = calculate_career_phase(starting_age)
    ending_phase = calculate_career_phase(ending_age)

    starting_ca = current_ability(player)
    starting_ovr = position_ovr(player, player.primary_position)

    rng = get_sha256_rng(career.seed, player.id, season_number)

    budget = calculate_development_budget(
        player=player,
        starting_age=starting_age,
        playing_time=playing_time,
        performance=performance,
        environment=environment,
        rng=rng,
    )

    group_summary, attribute_changes = allocate_two_stage_development(player, budget)
    apply_decline_effects(player, starting_age, attribute_changes)
    apply_attribute_changes(player, attribute_changes)

    ending_ca = current_ability(player)
    player.current_ability = ending_ca
    ending_ovr = position_ovr(player, player.primary_position)

    if ending_ca > career.peak_ability or ending_ovr > career.peak_ovr:
        if ending_ca > career.peak_ability:
            career.peak_ability = ending_ca
        if ending_ovr > career.peak_ovr:
            career.peak_ovr = ending_ovr
        career.peak_age = ending_age
        career.peak_position = player.primary_position
        career.peak_club_id = career.current_club_id

    career.career_phase = ending_phase
    season_seed_str = f"{career.seed}:{player.id}:{season_number}"

    season = Season(
        season_number=season_number,
        season_label=career.current_season_label,
        start_date=season_start_date,
        end_date=season_end_date,
        player_id=player.id,
        club_id=career.current_club_id,
        starting_age=starting_age,
        ending_age=ending_age,
        starting_position=player.primary_position,
        ending_position=player.primary_position,
        starting_ability=starting_ca,
        ending_ability=ending_ca,
        starting_ovr=starting_ovr,
        ending_ovr=ending_ovr,
        career_phase_at_start=starting_phase,
        career_phase_at_end=ending_phase,
        playing_time_input=playing_time,
        performance_input=performance,
        environment_input=environment,
        development_budget=budget,
        development_summary=group_summary,
        attribute_changes=attribute_changes,
        season_seed=season_seed_str,
        is_completed=True,
    )

    snapshot = SeasonSnapshot(
        season_number=season_number,
        season_label=career.current_season_label,
        starting_age=starting_age,
        ending_age=ending_age,
        club_id=career.current_club_id,
        starting_position=player.primary_position,
        ending_position=player.primary_position,
        starting_ability=starting_ca,
        ending_ability=ending_ca,
        starting_ovr=starting_ovr,
        ending_ovr=ending_ovr,
        career_phase_at_start=starting_phase,
        career_phase_at_end=ending_phase,
        playing_time_input=playing_time,
        performance_input=performance,
        environment_input=environment,
        development_budget=budget,
        development_summary=group_summary,
        attribute_changes=attribute_changes,
        season_seed=season_seed_str,
    )

    career.seasons.append(season)
    career.snapshots.append(snapshot)

    career.current_season_number += 1
    next_start_year = start_year + 1
    career.current_season_label = f"{next_start_year}/{str(next_start_year + 1)[-2:]}"

    return season
