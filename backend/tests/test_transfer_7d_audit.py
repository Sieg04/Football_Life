from datetime import date
from app.player.generation import generate_player
from app.transfer.contracts import generate_initial_contract
from app.transfer.decisions import resolve_competing_offers
from app.transfer.domain import OfferDecisionStatus
from app.transfer.offers import generate_transfer_offers
from app.world.entities import Club, Manager


def _create_test_club(club_id: str, squad=None, prestige=60.0) -> Club:
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
        squad=tuple(squad) if squad else (),
    )
    object.__setattr__(club, "id", club_id)
    return club


def test_transfer_7d_distribution_audit():
    clubs = [
        _create_test_club(club_id=f"c{i}", prestige=30.0 + i * 12.0)
        for i in range(1, 7)
    ]

    players = []
    contracts = {}
    club_squads = {c.name: [] for c in clubs}

    for i in range(1, 21):
        p_id = f"p{i}"
        club_idx = (i % 6)
        owner_club = clubs[club_idx]
        target_ability = 55.0 + (i * 1.8)
        pos = ["ST", "CM", "CB", "LW", "GK"][i % 5]

        player = generate_player(
            seed=i,
            player_id=p_id,
            position=pos,
            target_ability=target_ability,
        )
        players.append(player)
        club_squads[owner_club.name].append(player)

        contract = generate_initial_contract(player, owner_club.prestige, evaluation_date=date(2025, 7, 1))
        contracts[p_id] = contract

    # Re-instantiate clubs with squad tuples
    updated_clubs = []
    for c in clubs:
        sq = club_squads[c.name]
        updated_clubs.append(_create_test_club(club_id=c.name.replace("Club ", "c"), squad=sq, prestige=c.prestige))

    # Generate transfer offers
    offers = generate_transfer_offers(
        selling_clubs=updated_clubs,
        buying_clubs=updated_clubs,
        players=players,
        contracts=contracts,
        evaluation_date=date(2025, 7, 1),
        seed="audit_seed_7d",
    )

    assert len(offers) > 0

    # Resolve decisions
    decisions = resolve_competing_offers(
        offers=offers,
        players=players,
        clubs=updated_clubs,
        contracts=contracts,
        evaluation_date=date(2025, 7, 1),
    )

    assert len(decisions) == len(offers)

    # Count outcomes
    counts = {
        OfferDecisionStatus.ACCEPTED: 0,
        OfferDecisionStatus.PLAYER_REJECTED: 0,
        OfferDecisionStatus.CLUB_REJECTED: 0,
        OfferDecisionStatus.BOTH_REJECTED: 0,
        OfferDecisionStatus.COMPETING_OFFER_LOST: 0,
    }

    for dec in decisions:
        counts[dec.status] += 1
        assert 0.0 <= dec.player_decision.score <= 100.0
        assert 0.0 <= dec.club_decision.score <= 100.0

    total = sum(counts.values())
    assert total == len(offers)
