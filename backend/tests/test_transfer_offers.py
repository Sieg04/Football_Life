from copy import deepcopy
from datetime import date
import os
import subprocess
import pytest

from app.player.generation import generate_player
from app.transfer.contracts import ContractState
from app.transfer.domain import (
    StructuredReason,
    TransferCandidate,
    TransferOffer,
    TransferWindow,
)
from app.transfer.offers import (
    generate_transfer_offer,
    generate_transfer_offers,
    is_transfer_window_active,
)
from app.world.entities import Club, Manager


def _create_test_club(club_id: str, squad=(), prestige=60.0) -> Club:
    dummy_manager = Manager(
        name=f"Manager {club_id}",
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
        name=f"Club {club_id}",
        country_code="ENG",
        league_code="ENG1",
        manager=dummy_manager,
        prestige=prestige,
        financial_power=prestige,
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


def test_transfer_candidate_validation():
    tc = TransferCandidate(
        player_id="p1",
        selling_club_id="c1",
        buying_club_id="c2",
        market_value=1000000.0,
        fit_score=80.0,
        interest_score=75.0,
        priority_score=70.0,
    )
    assert tc.player_id == "p1"

    # Same buyer and seller
    with pytest.raises(ValueError, match="buying_club_id and selling_club_id must be different"):
        TransferCandidate(
            player_id="p1",
            selling_club_id="c1",
            buying_club_id="c1",
            market_value=1000000.0,
            fit_score=80.0,
            interest_score=75.0,
            priority_score=70.0,
        )

    # Negative market value
    with pytest.raises(ValueError, match="market_value"):
        TransferCandidate(
            player_id="p1",
            selling_club_id="c1",
            buying_club_id="c2",
            market_value=-100.0,
            fit_score=80.0,
            interest_score=75.0,
            priority_score=70.0,
        )


def test_transfer_offer_validation():
    to = TransferOffer(
        id="off_1",
        player_id="p1",
        selling_club_id="c1",
        buying_club_id="c2",
        transfer_fee=1200000.0,
        wage_offer=5000.0,
        contract_years=4,
        structured_reason=StructuredReason.STARTING_ROLE,
        seed="seed123",
    )
    assert to.transfer_fee == 1200000.0

    # Negative fee
    with pytest.raises(ValueError, match="transfer_fee"):
        TransferOffer(
            id="off_1",
            player_id="p1",
            selling_club_id="c1",
            buying_club_id="c2",
            transfer_fee=-10.0,
            wage_offer=5000.0,
            contract_years=4,
            structured_reason=StructuredReason.STARTING_ROLE,
            seed="seed123",
        )


def test_is_transfer_window_active():
    assert is_transfer_window_active(date(2025, 7, 15), window=TransferWindow.SUMMER_WINDOW) is True
    assert is_transfer_window_active(date(2025, 11, 15), window=TransferWindow.SUMMER_WINDOW) is False
    assert is_transfer_window_active(date(2025, 1, 15), window=TransferWindow.WINTER_WINDOW) is True


def test_generate_single_transfer_offer():
    p = generate_player(seed=1, player_id="p1", position="ST", target_ability=75.0)
    buyer = _create_test_club("buyer", prestige=70.0)
    seller = _create_test_club("seller", squad=[p], prestige=60.0)

    contract = ContractState(contract_start=date(2023, 7, 1), contract_end=date(2026, 6, 30), wage_band=4000.0)

    candidate = TransferCandidate(
        player_id="p1",
        selling_club_id="seller",
        buying_club_id="buyer",
        market_value=5000000.0,
        fit_score=85.0,
        interest_score=80.0,
        priority_score=80.0,
    )

    offer = generate_transfer_offer(
        candidate=candidate,
        buying_club=buyer,
        selling_club=seller,
        player=p,
        contract=contract,
        evaluation_date=date(2025, 7, 1),
        seed="test_seed_1",
    )

    assert offer.player_id == "p1"
    assert offer.buying_club_id == "buyer"
    assert offer.selling_club_id == "seller"
    assert offer.transfer_fee > 0.0
    assert offer.wage_offer > 4000.0
    assert offer.contract_years >= 1


def test_generate_transfer_offers_window_inactive():
    p = generate_player(seed=1, player_id="p1", position="ST", target_ability=75.0)
    buyer = _create_test_club("buyer", prestige=70.0)
    seller = _create_test_club("seller", squad=[p], prestige=60.0)

    offers = generate_transfer_offers(
        selling_clubs=[seller],
        buying_clubs=[buyer],
        players=[p],
        evaluation_date=date(2025, 11, 15), # Out of window
        window=TransferWindow.SUMMER_WINDOW,
    )

    assert len(offers) == 0


def test_generate_transfer_offers_limits_and_duplicates():
    p1 = generate_player(seed=1, player_id="p1", position="ST", target_ability=75.0)
    seller = _create_test_club("seller", squad=[p1], prestige=60.0)

    buyers = [_create_test_club(f"buyer_{i}", prestige=70.0) for i in range(5)]

    offers = generate_transfer_offers(
        selling_clubs=[seller],
        buying_clubs=buyers,
        players=[p1],
        evaluation_date=date(2025, 7, 1),
        window=TransferWindow.SUMMER_WINDOW,
        seed="limit_seed",
    )

    # Max offers per player is configured to 3 in transfers.json
    assert len(offers) <= 3
    # Distinct buying clubs
    buyer_ids = [o.buying_club_id for o in offers]
    assert len(buyer_ids) == len(set(buyer_ids))


def test_generate_transfer_offers_immutability():
    p1 = generate_player(seed=1, player_id="p1", position="ST", target_ability=75.0)
    seller = _create_test_club("seller", squad=[p1], prestige=60.0)
    buyer = _create_test_club("buyer", prestige=70.0)

    orig_p = deepcopy(p1)
    orig_s = deepcopy(seller)

    _ = generate_transfer_offers(
        selling_clubs=[seller],
        buying_clubs=[buyer],
        players=[p1],
        evaluation_date=date(2025, 7, 1),
    )

    assert p1 == orig_p
    assert seller == orig_s


def test_generate_transfer_offers_determinism_100x():
    p1 = generate_player(seed=1, player_id="p1", position="ST", target_ability=75.0)
    seller = _create_test_club("seller", squad=[p1], prestige=60.0)
    buyer = _create_test_club("buyer", prestige=70.0)

    first = generate_transfer_offers(
        selling_clubs=[seller],
        buying_clubs=[buyer],
        players=[p1],
        evaluation_date=date(2025, 7, 1),
        seed="det_seed",
    )

    for _ in range(100):
        res = generate_transfer_offers(
            selling_clubs=[seller],
            buying_clubs=[buyer],
            players=[p1],
            evaluation_date=date(2025, 7, 1),
            seed="det_seed",
        )
        assert res == first


def test_generate_transfer_offers_cross_process():
    import sys

    cmd = [
        sys.executable,
        "-c",
        (
            "from app.transfer.offers import generate_transfer_offers; "
            "from app.world.entities import Club, Manager; "
            "from app.player.generation import generate_player; "
            "from datetime import date; "
            "p = generate_player(seed=1, player_id='p1', position='ST', target_ability=75.0); "
            "s = Club('seller', 'ENG', 'ENG1', Manager('M1', 50, 50, 50, 50, 50, 'BALANCED', 50, 50), 60, 60, 50, 50, 50, 50, 0, 0, 60, 60, squad=(p,)); "
            "b = Club('buyer', 'ENG', 'ENG1', Manager('M2', 50, 50, 50, 50, 50, 'BALANCED', 50, 50), 70, 70, 50, 50, 50, 50, 0, 0, 70, 70); "
            "offers = generate_transfer_offers([s], [b], [p], evaluation_date=date(2025, 7, 1), seed='cp_seed'); "
            "print([(o.player_id, o.buying_club_id, o.transfer_fee, o.wage_offer, o.structured_reason.value) for o in offers])"
        ),
    ]
    env = os.environ.copy()
    env["PYTHONPATH"] = "backend"

    proc1 = subprocess.check_output(cmd, env=env).decode().strip()
    proc2 = subprocess.check_output(cmd, env=env).decode().strip()

    assert proc1 == proc2
