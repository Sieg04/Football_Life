import copy
import math
import pytest
from datetime import date

from app.player.generation import generate_player
from app.transfer.application import (
    TransferApplicationResult,
    apply_transfers,
    create_transfer_application,
)
from app.transfer.domain import (
    ClubDecision,
    ContractState,
    OfferDecisionStatus,
    PlayerDecision,
    StructuredReason,
    TransferApplication,
    TransferApplicationStatus,
    TransferDecision,
    TransferHistoryRecord,
    TransferOffer,
)
from app.world.entities import Club, ClubMembership, Manager, SquadRole


def _create_test_club(club_id: str, squad=(), prestige: float = 60.0) -> Club:
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
    mems = tuple(
        ClubMembership(
            player_id=p.id,
            club_id=club_id,
            role=SquadRole.STARTER,
            start_date=date(2024, 7, 1),
            end_date=date(2027, 6, 30),
        )
        for p in squad
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
        memberships=mems,
    )
    object.__setattr__(club, "id", club_id)
    return club


def _create_sample_contract(wage_band: float = 5000.0) -> ContractState:
    return ContractState(
        contract_start=date(2024, 7, 1),
        contract_end=date(2027, 6, 30),
        wage_band=wage_band,
    )


def _create_sample_offer(
    offer_id: str = "off1",
    player_id: str = "p1",
    selling_club_id: str = "c1",
    buying_club_id: str = "c2",
    transfer_fee: float = 10_000_000.0,
    wage_offer: float = 12_000.0,
    contract_years: int = 4,
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
        seed="seed_123",
    )


def _create_accepted_decision(
    offer_id: str = "off1",
    player_id: str = "p1",
    selling_club_id: str = "c1",
    buying_club_id: str = "c2",
) -> TransferDecision:
    return TransferDecision(
        offer_id=offer_id,
        player_id=player_id,
        buying_club_id=buying_club_id,
        selling_club_id=selling_club_id,
        status=OfferDecisionStatus.ACCEPTED,
        player_decision=PlayerDecision(accepted=True, score=80.0),
        club_decision=ClubDecision(accepted=True, score=80.0),
    )


# ------------------------------------------------------------------
# 1. Basic Application Tests
# ------------------------------------------------------------------

def test_basic_application_accepted_transfer():
    player = generate_player(seed=1, player_id="p1", position="ST", target_ability=75.0)
    seller = _create_test_club("c1", squad=[player])
    buyer = _create_test_club("c2", squad=[])
    contract = _create_sample_contract(wage_band=5000.0)

    offer = _create_sample_offer(player_id="p1", selling_club_id="c1", buying_club_id="c2", wage_offer=15000.0, contract_years=4)
    decision = _create_accepted_decision(player_id="p1", selling_club_id="c1", buying_club_id="c2")

    app = create_transfer_application(decision, offer, season=2027)

    result = apply_transfers(
        clubs=[seller, buyer],
        contracts={"p1": contract},
        applications=[app],
        season=2027,
    )

    updated_seller = result.updated_clubs["c1"]
    updated_buyer = result.updated_clubs["c2"]

    # Seller loses player
    assert not any(p.id == "p1" for p in updated_seller.squad)
    assert not any(m.player_id == "p1" for m in updated_seller.memberships)

    # Buyer gains player
    assert any(p.id == "p1" for p in updated_buyer.squad)
    buyer_mems = [m for m in updated_buyer.memberships if m.player_id == "p1"]
    assert len(buyer_mems) == 1
    assert buyer_mems[0].club_id == "c2"

    # Contract updated
    new_contract = result.updated_contracts["p1"]
    assert new_contract.wage_band == 15000.0
    assert new_contract.contract_start == date(2027, 7, 1)
    assert new_contract.contract_end == date(2031, 6, 30)

    # Application & History status
    assert len(result.applications) == 1
    assert result.applications[0].status == TransferApplicationStatus.APPLIED
    assert len(result.history_records) == 1
    assert result.history_records[0].status == TransferApplicationStatus.APPLIED


