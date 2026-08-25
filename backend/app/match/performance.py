from dataclasses import dataclass
import hashlib
import math
import random

from app.match.domain import (
    MatchContext,
    MatchEvent,
    MatchEventType,
    PlayerMatchPerformance,
    SimulationMode,
)
from app.match.lineup import Lineup, LineupSlot, evaluate_player_for_slot
from app.match.resolution import MatchResolutionState
from app.player.domain import Player


def get_sha256_player_rng(seed: str, match_id: str, player_id: str, stage: str = "perf") -> random.Random:
    seed_material = f"{seed}:{match_id}:{player_id}:{stage}"
    seed_hash = hashlib.sha256(seed_material.encode("utf-8")).hexdigest()
    seed_int = int(seed_hash[:16], 16)
    return random.Random(seed_int)


def calculate_latent_influence(
    player: Player,
    slot_position: str,
    role_effectiveness: float,
    match_importance: float,
    rng: random.Random,
) -> float:
    role_eff_contrib = role_effectiveness * 0.40
    form_contrib = player.state.form * 0.20
    fitness_contrib = player.state.fitness * 0.15
    state_avg = ((player.state.confidence + player.state.morale) / 2.0) * 0.15

    var = rng.uniform(-4.0, 4.0)
    if "BIG_GAME_PLAYER" in player.traits and match_importance >= 75.0:
        var += rng.uniform(2.0, 5.0)

    influence = role_eff_contrib + form_contrib + fitness_contrib + state_avg + var
    return max(0.0, min(100.0, influence))


def distribute_chance_shares(
    lineup_slots: list[LineupSlot],
    latent_influences: dict[str, float],
    rng: random.Random,
) -> dict[str, float]:
    base_pos_weights = {
        "ST": 32.0,
        "LW": 22.0,
        "RW": 18.0,
        "CAM": 15.0,
        "AM": 15.0,
        "LM": 14.0,
        "RM": 14.0,
        "CM": 8.0,
        "DM": 4.0,
        "LB": 3.0,
        "RB": 3.0,
        "LWB": 4.0,
        "RWB": 4.0,
        "CB": 2.0,
        "GK": 0.1,
    }

    raw_shares: dict[str, float] = {}
    for slot in lineup_slots:
        p = slot.player
        pos = slot.slot_position
        base_w = base_pos_weights.get(pos, 5.0)

        finishing = p.attributes.finishing
        positioning = p.attributes.positioning
        inf = latent_influences.get(p.id, 50.0)

        weight = base_w * (finishing / 50.0) * (positioning / 50.0) * (inf / 50.0)

        if "RAPID" in p.traits:
            weight *= 1.10
        if "AERIAL" in p.traits and pos in ("ST", "CB"):
            weight *= 1.05

        raw_shares[p.id] = weight

    total_weight = sum(raw_shares.values()) or 1.0
    return {pid: w / total_weight for pid, w in raw_shares.items()}


