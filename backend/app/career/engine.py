import hashlib
import json
import random
from datetime import date
from pathlib import Path
from types import MappingProxyType
from typing import Any

from app.career.domain import (
    Career,
    CareerAdvanceResult,
    CareerPhase,
    CareerSession,
    CareerSessionNotification,
    CareerSessionStatus,
    CareerSetupRequest,
    MatchDrivenSeasonInput,
    Season,
    SeasonalEnvironmentInput,
    SeasonalPerformanceInput,
    SeasonalPlayingTimeInput,
    SeasonSnapshot,
)
from app.career.exceptions import (
    CareerCompletedException,
    CareerSimulationException,
    DecisionRequiredException,
    InvalidCareerStateException,
    InvalidDecisionOptionException,
)
from app.event.career_domain import CareerEvent, CareerRecord, EventCategory, EventSignificance
from app.event.career_engine import process_career_events
from app.event.decisions import Decision, DecisionOption, DecisionResult, DecisionResolutionType, resolve_decision
from app.event.domain import EventContext, EventType
from app.event.effects import apply_effects
from app.event.presentation_domain import CareerPresentation
from app.event.presentation_engine import build_career_presentation
from app.football.competition_engine import simulate_full_season
from app.match.aggregation import SeasonPerformance
from app.player.domain import DevelopmentProfile, Player, PlayerAttributes, PlayerState
from app.player.engine import current_ability, position_ovr


def _load_rules(filename: str) -> dict:
    path = Path(__file__).resolve().parents[2] / "data" / "rules" / filename
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return {}


_development_rules = _load_rules("player_development.json")
_attribute_rules = _load_rules("player_attributes.json")

BASE_RATE = _development_rules.get("base_rate", 4.0)
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

    if playing_time.playing_time_factor is not None:
        playing_time_factor = playing_time.playing_time_factor
    else:
        playing_time_factor = get_playing_time_factor(playing_time.minutes_played)

    facilities_mod = 1.0 + ((environment.facilities - 50.0) / 500.0)
    manager_mod = 1.0 + ((environment.manager_player_development - 50.0) / 500.0)
    environment_factor = facilities_mod * manager_mod

    prof = player.personality.get("professionalism", 50.0)
    professionalism_factor = 1.0 + ((prof - 50.0) / 625.0)

    if performance.performance_factor is not None:
        performance_factor = performance.performance_factor
    else:
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
        if current_val <= rule.get("max_val", rule.get("max", 100.0)):
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
        if not attr_subweights:
            continue

        sum_w = sum(attr_subweights.values()) or 1.0
        sum_w_sq = sum(w * w for w in attr_subweights.values()) or 1.0
        normalization = sum_w / sum_w_sq

        for attr_name, subweight in attr_subweights.items():
            if not hasattr(player.attributes, attr_name):
                continue
            delta_raw = group_budget * subweight * normalization
            current_val = getattr(player.attributes, attr_name)
            soft_cap_mult = get_soft_cap_multiplier(current_val)
            net_delta = delta_raw * soft_cap_mult
            stage2_attribute_changes[attr_name] = stage2_attribute_changes.get(attr_name, 0.0) + net_delta

    return stage1_group_budget, stage2_attribute_changes


def apply_decline_effects(player: Player, age: int, attribute_changes: dict[str, float]) -> None:
    start_age = DECLINE_RULES.get("start_age", 29)
    if age < start_age:
        return

    years_over = age - start_age + 1
    physical_attrs = set(DECLINE_RULES.get("physical_attributes", ["acceleration", "sprint_speed", "agility", "stamina", "jumping", "reactions"]))
    technical_attrs = set(DECLINE_RULES.get("technical_attributes", []))

    base_phys_rate = DECLINE_RULES.get("physical_rate", 0.15)
    base_tech_rate = DECLINE_RULES.get("technical_rate", 0.015)
    base_ment_rate = DECLINE_RULES.get("mental_rate", 0.0)

    phys_decline = base_phys_rate * (1.0 + 0.1 * years_over)
    tech_decline = base_tech_rate * (1.0 + 0.05 * years_over)
    ment_decline = base_ment_rate

    for attr_name in vars(player.attributes):
        if attr_name in physical_attrs:
            loss = phys_decline
        elif attr_name in technical_attrs:
            loss = tech_decline
        else:
            loss = ment_decline
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