def test_rejected_decision_not_applied():
    player = generate_player(seed=1, player_id="p1", position="ST", target_ability=75.0)
    seller = _create_test_club("c1", squad=[player])
    buyer = _create_test_club("c2", squad=[])
    contract = _create_sample_contract()

    offer = _create_sample_offer()
    decision = TransferDecision(
        offer_id="off1",
        player_id="p1",
        buying_club_id="c2",
        selling_club_id="c1",
        status=OfferDecisionStatus.PLAYER_REJECTED,
        player_decision=PlayerDecision(accepted=False, score=40.0),
        club_decision=ClubDecision(accepted=True, score=70.0),
    )

    app = create_transfer_application(decision, offer, season=2027)
    assert app.status == TransferApplicationStatus.SKIPPED

    result = apply_transfers(
        clubs=[seller, buyer],
        contracts={"p1": contract},
        applications=[app],
        season=2027,
    )

    # Roster remains unchanged
    assert any(p.id == "p1" for p in result.updated_clubs["c1"].squad)
    assert not any(p.id == "p1" for p in result.updated_clubs["c2"].squad)
    assert len(result.history_records) == 0


# ------------------------------------------------------------------
# 2. Strict Validation Tests
# ------------------------------------------------------------------

def test_validation_invalid_parameters():
    with pytest.raises(ValueError):
        TransferApplication(
            application_id="",
            transfer_decision_id="d1",
            player_id="p1",
            seller_club_id="c1",
            buyer_club_id="c2",
            transfer_fee=100.0,
            wage=10.0,
            contract_years=3,
            status=TransferApplicationStatus.PENDING,
            season=2027,
        )

    with pytest.raises(ValueError):
        TransferApplication(
            application_id="app1",
            transfer_decision_id="d1",
            player_id="p1",
            seller_club_id="c1",
            buyer_club_id="c1",
            transfer_fee=100.0,
            wage=10.0,
            contract_years=3,
            status=TransferApplicationStatus.PENDING,
            season=2027,
        )

    with pytest.raises(ValueError):
        TransferApplication(
            application_id="app1",
            transfer_decision_id="d1",
            player_id="p1",
            seller_club_id="c1",
            buyer_club_id="c2",
            transfer_fee=-500.0,
            wage=10.0,
            contract_years=3,
            status=TransferApplicationStatus.PENDING,
            season=2027,
        )

    with pytest.raises(ValueError):
        TransferApplication(
            application_id="app1",
            transfer_decision_id="d1",
            player_id="p1",
            seller_club_id="c1",
            buyer_club_id="c2",
            transfer_fee=float("nan"),
            wage=10.0,
            contract_years=3,
            status=TransferApplicationStatus.PENDING,
            season=2027,
        )


# ------------------------------------------------------------------
# 3. Conflict Handling Tests
# ------------------------------------------------------------------

def test_conflict_same_player_transferred_twice():
    player = generate_player(seed=1, player_id="p1", position="ST", target_ability=75.0)
    seller = _create_test_club("c1", squad=[player])
    buyer1 = _create_test_club("c2", squad=[])
    buyer2 = _create_test_club("c3", squad=[])
    contract = _create_sample_contract()

    off1 = _create_sample_offer(offer_id="off1", player_id="p1", selling_club_id="c1", buying_club_id="c2")
    dec1 = _create_accepted_decision(offer_id="off1", player_id="p1", selling_club_id="c1", buying_club_id="c2")

    off2 = _create_sample_offer(offer_id="off2", player_id="p1", selling_club_id="c1", buying_club_id="c3")
    dec2 = _create_accepted_decision(offer_id="off2", player_id="p1", selling_club_id="c1", buying_club_id="c3")

    app1 = create_transfer_application(dec1, off1, season=2027, application_id="app1")
    app2 = create_transfer_application(dec2, off2, season=2027, application_id="app2")

    result = apply_transfers(
        clubs=[seller, buyer1, buyer2],
        contracts={"p1": contract},
        applications=[app1, app2],
        season=2027,
    )

    # Exactly one application APPLIED, second CONFLICT
    applied = [a for a in result.applications if a.status == TransferApplicationStatus.APPLIED]
    conflict = [a for a in result.applications if a.status == TransferApplicationStatus.CONFLICT]

    assert len(applied) == 1
    assert len(conflict) == 1
    assert len(result.history_records) == 1


