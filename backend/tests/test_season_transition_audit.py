from datetime import date
import pytest

from app.player.generation import generate_player
from app.transfer.domain import (
    ContractState,
    OfferDecisionStatus,
    TransferDecision,
    TransferOffer,
    PlayerDecision,
    ClubDecision,
    StructuredReason,
)
from app.transfer.application import create_transfer_application
from app.world.data import generate_world, World
from app.world.entities import CompetitionType
from app.world.season import transition_to_next_season, validate_world_state


def build_synthetic_large_world(seed: int = 999) -> World:
    definitions = {
        "countries": [
            {"code": "ENG", "name": "England", "fifa_rank": 1, "fifa_points": 1800, "national_strength": 90.0},
            {"code": "ESP", "name": "Spain", "fifa_rank": 2, "fifa_points": 1750, "national_strength": 88.0},
            {"code": "GER", "name": "Germany", "fifa_rank": 3, "fifa_points": 1720, "national_strength": 86.0},
            {"code": "ITA", "name": "Italy", "fifa_rank": 4, "fifa_points": 1700, "national_strength": 85.0},
        ],
        "leagues": [
            {"code": "ENG1", "name": "Premier League", "country_code": "ENG", "tier": 1, "prestige": 90.0, "financial_strength": 90.0, "european_performance": 85.0, "global_reputation": 95.0},
            {"code": "ESP1", "name": "La Liga", "country_code": "ESP", "tier": 1, "prestige": 88.0, "financial_strength": 85.0, "european_performance": 88.0, "global_reputation": 92.0},
            {"code": "GER1", "name": "Bundesliga", "country_code": "GER", "tier": 1, "prestige": 85.0, "financial_strength": 84.0, "european_performance": 82.0, "global_reputation": 88.0},
            {"code": "ITA1", "name": "Serie A", "country_code": "ITA", "tier": 1, "prestige": 84.0, "financial_strength": 80.0, "european_performance": 80.0, "global_reputation": 86.0},
        ],
        "clubs": [
            {
                "name": f"Club_{i}",
                "country_code": ["ENG", "ESP", "GER", "ITA"][i % 4],
                "league_code": [ "ENG1", "ESP1", "GER1", "ITA1" ][i % 4],
                "target_strength": 75.0 + (i % 15),
                "prestige": 70.0 + (i % 20),
                "financial_power": 70.0 + (i % 20),
                "academy_quality": 70.0 + (i % 15),
                "facilities": 75.0 + (i % 15),
                "fan_pressure": 65.0 + (i % 25),
                "uefa_coefficient_raw": 60.0 + (i % 30),
                "domestic_reputation": 70.0 + (i % 20),
                "international_reputation": 65.0 + (i % 25),
                "momentum": float((i % 20) - 10),
                "manager": {
                    "name": f"Manager_{i}",
                    "tactical_quality": 75,
                    "player_development": 75,
                    "game_management": 75,
                    "rotation": 75,
                    "adaptability": 75,
                    "tactical_style": "BALANCED",
                    "youth_preference": 75,
                    "discipline": 75,
                },
            }
            for i in range(12)
        ],
        "competitions": [
            {"name": "EPL", "competition_type": CompetitionType.LEAGUE, "country_code": "ENG", "tier": 1, "prestige": 90.0, "strength": 88.0},
            {"name": "La Liga", "competition_type": CompetitionType.LEAGUE, "country_code": "ESP", "tier": 1, "prestige": 88.0, "strength": 86.0},
            {"name": "Champions League", "competition_type": CompetitionType.EUROPEAN, "country_code": None, "tier": 1, "prestige": 100.0, "strength": 95.0},
        ],
    }
    return generate_world(seed=seed, definitions=definitions)


def test_large_scale_season_transition_audit():
    world = build_synthetic_large_world(seed=888)

    # Initial validation
    validate_world_state(world)

    # Collect initial total player count and mapping
    initial_players: set[str] = set()
    player_club_map: dict[str, str] = {}
    for club in world.clubs:
        for p in club.squad:
            initial_players.add(p.id)
            player_club_map[p.id] = club.name

    contracts = {
        p_id: ContractState(contract_start=date(2023, 7, 1), contract_end=date(2027, 6, 30), wage_band=25000.0)
        for p_id in initial_players
    }

    # Generate 3 valid transfer applications between distinct clubs
    c0 = world.clubs[0]
    c1 = world.clubs[1]
    c2 = world.clubs[2]
    c3 = world.clubs[3]

    p0 = c0.squad[0]
    p1 = c1.squad[0]
    p2 = c2.squad[0]

    offers = [
        TransferOffer(id="o1", player_id=p0.id, selling_club_id=c0.name, buying_club_id=c1.name, transfer_fee=20000000.0, wage_offer=30000.0, contract_years=3, structured_reason=StructuredReason.DEPTH, seed="s1"),
        TransferOffer(id="o2", player_id=p1.id, selling_club_id=c1.name, buying_club_id=c2.name, transfer_fee=15000000.0, wage_offer=25000.0, contract_years=3, structured_reason=StructuredReason.DEPTH, seed="s2"),
        TransferOffer(id="o3", player_id=p2.id, selling_club_id=c2.name, buying_club_id=c3.name, transfer_fee=25000000.0, wage_offer=40000.0, contract_years=3, structured_reason=StructuredReason.DEPTH, seed="s3"),
    ]
    decisions = [
        TransferDecision(offer_id="o1", player_id=p0.id, selling_club_id=c0.name, buying_club_id=c1.name, status=OfferDecisionStatus.ACCEPTED, player_decision=PlayerDecision(accepted=True, score=80.0), club_decision=ClubDecision(accepted=True, score=80.0)),
        TransferDecision(offer_id="o2", player_id=p1.id, selling_club_id=c1.name, buying_club_id=c2.name, status=OfferDecisionStatus.ACCEPTED, player_decision=PlayerDecision(accepted=True, score=80.0), club_decision=ClubDecision(accepted=True, score=80.0)),
        TransferDecision(offer_id="o3", player_id=p2.id, selling_club_id=c2.name, buying_club_id=c3.name, status=OfferDecisionStatus.ACCEPTED, player_decision=PlayerDecision(accepted=True, score=80.0), club_decision=ClubDecision(accepted=True, score=80.0)),
    ]
    apps = [create_transfer_application(d, o, season=2025) for d, o in zip(decisions, offers)]

    # Execute season transition
    res = transition_to_next_season(
        world=world,
        current_season=2025,
        contracts=contracts,
        applications=apps,
    )

    # 1. Verify season advancement
    assert res.previous_season_id == "2025"
    assert res.next_season_id == "2026"

    # 2. Verify total player set remains identical (no lost or duplicated players)
    final_players: set[str] = set()
    final_player_club_map: dict[str, str] = {}
    for club in res.world.clubs:
        for p in club.squad:
            assert p.id not in final_players, f"Player {p.id} appears in multiple clubs!"
            final_players.add(p.id)
            final_player_club_map[p.id] = club.name

    assert initial_players == final_players, "Player population changed during season transition!"

    # 3. Verify transferred players moved to exactly 1 new club
    assert final_player_club_map[p0.id] == c1.name
    assert final_player_club_map[p1.id] == c2.name
    assert final_player_club_map[p2.id] == c3.name

    # 4. Verify historical transfer records preserved
    assert len(res.history_records) == 3
    for hist in res.history_records:
        assert hist.season == 2025
        assert hist.applied_date == date(2026, 7, 1)

    # 5. Verify world state validation passes
    validate_world_state(res.world, res.updated_contracts)