def simulate_match_driven_season(
    career: Career,
    season_performance: SeasonPerformance,
    environment: SeasonalEnvironmentInput | None = None,
) -> Season:
    """Adapts a match-aggregated SeasonPerformance into Season inputs and executes simulate_season."""
    if environment is None:
        environment = SeasonalEnvironmentInput()

    driven_input = MatchDrivenSeasonInput(
        season_performance=season_performance,
        environment_input=environment,
    )

    playing_time_input = SeasonalPlayingTimeInput(
        minutes_played=season_performance.minutes_played,
        playing_time_factor=driven_input.playing_time_factor,
    )
    performance_input = SeasonalPerformanceInput(
        average_rating=season_performance.average_rating,
        performance_factor=driven_input.performance_factor,
    )

    return simulate_season(
        career=career,
        playing_time=playing_time_input,
        performance=performance_input,
        environment=environment,
    )


def _generate_default_player(request: CareerSetupRequest) -> Player:
    attrs = PlayerAttributes(
        acceleration=75.0, sprint_speed=76.0, finishing=78.0, shot_power=75.0,
        long_shots=70.0, volleys=68.0, penalties=72.0, vision=70.0, short_passing=72.0,
        long_passing=68.0, crossing=65.0, curve=66.0, agility=74.0, balance=72.0,
        ball_control=76.0, dribbling=75.0, reactions=74.0, defensive_awareness=40.0,
        standing_tackle=38.0, interceptions=35.0, heading=68.0, strength=72.0,
        stamina=74.0, jumping=70.0, aggression=65.0, decision_making=72.0, composure=74.0,
        creativity=70.0, positioning=75.0, concentration=70.0, work_rate=72.0, leadership=65.0,
        diving=10.0, handling=10.0, kicking=10.0, reflexes=10.0, speed=10.0, goalkeeper_positioning=10.0,
    )

    player_id = f"p_{hashlib.sha256(request.player_name.encode('utf-8')).hexdigest()[:12]}"
    names = request.player_name.strip().split(" ", 1)
    first_name = names[0]
    surname = names[1] if len(names) > 1 else ""
    pos = request.position.upper() if request.position else "ST"

    return Player(
        id=player_id,
        name=first_name,
        surname=surname,
        nationality=request.nationality,
        birth_date=date(2005, 5, 15),
        height=182.0,
        weight=75.0,
        preferred_foot="Right",
        primary_position=pos,
        secondary_positions=(),
        attributes=attrs,
        current_ability=73.0,
        potential=88.0,
        development_rate=75.0,
        development_profile=DevelopmentProfile.BALANCED,
        role_familiarity={pos: 90.0},
        traits=("FINESSE_SHOT",),
        personality={"ambition": 80.0, "professionalism": 85.0},
        state=PlayerState(),
        archetype="BALANCED",
    )


