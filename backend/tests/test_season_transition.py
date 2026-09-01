import os
import subprocess
import json
from datetime import date
import pytest

from app.player.generation import generate_player
from app.transfer.domain import (
    ContractState,
    OfferDecisionStatus,
    TransferApplication,
    TransferDecision,
    TransferOffer,
    PlayerDecision,
    ClubDecision,
    StructuredReason,
)
from app.transfer.application import create_transfer_application
from app.world.data import generate_world, World
from app.world.entities import Club, Manager, Country, League, Competition, CompetitionType, SquadRole, ClubMembership
from app.world.season import (
    SeasonState,
    SeasonTransition,
    SeasonTransitionResult,
    SeasonTransitionStatus,
    advance_season,
    create_season_transition,
    transition_to_next_season,
    validate_world_state,
)


def build_test_world(seed: int = 42) -> World:
    definitions = {
        "countries": [
            {"code": "ENG", "name": "England", "fifa_rank": 1, "fifa_points": 1800, "national_strength": 90.0},
            {"code": "ESP", "name": "Spain", "fifa_rank": 2, "fifa_points": 1750, "national_strength": 88.0},
        ],
        "leagues": [
            {"code": "ENG1", "name": "Premier League", "country_code": "ENG", "tier": 1, "prestige": 90.0, "financial_strength": 90.0, "european_performance": 85.0, "global_reputation": 95.0},
            {"code": "ESP1", "name": "La Liga", "country_code": "ESP", "tier": 1, "prestige": 88.0, "financial_strength": 85.0, "european_performance": 88.0, "global_reputation": 92.0},
        ],
        "clubs": [
            {
                "name": "Arsenal",
                "country_code": "ENG",
                "league_code": "ENG1",
                "target_strength": 85.0,
                "prestige": 88.0,
                "financial_power": 85.0,
                "academy_quality": 80.0,
                "facilities": 85.0,
                "fan_pressure": 75.0,
                "uefa_coefficient_raw": 80.0,
                "domestic_reputation": 85.0,
                "international_reputation": 80.0,
                "momentum": 15.0,
                "manager": {"name": "Arteta", "tactical_quality": 85, "player_development": 80, "game_management": 80, "rotation": 75, "adaptability": 75, "tactical_style": "BALANCED", "youth_preference": 75, "discipline": 80},
            },
            {
                "name": "Chelsea",
                "country_code": "ENG",
                "league_code": "ENG1",
                "target_strength": 82.0,
                "prestige": 85.0,
                "financial_power": 88.0,
                "academy_quality": 82.0,
                "facilities": 88.0,
                "fan_pressure": 80.0,
                "uefa_coefficient_raw": 78.0,
                "domestic_reputation": 82.0,
                "international_reputation": 82.0,
                "momentum": -10.0,
                "manager": {"name": "Maresca", "tactical_quality": 80, "player_development": 80, "game_management": 75, "rotation": 80, "adaptability": 75, "tactical_style": "BALANCED", "youth_preference": 80, "discipline": 75},
            },
        ],
        "competitions": [
            {"name": "Premier League", "competition_type": CompetitionType.LEAGUE, "country_code": "ENG", "tier": 1, "prestige": 90.0, "strength": 88.0},
        ],
    }
    return generate_world(seed=seed, definitions=definitions)


class TestSeasonAdvancement:
    def test_advance_season_integers(self):
        assert advance_season(2025) == 2026
        assert advance_season(2030) == 2031

    def test_advance_season_numeric_strings(self):
        assert advance_season("2025") == "2026"
        assert advance_season(" 2029 ") == "2030"

    def test_advance_season_slash_notation(self):
        assert advance_season("2025/26") == "2026/27"
        assert advance_season("2029/30") == "2030/31"
        assert advance_season("2025/2026") == "2026/2027"

    def test_advance_season_invalid_inputs(self):
        with pytest.raises(ValueError, match="cannot be empty or None"):
            advance_season("")
        with pytest.raises(ValueError, match="cannot be empty or None"):
            advance_season(None)
        with pytest.raises(ValueError, match="Invalid integer season year"):
            advance_season(-5)
        with pytest.raises(ValueError, match="Malformed season label"):
            advance_season("abc/xyz")
        with pytest.raises(ValueError, match="Malformed season label"):
            advance_season("2025/26/27")


class TestSeasonTransitionCreation:
    def test_create_season_transition(self):
        trans = create_season_transition("2025", "2026")
        assert trans.source_season_id == "2025"
        assert trans.target_season_id == "2026"
        assert trans.status == SeasonTransitionStatus.PENDING
        assert trans.transition_id == "trans_2025_to_2026"

    def test_invalid_season_transition_same_season(self):
        with pytest.raises(ValueError, match="must be different"):
            create_season_transition("2025", "2025")

    def test_invalid_season_transition_empty_id(self):
        with pytest.raises(ValueError, match="must be a non-empty string"):
            SeasonTransition(transition_id="", source_season_id="2025", target_season_id="2026")


