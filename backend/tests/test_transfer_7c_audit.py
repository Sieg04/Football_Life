from datetime import date
from statistics import mean, median

from app.player.generation import generate_player
from app.transfer.contracts import ContractState
from app.transfer.domain import TransferWindow
from app.transfer.offers import generate_transfer_offers
from app.world.entities import Club, Manager


def test_transfer_7c_market_offer_audit():
    eval_date = date(2025, 7, 1)

    # Construct synthetic world with 10 selling clubs and 10 buying clubs across tiers
    selling_clubs = []
    buying_clubs = []
    all_players = []
    contracts = {}

    for c_idx in range(10):
        s_prestige = 30.0 + c_idx * 6.0
        b_prestige = 35.0 + c_idx * 6.0

        s_mgr = Manager(f"SMgr {c_idx}", 50, 50, 50, 50, 50, "BALANCED", 50, 50)
        b_mgr = Manager(f"BMgr {c_idx}", 50, 50, 50, 50, 50, "BALANCED", 50, 50)

        s_squad = []
        for p_idx in range(10):
            pid = f"s_c{c_idx}_p{p_idx}"
            target_ca = 45.0 + (c_idx * 3.5) + (p_idx * 1.5)
            p = generate_player(seed=c_idx * 100 + p_idx, player_id=pid, target_ability=target_ca)
            s_squad.append(p)
            all_players.append(p)

            # Assign contract
            contracts[pid] = ContractState(
                contract_start=date(2023, 7, 1),
                contract_end=date(2026 + (p_idx % 3), 6, 30),
                wage_band=2000.0 + target_ca * 100.0,
            )

        seller = Club(
            name=f"Seller Club {c_idx}",
            country_code="ENG",
            league_code="ENG1",
            manager=s_mgr,
            prestige=s_prestige,
            financial_power=s_prestige,
            academy_quality=50,
            facilities=50,
            fan_pressure=50,
            squad_depth=50,
            uefa_coefficient_raw=0,
            uefa_coefficient_normalized=0,
            domestic_reputation=s_prestige,
            international_reputation=s_prestige,
            squad=tuple(s_squad),
        )
        selling_clubs.append(seller)

        buyer = Club(
            name=f"Buyer Club {c_idx}",
            country_code="ENG",
            league_code="ENG1",
            manager=b_mgr,
            prestige=b_prestige,
            financial_power=b_prestige,
            academy_quality=50,
            facilities=50,
            fan_pressure=50,
            squad_depth=50,
            uefa_coefficient_raw=0,
            uefa_coefficient_normalized=0,
            domestic_reputation=b_prestige,
            international_reputation=b_prestige,
            squad=(),
        )
        buying_clubs.append(buyer)

    offers = generate_transfer_offers(
        selling_clubs=selling_clubs,
        buying_clubs=buying_clubs,
        players=all_players,
        contracts=contracts,
        evaluation_date=eval_date,
        window=TransferWindow.SUMMER_WINDOW,
        seed="audit_7c_seed",
    )

    print(f"\n--- PHASE 7C TRANSFER OFFER AUDIT (Generated {len(offers)} offers) ---")
    fees = [o.transfer_fee for o in offers]
    wages = [o.wage_offer for o in offers]

    if fees:
        print(f"Fee Min: €{min(fees):,.0f}")
        print(f"Fee Median: €{median(fees):,.0f}")
        print(f"Fee Max: €{max(fees):,.0f}")
        print(f"Fee Mean: €{mean(fees):,.0f}")
        print(f"Wage Median: €{median(wages):,.2f}")

    assert 0 < len(offers) <= 50  # 10 buyers * max 5 targets per club
    assert all(o.buying_club_id != o.selling_club_id for o in offers)
    assert all(o.transfer_fee >= 10000.0 for o in offers)
    assert all(o.wage_offer >= 1000.0 for o in offers)
    assert all(1 <= o.contract_years <= 5 for o in offers)
    assert all(o.structured_reason is not None for o in offers)
