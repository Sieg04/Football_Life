import copy
import json
import subprocess
import sys
from datetime import date
import pytest

from app.player.generation import generate_player
from app.transfer.decisions import (
    evaluate_club_decision,
    evaluate_player_decision,
    resolve_competing_offers,
    resolve_transfer_offer,
)
from app.transfer.domain import (
    ClubDecision,
    ContractState,
    OfferDecisionStatus,
    PlayerDecision,
    StructuredReason,
    TransferDecision,
    TransferOffer,
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
    club = Club(
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
    object.__setattr__(club, "id", club_id)
    return club


def _create_sample_contract(wage_band: float = 5000.0, release_clause: float | None = None) -> ContractState:
    return ContractState(
        contract_start=date(2024, 7, 1),
        contract_end=date(2027, 7, 1),
        wage_band=wage_band,
        release_clause=release_clause,
    )


def _create_sample_offer(
    offer_id: str = "off1",
    player_id: str = "p1",
    selling_club_id: str = "c1",
    buying_club_id: str = "c2",
    transfer_fee: float = 10_000_000.0,
    wage_offer: float = 10_000.0,
    contract_years: int = 3,
) -> TransferOffer:
    return TransferOffer(
        id=offer_id,
        player_id=player_id,
        selling_club_id=selling_club_id,
        buying_club_id=buying_club_id,
        transfer_fee=transfer_fee,
        wage_offer=wage_offer,
        contract_years=contract_years,
        structured_reason=StructuredReason.STARTING_ROLE,
        seed="test_seed_123",
    )


# ------------------------------------------------------------------
# 18.1 Player Decision Tests
# ------------------------------------------------------------------

def test_player_decision_clear_acceptance():
    player = generate_player(seed=1, player_id="p1", position="ST", target_ability=75.0)
    seller = _create_test_club("c1", prestige=40.0, squad=[player])
    buyer = _create_test_club("c2", prestige=80.0)
    contract = _create_sample_contract(wage_band=2000.0)
    offer = _create_sample_offer(wage_offer=20000.0)

    dec = evaluate_player_decision(offer, player, buyer, seller, contract)
    assert dec.accepted is True
    assert dec.score >= 50.0
    assert 0.0 <= dec.score <= 100.0
    assert StructuredReason.PLAYER_WAGE in dec.reasons


def test_player_decision_clear_rejection():
    player = generate_player(seed=1, player_id="p1", position="ST", target_ability=75.0)
    seller = _create_test_club("c1", prestige=90.0, squad=[player])
    buyer = _create_test_club("c2", prestige=10.0)
    contract = _create_sample_contract(wage_band=50000.0)
    offer = _create_sample_offer(wage_offer=1000.0)

    dec = evaluate_player_decision(offer, player, buyer, seller, contract)
    assert dec.accepted is False
    assert dec.score < 50.0


def test_player_decision_wage_monotonicity():
    player = generate_player(seed=1, player_id="p1", position="ST", target_ability=75.0)
    seller = _create_test_club("c1", squad=[player])
    buyer = _create_test_club("c2")
    contract = _create_sample_contract(wage_band=5000.0)

    offer_low = _create_sample_offer(wage_offer=6000.0)
    offer_high = _create_sample_offer(wage_offer=15000.0)

    dec_low = evaluate_player_decision(offer_low, player, buyer, seller, contract)
    dec_high = evaluate_player_decision(offer_high, player, buyer, seller, contract)

    assert dec_high.score >= dec_low.score


# ------------------------------------------------------------------
# 18.2 Club Decision Tests
# ------------------------------------------------------------------

def test_club_decision_clear_acceptance():
    player = generate_player(seed=1, player_id="p1", position="ST", target_ability=70.0)
    seller = _create_test_club("c1", squad=[player])
    contract = _create_sample_contract()
    # High fee relative to market value
    offer = _create_sample_offer(transfer_fee=30_000_000.0)

    dec = evaluate_club_decision(offer, player, seller, contract)
    assert dec.accepted is True
    assert dec.score >= 50.0


def test_club_decision_release_clause_trigger():
    player = generate_player(seed=1, player_id="p1", position="ST", target_ability=75.0)
    seller = _create_test_club("c1", squad=[player])
    contract = _create_sample_contract(release_clause=15_000_000.0)
    offer = _create_sample_offer(transfer_fee=15_000_000.0)

    dec = evaluate_club_decision(offer, player, seller, contract)
    assert dec.accepted is True
    assert dec.score == 100.0


def test_club_decision_fee_monotonicity():
    player = generate_player(seed=1, player_id="p1", position="ST", target_ability=75.0)
    seller = _create_test_club("c1", squad=[player])
    contract = _create_sample_contract()

    offer_low = _create_sample_offer(transfer_fee=2_000_000.0)
    offer_high = _create_sample_offer(transfer_fee=20_000_000.0)

    dec_low = evaluate_club_decision(offer_low, player, seller, contract)
    dec_high = evaluate_club_decision(offer_high, player, seller, contract)

    assert dec_high.score >= dec_low.score


# ------------------------------------------------------------------
# 18.3 Final Offer Resolution Combinations
# ------------------------------------------------------------------

def test_resolve_offer_all_combinations():
    player = generate_player(seed=1, player_id="p1", position="ST", target_ability=75.0)
    seller = _create_test_club("c1", prestige=50.0, squad=[player])
    buyer = _create_test_club("c2", prestige=50.0)
    contract = _create_sample_contract(wage_band=5000.0)

    # 1. BOTH ACCEPT
    offer_acc = _create_sample_offer(transfer_fee=30_000_000.0, wage_offer=20_000.0)
    res_acc = resolve_transfer_offer(offer_acc, player, buyer, seller, contract)
    assert res_acc.status == OfferDecisionStatus.ACCEPTED

    # 2. PLAYER REJECT, CLUB ACCEPT
    offer_p_rej = _create_sample_offer(transfer_fee=30_000_000.0, wage_offer=100.0)
    res_p_rej = resolve_transfer_offer(offer_p_rej, player, buyer, seller, contract)
    assert res_p_rej.status == OfferDecisionStatus.PLAYER_REJECTED

    # 3. PLAYER ACCEPT, CLUB REJECT
    offer_c_rej = _create_sample_offer(transfer_fee=100.0, wage_offer=20_000.0)
    res_c_rej = resolve_transfer_offer(offer_c_rej, player, buyer, seller, contract)
    assert res_c_rej.status == OfferDecisionStatus.CLUB_REJECTED

    # 4. BOTH REJECT
    offer_both_rej = _create_sample_offer(transfer_fee=100.0, wage_offer=100.0)
    res_both_rej = resolve_transfer_offer(offer_both_rej, player, buyer, seller, contract)
    assert res_both_rej.status == OfferDecisionStatus.BOTH_REJECTED


# ------------------------------------------------------------------
# 18.4 Competing Offers Resolution
# ------------------------------------------------------------------

def test_competing_offers_resolution():
    player = generate_player(seed=1, player_id="p1", position="ST", target_ability=75.0)
    seller = _create_test_club("c1", squad=[player])
    buyer1 = _create_test_club("c2", prestige=80.0)
    buyer2 = _create_test_club("c3", prestige=60.0)
    contract = _create_sample_contract()

    offer1 = _create_sample_offer(offer_id="off1", player_id="p1", selling_club_id="c1", buying_club_id="c2", transfer_fee=25_000_000.0, wage_offer=15_000.0)
    offer2 = _create_sample_offer(offer_id="off2", player_id="p1", selling_club_id="c1", buying_club_id="c3", transfer_fee=20_000_000.0, wage_offer=10_000.0)

    offers = [offer1, offer2]
    players = [player]
    clubs = [seller, buyer1, buyer2]
    contracts = {"p1": contract}

    resolved = resolve_competing_offers(offers, players, clubs, contracts)

    assert len(resolved) == 2
    # offer1 should win (higher fee & prestige)
    r1 = next(r for r in resolved if r.offer_id == "off1")
    r2 = next(r for r in resolved if r.offer_id == "off2")

    assert r1.status == OfferDecisionStatus.ACCEPTED
    assert r2.status == OfferDecisionStatus.COMPETING_OFFER_LOST


# ------------------------------------------------------------------
# 18.5 Input Validation
# ------------------------------------------------------------------

def test_input_validation():
    with pytest.raises(ValueError):
        PlayerDecision(accepted=True, score=-5.0)

    with pytest.raises(ValueError):
        PlayerDecision(accepted=True, score=105.0)

    with pytest.raises(ValueError):
        ClubDecision(accepted=True, score=float("nan"))

    with pytest.raises(ValueError):
        TransferDecision(
            offer_id="off1",
            player_id="p1",
            buying_club_id="c1",
            selling_club_id="c1",
            status=OfferDecisionStatus.ACCEPTED,
            player_decision=PlayerDecision(accepted=True, score=80.0),
            club_decision=ClubDecision(accepted=True, score=80.0),
        )


# ------------------------------------------------------------------
# 18.6 Immutability
# ------------------------------------------------------------------

def test_input_immutability():
    player = generate_player(seed=1, player_id="p1", position="ST", target_ability=75.0)
    seller = _create_test_club("c1", squad=[player])
    buyer = _create_test_club("c2")
    contract = _create_sample_contract()
    offer = _create_sample_offer()

    player_copy = copy.deepcopy(player)
    seller_copy = copy.deepcopy(seller)
    buyer_copy = copy.deepcopy(buyer)
    contract_copy = copy.deepcopy(contract)
    offer_copy = copy.deepcopy(offer)

    resolve_transfer_offer(offer, player, buyer, seller, contract)

    assert player == player_copy
    assert seller == seller_copy
    assert buyer == buyer_copy
    assert contract == contract_copy
    assert offer == offer_copy


# ------------------------------------------------------------------
# 18.7 Repeated Execution Determinism
# ------------------------------------------------------------------

def test_repeated_execution_determinism():
    player = generate_player(seed=1, player_id="p1", position="ST", target_ability=75.0)
    seller = _create_test_club("c1", squad=[player])
    buyer = _create_test_club("c2")
    contract = _create_sample_contract()
    offer = _create_sample_offer()

    first_run = resolve_transfer_offer(offer, player, buyer, seller, contract)

    for _ in range(100):
        run = resolve_transfer_offer(offer, player, buyer, seller, contract)
        assert run == first_run


# ------------------------------------------------------------------
# 18.8 Cross-Process Determinism
# ------------------------------------------------------------------

def test_cross_process_determinism():
    code = """
import json
from datetime import date
from app.player.generation import generate_player
from app.world.entities import Club, Manager
from app.transfer.domain import ContractState, TransferOffer, StructuredReason
from app.transfer.decisions import resolve_transfer_offer

player = generate_player(seed=1, player_id="p1", position="ST", target_ability=75.0)
mgr = Manager("M", 50, 50, 50, 50, 50, "BALANCED", 50, 50)
seller = Club("Seller", "ENG", "ENG1", mgr, 50, 50, 50, 50, 50, 50, 0, 0, 50, 50, squad=(player,))
buyer = Club("Buyer", "ENG", "ENG1", mgr, 60, 60, 50, 50, 50, 50, 0, 0, 60, 60)
contract = ContractState(contract_start=date(2024, 1, 1), contract_end=date(2027, 1, 1), wage_band=5000.0)
offer = TransferOffer(id="off1", player_id="p1", selling_club_id="Seller", buying_club_id="Buyer", transfer_fee=15000000.0, wage_offer=10000.0, contract_years=3, structured_reason=StructuredReason.STARTING_ROLE, seed="s1")

dec = resolve_transfer_offer(offer, player, buyer, seller, contract)
print(json.dumps({
    "status": dec.status.value,
    "player_score": dec.player_decision.score,
    "club_score": dec.club_decision.score,
    "player_reasons": [r.value for r in dec.player_decision.reasons],
    "club_reasons": [r.value for r in dec.club_decision.reasons],
}))
"""
    cmd = [sys.executable, "-c", code]
    res1 = subprocess.run(cmd, capture_output=True, text=True, check=True, env={"PYTHONPATH": "backend"})
    res2 = subprocess.run(cmd, capture_output=True, text=True, check=True, env={"PYTHONPATH": "backend"})

    assert res1.stdout == res2.stdout
    data = json.loads(res1.stdout)
    assert "status" in data
    assert "player_score" in data
    assert "club_score" in data


# ------------------------------------------------------------------
# 18.9 Reason Determinism
# ------------------------------------------------------------------

def test_reason_determinism():
    player = generate_player(seed=1, player_id="p1", position="ST", target_ability=75.0)
    seller = _create_test_club("c1", squad=[player])
    buyer = _create_test_club("c2")
    contract = _create_sample_contract()
    offer = _create_sample_offer()

    d1 = resolve_transfer_offer(offer, player, buyer, seller, contract)
    d2 = resolve_transfer_offer(offer, player, buyer, seller, contract)

    assert d1.player_decision.reasons == d2.player_decision.reasons
    assert d1.club_decision.reasons == d2.club_decision.reasons
    assert d1.player_decision.reasons == sorted(d1.player_decision.reasons, key=lambda r: r.value)
