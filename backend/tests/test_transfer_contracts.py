from datetime import date
import pytest

from app.player.generation import generate_player
from app.transfer.contracts import (
    calculate_contract_pressure,
    calculate_contract_status,
    calculate_contract_years_remaining,
    generate_initial_contract,
)
from app.transfer.domain import ContractState, ContractStatus


def test_contract_state_validation():
    # Valid
    c = ContractState(
        contract_start=date(2025, 7, 1),
        contract_end=date(2028, 6, 30),
        wage_band=5000.0,
        release_clause=50000000.0,
    )
    assert c.wage_band == 5000.0

    # Invalid end date <= start date
    with pytest.raises(ValueError, match="contract_end"):
        ContractState(
            contract_start=date(2025, 7, 1),
            contract_end=date(2025, 7, 1),
            wage_band=5000.0,
        )

    # Invalid negative wage
    with pytest.raises(ValueError, match="wage_band"):
        ContractState(
            contract_start=date(2025, 7, 1),
            contract_end=date(2028, 6, 30),
            wage_band=-100.0,
        )

    # Invalid negative release clause
    with pytest.raises(ValueError, match="release_clause"):
        ContractState(
            contract_start=date(2025, 7, 1),
            contract_end=date(2028, 6, 30),
            wage_band=5000.0,
            release_clause=-1.0,
        )


def test_calculate_contract_years_remaining():
    eval_date = date(2025, 7, 1)

    # 3 years remaining
    c_3y = date(2028, 7, 1)
    yr = calculate_contract_years_remaining(c_3y, eval_date)
    assert 2.99 <= yr <= 3.01

    # Exact same day (expires today)
    assert calculate_contract_years_remaining(eval_date, eval_date) == 0.0

    # Past date
    c_past = date(2024, 6, 30)
    assert calculate_contract_years_remaining(c_past, eval_date) == 0.0


def test_calculate_contract_status():
    eval_date = date(2025, 7, 1)

    # Active (> 1 year remaining)
    assert calculate_contract_status(date(2027, 7, 1), eval_date) == ContractStatus.ACTIVE

    # Expiring soon (<= 1 year remaining)
    assert calculate_contract_status(date(2026, 6, 30), eval_date) == ContractStatus.EXPIRING_SOON

    # Expired (today or past)
    assert calculate_contract_status(date(2025, 7, 1), eval_date) == ContractStatus.EXPIRED
    assert calculate_contract_status(date(2024, 6, 30), eval_date) == ContractStatus.EXPIRED


def test_calculate_contract_pressure():
    eval_date = date(2025, 7, 1)

    p_3y = calculate_contract_pressure(date(2028, 7, 1), eval_date)
    p_2y = calculate_contract_pressure(date(2027, 7, 1), eval_date)
    p_1y = calculate_contract_pressure(date(2026, 7, 1), eval_date)
    p_sub = calculate_contract_pressure(date(2025, 12, 31), eval_date)
    p_exp = calculate_contract_pressure(date(2025, 7, 1), eval_date)

    assert p_3y < p_2y < p_1y < p_sub < p_exp
    assert p_3y == 15.0
    assert p_exp == 100.0


def test_generate_initial_contract():
    player = generate_player(seed=42, player_id="p1", target_ability=75.0)
    eval_date = date(2025, 7, 1)

    contract1 = generate_initial_contract(player, club_prestige=80.0, evaluation_date=eval_date, seed="seed-123")
    contract2 = generate_initial_contract(player, club_prestige=80.0, evaluation_date=eval_date, seed="seed-123")

    assert contract1 == contract2
    assert contract1.contract_end > eval_date
    assert contract1.wage_band > 0.0