def test_conflict_wrong_seller():
    player = generate_player(seed=1, player_id="p1", position="ST", target_ability=75.0)
    c1 = _create_test_club("c1", squad=[player])
    c2 = _create_test_club("c2", squad=[])
    c3 = _create_test_club("c3", squad=[])
    contract = _create_sample_contract()

    # Claiming seller is c2, but player belongs to c1
    off = _create_sample_offer(offer_id="off1", player_id="p1", selling_club_id="c2", buying_club_id="c3")
    dec = _create_accepted_decision(offer_id="off1", player_id="p1", selling_club_id="c2", buying_club_id="c3")

    app = create_transfer_application(dec, off, season=2027)

    result = apply_transfers(
        clubs=[c1, c2, c3],
        contracts={"p1": contract},
        applications=[app],
        season=2027,
    )

    assert result.applications[0].status == TransferApplicationStatus.CONFLICT
    assert len(result.history_records) == 0


def test_idempotent_duplicate_application():
    player = generate_player(seed=1, player_id="p1", position="ST", target_ability=75.0)
    seller = _create_test_club("c1", squad=[player])
    buyer = _create_test_club("c2", squad=[])
    contract = _create_sample_contract()

    off = _create_sample_offer()
    dec = _create_accepted_decision()
    app1 = create_transfer_application(dec, off, season=2027, application_id="app1")
    app2 = create_transfer_application(dec, off, season=2027, application_id="app1") # Duplicate ID

    result = apply_transfers(
        clubs=[seller, buyer],
        contracts={"p1": contract},
        applications=[app1, app2],
        season=2027,
    )

    statuses = [a.status for a in result.applications]
    assert TransferApplicationStatus.APPLIED in statuses
    assert TransferApplicationStatus.DUPLICATE in statuses
    assert len(result.history_records) == 1


# ------------------------------------------------------------------
# 4. Immutability & Determinism Tests
# ------------------------------------------------------------------

def test_input_immutability():
    player = generate_player(seed=1, player_id="p1", position="ST", target_ability=75.0)
    seller = _create_test_club("c1", squad=[player])
    buyer = _create_test_club("c2", squad=[])
    contract = _create_sample_contract()

    off = _create_sample_offer()
    dec = _create_accepted_decision()
    app = create_transfer_application(dec, off, season=2027)

    clubs_dict = {"c1": seller, "c2": buyer}
    contracts_dict = {"p1": contract}
    apps_list = [app]

    clubs_copy = copy.deepcopy(clubs_dict)
    contracts_copy = copy.deepcopy(contracts_dict)
    apps_copy = copy.deepcopy(apps_list)

    apply_transfers(
        clubs=clubs_dict,
        contracts=contracts_dict,
        applications=apps_list,
        season=2027,
    )

    assert clubs_dict == clubs_copy
    assert contracts_dict == contracts_copy
    assert apps_list == apps_copy


def test_repeated_execution_determinism():
    player1 = generate_player(seed=1, player_id="p1", position="ST", target_ability=75.0)
    player2 = generate_player(seed=2, player_id="p2", position="CB", target_ability=80.0)

    seller = _create_test_club("c1", squad=[player1, player2])
    buyer1 = _create_test_club("c2", squad=[])
    buyer2 = _create_test_club("c3", squad=[])

    off1 = _create_sample_offer(offer_id="off1", player_id="p1", selling_club_id="c1", buying_club_id="c2")
    dec1 = _create_accepted_decision(offer_id="off1", player_id="p1", selling_club_id="c1", buying_club_id="c2")

    off2 = _create_sample_offer(offer_id="off2", player_id="p2", selling_club_id="c1", buying_club_id="c3")
    dec2 = _create_accepted_decision(offer_id="off2", player_id="p2", selling_club_id="c1", buying_club_id="c3")

    app1 = create_transfer_application(dec1, off1, season=2027, application_id="app1")
    app2 = create_transfer_application(dec2, off2, season=2027, application_id="app2")

    contracts = {"p1": _create_sample_contract(), "p2": _create_sample_contract()}

    baseline = apply_transfers([seller, buyer1, buyer2], contracts, [app2, app1], season=2027)

    for _ in range(100):
        res = apply_transfers([seller, buyer1, buyer2], contracts, [app2, app1], season=2027)
        assert res.applications == baseline.applications
        assert res.history_records == baseline.history_records
        assert res.updated_contracts == baseline.updated_contracts
        for k in res.updated_clubs:
            assert [p.id for p in res.updated_clubs[k].squad] == [p.id for p in baseline.updated_clubs[k].squad]
