import math
from datetime import date
from statistics import mean, median

from app.player.engine import position_ovr
from app.player.generation import generate_player
from app.transfer.contracts import generate_initial_contract
from app.transfer.market import calculate_market_value
from app.world.entities import Club, Manager


def _percentile(data: list[float], p: float) -> float:
    if not data:
        return 0.0
    sorted_data = sorted(data)
    k = (len(sorted_data) - 1) * (p / 100.0)
    f = math.floor(k)
    c = math.ceil(k)
    if f == c:
        return sorted_data[int(k)]
    return sorted_data[int(f)] * (c - k) + sorted_data[int(c)] * (k - f)


def test_market_value_distribution_audit():
    eval_date = date(2025, 7, 1)
    positions = ("ST", "CM", "CB", "GK", "LW", "RW", "LB", "CAM")
    records = []

    # Generate 200 representative players across varying specs
    for idx in range(200):
        pos = positions[idx % len(positions)]
        # Target ability ranging from 50 to 88
        target_ability = 50.0 + (idx * 0.19) % 38.0
        player = generate_player(seed=idx + 1000, player_id=f"audit_{idx}", position=pos, target_ability=target_ability)

        # Vary age between 17 and 35
        birth_year = 2025 - (17 + (idx % 19))
        player.birth_date = date(birth_year, 1, 1)

        club_prestige = 20.0 + (idx * 0.38) % 75.0
        contract = generate_initial_contract(player, club_prestige=club_prestige, evaluation_date=eval_date, seed=f"audit_c_{idx}")

        dummy_manager = Manager(
            name="Manager",
            tactical_quality=50,
            player_development=50,
            game_management=50,
            rotation=50,
            adaptability=50,
            tactical_style="BALANCED",
            youth_preference=50,
            discipline=50,
        )
        club = Club(
            name="Audit Club",
            country_code="ENG",
            league_code="ENG1",
            manager=dummy_manager,
            prestige=club_prestige,
            financial_power=club_prestige,
            academy_quality=50,
            facilities=50,
            fan_pressure=50,
            squad_depth=50,
            uefa_coefficient_raw=0,
            uefa_coefficient_normalized=0,
            domestic_reputation=club_prestige,
            international_reputation=club_prestige,
        )

        mv = calculate_market_value(player, contract=contract, club=club, evaluation_date=eval_date)
        ovr = position_ovr(player, player.primary_position)
        age = eval_date.year - player.birth_date.year

        records.append({
            "player": player,
            "age": age,
            "ovr": ovr,
            "position": pos,
            "club_prestige": club_prestige,
            "value": mv.value,
        })

    values = [r["value"] for r in records]

    p_min = min(values)
    p_max = max(values)
    p_mean = mean(values)
    p_median = median(values)
    p10 = _percentile(values, 10)
    p25 = _percentile(values, 25)
    p50 = _percentile(values, 50)
    p75 = _percentile(values, 75)
    p90 = _percentile(values, 90)
    p95 = _percentile(values, 95)
    p99 = _percentile(values, 99)

    print(f"\n--- MARKET VALUE AUDIT (N={len(records)}) ---")
    print(f"Min: €{p_min:,.0f}")
    print(f"P10: €{p10:,.0f}")
    print(f"P25: €{p25:,.0f}")
    print(f"P50 (Median): €{p_median:,.0f}")
    print(f"P75: €{p75:,.0f}")
    print(f"P90: €{p90:,.0f}")
    print(f"P95: €{p95:,.0f}")
    print(f"P99: €{p99:,.0f}")
    print(f"Max: €{p_max:,.0f}")
    print(f"Mean: €{p_mean:,.0f}")

    # Sanity checks
    assert p_min >= 10000.0
    assert p_max <= 350000000.0
    assert 200000.0 <= p_median <= 15000000.0

    # Check breakdown by OVR band
    high_ovr_vals = [r["value"] for r in records if r["ovr"] >= 80]
    low_ovr_vals = [r["value"] for r in records if r["ovr"] <= 65]

    if high_ovr_vals and low_ovr_vals:
        assert median(high_ovr_vals) > median(low_ovr_vals) * 3.0


def test_club_needs_and_player_fit_distribution_audit():
    from app.transfer.fit import calculate_club_attractiveness, evaluate_player_fit
    from app.transfer.needs import evaluate_club_needs

    eval_date = date(2025, 7, 1)
    # Generate 50 clubs and test fit for 50 players
    clubs = []
    for c_idx in range(50):
        prestige = 20.0 + (c_idx * 1.5)
        fin = 15.0 + (c_idx * 1.6)
        dummy_mgr = Manager(
            name=f"Manager {c_idx}",
            tactical_quality=40.0 + (c_idx % 50),
            player_development=40.0 + ((c_idx * 3) % 50),
            game_management=50.0,
            rotation=50.0,
            adaptability=50.0,
            tactical_style="BALANCED",
            youth_preference=30.0 + ((c_idx * 7) % 60),
            discipline=50.0,
        )
        squad = [
            generate_player(seed=c_idx * 100 + p_i, player_id=f"c{c_idx}_p{p_i}", position="CM", target_ability=45.0 + prestige * 0.4)
            for p_i in range(15)
        ]
        club = Club(
            name=f"Club {c_idx}",
            country_code="ENG",
            league_code="ENG1",
            manager=dummy_mgr,
            prestige=prestige,
            financial_power=fin,
            academy_quality=50.0,
            facilities=50.0,
            fan_pressure=50.0,
            squad_depth=50.0,
            uefa_coefficient_raw=0.0,
            uefa_coefficient_normalized=0.0,
            domestic_reputation=prestige,
            international_reputation=prestige,
            squad=tuple(squad),
        )
        clubs.append(club)

    attractiveness_scores = [calculate_club_attractiveness(c) for c in clubs]
    assert min(attractiveness_scores) >= 0.0
    assert max(attractiveness_scores) <= 100.0
    assert median(attractiveness_scores) > 20.0

    test_player = generate_player(seed=999, player_id="star_p", position="ST", target_ability=80.0)
    fit_scores = []
    for club in clubs:
        c_needs = evaluate_club_needs(club, evaluation_date=eval_date)
        fit = evaluate_player_fit(test_player, club, squad_needs=c_needs, evaluation_date=eval_date)
        fit_scores.append(fit.fit_score)

    assert all(0.0 <= score <= 100.0 for score in fit_scores)
    # Star striker should have very high fit score for clubs that lack ST depth/quality
    assert max(fit_scores) > 60.0
