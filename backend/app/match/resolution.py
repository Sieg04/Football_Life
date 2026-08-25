from dataclasses import dataclass
import hashlib
import math
import random

from app.match.domain import MatchContext
from app.match.lineup import EffectiveTeamStrength


@dataclass
class MatchResolutionState:
    home_effective_strength: float
    away_effective_strength: float
    home_raw_xg: float
    away_raw_xg: float
    home_xg: float
    away_xg: float
    home_score: int
    away_score: int
    home_possession: float
    away_possession: float
    home_shots: int
    away_shots: int
    home_shots_on_target: int
    away_shots_on_target: int
    derived_home_win_probability: float
    derived_draw_probability: float
    derived_away_win_probability: float


def get_sha256_match_rng(seed: str, match_id: str) -> random.Random:
    seed_material = f"{seed}:{match_id}:resolution"
    seed_hash = hashlib.sha256(seed_material.encode("utf-8")).hexdigest()
    seed_int = int(seed_hash[:16], 16)
    return random.Random(seed_int)


def poisson_sample(lam: float, rng: random.Random) -> int:
    if lam <= 0.0:
        return 0
    # Knuth's algorithm for discrete Poisson sampling
    L = math.exp(-lam)
    k = 0
    p = 1.0
    while p > L:
        k += 1
        p *= rng.random()
    return k - 1


def derive_match_probabilities(home_xg: float, away_xg: float, max_goals: int = 15) -> tuple[float, float, float]:
    home_probs = []
    away_probs = []

    for i in range(max_goals + 1):
        p_home = (math.exp(-home_xg) * (home_xg ** i)) / math.factorial(i)
        p_away = (math.exp(-away_xg) * (away_xg ** i)) / math.factorial(i)
        home_probs.append(p_home)
        away_probs.append(p_away)

    p_home_win = 0.0
    p_draw = 0.0
    p_away_win = 0.0

    for i in range(max_goals + 1):
        for j in range(max_goals + 1):
            prob = home_probs[i] * away_probs[j]
            if i > j:
                p_home_win += prob
            elif i == j:
                p_draw += prob
            else:
                p_away_win += prob

    total_prob = p_home_win + p_draw + p_away_win
    if total_prob > 0.0:
        p_home_win /= total_prob
        p_draw /= total_prob
        p_away_win /= total_prob

    return p_home_win, p_draw, p_away_win


def calculate_xg(
    home_strength: float,
    away_strength: float,
    rivalry_factor: float = 1.0,
    rng: random.Random | None = None,
) -> tuple[float, float, float, float]:
    if rng is None:
        rng = random.Random(42)

    ratio_home = home_strength / max(1.0, away_strength)
    ratio_away = away_strength / max(1.0, home_strength)

    var_home = rng.uniform(0.85, 1.15)
    var_away = rng.uniform(0.85, 1.15)

    base_home_xg = 1.35 * (ratio_home ** 1.10) * var_home
    base_away_xg = 1.15 * (ratio_away ** 1.10) * var_away

    if rivalry_factor > 1.0:
        riv_mod = 1.0 + (min(2.0, rivalry_factor) - 1.0) * 0.1
        base_home_xg *= riv_mod
        base_away_xg *= riv_mod

    clamped_home_xg = max(0.15, min(4.50, base_home_xg))
    clamped_away_xg = max(0.15, min(4.50, base_away_xg))

    return base_home_xg, base_away_xg, clamped_home_xg, clamped_away_xg


def calculate_possession(
    home_strength: float,
    away_strength: float,
    home_tactical_fit: float = 50.0,
    away_tactical_fit: float = 50.0,
    rng: random.Random | None = None,
) -> tuple[float, float]:
    if rng is None:
        rng = random.Random(42)

    home_rating = home_strength * 0.7 + home_tactical_fit * 0.3
    away_rating = away_strength * 0.7 + away_tactical_fit * 0.3

    raw_ratio = home_rating / max(1.0, home_rating + away_rating)
    possession_var = rng.uniform(-0.04, 0.04)

    home_possession = max(20.0, min(80.0, (raw_ratio + possession_var) * 100.0))
    home_possession = round(home_possession, 1)
    away_possession = round(100.0 - home_possession, 1)

    return home_possession, away_possession


def generate_shots(
    xg: float,
    goals: int,
    rng: random.Random,
) -> tuple[int, int]:
    base_shots = int(round(xg * 5.0 + rng.uniform(2.0, 6.0)))
    shots = max(goals, base_shots)

    min_sot = goals
    max_sot = shots
    if min_sot == max_sot:
        shots_on_target = min_sot
    else:
        shots_on_target = max(min_sot, min(shots, int(round(goals + (shots - goals) * rng.uniform(0.3, 0.6)))))

    return shots, shots_on_target


def resolve_match_resolution(
    context: MatchContext,
    home_strength: EffectiveTeamStrength,
    away_strength: EffectiveTeamStrength,
) -> MatchResolutionState:
    rng = get_sha256_match_rng(context.seed, context.match_id)

    raw_h_xg, raw_a_xg, h_xg, a_xg = calculate_xg(
        home_strength=home_strength.effective_strength,
        away_strength=away_strength.effective_strength,
        rivalry_factor=context.rivalry_factor,
        rng=rng,
    )

    home_score = poisson_sample(h_xg, rng)
    away_score = poisson_sample(a_xg, rng)

    home_poss, away_poss = calculate_possession(
        home_strength=home_strength.effective_strength,
        away_strength=away_strength.effective_strength,
        home_tactical_fit=home_strength.tactical_fit,
        away_tactical_fit=away_strength.tactical_fit,
        rng=rng,
    )

    home_shots, home_sot = generate_shots(h_xg, home_score, rng)
    away_shots, away_sot = generate_shots(a_xg, away_score, rng)

    p_home_win, p_draw, p_away_win = derive_match_probabilities(h_xg, a_xg)

    return MatchResolutionState(
        home_effective_strength=home_strength.effective_strength,
        away_effective_strength=away_strength.effective_strength,
        home_raw_xg=raw_h_xg,
        away_raw_xg=raw_a_xg,
        home_xg=h_xg,
        away_xg=a_xg,
        home_score=home_score,
        away_score=away_score,
        home_possession=home_poss,
        away_possession=away_poss,
        home_shots=home_shots,
        away_shots=away_shots,
        home_shots_on_target=home_sot,
        away_shots_on_target=away_sot,
        derived_home_win_probability=p_home_win,
        derived_draw_probability=p_draw,
        derived_away_win_probability=p_away_win,
    )