def allocate_player_shots(
    lineup_slots: list[LineupSlot],
    team_shots: int,
    team_shots_on_target: int,
    chance_shares: dict[str, float],
    rng: random.Random,
) -> dict[str, tuple[int, int]]:
    player_shots: dict[str, int] = {slot.player.id: 0 for slot in lineup_slots}
    player_sot: dict[str, int] = {slot.player.id: 0 for slot in lineup_slots}

    if team_shots <= 0 or not lineup_slots:
        return {slot.player.id: (0, 0) for slot in lineup_slots}

    # Deterministic Hare-Niemeyer / Largest Remainder shot allocation
    exact_shots = {pid: chance_shares.get(pid, 0.0) * team_shots for pid in player_shots}
    floor_shots = {pid: int(math.floor(val)) for pid, val in exact_shots.items()}
    remainders = {pid: exact_shots[pid] - floor_shots[pid] for pid in player_shots}

    allocated_sum = sum(floor_shots.values())
    unallocated = team_shots - allocated_sum

    sorted_pids = sorted(player_shots.keys(), key=lambda pid: (-remainders[pid], -chance_shares.get(pid, 0.0), pid))
    for i in range(unallocated):
        pid = sorted_pids[i % len(sorted_pids)]
        floor_shots[pid] += 1

    player_shots = floor_shots

    # Allocate shots_on_target among players who have shots
    shooting_pids = [pid for pid in player_shots if player_shots[pid] > 0]
    if team_shots_on_target > 0 and shooting_pids:
        sot_weights = {}
        for slot in lineup_slots:
            pid = slot.player.id
            if pid in shooting_pids:
                sot_weights[pid] = player_shots[pid] * (slot.player.attributes.finishing / 50.0)

        tot_sot_w = sum(sot_weights.values()) or 1.0
        exact_sot = {pid: (sot_weights.get(pid, 0.0) / tot_sot_w) * team_shots_on_target for pid in shooting_pids}
        floor_sot = {pid: min(player_shots[pid], int(math.floor(exact_sot[pid]))) for pid in shooting_pids}
        remainders_sot = {pid: exact_sot[pid] - floor_sot[pid] for pid in shooting_pids}

        unallocated_sot = team_shots_on_target - sum(floor_sot.values())
        sorted_sot_pids = sorted(shooting_pids, key=lambda pid: (-remainders_sot[pid], -sot_weights.get(pid, 0.0), pid))

        idx = 0
        while unallocated_sot > 0 and idx < len(sorted_sot_pids) * 2:
            pid = sorted_sot_pids[idx % len(sorted_sot_pids)]
            if floor_sot[pid] < player_shots[pid]:
                floor_sot[pid] += 1
                unallocated_sot -= 1
            idx += 1

        for pid, sot_val in floor_sot.items():
            player_sot[pid] = sot_val

    result = {}
    for slot in lineup_slots:
        pid = slot.player.id
        s = player_shots.get(pid, 0)
        sot = min(s, player_sot.get(pid, 0))
        result[pid] = (s, sot)

    return result


def resolve_goal_conversions(
    lineup_slots: list[LineupSlot],
    team_score: int,
    player_shots: dict[str, tuple[int, int]],
    opponent_gk: Player | None,
    match_importance: float,
    rng: random.Random,
) -> dict[str, int]:
    player_goals: dict[str, int] = {slot.player.id: 0 for slot in lineup_slots}
    if team_score <= 0 or not lineup_slots:
        return player_goals

    # Data-driven positional conversion priority priors
    position_priors = {
        "ST": 1.35,
        "LW": 1.10,
        "RW": 1.10,
        "CAM": 1.00,
        "AM": 1.00,
        "LM": 0.85,
        "RM": 0.85,
        "CM": 0.70,
        "DM": 0.45,
        "CB": 0.20,
        "LB": 0.20,
        "RB": 0.20,
        "LWB": 0.25,
        "RWB": 0.25,
        "GK": 0.01,
    }

    # Filter candidate slots
    candidate_slots = [
        slot for slot in lineup_slots
        if player_shots.get(slot.player.id, (0, 0))[1] > 0
    ]
    if not candidate_slots:
        candidate_slots = [
            slot for slot in lineup_slots
            if player_shots.get(slot.player.id, (0, 0))[0] > 0
        ]
        if not candidate_slots:
            candidate_slots = lineup_slots

    base_scoring_weights: dict[str, float] = {}
    for slot in candidate_slots:
        p = slot.player
        shots, sot = player_shots.get(p.id, (0, 0))
        sot_effective = max(1, sot)

        pos_priority = position_priors.get(slot.slot_position, 0.70)
        weight = sot_effective * (p.attributes.finishing / 50.0) * (p.attributes.composure / 50.0) * pos_priority

        if "FINESSE_SHOT" in p.traits:
            weight *= 1.15
        if "COMPOSED" in p.traits:
            weight *= 1.10

        base_scoring_weights[p.id] = weight

    # Weighted stochastic sampling for goal allocation
    # Sample goal by goal, capping player goals at their shots on target (or max(1, sot))
    for _ in range(team_score):
        current_candidates = []
        current_weights = []

        for pid, base_w in base_scoring_weights.items():
            curr_goals = player_goals[pid]
            _, sot = player_shots.get(pid, (0, 0))
            max_allowed = max(1, sot)

            if curr_goals < max_allowed:
                # Diminishing returns factor 0.70^k for repeat goals
                eff_weight = base_w * (0.70 ** curr_goals)
                current_candidates.append(pid)
                current_weights.append(max(0.001, eff_weight))

        if not current_candidates:
            # Fallback if team_score exceeds total team SOT
            current_candidates = list(base_scoring_weights.keys())
            current_weights = [base_scoring_weights[pid] * (0.70 ** player_goals[pid]) for pid in current_candidates]

        # Sample 1 goalscorer deterministically using seeded RNG
        chosen_pid = rng.choices(current_candidates, weights=current_weights, k=1)[0]
        player_goals[chosen_pid] += 1

    return player_goals


