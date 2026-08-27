from copy import deepcopy
from datetime import date
import os
import subprocess
import pytest

from app.player.generation import generate_player
from app.transfer.domain import ClubNeed
from app.transfer.needs import evaluate_club_needs, evaluate_position_need
from app.world.entities import Club, Manager


def _create_test_club(squad=(), prestige=60.0, financial_power=60.0) -> Club:
    dummy_manager = Manager(
        name="Test Manager",
        tactical_quality=60.0,
        player_development=60.0,
        game_management=60.0,
        rotation=50.0,
        adaptability=50.0,
        tactical_style="BALANCED",
        youth_preference=60.0,
        discipline=60.0,
    )
    return Club(
        name="Test FC",
        country_code="ENG",
        league_code="ENG1",
        manager=dummy_manager,
        prestige=prestige,
        financial_power=financial_power,
        academy_quality=60.0,
        facilities=60.0,
        fan_pressure=50.0,
        squad_depth=50.0,
        uefa_coefficient_raw=0.0,
        uefa_coefficient_normalized=0.0,
        domestic_reputation=prestige,
        international_reputation=prestige,
        squad=tuple(squad),
    )


def test_club_need_dataclass_validation():
    cn = ClubNeed(position="ST", need_score=50.0, depth_gap=50.0)
    assert cn.position == "ST"
    assert cn.need_score == 50.0

    with pytest.raises(ValueError, match="need_score"):
        ClubNeed(position="ST", need_score=-5.0)

    with pytest.raises(ValueError, match="need_score"):
        ClubNeed(position="ST", need_score=105.0)


def test_evaluate_position_need_empty_squad():
    club = _create_test_club(squad=[])
    need = evaluate_position_need(club, "ST", evaluation_date=date(2025, 7, 1))

    assert need.position == "ST"
    assert need.need_score > 60.0
    assert need.depth_gap == 100.0
    assert need.quality_gap == 100.0


def test_evaluate_position_need_depth_and_quality():
    p1 = generate_player(seed=1, player_id="p1", position="ST", target_ability=75.0)
    p2 = generate_player(seed=2, player_id="p2", position="ST", target_ability=72.0)
    p3 = generate_player(seed=3, player_id="p3", position="ST", target_ability=70.0)

    club = _create_test_club(squad=[p1, p2, p3], prestige=50.0)
    need = evaluate_position_need(club, "ST", evaluation_date=date(2025, 7, 1))

    assert need.need_score < 30.0
    assert need.depth_gap == 0.0
    assert need.quality_gap == 0.0


def test_evaluate_club_needs_all_positions():
    club = _create_test_club(squad=[])
    needs = evaluate_club_needs(club, evaluation_date=date(2025, 7, 1))

    assert len(needs) == 10
    assert "ST" in needs
    assert "GK" in needs
    assert "CB" in needs
    for pos, cn in needs.items():
        assert 0.0 <= cn.need_score <= 100.0


def test_evaluate_position_need_immutability():
    p1 = generate_player(seed=1, player_id="p1", position="ST", target_ability=75.0)
    club = _create_test_club(squad=[p1])
    original_club = deepcopy(club)

    _ = evaluate_position_need(club, "ST", evaluation_date=date(2025, 7, 1))

    assert club == original_club


def test_evaluate_position_need_determinism():
    p1 = generate_player(seed=1, player_id="p1", position="ST", target_ability=75.0)
    club = _create_test_club(squad=[p1])

    first_result = evaluate_position_need(club, "ST", evaluation_date=date(2025, 7, 1))
    for _ in range(100):
        res = evaluate_position_need(club, "ST", evaluation_date=date(2025, 7, 1))
        assert res == first_result


def test_evaluate_position_need_cross_process():
    cmd = [
        "python3",
        "-c",
        (
            "import json; "
            "from app.transfer.needs import evaluate_position_need; "
            "from app.world.entities import Club, Manager; "
            "from app.player.generation import generate_player; "
            "from datetime import date; "
            "p = generate_player(seed=1, player_id='p1', position='ST', target_ability=75.0); "
            "c = Club(name='C1', country_code='ENG', league_code='ENG1', manager=Manager('M', 50, 50, 50, 50, 50, 'BALANCED', 50, 50), prestige=50, financial_power=50, academy_quality=50, facilities=50, fan_pressure=50, squad_depth=50, uefa_coefficient_raw=0, uefa_coefficient_normalized=0, domestic_reputation=50, international_reputation=50, squad=(p,)); "
            "res = evaluate_position_need(c, 'ST', evaluation_date=date(2025, 7, 1)); "
            "print(res.need_score)"
        ),
    ]
    env = os.environ.copy()
    env["PYTHONPATH"] = "backend"

    proc1 = subprocess.check_output(cmd, env=env).decode().strip()
    proc2 = subprocess.check_output(cmd, env=env).decode().strip()

    assert proc1 == proc2
