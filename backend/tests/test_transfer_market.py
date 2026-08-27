import subprocess
import sys
from datetime import date
import pytest

from app.player.generation import generate_player
from app.transfer.contracts import ContractState
from app.transfer.domain import MarketValue
from app.transfer.market import calculate_market_value


def test_market_value_basic_validity():
    player = generate_player(seed=101, player_id="p101", target_ability=72.0)
    eval_date = date(2025, 7, 1)

    mv = calculate_market_value(player, evaluation_date=eval_date)
    assert isinstance(mv, MarketValue)
    assert mv.value >= 10000.0
    assert mv.currency == "EUR"
    assert "base_value" in mv.breakdown


def test_market_value_ability_monotonicity():
    p_low = generate_player(seed=201, player_id="p_low", target_ability=60.0)
    p_high = generate_player(seed=202, player_id="p_high", target_ability=80.0)

    # Force same age
    p_low.birth_date = date(2002, 1, 1)
    p_high.birth_date = date(2002, 1, 1)
    p_low.potential = 70.0
    p_high.potential = 85.0

    eval_date = date(2025, 7, 1)

    mv_low = calculate_market_value(p_low, evaluation_date=eval_date)
    mv_high = calculate_market_value(p_high, evaluation_date=eval_date)

    assert mv_high.value > mv_low.value


def test_market_value_young_potential_weighting():
    # Young player (age 18) with high potential vs low potential (same CA = 70)
    p_young_high_pot = generate_player(seed=301, player_id="p1", target_ability=70.0)
    p_young_low_pot = generate_player(seed=302, player_id="p2", target_ability=70.0)

    p_young_high_pot.birth_date = date(2007, 1, 1)
    p_young_low_pot.birth_date = date(2007, 1, 1)

    p_young_high_pot.current_ability = 70.0
    p_young_high_pot.potential = 90.0

    p_young_low_pot.current_ability = 70.0
    p_young_low_pot.potential = 72.0

    eval_date = date(2025, 7, 1)

    mv_high = calculate_market_value(p_young_high_pot, evaluation_date=eval_date)
    mv_low = calculate_market_value(p_young_low_pot, evaluation_date=eval_date)

    assert mv_high.value > mv_low.value


def test_market_value_age_curve():
    # Young prospect (19), Prime (26), Veteran (34) all CA 75, potential equal to CA
    p_young = generate_player(seed=401, player_id="py", target_ability=75.0)
    p_prime = generate_player(seed=402, player_id="pp", target_ability=75.0)
    p_vet = generate_player(seed=403, player_id="pv", target_ability=75.0)

    eval_date = date(2025, 7, 1)

    p_young.birth_date = date(2006, 1, 1)  # age 19
    p_prime.birth_date = date(1999, 1, 1)  # age 26
    p_vet.birth_date = date(1991, 1, 1)    # age 34

    p_young.current_ability = 75.0
    p_young.potential = 75.0
    p_prime.current_ability = 75.0
    p_prime.potential = 75.0
    p_vet.current_ability = 75.0
    p_vet.potential = 75.0

    mv_young = calculate_market_value(p_young, evaluation_date=eval_date)
    mv_prime = calculate_market_value(p_prime, evaluation_date=eval_date)
    mv_vet = calculate_market_value(p_vet, evaluation_date=eval_date)

    assert mv_young.value > mv_vet.value
    assert mv_prime.value > mv_vet.value


def test_market_value_contract_duration_effect():
    player = generate_player(seed=501, player_id="p501", target_ability=75.0)
    eval_date = date(2025, 7, 1)

    c_3yr = ContractState(contract_start=date(2025, 7, 1), contract_end=date(2028, 6, 30), wage_band=10000.0)
    c_1yr = ContractState(contract_start=date(2025, 7, 1), contract_end=date(2026, 6, 30), wage_band=10000.0)
    c_exp = ContractState(contract_start=date(2022, 7, 1), contract_end=date(2025, 6, 30), wage_band=10000.0)

    mv_3 = calculate_market_value(player, contract=c_3yr, evaluation_date=eval_date)
    mv_1 = calculate_market_value(player, contract=c_1yr, evaluation_date=eval_date)
    mv_exp = calculate_market_value(player, contract=c_exp, evaluation_date=eval_date)

    assert mv_3.value > mv_1.value > mv_exp.value


def test_market_value_performance_effect():
    player = generate_player(seed=601, player_id="p601", target_ability=75.0)
    eval_date = date(2025, 7, 1)

    class MockPerf:
        def __init__(self, rating):
            self.average_rating = rating

    mv_good = calculate_market_value(player, season_performance=MockPerf(7.8), evaluation_date=eval_date)
    mv_bad = calculate_market_value(player, season_performance=MockPerf(6.0), evaluation_date=eval_date)

    assert mv_good.value > mv_bad.value


def test_market_value_100x_determinism():
    player = generate_player(seed=701, player_id="p701", target_ability=78.0)
    eval_date = date(2025, 7, 1)
    c = ContractState(contract_start=date(2025, 7, 1), contract_end=date(2028, 6, 30), wage_band=15000.0)

    first_mv = calculate_market_value(player, contract=c, evaluation_date=eval_date)

    for _ in range(100):
        mv = calculate_market_value(player, contract=c, evaluation_date=eval_date)
        assert mv.value == first_mv.value
        assert mv.breakdown == first_mv.breakdown


def test_cross_process_determinism():
    code = """
import sys
from datetime import date
from app.player.generation import generate_player
from app.transfer.contracts import ContractState
from app.transfer.market import calculate_market_value

p = generate_player(seed=999, player_id="p999", target_ability=82.0)
c = ContractState(contract_start=date(2025, 7, 1), contract_end=date(2029, 6, 30), wage_band=25000.0)
mv = calculate_market_value(p, contract=c, evaluation_date=date(2025, 7, 1))
print(f"MV:{mv.value}")
"""
    cmd = [sys.executable, "-c", code]
    res1 = subprocess.check_output(cmd, env={"PYTHONPATH": "backend"}).decode().strip()
    res2 = subprocess.check_output(cmd, env={"PYTHONPATH": "backend"}).decode().strip()

    assert res1 == res2
    assert res1.startswith("MV:")