def attribute_assists(
    lineup_slots: list[LineupSlot],
    team_goals: int,
    player_goals: dict[str, int],
    latent_influences: dict[str, float],
    rng: random.Random,
) -> dict[str, int]:
    player_assists: dict[str, int] = {slot.player.id: 0 for slot in lineup_slots}
    if team_goals <= 0 or len(lineup_slots) <= 1:
        return player_assists

    assist_position_priors = {
        "CAM": 1.35,
        "AM": 1.35,
        "LW": 1.25,
        "RW": 1.25,
        "LM": 1.20,
        "RM": 1.20,
        "CM": 1.10,
        "DM": 0.85,
        "ST": 0.60,
        "LB": 0.50,
        "RB": 0.50,
        "LWB": 0.60,
        "RWB": 0.60,
        "CB": 0.20,
        "GK": 0.05,
    }

    # Construct list of goalscorer PIDs per goal event
    goalscorer_pids = [pid for pid, g_cnt in player_goals.items() for _ in range(g_cnt)]

    # Process each goal event probabilistically (~75% assist rate per goal)
    for g_idx in range(team_goals):
        if rng.random() > 0.75:
            continue  # Goal unassisted

        goalscorer_pid = goalscorer_pids[g_idx] if g_idx < len(goalscorer_pids) else None

        # Eligible teammates (excluding the goalscorer for this goal)
        eligible_slots = [s for s in lineup_slots if s.player.id != goalscorer_pid]
        if not eligible_slots:
            continue

        candidate_pids = [s.player.id for s in eligible_slots]
        weights = []

        for slot in eligible_slots:
            p = slot.player
            pos = slot.slot_position
            pos_mod = assist_position_priors.get(pos, 0.80)

            vision = p.attributes.vision
            short_pass = p.attributes.short_passing
            creativity = p.attributes.creativity
            inf = latent_influences.get(p.id, 50.0)

            w = pos_mod * (vision / 50.0) * (short_pass / 50.0) * (creativity / 50.0) * (inf / 50.0)

            if "CREATIVE" in p.traits:
                w *= 1.20
            if "LONG_BALL" in p.traits:
                w *= 1.15

            weights.append(max(0.001, w))

        # Sample 1 assist provider deterministically
        chosen_assister = rng.choices(candidate_pids, weights=weights, k=1)[0]
        player_assists[chosen_assister] += 1

    return player_assists