class CareerSessionEngine:
    """
    Pure orchestrator for Phase 14 career session progression.
    Integrates Phase 8-13 engines atomically and deterministically.
    """

    @staticmethod
    def create_session(request: CareerSetupRequest) -> CareerSession:
        player = _generate_default_player(request)
        career_id = f"cs_{hashlib.sha256(f'{player.id}:{request.seed}'.encode('utf-8')).hexdigest()[:16]}"
        start_d = date(2026, 7, 1)

        initial_season = Season(
            season_number=1,
            season_label="2026/27",
            start_date=start_d,
            end_date=date(2027, 6, 30),
            player_id=player.id,
            club_id=1,
            starting_age=21,
            ending_age=21,
            starting_position=player.primary_position,
            ending_position=player.primary_position,
            starting_ability=player.current_ability,
            ending_ability=player.current_ability,
            starting_ovr=75.0,
            ending_ovr=75.0,
            career_phase_at_start=CareerPhase.EARLY_PRO,
            career_phase_at_end=CareerPhase.EARLY_PRO,
            playing_time_input=SeasonalPlayingTimeInput(minutes_played=1200),
            performance_input=SeasonalPerformanceInput(average_rating=7.1),
            environment_input=SeasonalEnvironmentInput(),
            development_budget=3.5,
            development_summary={"shooting": 1.2, "pace": 1.0, "dribbling": 0.8},
            attribute_changes={"shooting": 1.2, "pace": 1.0},
            season_seed=f"{request.seed}:s1",
            is_completed=False,
        )

        career = Career(
            id=career_id,
            player=player,
            start_date=start_d,
            end_date=None,
            current_season_number=1,
            current_season_label="2026/27",
            current_club_id=1,
            career_phase=CareerPhase.EARLY_PRO,
            peak_ability=player.current_ability,
            peak_ovr=75.0,
            peak_age=21,
            peak_position=player.primary_position,
            peak_club_id=1,
            seasons=[initial_season],
            snapshots=[],
            seed=request.seed,
        )

        initial_record = CareerRecord(player_id=player.id)
        # Create initial debut event
        debut_raw_key = f"{player.id}:initial_debut:1"
        debut_ev_id = f"ce_{hashlib.sha256(debut_raw_key.encode('utf-8')).hexdigest()[:16]}"
        initial_event = CareerEvent(
            event_id=debut_ev_id,
            source_event_id="evt_debut_001",
            player_id=player.id,
            season="2026/27",
            sequence=1,
            event_type=EventType.PLAYER,
            category=EventCategory.DEBUT,
            significance=EventSignificance.MAJOR,
            summary_data=MappingProxyType({"title": "Professional Debut", "description": f"{player.name} {player.surname} made his professional debut."}),
            state_changes=MappingProxyType({"confidence": 10.0}),
            participants=(player.id,),
            clubs=("1",),
            competitions=("comp_1",),
            tags=("debut", "first_team"),
        )

        record_with_debut = process_career_events(initial_record, (initial_event,))
        presentation = build_career_presentation(record_with_debut, career)

        welcome_notification = CareerSessionNotification(
            id=f"notif_{hashlib.sha256(f'{career_id}:welcome'.encode('utf-8')).hexdigest()[:12]}",
            title="Career Started",
            message=f"Career created for {player.name} {player.surname} at starting club.",
            type="INFO",
            created_at_season="2026/27",
        )

        return CareerSession(
            career_id=career_id,
            player_id=player.id,
            current_season="2026/27",
            simulation_position=1,
            status=CareerSessionStatus.ACTIVE,
            career=career,
            career_record=record_with_debut,
            presentation=presentation,
            pending_decision=None,
            pending_events=(initial_event,),
            notifications=(welcome_notification,),
            last_processed_event_id=debut_ev_id,
            seed=request.seed,
        )

    @staticmethod
    def advance_season(session: CareerSession) -> CareerAdvanceResult:
        if session.status == CareerSessionStatus.COMPLETED:
            raise CareerCompletedException(session.career_id)
        if session.status == CareerSessionStatus.DECISION_PENDING and session.pending_decision is not None:
            raise DecisionRequiredException(
                session.career_id,
                session.pending_decision.id,
                {"details": "Must resolve decision before advancing career."},
            )

        prev_season = session.current_season
        next_season_num = session.career.current_season_number + 1
        if next_season_num > 15:
            # Mark career completed
            completed_career = Career(
                id=session.career.id,
                player=session.career.player,
                start_date=session.career.start_date,
                end_date=date(2026 + next_season_num - 1, 6, 30),
                current_season_number=session.career.current_season_number,
                current_season_label=session.career.current_season_label,
                current_club_id=session.career.current_club_id,
                career_phase=CareerPhase.VETERAN,
                peak_ability=session.career.peak_ability,
                peak_ovr=session.career.peak_ovr,
                peak_age=session.career.peak_age,
                peak_position=session.career.peak_position,
                peak_club_id=session.career.current_club_id,
                seasons=session.career.seasons,
                snapshots=session.career.snapshots,
                seed=session.seed,
            )
            # Create retirement event
            ret_raw_key = f"{session.player_id}:retirement:{next_season_num}"
            ret_ev_id = f"ce_{hashlib.sha256(ret_raw_key.encode('utf-8')).hexdigest()[:16]}"
            ret_event = CareerEvent(
                event_id=ret_ev_id,
                source_event_id=f"evt_retire_{next_season_num}",
                player_id=session.player_id,
                season=prev_season,
                sequence=session.career_record.last_sequence + 1,
                event_type=EventType.PLAYER,
                category=EventCategory.RETIREMENT,
                significance=EventSignificance.LEGENDARY,
                summary_data=MappingProxyType({"title": "Career Retirement", "description": "Retired from professional football."}),
                state_changes=MappingProxyType({"status": "RETIRED"}),
                participants=(session.player_id,),
                clubs=("1",),
                competitions=(),
                tags=("retirement", "legendary"),
            )
            new_record = process_career_events(session.career_record, (ret_event,))
            pres = build_career_presentation(new_record, completed_career)
            notif = CareerSessionNotification(
                id=f"notif_{hashlib.sha256(f'{session.career_id}:retire'.encode('utf-8')).hexdigest()[:12]}",
                title="Career Completed",
                message="You have completed a legendary 15-year career!",
                type="SUCCESS",
                created_at_season=prev_season,
            )
            return CareerAdvanceResult(
                career_id=session.career_id,
                previous_season=prev_season,
                current_season=prev_season,
                status=CareerSessionStatus.COMPLETED,
                processed_events=(ret_event,),
                new_notifications=(notif,),
                pending_decision=None,
                presentation=pres,
                updated_career=completed_career,
                success=True,
            )

        start_yr = 2026 + next_season_num - 1
        end_yr = start_yr + 1
        next_season_label = f"{start_yr}/{str(end_yr)[2:]}"
        age = 21 + (next_season_num - 1)

        # Calculate growth / performance
        ca_boost = 1.5 if age <= 27 else (-1.0 if age >= 31 else 0.2)
        new_ca = round(max(50.0, min(99.0, session.career.player.current_ability + ca_boost)), 1)
        new_ovr = round(new_ca + 2.0, 1)

        # Check for Decision trigger on season 3 or 7
        trigger_decision = None
        if next_season_num in (3, 7):
            dec_id = f"dec_contract_{session.career_id}_{next_season_num}"
            opt1 = DecisionOption(
                id="opt_sign_extension",
                label="Sign Extension",
                description="Secure long-term future at the club.",
                effects=(),
            )
            opt2 = DecisionOption(
                id="opt_explore_market",
                label="Explore Transfer Market",
                description="Wait for better offers from top European clubs.",
                effects=(),
            )
            trigger_decision = Decision(
                id=dec_id,
                prompt=f"Your manager has offered a contract extension for season {next_season_label}.",
                options=(opt1, opt2),
                resolution_type=DecisionResolutionType.EXPLICIT,
                default_option_id=opt1.id,
                metadata=MappingProxyType({"season": next_season_label}),
            )

        # Update player object
        updated_player = Player(
            id=session.career.player.id,
            name=session.career.player.name,
            surname=session.career.player.surname,
            nationality=session.career.player.nationality,
            birth_date=session.career.player.birth_date,
            height=session.career.player.height,
            weight=session.career.player.weight,
            preferred_foot=session.career.player.preferred_foot,
            primary_position=session.career.player.primary_position,
            secondary_positions=session.career.player.secondary_positions,
            attributes=session.career.player.attributes,
            current_ability=new_ca,
            potential=session.career.player.potential,
            development_rate=session.career.player.development_rate,
            development_profile=session.career.player.development_profile,
            role_familiarity=session.career.player.role_familiarity,
            traits=session.career.player.traits,
            personality=session.career.player.personality,
            state=session.career.player.state,
            archetype=session.career.player.archetype,
        )

        club_name_str = str(session.career.current_club_id)
        world_rules = _load_rules("world.json")
        detected_league_code = "ESP1"
        for c_item in world_rules.get("clubs", []):
            if c_item.get("name") == club_name_str or str(c_item.get("id")) == club_name_str:
                detected_league_code = c_item.get("league_code", "ESP1")
                club_name_str = c_item.get("name", club_name_str)
                break
        if club_name_str.startswith("club_") or club_name_str.isdigit():
            club_name_str = "Real Madrid"

        season_summary = simulate_full_season(
            season_number=next_season_num,
            season_label=next_season_label,
            player_id=session.player_id,
            player_name=f"{updated_player.name} {updated_player.surname}".strip(),
            player_age=age,
            player_nationality=updated_player.nationality,
            player_position=updated_player.primary_position,
            player_ovr=new_ovr,
            club_name=club_name_str,
            league_code=detected_league_code,
            seed=f"{session.seed}:football:{next_season_num}",
        )

        st = season_summary.statistics
        ev_type = EventCategory.BREAKTHROUGH if ca_boost > 1.0 else (EventCategory.FORM_CHANGE if ca_boost < 0 else EventCategory.PERFORMANCE)
        season_ev_raw_key = f"{session.player_id}:season_{next_season_num}"
        season_ev_id = f"ce_{hashlib.sha256(season_ev_raw_key.encode('utf-8')).hexdigest()[:16]}"
        season_event = CareerEvent(
            event_id=season_ev_id,
            source_event_id=f"evt_season_{next_season_num}",
            player_id=session.player_id,
            season=next_season_label,
            sequence=session.career_record.last_sequence + 1,
            event_type=EventType.PLAYER,
            category=ev_type,
            significance=EventSignificance.MODERATE if ca_boost > 1.0 else EventSignificance.MINOR,
            summary_data=MappingProxyType({
                "title": f"Season {next_season_label} Summary",
                "description": f"Scored {st.goals} goals & {st.assists} assists in {st.appearances} matches with {club_name_str}. Finished {season_summary.league_position}th in league.",
            }),
            state_changes=MappingProxyType({
                "current_ability": new_ca,
                "ovr": new_ovr,
                "goals": float(st.goals),
                "assists": float(st.assists),
                "appearances": float(st.appearances),
            }),
            participants=(session.player_id,),
            clubs=(club_name_str,),
            competitions=(season_summary.league_code,),
            tags=("season_progress", "football_stats"),
        )

        new_events = [season_event]

        # Add Trophy Events
        for tr in season_summary.trophies:
            tr_ev_id = f"ce_{hashlib.sha256(f'{session.player_id}:tr:{tr.id}'.encode('utf-8')).hexdigest()[:16]}"
            tr_ev = CareerEvent(
                event_id=tr_ev_id,
                source_event_id=tr.id,
                player_id=session.player_id,
                season=next_season_label,
                sequence=session.career_record.last_sequence + len(new_events) + 1,
                event_type=EventType.COMPETITION,
                category=EventCategory.TROPHY,
                significance=EventSignificance.MAJOR,
                summary_data=MappingProxyType({"title": f"Trophy: {tr.competition_name}", "description": f"Won the {tr.competition_name} with {club_name_str}!"}),
                state_changes=MappingProxyType({"trophy": 1.0}),
                participants=(session.player_id,),
                clubs=(club_name_str,),
                competitions=(tr.competition_id,),
                tags=("trophy", "champion"),
            )
            new_events.append(tr_ev)

        # Add Award Events
        for aw in season_summary.awards:
            aw_ev_id = f"ce_{hashlib.sha256(f'{session.player_id}:aw:{aw.id}'.encode('utf-8')).hexdigest()[:16]}"
            aw_ev = CareerEvent(
                event_id=aw_ev_id,
                source_event_id=aw.id,
                player_id=session.player_id,
                season=next_season_label,
                sequence=session.career_record.last_sequence + len(new_events) + 1,
                event_type=EventType.PLAYER,
                category=EventCategory.AWARD,
                significance=EventSignificance.MAJOR,
                summary_data=MappingProxyType({"title": f"Award: {aw.name}", "description": aw.description}),
                state_changes=MappingProxyType({"award": 1.0}),
                participants=(session.player_id,),
                clubs=(club_name_str,),
                competitions=(),
                tags=("award", "individual_honor"),
            )
            new_events.append(aw_ev)

        # Add International Call-up Event
        if season_summary.international_call_up and season_summary.international_call_up.caps > 0:
            icu = season_summary.international_call_up
            int_ev_id = f"ce_{hashlib.sha256(f'{session.player_id}:int:{icu.id}'.encode('utf-8')).hexdigest()[:16]}"
            int_ev = CareerEvent(
                event_id=int_ev_id,
                source_event_id=icu.id,
                player_id=session.player_id,
                season=next_season_label,
                sequence=session.career_record.last_sequence + len(new_events) + 1,
                event_type=EventType.PLAYER,
                category=EventCategory.INTERNATIONAL,
                significance=EventSignificance.MAJOR,
                summary_data=MappingProxyType({"title": f"International Debut & Caps", "description": f"Earned {icu.caps} caps and {icu.goals} goals for {icu.country_code}."}),
                state_changes=MappingProxyType({"caps": float(icu.caps), "intl_goals": float(icu.goals)}),
                participants=(session.player_id,),
                clubs=(),
                competitions=("INTERNATIONAL",),
                tags=("international", "national_team"),
            )
            new_events.append(int_ev)

        # Add Injury Event
        for inj in season_summary.injuries:
            inj_ev_id = f"ce_{hashlib.sha256(f'{session.player_id}:inj:{inj.id}'.encode('utf-8')).hexdigest()[:16]}"
            inj_ev = CareerEvent(
                event_id=inj_ev_id,
                source_event_id=inj.id,
                player_id=session.player_id,
                season=next_season_label,
                sequence=session.career_record.last_sequence + len(new_events) + 1,
                event_type=EventType.PLAYER,
                category=EventCategory.INJURY,
                significance=EventSignificance.MAJOR if inj.category in ("MAJOR", "SEASON_ENDING") else EventSignificance.MINOR,
                summary_data=MappingProxyType({"title": f"Injury: {inj.name}", "description": f"Suffered {inj.name} ({inj.category.value}). Missed {inj.matches_missed} matches."}),
                state_changes=MappingProxyType({"matches_missed": float(inj.matches_missed)}),
                participants=(session.player_id,),
                clubs=(club_name_str,),
                competitions=(),
                tags=("injury", "setback"),
            )
            new_events.append(inj_ev)

        updated_record = process_career_events(session.career_record, tuple(new_events))

        phase = CareerPhase.PRIME if 24 <= age <= 28 else (CareerPhase.LATE_PRIME if 29 <= age <= 31 else (CareerPhase.DECLINE if age >= 32 else CareerPhase.DEVELOPMENT))
        peak_ca = max(session.career.peak_ability, new_ca)
        peak_ovr = max(session.career.peak_ovr, new_ovr)

        new_season_obj = Season(
            season_number=next_season_num,
            season_label=next_season_label,
            start_date=date(start_yr, 7, 1),
            end_date=date(end_yr, 6, 30),
            player_id=session.player_id,
            club_id=club_name_str,
            starting_age=age,
            ending_age=age,
            starting_position=updated_player.primary_position,
            ending_position=updated_player.primary_position,
            starting_ability=session.career.player.current_ability,
            ending_ability=new_ca,
            starting_ovr=session.career.peak_ovr,
            ending_ovr=new_ovr,
            career_phase_at_start=session.career.career_phase,
            career_phase_at_end=phase,
            playing_time_input=SeasonalPlayingTimeInput(minutes_played=st.minutes),
            performance_input=SeasonalPerformanceInput(average_rating=st.average_rating),
            environment_input=SeasonalEnvironmentInput(),
            development_budget=3.0,
            development_summary={"shooting": 0.8, "pace": 0.5},
            attribute_changes={"shooting": 0.8, "pace": 0.5},
            season_seed=f"{session.seed}:s{next_season_num}",
            is_completed=True,
            season_summary=season_summary,
        )

        updated_career = Career(
            id=session.career.id,
            player=updated_player,
            start_date=session.career.start_date,
            end_date=None,
            current_season_number=next_season_num,
            current_season_label=next_season_label,
            current_club_id=club_name_str,
            career_phase=phase,
            peak_ability=peak_ca,
            peak_ovr=peak_ovr,
            peak_age=age if new_ca >= session.career.peak_ability else session.career.peak_age,
            peak_position=updated_player.primary_position,
            peak_club_id=club_name_str,
            seasons=session.career.seasons + [new_season_obj],
            snapshots=session.career.snapshots,
            seed=session.seed,
        )

        presentation = build_career_presentation(updated_record, updated_career)

        notif = CareerSessionNotification(
            id=f"notif_{hashlib.sha256(f'{session.career_id}:{next_season_num}'.encode('utf-8')).hexdigest()[:12]}",
            title=f"Advanced to {next_season_label}",
            message=f"Season {next_season_label} completed. Rating now {new_ovr} OVR.",
            type="SUCCESS" if ca_boost > 0 else "WARNING",
            created_at_season=next_season_label,
        )

        new_status = CareerSessionStatus.DECISION_PENDING if trigger_decision else CareerSessionStatus.ACTIVE

        return CareerAdvanceResult(
            career_id=session.career_id,
            previous_season=prev_season,
            current_season=next_season_label,
            status=new_status,
            processed_events=tuple(new_events),
            new_notifications=(notif,),
            pending_decision=trigger_decision,
            presentation=presentation,
            updated_career=updated_career,
            updated_record=updated_record,
            success=True,
        )

    @staticmethod
    def resolve_session_decision(session: CareerSession, option_id: str) -> tuple[CareerSession, CareerEvent]:
        if session.pending_decision is None:
            raise InvalidCareerStateException("No decision is pending for this career session.")

        decision = session.pending_decision
        selected_opt = next((opt for opt in decision.options if opt.id == option_id), None)
        if selected_opt is None:
            raise InvalidDecisionOptionException(decision.id, option_id)

        context = EventContext(
            player_id=session.player_id,
            club_id=str(session.career.current_club_id),
            season=session.current_season,
        )

        dec_result = resolve_decision(
            decision=decision,
            context=context,
            seed=session.seed,
            explicit_option_id=option_id,
            resolution_type=DecisionResolutionType.EXPLICIT,
        )

        # Apply effects
        if selected_opt.effects:
            apply_effects(session.career, selected_opt.effects, context, event_id=decision.id)

        # Record decision career event
        dec_ev_raw_key = f"{session.player_id}:dec_{decision.id}:{option_id}"
        dec_ev_id = f"ce_{hashlib.sha256(dec_ev_raw_key.encode('utf-8')).hexdigest()[:16]}"
        dec_event = CareerEvent(
            event_id=dec_ev_id,
            source_event_id=decision.id,
            player_id=session.player_id,
            season=session.current_season,
            sequence=session.career_record.last_sequence + 1,
            event_type=EventType.PLAYER,
            category=EventCategory.DECISION,
            significance=EventSignificance.MAJOR,
            summary_data=MappingProxyType({
                "title": f"Decision Resolved",
                "description": f"Resolved decision: {selected_opt.label}",
                "selected_option_id": selected_opt.id,
                "selected_option_label": selected_opt.label,
            }),
            state_changes=MappingProxyType({"decision_resolved": 1.0}),
            participants=(session.player_id,),
            clubs=(str(session.career.current_club_id),),
            competitions=(),
            tags=("decision", "user_choice"),
        )

        updated_record = process_career_events(session.career_record, (dec_event,))
        updated_presentation = build_career_presentation(updated_record, session.career)

        decision_notif = CareerSessionNotification(
            id=f"notif_{hashlib.sha256(f'{session.career_id}:dec_{decision.id}'.encode('utf-8')).hexdigest()[:12]}",
            title="Decision Made",
            message=f"You chose: '{selected_opt.label}'. Consequences applied.",
            type="INFO",
            created_at_season=session.current_season,
        )

        updated_session = CareerSession(
            career_id=session.career_id,
            player_id=session.player_id,
            current_season=session.current_season,
            simulation_position=session.simulation_position,
            status=CareerSessionStatus.ACTIVE,
            career=session.career,
            career_record=updated_record,
            presentation=updated_presentation,
            pending_decision=None,
            pending_events=session.pending_events + (dec_event,),
            notifications=session.notifications + (decision_notif,),
            last_processed_event_id=dec_ev_id,
            seed=session.seed,
        )

        return updated_session, dec_event

    @staticmethod
    def resolve_transfer_choice(session: CareerSession, offer_id: str, action: str) -> CareerSession:
        if action.upper() == "STAY":
            stay_ev_raw_key = f"{session.player_id}:transfer_stay:{session.current_season}"
            stay_ev_id = f"ce_{hashlib.sha256(stay_ev_raw_key.encode('utf-8')).hexdigest()[:16]}"
            stay_event = CareerEvent(
                event_id=stay_ev_id,
                source_event_id=f"tr_stay_{session.current_season}",
                player_id=session.player_id,
                season=session.current_season,
                sequence=session.career_record.last_sequence + 1,
                event_type=EventType.PLAYER,
                category=EventCategory.TRANSFER,
                significance=EventSignificance.MINOR,
                summary_data=MappingProxyType({
                    "title": "Decided to Stay",
                    "description": f"Rejected incoming transfer offers to remain focused at {session.career.current_club_id}.",
                }),
                state_changes=MappingProxyType({"transfer_stay": 1.0}),
                participants=(session.player_id,),
                clubs=(str(session.career.current_club_id),),
                competitions=(),
                tags=("transfer", "stay"),
            )
            updated_record = process_career_events(session.career_record, (stay_event,))
            pres = build_career_presentation(updated_record, session.career)
            notif = CareerSessionNotification(
                id=f"notif_{hashlib.sha256(f'{session.career_id}:stay'.encode('utf-8')).hexdigest()[:12]}",
                title="Transfer Decision",
                message="You decided to remain at your current club.",
                type="INFO",
                created_at_season=session.current_season,
            )
            return CareerSession(
                career_id=session.career_id,
                player_id=session.player_id,
                current_season=session.current_season,
                simulation_position=session.simulation_position,
                status=CareerSessionStatus.ACTIVE,
                career=session.career,
                career_record=updated_record,
                presentation=pres,
                pending_decision=None,
                pending_events=session.pending_events + (stay_event,),
                notifications=session.notifications + (notif,),
                last_processed_event_id=stay_ev_id,
                seed=session.seed,
            )

        # Generating offers to match offer_id
        world_rules = _load_rules("world.json")
        world_clubs = world_rules.get("clubs", [])
        world_leagues = world_rules.get("leagues", [])
        rep = calculate_reputation(
            player_ovr=session.career.player.current_ability,
            age=21 + session.career.current_season_number - 1,
            club_prestige=80.0,
        )
        offers_res = generate_transfer_offers(
            player_id=session.player_id,
            player_ovr=session.career.player.current_ability,
            age=21 + session.career.current_season_number - 1,
            position=session.career.player.primary_position,
            current_club_id=str(session.career.current_club_id),
            reputation=rep,
            season_number=session.career.current_season_number,
            seed=session.seed,
            world_clubs=world_clubs,
            world_leagues=world_leagues,
        )

        matched_offer = next((o for o in offers_res.available_offers if o.offer_id == offer_id), None)
        if not matched_offer and offers_res.available_offers:
            matched_offer = offers_res.available_offers[0]

        if not matched_offer:
            raise InvalidCareerStateException("Transfer offer not found.")

        if action.upper() == "REJECT":
            rej_ev_raw_key = f"{session.player_id}:rej_{matched_offer.offer_id}"
            rej_ev_id = f"ce_{hashlib.sha256(rej_ev_raw_key.encode('utf-8')).hexdigest()[:16]}"
            rej_event = CareerEvent(
                event_id=rej_ev_id,
                source_event_id=matched_offer.offer_id,
                player_id=session.player_id,
                season=session.current_season,
                sequence=session.career_record.last_sequence + 1,
                event_type=EventType.PLAYER,
                category=EventCategory.TRANSFER,
                significance=EventSignificance.MINOR,
                summary_data=MappingProxyType({
                    "title": f"Offer Rejected: {matched_offer.destination_club_name}",
                    "description": f"Turned down offer from {matched_offer.destination_club_name}.",
                }),
                state_changes=MappingProxyType({"transfer_reject": 1.0}),
                participants=(session.player_id,),
                clubs=(matched_offer.destination_club_name,),
                competitions=(),
                tags=("transfer", "rejected"),
            )
            updated_record = process_career_events(session.career_record, (rej_event,))
            pres = build_career_presentation(updated_record, session.career)
            notif = CareerSessionNotification(
                id=f"notif_{hashlib.sha256(f'{session.career_id}:rej_{matched_offer.offer_id}'.encode('utf-8')).hexdigest()[:12]}",
                title="Transfer Rejected",
                message=f"Rejected transfer offer from {matched_offer.destination_club_name}.",
                type="INFO",
                created_at_season=session.current_season,
            )
            return CareerSession(
                career_id=session.career_id,
                player_id=session.player_id,
                current_season=session.current_season,
                simulation_position=session.simulation_position,
                status=CareerSessionStatus.ACTIVE,
                career=session.career,
                career_record=updated_record,
                presentation=pres,
                pending_decision=None,
                pending_events=session.pending_events + (rej_event,),
                notifications=session.notifications + (notif,),
                last_processed_event_id=rej_ev_id,
                seed=session.seed,
            )

        # ACCEPT ACTION
        new_club_name = matched_offer.destination_club_name
        updated_career = Career(
            id=session.career.id,
            player=session.career.player,
            start_date=session.career.start_date,
            end_date=session.career.end_date,
            current_season_number=session.career.current_season_number,
            current_season_label=session.career.current_season_label,
            current_club_id=new_club_name,
            career_phase=session.career.career_phase,
            peak_ability=session.career.peak_ability,
            peak_ovr=session.career.peak_ovr,
            peak_age=session.career.peak_age,
            peak_position=session.career.peak_position,
            peak_club_id=new_club_name if session.career.player.current_ability >= session.career.peak_ability else session.career.peak_club_id,
            seasons=session.career.seasons,
            snapshots=session.career.snapshots,
            seed=session.seed,
        )

        acc_ev_raw_key = f"{session.player_id}:acc_{matched_offer.offer_id}"
        acc_ev_id = f"ce_{hashlib.sha256(acc_ev_raw_key.encode('utf-8')).hexdigest()[:16]}"
        acc_event = CareerEvent(
            event_id=acc_ev_id,
            source_event_id=matched_offer.offer_id,
            player_id=session.player_id,
            season=session.current_season,
            sequence=session.career_record.last_sequence + 1,
            event_type=EventType.PLAYER,
            category=EventCategory.TRANSFER,
            significance=EventSignificance.MAJOR,
            summary_data=MappingProxyType({
                "title": f"Transfer Complete: {new_club_name}",
                "description": f"Transferred to {new_club_name} ({matched_offer.league_name}) for €{matched_offer.transfer_fee:,}.",
            }),
            state_changes=MappingProxyType({"transfer_accepted": 1.0}),
            participants=(session.player_id,),
            clubs=(new_club_name,),
            competitions=(matched_offer.league_code,),
            tags=("transfer", "accepted", "new_club"),
        )

        updated_record = process_career_events(session.career_record, (acc_event,))
        pres = build_career_presentation(updated_record, updated_career)
        notif = CareerSessionNotification(
            id=f"notif_{hashlib.sha256(f'{session.career_id}:acc_{matched_offer.offer_id}'.encode('utf-8')).hexdigest()[:12]}",
            title="Transfer Complete",
            message=f"Joined {new_club_name}! Contract signed.",
            type="SUCCESS",
            created_at_season=session.current_season,
        )

        return CareerSession(
            career_id=session.career_id,
            player_id=session.player_id,
            current_season=session.current_season,
            simulation_position=session.simulation_position,
            status=CareerSessionStatus.ACTIVE,
            career=updated_career,
            career_record=updated_record,
            presentation=pres,
            pending_decision=None,
            pending_events=session.pending_events + (acc_event,),
            notifications=session.notifications + (notif,),
            last_processed_event_id=acc_ev_id,
            seed=session.seed,
        )
