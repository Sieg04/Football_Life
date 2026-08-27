import json
import subprocess
import sys
from datetime import date

from app.player.generation import generate_player
from app.transfer.application import apply_transfers, create_transfer_application
from app.transfer.contracts import generate_initial_contract
from app.transfer.decisions import resolve_competing_offers, resolve_transfer_offer
from app.transfer.domain import TransferApplicationStatus
from app.transfer.offers import generate_transfer_offers
from app.world.entities import Club, Manager


def _create_synthetic_world(num_clubs: int = 10, players_per_club: int = 15):
    clubs = []
    all_players = []
    contracts = {}

    for c_idx in range(num_clubs):
        club_id = f"club_{c_idx + 1}"
        squad = []
        for p_idx in range(players_per_club):
            player_id = f"p_{c_idx + 1}_{p_idx + 1}"
            pos = ["GK", "CB", "LB", "RB", "CM", "CAM", "LW", "RW", "ST"][p_idx % 9]
            target_ca = min(92.0, 55.0 + (c_idx * 2.5) + (p_idx % 5) * 1.5)
            player = generate_player(seed=c_idx * 100 + p_idx, player_id=player_id, position=pos, target_ability=target_ca)
            squad.append(player)
            all_players.append(player)

            contract = generate_initial_contract(player, club_prestige=50.0 + c_idx * 4.0, seed=f"contract_{player_id}")
            contracts[player_id] = contract

        mgr = Manager(
            name=f"Manager_{club_id}",
            tactical_quality=65.0,
            player_development=65.0,
            game_management=65.0,
            rotation=50.0,
            adaptability=50.0,
            tactical_style="BALANCED",
            youth_preference=50.0,
            discipline=50.0,
        )

        prestige = 40.0 + c_idx * 5.0
        club = Club(
            name=f"Club {club_id}",
            country_code="ENG",
            league_code="ENG1",
            manager=mgr,
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
        clubs.append(club)

    return clubs, all_players, contracts


def test_transfer_7e_large_scale_audit():
    clubs, players, contracts = _create_synthetic_world(num_clubs=12, players_per_club=15)
    total_players_initial = len(players)
    total_clubs_initial = len(clubs)

    # 1. Generate Phase 7C Offers
    offers = generate_transfer_offers(
        selling_clubs=clubs,
        buying_clubs=clubs,
        players=players,
        contracts=contracts,
        evaluation_date=date(2027, 7, 15),
        seed="audit_7e_seed",
    )
    assert len(offers) > 0

    # 2. Resolve Phase 7D Decisions
    decisions = resolve_competing_offers(
        offers=offers,
        players=players,
        clubs=clubs,
        contracts=contracts,
        evaluation_date=date(2027, 7, 15),
    )
    assert len(decisions) == len(offers)

    offer_map = {o.id: o for o in offers}
    applications = [create_transfer_application(d, offer_map[d.offer_id], season=2027) for d in decisions]

    # 3. Apply Phase 7E Transfers
    result = apply_transfers(
        clubs=clubs,
        contracts=contracts,
        applications=applications,
        season=2027,
    )

    # --- INVARIANT ASSERIONS ---
    applied_count = len(result.history_records)
    applied_apps = [a for a in result.applications if a.status == TransferApplicationStatus.APPLIED]
    assert len(applied_apps) == applied_count

    # Club Conservation
    assert len(result.updated_clubs) == total_clubs_initial

    # Player Conservation & Uniqueness across squads
    player_club_map = {}
    total_players_after = 0
    for c_id, c in result.updated_clubs.items():
        total_players_after += len(c.squad)
        for p in c.squad:
            assert p.id not in player_club_map, f"Player {p.id} appears in multiple clubs!"
            player_club_map[p.id] = c_id

    assert total_players_after == total_players_initial

    # Transfer Conservation
    for record in result.history_records:
        assert record.status == TransferApplicationStatus.APPLIED
        p_id = record.player_id
        # Player belongs to buyer
        assert player_club_map[p_id] == record.buyer_club_id
        # Contract updated
        new_c = result.updated_contracts[p_id]
        assert new_c.wage_band == record.wage
        assert new_c.contract_start == date(2027, 7, 1)


def test_transfer_7e_cross_process_determinism():
    code = """
import json
from datetime import date
from app.player.generation import generate_player
from app.world.entities import Club, Manager
from app.transfer.domain import ContractState, TransferOffer, TransferDecision, OfferDecisionStatus, PlayerDecision, ClubDecision
from app.transfer.application import create_transfer_application, apply_transfers

player = generate_player(seed=42, player_id="p42", position="ST", target_ability=78.0)
mgr = Manager("M", 50, 50, 50, 50, 50, "BALANCED", 50, 50)
seller = Club("Seller", "ENG", "ENG1", mgr, 50, 50, 50, 50, 50, 50, 0, 0, 50, 50, squad=(player,))
object.__setattr__(seller, "id", "c1")
buyer = Club("Buyer", "ENG", "ENG1", mgr, 70, 70, 50, 50, 50, 50, 0, 0, 70, 70)
object.__setattr__(buyer, "id", "c2")

contract = ContractState(contract_start=date(2024, 7, 1), contract_end=date(2027, 6, 30), wage_band=5000.0)

dec = TransferDecision(
    offer_id="off_sub",
    player_id="p42",
    buying_club_id="c2",
    selling_club_id="c1",
    status=OfferDecisionStatus.ACCEPTED,
    player_decision=PlayerDecision(accepted=True, score=85.0),
    club_decision=ClubDecision(accepted=True, score=85.0),
)
offer = TransferOffer(
    id="off_sub", player_id="p42", selling_club_id="c1", buying_club_id="c2",
    transfer_fee=20000000.0, wage_offer=15000.0, contract_years=4,
    structured_reason=PlayerDecision(accepted=True, score=85.0).reasons[0] if PlayerDecision(accepted=True, score=85.0).reasons else "STARTING_ROLE", seed="s1"
)

app = create_transfer_application(dec, offer, season=2027)
res = apply_transfers([seller, buyer], {"p42": contract}, [app], season=2027)

out = {
    "applied_count": len(res.history_records),
    "buyer_squad": [p.id for p in res.updated_clubs["c2"].squad],
    "seller_squad": [p.id for p in res.updated_clubs["c1"].squad],
    "contract_end": str(res.updated_contracts["p42"].contract_end)
}
print(json.dumps(out))
"""

    cmd = [sys.executable, "-c", code]
    res1 = subprocess.run(cmd, capture_output=True, text=True, check=True, env={"PYTHONPATH": "backend"})
    res2 = subprocess.run(cmd, capture_output=True, text=True, check=True, env={"PYTHONPATH": "backend"})

    assert res1.stdout == res2.stdout
    data = json.loads(res1.stdout)
    assert data["applied_count"] == 1
    assert data["buyer_squad"] == ["p42"]
    assert data["seller_squad"] == []
    assert data["contract_end"] == "2031-06-30"