class TestSeasonTransitionEngine:
    def test_transition_no_transfers(self):
        world = build_test_world(seed=123)
        assert world.clubs[0].momentum == 15.0
        assert world.clubs[1].momentum == -10.0

        res = transition_to_next_season(world, current_season="2025")
        assert res.previous_season_id == "2025"
        assert res.next_season_id == "2026"
        assert res.transition.status == SeasonTransitionStatus.COMPLETED
        assert res.applied_transfers_count == 0

        # Verify transient state reset
        for club in res.world.clubs:
            assert club.momentum == 0.0

        # Verify persistent properties remain
        assert res.world.clubs[0].prestige == 88.0
        assert res.world.clubs[1].prestige == 85.0

    def test_transition_with_applied_transfers(self):
        world = build_test_world(seed=456)
        seller = world.clubs[0]
        buyer = world.clubs[1]
        transferred_player = seller.squad[0]

        # Initial contracts
        contracts = {
            p.id: ContractState(
                contract_start=date(2023, 7, 1),
                contract_end=date(2026, 6, 30),
                wage_band=20000.0,
            )
            for c in world.clubs for p in c.squad
        }

        # Build transfer offer & decision
        offer = TransferOffer(
            id="off_100",
            player_id=transferred_player.id,
            selling_club_id=seller.name,
            buying_club_id=buyer.name,
            transfer_fee=35000000.0,
            wage_offer=45000.0,
            contract_years=3,
            structured_reason=StructuredReason.DEPTH,
            seed="seed100",
        )
        decision = TransferDecision(
            offer_id="off_100",
            player_id=transferred_player.id,
            selling_club_id=seller.name,
            buying_club_id=buyer.name,
            status=OfferDecisionStatus.ACCEPTED,
            player_decision=PlayerDecision(accepted=True, score=80.0),
            club_decision=ClubDecision(accepted=True, score=80.0),
        )
        app = create_transfer_application(decision, offer=offer, season=2025)

        res = transition_to_next_season(
            world=world,
            current_season=2025,
            contracts=contracts,
            applications=[app],
        )

        assert res.applied_transfers_count == 1
        assert res.previous_season_id == "2025"
        assert res.next_season_id == "2026"

        # Check player roster movement
        new_seller = next(c for c in res.world.clubs if c.name == seller.name)
        new_buyer = next(c for c in res.world.clubs if c.name == buyer.name)

        assert not any(p.id == transferred_player.id for p in new_seller.squad)
        assert any(p.id == transferred_player.id for p in new_buyer.squad)

        # Check updated contract
        new_contract = res.updated_contracts[transferred_player.id]
        assert new_contract.wage_band == 45000.0

    def test_immutability(self):
        world = build_test_world(seed=789)
        original_momentum = [c.momentum for c in world.clubs]
        original_squad_lens = [len(c.squad) for c in world.clubs]

        contracts = {
            p.id: ContractState(contract_start=date(2023, 7, 1), contract_end=date(2026, 6, 30), wage_band=20000.0)
            for c in world.clubs for p in c.squad
        }
        original_contracts = dict(contracts)

        res = transition_to_next_season(world, current_season=2025, contracts=contracts)

        # Confirm original input objects are untouched
        for idx, c in enumerate(world.clubs):
            assert c.momentum == original_momentum[idx]
            assert len(c.squad) == original_squad_lens[idx]

        assert contracts == original_contracts
        assert world is not res.world

    def test_double_transition_protection(self):
        world = build_test_world(seed=101)
        res1 = transition_to_next_season(world, current_season=2025)

        # Attempting to re-apply completed transition must fail
        with pytest.raises(ValueError, match="has already been completed"):
            transition_to_next_season(world, current_season=2025, transition=res1.transition)

    def test_determinism_100_runs(self):
        world = build_test_world(seed=202)
        contracts = {
            p.id: ContractState(contract_start=date(2023, 7, 1), contract_end=date(2026, 6, 30), wage_band=20000.0)
            for c in world.clubs for p in c.squad
        }

        res_first = transition_to_next_season(world, current_season=2025, contracts=contracts)
        first_club_squads = {c.name: [p.id for p in c.squad] for c in res_first.world.clubs}

        for _ in range(100):
            res_nth = transition_to_next_season(world, current_season=2025, contracts=contracts)
            nth_club_squads = {c.name: [p.id for p in c.squad] for c in res_nth.world.clubs}
            assert first_club_squads == nth_club_squads
            assert res_first.next_season_id == res_nth.next_season_id

    def test_cross_process_determinism(self):
        import sys

        cmd = [
            sys.executable,
            "-c",
            (
                "from app.world.season import transition_to_next_season, advance_season; "
                "from app.world.data import generate_world; "
                "from app.world.entities import CompetitionType; "
                "defs = {'countries': [{'code': 'ENG', 'name': 'England'}], 'leagues': [{'code': 'ENG1', 'name': 'EPL', 'country_code': 'ENG', 'tier': 1, 'prestige': 90, 'financial_strength': 90, 'european_performance': 85, 'global_reputation': 95}], 'clubs': [{'name': 'C1', 'country_code': 'ENG', 'league_code': 'ENG1', 'target_strength': 80, 'prestige': 80, 'financial_power': 80, 'academy_quality': 80, 'facilities': 80, 'fan_pressure': 80, 'uefa_coefficient_raw': 80, 'domestic_reputation': 80, 'international_reputation': 80, 'momentum': 5.0, 'manager': {'name': 'M1', 'tactical_quality': 80, 'player_development': 80, 'game_management': 80, 'rotation': 80, 'adaptability': 80, 'tactical_style': 'BALANCED', 'youth_preference': 80, 'discipline': 80}}], 'competitions': [{'name': 'C', 'competition_type': CompetitionType.LEAGUE, 'country_code': 'ENG', 'tier': 1, 'prestige': 80, 'strength': 80}]}; "
                "w = generate_world(seed=12, definitions=defs); "
                "res = transition_to_next_season(w, current_season=2025); "
                "print(f'{res.previous_season_id}->{res.next_season_id}|momo:{res.world.clubs[0].momentum}')"
            ),
        ]
        env = os.environ.copy()
        env["PYTHONPATH"] = "backend"

        out1 = subprocess.check_output(cmd, env=env).decode().strip()
        out2 = subprocess.check_output(cmd, env=env).decode().strip()

        assert out1 == "2025->2026|momo:0.0"
        assert out1 == out2
