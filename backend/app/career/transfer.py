import hashlib
import random
from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any

from app.career.context import ClubContext, SquadPlayingRole, build_club_context
from app.career.reputation import CareerReputation, calculate_reputation


class TransferType(StrEnum):
    PERMANENT = "PERMANENT"
    LOAN = "LOAN"


class CareerImpact(StrEnum):
    MAJOR_STEP_UP = "MAJOR_STEP_UP"
    PROGRESSION = "PROGRESSION"
    LATERAL_MOVE = "LATERAL_MOVE"
    STEP_DOWN = "STEP_DOWN"


@dataclass(frozen=True)
class TransferOffer:
    offer_id: str
    destination_club_id: str
    destination_club_name: str
    country_code: str
    league_code: str
    league_name: str
    club_prestige: float
    league_prestige: float
    transfer_type: TransferType
    transfer_fee: int
    weekly_salary: int
    contract_years: int
    proposed_role: SquadPlayingRole
    expected_playing_time: str
    career_impact: CareerImpact
    interest_reason: str
    offer_score: float


@dataclass(frozen=True)
class TransferMarketResult:
    available_offers: tuple[TransferOffer, ...]
    stay_option_role: SquadPlayingRole
    stay_option_salary: int
    market_interest_score: float


def generate_transfer_offers(
    player_id: str,
    player_ovr: float,
    age: int,
    position: str,
    current_club_id: str,
    reputation: CareerReputation,
    season_number: int,
    seed: str,
    world_clubs: list[dict[str, Any]] | None = None,
    world_leagues: list[dict[str, Any]] | None = None,
) -> TransferMarketResult:
    """Generates contextual transfer and loan offers for the player."""
    current_ctx = build_club_context(current_club_id, world_clubs, world_leagues)

    seed_hash = hashlib.sha256(f"{seed}:transfer:{player_id}:{season_number}".encode("utf-8")).hexdigest()
    rng = random.Random(int(seed_hash[:16], 16))

    market_score = min(100.0, max(10.0, (reputation.overall_prestige * 0.5) + (player_ovr * 0.3) + ((28 - age) * 1.5)))

    offers: list[TransferOffer] = []
    available_clubs = world_clubs if world_clubs else []

    # Filter eligible destination clubs
    candidate_clubs = [c for c in available_clubs if str(c.get("name")) != current_ctx.club_name and str(c.get("id")) != current_ctx.club_id]

    if not candidate_clubs:
        # Fallback dummy candidate clubs
        candidate_clubs = [
            {"id": "club_ars", "name": "Arsenal", "country_code": "ENG", "league_code": "ENG1", "prestige": 88.0, "target_strength": 86.0},
            {"id": "club_atm", "name": "Atlético Madrid", "country_code": "ESP", "league_code": "ESP1", "prestige": 86.0, "target_strength": 84.0},
            {"id": "club_sev", "name": "Sevilla", "country_code": "ESP", "league_code": "ESP1", "prestige": 78.0, "target_strength": 78.0},
        ]

    # Pick up to 3 suitable candidate clubs based on market score and prestige proximity
    scored_candidates = []
    for c in candidate_clubs:
        p = float(c.get("prestige", 70.0))
        diff = abs(p - current_ctx.club_prestige)
        if diff <= 25.0 or (market_score > 75.0 and p > current_ctx.club_prestige):
            scored_candidates.append(c)

    rng.shuffle(scored_candidates)
    selected_candidates = scored_candidates[:3]

    for idx, c in enumerate(selected_candidates):
        dest_name = c.get("name", f"Club {idx+1}")
        dest_id = str(c.get("id", dest_name))
        c_code = c.get("country_code", "ESP")
        l_code = c.get("league_code", "ESP1")
        c_prestige = float(c.get("prestige", 75.0))
        l_prestige = c_prestige * 0.95

        is_loan = (age <= 21 and player_ovr < c_prestige - 10) or (player_ovr < 70 and c_prestige > 80)
        t_type = TransferType.LOAN if is_loan else TransferType.PERMANENT

        # Role calculation
        ovr_diff = player_ovr - (c_prestige * 0.95)
        if ovr_diff >= 4:
            role = SquadPlayingRole.STARTER
            role_desc = "Regular Starter"
        elif ovr_diff >= -3:
            role = SquadPlayingRole.ROTATION
            role_desc = "Rotation Player"
        else:
            role = SquadPlayingRole.BACKUP
            role_desc = "Backup / Squad Player"

        # Fee & Salary calculation
        base_fee = int(max(1000000, (player_ovr ** 3.8) * 1.5 * (1.2 if age < 24 else 0.9)))
        fee = 0 if is_loan else int(round(base_fee, -5))
        salary = int(round(max(5000, (player_ovr * 1800) + (c_prestige * 1200)), -3))

        # Career impact
        p_diff = c_prestige - current_ctx.club_prestige
        if p_diff >= 10.0:
            impact = CareerImpact.MAJOR_STEP_UP
            reason = f"Impressionable performances that warrant a major move to a European giant."
        elif p_diff >= 3.0:
            impact = CareerImpact.PROGRESSION
            reason = f"Strong consistency making you an ideal target to strengthen their squad."
        elif p_diff >= -5.0:
            impact = CareerImpact.LATERAL_MOVE
            reason = f"Seeking a fresh challenge with similar competition standards."
        else:
            impact = CareerImpact.STEP_DOWN
            reason = f"Offering guaranteed first-team minutes and key player status."

        offer_id = f"off_{hashlib.sha256(f'{seed}:{player_id}:{dest_id}:{season_number}'.encode('utf-8')).hexdigest()[:12]}"

        offers.append(
            TransferOffer(
                offer_id=offer_id,
                destination_club_id=dest_id,
                destination_club_name=dest_name,
                country_code=c_code,
                league_code=l_code,
                league_name=l_code,
                club_prestige=c_prestige,
                league_prestige=l_prestige,
                transfer_type=t_type,
                transfer_fee=fee,
                weekly_salary=salary,
                contract_years=1 if is_loan else (4 if age < 25 else 3),
                proposed_role=role,
                expected_playing_time=role_desc,
                career_impact=impact,
                interest_reason=reason,
                offer_score=round(c_prestige + (10 if role == SquadPlayingRole.STARTER else 0), 1),
            )
        )

    stay_role = SquadPlayingRole.STARTER if player_ovr >= current_ctx.squad_quality else SquadPlayingRole.ROTATION
    stay_salary = int(round(max(5000, (player_ovr * 1600) + (current_ctx.club_prestige * 1000)), -3))

    return TransferMarketResult(
        available_offers=tuple(offers),
        stay_option_role=stay_role,
        stay_option_salary=stay_salary,
        market_interest_score=round(market_score, 1),
    )