def generate_defensive_contributions(
    lineup_slots: list[LineupSlot],
    opponent_shots: int,
    opponent_shots_on_target: int,
    opponent_score: int,
    latent_influences: dict[str, float],
    rng: random.Random,
) -> dict[str, dict[str, int]]:
    result: dict[str, dict[str, int]] = {
        slot.player.id: {"tackles": 0, "interceptions": 0, "clearances": 0, "saves": 0, "key_passes": 0}
        for slot in lineup_slots
    }

    # Goalkeeper saves calculation
    gk_slot = next((s for s in lineup_slots if s.slot_position == "GK"), None)
    if gk_slot:
        gk = gk_slot.player
        expected_saves = max(0, opponent_shots_on_target - opponent_score)
        result[gk.id]["saves"] = expected_saves

    # Field defensive stats
    for slot in lineup_slots:
        p = slot.player
        pos = slot.slot_position
        if pos == "GK":
            # GK key passes / distribution
            result[p.id]["key_passes"] = 1 if rng.random() < 0.15 else 0
            continue

        def_awareness = p.attributes.defensive_awareness
        tackle_attr = p.attributes.standing_tackle
        interc_attr = p.attributes.interceptions
        heading = p.attributes.heading
        inf = latent_influences.get(p.id, 50.0)

        # Baseline actions based on position and opponent shots
        is_def = pos in ("CB", "LB", "RB", "LWB", "RWB", "DM")
        pos_mult = 1.5 if is_def else 0.7

        t_base = (tackle_attr / 30.0) * pos_mult * (inf / 50.0) * rng.uniform(0.6, 1.4)
        i_base = (interc_attr / 30.0) * pos_mult * (inf / 50.0) * rng.uniform(0.6, 1.4)
        c_base = (heading / 35.0) * (2.0 if pos == "CB" else 0.5) * rng.uniform(0.6, 1.4)

        if "STRONG" in p.traits:
            t_base *= 1.15
        if "AERIAL" in p.traits:
            c_base *= 1.20

        # Key passes
        kp_base = (p.attributes.vision / 35.0) * (p.attributes.short_passing / 35.0) * (1.2 if pos in ("CAM", "CM", "LW", "RW") else 0.5) * rng.uniform(0.5, 1.5)

        result[p.id]["tackles"] = max(0, int(round(t_base)))
        result[p.id]["interceptions"] = max(0, int(round(i_base)))
        result[p.id]["clearances"] = max(0, int(round(c_base)))
        result[p.id]["key_passes"] = max(0, int(round(kp_base)))

    return result


def calculate_minutes_and_substitutions(
    lineup: Lineup,
    team_score: int,
    opponent_score: int,
    match_importance: float,
    rng: random.Random,
) -> tuple[dict[str, int], list[dict]]:
    minutes_map: dict[str, int] = {}
    sub_events: list[dict] = []

    starters = lineup.starters
    bench = lineup.bench

    # Starters default 90 mins
    for slot in starters:
        minutes_map[slot.player.id] = 90

    # Bench default 0 mins
    for p in bench:
        minutes_map[p.id] = 0

    # Select up to 3-5 subs (max 5 substitutions)
    max_subs = 5
    num_subs = min(len(bench), min(max_subs, int(round(rng.uniform(3, 5)))))

    if num_subs > 0 and starters and bench:
        # Candidates for sub-off: starters with low fitness or poor latent influence
        sub_off_candidates = sorted(
            starters,
            key=lambda slot: (slot.player.state.fitness, slot.role_effectiveness),
        )[:num_subs]

        # Model D: Deterministic Weighted Stochastic Substitute Selection
        # Exclude GKs unless sub_off is GK
        field_bench = [p for p in bench if p.primary_position != "GK"]
        if not field_bench:
            field_bench = list(bench)

        # Select unique substitute candidates using sub_priority_score weights
        sub_on_candidates = []
        available_bench = list(field_bench)

        # High importance match exponent sharpens preference for top bench players
        importance_exponent = 1.0 + (max(0.0, match_importance - 50.0) / 25.0)

        for _ in range(min(num_subs, len(available_bench))):
            bench_scores = []
            for p in available_bench:
                # Retrieve precomputed sub_priority_score from Lineup or calculate using manager context
                if p.id in lineup.sub_priority_scores:
                    score = lineup.sub_priority_scores[p.id]
                else:
                    _, slot = evaluate_player_for_slot(
                        p,
                        p.primary_position,
                        manager=lineup.manager,
                        competition_importance=match_importance,
                    )
                    score = slot.sub_priority_score
                bench_scores.append((p, score))

            # Calculate exponentiated weights for sampling
            weights = [max(0.001, (score / 50.0) ** importance_exponent) for _, score in bench_scores]
            candidate_players = [p for p, _ in bench_scores]

            chosen = rng.choices(candidate_players, weights=weights, k=1)[0]
            sub_on_candidates.append(chosen)
            available_bench.remove(chosen)

        sub_minutes = [60, 68, 75, 80, 85]

        for i in range(min(len(sub_off_candidates), len(sub_on_candidates))):
            s_off = sub_off_candidates[i]
            p_on = sub_on_candidates[i]
            sub_min = sub_minutes[i % len(sub_minutes)]

            minutes_map[s_off.player.id] = sub_min
            minutes_map[p_on.id] = 90 - sub_min

            sub_events.append({
                "minute": sub_min,
                "event_type": MatchEventType.SUBSTITUTION,
                "primary_player_id": p_on.id,
                "secondary_player_id": s_off.player.id,
                "metadata": {"reason": "TACTICAL" if team_score >= opponent_score else "POOR_PERFORMANCE"},
            })

    return minutes_map, sub_events


