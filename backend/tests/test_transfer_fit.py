from copy import deepcopy
from datetime import date
import os
import subprocess
import pytest

from app.player.generation import generate_player
from app.transfer.domain import PlayerFit
from app.transfer.fit import calculate_club_attractiveness, evaluate_player_fit
from app.world.entities import Club, Manager


def _create_test_club(squad=(), prestige=60.0, financial_power=60.0) -> Club:
    dummy_manager = Manager(
        name="Test Manager",
        tactical_quality=70.0,
        player_development=70.0,
        game_management=60.0,
        rotation=50.0,
        adaptability=50.0,
        tactical_style="BALANCED",
        youth_preference=70.0,
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


def test_player_fit_dataclass_validation():
    pf = PlayerFit(player_id="p1", club_id="c1", fit_score=75.0, quality_fit=80.0)
    assert pf.player_id == "p1"
    assert pf.fit_score == 75.0

    with pytest.raises(ValueError, match="fit_score"):
        PlayerFit(player_id="p1", club_id="c1", fit_score=-1.0)

    with pytest.raises(ValueError, match="fit_score"):
        PlayerFit(player_id="p1", club_id="c1", fit_score=101.0)


def test_calculate_club_attractiveness():
    c_high = _create_test_club(prestige=85.0, financial_power=90.0)
    c_low = _create_test_club(prestige=30.0, financial_power=30.0)

    attr_high = calculate_club_attractiveness(c_high, league_strength=80.0)
    attr_low = calculate_club_attractiveness(c_low, league_strength=30.0)

    assert 0.0 <= attr_high <= 100.0
    assert 0.0 <= attr_low <= 100.0
    assert attr_high > attr_low


def test_evaluate_player_fit_determinism_and_bounds():
    player = generate_player(seed=42, player_id="p1", position="ST", target_ability=75.0)
    club = _create_test_club(prestige=70.0)

    fit1 = evaluate_player_fit(player, club, evaluation_date=date(2025, 7, 1))
    fit2 = evaluate_player_fit(player, club, evaluation_date=date(2025, 7, 1))

    assert fit1 == fit2
    assert 0.0 <= fit1.fit_score <= 100.0
    assert fit1.quality_fit > 0.0


def test_evaluate_player_fit_immutability():
    player = generate_player(seed=42, player_id="p1", position="ST", target_ability=75.0)
    club = _create_test_club(prestige=70.0)
    orig_p = deepcopy(player)
    orig_c = deepcopy(club)

    _ = evaluate_player_fit(player, club, evaluation_date=date(2025, 7, 1))

    assert player == orig_p
    assert club == orig_c


def test_evaluate_player_fit_monotonicity_with_squad_need():
    player = generate_player(seed=42, player_id="p1", position="ST", target_ability=75.0)
    club_empty_st = _create_test_club(squad=[], prestige=70.0)
    club_full_st = _create_test_club(
        squad=[
            generate_player(seed=i, player_id=f"st_{i}", position="ST", target_ability=78.0)
            for i in range(4)
        ],
        prestige=70.0,
    )

    fit_empty = evaluate_player_fit(player, club_empty_st, evaluation_date=date(2025, 7, 1))
    fit_full = evaluate_player_fit(player, club_full_st, evaluation_date=date(2025, 7, 1))

    assert fit_empty.squad_need_fit > fit_full.squad_need_fit
    assert fit_empty.fit_score > fit_full.fit_score


def test_evaluate_player_fit_cross_process():
    cmd = [
        "python3",
        "-c",
        (
            "import json; "
            "from app.transfer.fit import evaluate_player_fit; "
            "from app.world.entities import Club, Manager; "
            "from app.player.generation import generate_player; "
            "from datetime import date; "
            "p = generate_player(seed=42, player_id='p1', position='ST', target_ability=75.0); "
            "c = Club(name='C1', country_code='ENG', league_code='ENG1', manager=Manager('M', 50, 50, 50, 50, 50, 'BALANCED', 50, 50), prestige=50, financial_power=50, academy_quality=50, facilities=50, fan_pressure=50, squad_depth=50, uefa_coefficient_raw=0, uefa_coefficient_normalized=0, domestic_reputation=50, international_reputation=50); "
            "res = evaluate_player_fit(p, c, evaluation_date=date(2025, 7, 1)); "
            "print(res.fit_score)"
        ),
    ]
    env = os.environ.copy()
    env["PYTHONPATH"] = "backend"

    proc1 = subprocess.check_output(cmd, env=env).decode().strip()
    proc2 = subprocess.check_output(cmd, env=env).decode().strip()

    assert proc1 == proc2