def calculate_contextual_match_rating(
    player: Player,
    slot_position: str,
    evaluated_role: str,
    minutes: int,
    stats: dict,
    team_won: bool,
    team_draw: bool,
) -> float:
    if minutes <= 0:
        return 6.0

    base_rating = 6.0

    goals = stats.get("goals", 0)
    assists = stats.get("assists", 0)
    shots = stats.get("shots", 0)
    sot = stats.get("shots_on_target", 0)
    key_passes = stats.get("key_passes", 0)
    tackles = stats.get("tackles", 0)
    interceptions = stats.get("interceptions", 0)
    clearances = stats.get("clearances", 0)
    saves = stats.get("saves", 0)

    # Position-specific rating weights
    if slot_position in ("ST", "LW", "RW"):
        pos_contrib = (
            (goals * 1.0)
            + (assists * 0.6)
            + (sot * 0.15)
            + (key_passes * 0.10)
            - ((shots - sot) * 0.10)
        )
    elif slot_position in ("CAM", "AM", "CM", "DM", "LM", "RM"):
        pos_contrib = (
            (assists * 0.8)
            + (key_passes * 0.20)
            + (goals * 0.8)
            + (tackles * 0.10)
            + (interceptions * 0.10)
        )
    elif slot_position in ("CB", "LB", "RB", "LWB", "RWB"):
        pos_contrib = (
            (tackles * 0.12)
            + (interceptions * 0.12)
            + (clearances * 0.08)
            + (assists * 0.7)
            + (goals * 0.9)
        )
    elif slot_position == "GK":
        pos_contrib = (saves * 0.35)
    else:
        pos_contrib = (goals * 0.8) + (assists * 0.6) + (key_passes * 0.1)

    result_bonus = 0.3 if team_won else (-0.2 if not team_draw else 0.0)

    # Short minute scaling for sub appearances
    raw_rating = base_rating + pos_contrib + result_bonus
    if minutes < 20:
        raw_rating = 6.0 + (raw_rating - 6.0) * (minutes / 20.0)

    return max(1.0, min(10.0, round(raw_rating, 1)))


def simulate_player_performances(
    context: MatchContext,
    resolution: MatchResolutionState,
    home_lineup: Lineup,
    away_lineup: Lineup,
) -> tuple[list[PlayerMatchPerformance], list[MatchEvent]]:
    all_performances: list[PlayerMatchPerformance] = []
    all_events: list[MatchEvent] = []

    # Process Home & Away Teams
    teams = [
        ("home", home_lineup, resolution.home_score, resolution.away_score, resolution.home_shots, resolution.home_shots_on_target, resolution.away_shots, resolution.away_shots_on_target),
        ("away", away_lineup, resolution.away_score, resolution.home_score, resolution.away_shots, resolution.away_shots_on_target, resolution.home_shots, resolution.home_shots_on_target),
    ]

    for side, lineup, team_score, opp_score, team_shots, team_sot, opp_shots, opp_sot in teams:
        team_won = team_score > opp_score
        team_draw = team_score == opp_score

        # Identify opponent goalkeeper
        opp_lineup = away_lineup if side == "home" else home_lineup
        opp_gk_slot = next((s for s in opp_lineup.starters if s.slot_position == "GK"), None)
        opp_gk = opp_gk_slot.player if opp_gk_slot else None

        # 1. Minutes & Substitutions
        rng_team = get_sha256_player_rng(context.seed, context.match_id, f"{side}_team", "minutes")
        minutes_map, sub_events = calculate_minutes_and_substitutions(
            lineup, team_score, opp_score, context.match_importance, rng_team
        )

        for sub_ev in sub_events:
            all_events.append(MatchEvent(
                minute=sub_ev["minute"],
                event_type=sub_ev["event_type"],
                primary_player_id=sub_ev["primary_player_id"],
                secondary_player_id=sub_ev["secondary_player_id"],
                metadata={"reason": sub_ev["metadata"].get("reason", "TACTICAL")},
            ))

        # Active participants (starters + substitutes with >0 mins)
        active_slots = [
            slot for slot in lineup.starters if minutes_map.get(slot.player.id, 0) > 0
        ]
        # Include substitute bench players who played >0 mins
        for bench_p in lineup.bench:
            if minutes_map.get(bench_p.id, 0) > 0:
                active_slots.append(LineupSlot(
                    slot_position=bench_p.primary_position,
                    player=bench_p,
                    evaluated_role="SUBSTITUTE",
                    role_familiarity=80.0,
                    role_attribute_fit=70.0,
                    role_effectiveness=70.0,
                ))

        # 2. Latent Player Influence
        latent_influences: dict[str, float] = {}
        for slot in active_slots:
            p = slot.player
            rng_p = get_sha256_player_rng(context.seed, context.match_id, p.id, "influence")
            latent_influences[p.id] = calculate_latent_influence(
                p, slot.slot_position, slot.role_effectiveness, context.match_importance, rng_p
            )

        # FAST mode short-circuit
        if context.simulation_mode == SimulationMode.FAST:
            chance_shares = distribute_chance_shares(active_slots, latent_influences, rng_team)
            player_shots = allocate_player_shots(active_slots, team_shots, team_sot, chance_shares, rng_team)
            player_goals = resolve_goal_conversions(active_slots, team_score, player_shots, opp_gk, context.match_importance, rng_team)
            player_assists = attribute_assists(active_slots, team_score, player_goals, latent_influences, rng_team)
            def_contribs = generate_defensive_contributions(active_slots, opp_shots, opp_sot, opp_score, latent_influences, rng_team)

            for slot in active_slots:
                p = slot.player
                pid = p.id
                shots, sot = player_shots.get(pid, (0, 0))
                g = player_goals.get(pid, 0)
                a = player_assists.get(pid, 0)
                dc = def_contribs.get(pid, {})
                mins = minutes_map.get(pid, 0)

                stats = {
                    "goals": g, "assists": a, "shots": shots, "shots_on_target": sot,
                    "key_passes": dc.get("key_passes", 0), "tackles": dc.get("tackles", 0),
                    "interceptions": dc.get("interceptions", 0), "clearances": dc.get("clearances", 0),
                    "saves": dc.get("saves", 0),
                }
                rating = calculate_contextual_match_rating(p, slot.slot_position, slot.evaluated_role, mins, stats, team_won, team_draw)

                perf = PlayerMatchPerformance(
                    player_id=pid,
                    match_id=context.match_id,
                    starter=any(s.player.id == pid for s in lineup.starters),
                    minutes=mins,
                    rating=rating,
                    goals=g,
                    assists=a,
                    shots=shots,
                    shots_on_target=sot,
                    key_passes=stats["key_passes"],
                    tackles=stats["tackles"],
                    interceptions=stats["interceptions"],
                    clearances=stats["clearances"],
                    saves=stats["saves"],
                    role=slot.evaluated_role,
                    position=slot.slot_position,
                    latent_influence=latent_influences.get(pid, 50.0),
                )
                all_performances.append(perf)

            continue  # End FAST mode for this team

        # 3. DETAILED mode simulation
        chance_shares = distribute_chance_shares(active_slots, latent_influences, rng_team)
        player_shots = allocate_player_shots(active_slots, team_shots, team_sot, chance_shares, rng_team)
        player_goals = resolve_goal_conversions(active_slots, team_score, player_shots, opp_gk, context.match_importance, rng_team)
        player_assists = attribute_assists(active_slots, team_score, player_goals, latent_influences, rng_team)
        def_contribs = generate_defensive_contributions(active_slots, opp_shots, opp_sot, opp_score, latent_influences, rng_team)

        # Generate MatchEvents for DETAILED mode
        # Match events for goals & assists
        assist_pool = [pid for pid, ast_cnt in player_assists.items() for _ in range(ast_cnt)]
        goal_minutes = sorted([int(round(rng_team.uniform(5, 88))) for _ in range(team_score)])

        goal_idx = 0
        for pid, g_cnt in player_goals.items():
            for _ in range(g_cnt):
                m_min = goal_minutes[goal_idx % len(goal_minutes)] if goal_minutes else 45
                goal_idx += 1
                sec_pid = assist_pool.pop(0) if assist_pool else None

                all_events.append(MatchEvent(
                    minute=m_min,
                    event_type=MatchEventType.GOAL,
                    primary_player_id=pid,
                    secondary_player_id=sec_pid,
                    metadata={"side": side},
                ))
                if sec_pid:
                    all_events.append(MatchEvent(
                        minute=m_min,
                        event_type=MatchEventType.ASSIST,
                        primary_player_id=sec_pid,
                        secondary_player_id=pid,
                        metadata={"side": side},
                    ))

        # Generate performances
        for slot in active_slots:
            p = slot.player
            pid = p.id
            shots, sot = player_shots.get(pid, (0, 0))
            g = player_goals.get(pid, 0)
            a = player_assists.get(pid, 0)
            dc = def_contribs.get(pid, {})
            mins = minutes_map.get(pid, 0)

            stats = {
                "goals": g, "assists": a, "shots": shots, "shots_on_target": sot,
                "key_passes": dc.get("key_passes", 0), "tackles": dc.get("tackles", 0),
                "interceptions": dc.get("interceptions", 0), "clearances": dc.get("clearances", 0),
                "saves": dc.get("saves", 0),
            }
            rating = calculate_contextual_match_rating(p, slot.slot_position, slot.evaluated_role, mins, stats, team_won, team_draw)

            perf = PlayerMatchPerformance(
                player_id=pid,
                match_id=context.match_id,
                starter=any(s.player.id == pid for s in lineup.starters),
                minutes=mins,
                rating=rating,
                goals=g,
                assists=a,
                shots=shots,
                shots_on_target=sot,
                key_passes=stats["key_passes"],
                tackles=stats["tackles"],
                interceptions=stats["interceptions"],
                clearances=stats["clearances"],
                saves=stats["saves"],
                role=slot.evaluated_role,
                position=slot.slot_position,
                latent_influence=latent_influences.get(pid, 50.0),
            )
            all_performances.append(perf)

    # Sort events deterministically by minute
    all_events.sort(key=lambda e: (e.minute, e.event_type.value, e.primary_player_id))

    return all_performances, all_events
