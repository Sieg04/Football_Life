import hashlib
import json
from datetime import date
from pathlib import Path
from random import Random

from app.player.domain import Player
from app.player.engine import position_ovr
from app.transfer.contracts import calculate_contract_pressure, calculate_contract_status, calculate_contract_years_remaining
from app.transfer.domain import (
    ContractState,
    ContractStatus,
    MarketValue,
    StructuredReason,
    TransferCandidate,
    TransferOffer,
    TransferWindow,
)
from app.transfer.market import calculate_market_value
from app.world.entities import Club

RULES_PATH = Path(__file__).resolve().parents[2] / "data" / "rules" / "transfers.json"


def _load_transfer_rules() -> dict:
    if RULES_PATH.exists():
        return json.loads(RULES_PATH.read_text(encoding="utf-8"))
    return {}


def is_transfer_window_active(
    evaluation_date: date,
    window: TransferWindow = TransferWindow.SUMMER_WINDOW,
    rules: dict | None = None,
) -> bool:
    """Checks if evaluation_date falls inside a configured transfer window."""
    if rules is None:
        rules = _load_transfer_rules()

    window_cfg = rules.get("transfer_windows", {}).get(window.value, {})
    if not window_cfg:
        # Default summer: July 1 - Sept 1, winter: Jan 1 - Feb 1
        if window == TransferWindow.SUMMER_WINDOW:
            start_m, start_d = 7, 1
            end_m, end_d = 9, 1
        else:
            start_m, start_d = 1, 1
            end_m, end_d = 2, 1
    else:
        start_m = window_cfg.get("start_month", 7 if window == TransferWindow.SUMMER_WINDOW else 1)
        start_d = window_cfg.get("start_day", 1)
        end_m = window_cfg.get("end_month", 9 if window == TransferWindow.SUMMER_WINDOW else 2)
        end_d = window_cfg.get("end_day", 1)

    window_start = date(evaluation_date.year, start_m, start_d)
    window_end = date(evaluation_date.year, end_m, end_d)

    if window_start <= window_end:
        return window_start <= evaluation_date <= window_end
    else:
        # Handles wrap-around window
        return evaluation_date >= window_start or evaluation_date <= window_end


def _determine_structured_reason(
    player: Player,
    buyer: Club,
    seller: Club,
    contract: ContractState | None,
    evaluation_date: date,
) -> StructuredReason:
    pos = player.primary_position
    p_ovr = position_ovr(player, pos)

    # Check contract status
    if contract:
        status = calculate_contract_status(contract.contract_end, evaluation_date)
        if status in (ContractStatus.EXPIRING_SOON, ContractStatus.EXPIRED):
            return StructuredReason.CONTRACT_EXPIRY

    # Age check
    bdate = player.birth_date
    age = evaluation_date.year - bdate.year - ((evaluation_date.month, evaluation_date.day) < (bdate.month, bdate.day))
    if age <= 21 and player.potential >= p_ovr + 8.0:
        return StructuredReason.YOUTH_INVESTMENT

    # Buyer squad comparison
    buyer_squad = list(buyer.squad) if buyer.squad else []
    pos_ovrs = [position_ovr(p, pos) for p in buyer_squad if p.primary_position == pos or pos in p.secondary_positions]

    if not pos_ovrs:
        return StructuredReason.DEPTH
    best_buyer_ovr = max(pos_ovrs)

    if p_ovr > best_buyer_ovr + 3.0:
        return StructuredReason.STAR_REPLACEMENT if p_ovr >= 82.0 else StructuredReason.STARTING_ROLE
    elif p_ovr >= best_buyer_ovr - 2.0:
        return StructuredReason.STARTING_ROLE
    elif len(pos_ovrs) < 2:
        return StructuredReason.DEPTH
    else:
        return StructuredReason.VALUE_OPPORTUNITY


def generate_transfer_offer(
    candidate: TransferCandidate,
    buying_club: Club,
    selling_club: Club,
    player: Player,
    contract: ContractState | None = None,
    evaluation_date: date = date(2025, 7, 1),
    seed: str | None = None,
    rules: dict | None = None,
) -> TransferOffer:
    """Generates a deterministic TransferOffer for a TransferCandidate."""
    if candidate.buying_club_id == candidate.selling_club_id:
        raise ValueError("Buying club and selling club must be different")

    if rules is None:
        rules = _load_transfer_rules()

    og_rules = rules.get("offer_generation", {})

    seed_material = seed or f"{candidate.buying_club_id}:{candidate.selling_club_id}:{player.id}:{candidate.market_value}"
    seed_hash = hashlib.sha256(f"{seed_material}:offer".encode("utf-8")).hexdigest()
    rng = Random(int(seed_hash[:16], 16))

    market_val = candidate.market_value

    # Negotiation & Urgency factors
    min_neg = og_rules.get("min_negotiation_factor", 0.90)
    max_neg = og_rules.get("max_negotiation_factor", 1.25)
    neg_factor = rng.uniform(min_neg, max_neg)

    # Contract pressure factor
    if contract:
        pressure = calculate_contract_pressure(contract.contract_end, evaluation_date)
        # Higher pressure -> lower fee demand
        contract_fee_factor = 1.15 - (pressure / 200.0)
    else:
        contract_fee_factor = 1.00

    raw_fee = market_val * neg_factor * contract_fee_factor
    clamped_fee = max(10000.0, raw_fee)

    if clamped_fee >= 1000000.0:
        final_fee = round(clamped_fee / 10000.0) * 10000.0
    else:
        final_fee = round(clamped_fee / 1000.0) * 1000.0

    # Wage Offer
    current_wage = contract.wage_band if contract else 2000.0
    buyer_prestige = max(1.0, min(100.0, getattr(buying_club, "prestige", 50.0)))
    wage_bump = 1.10 + (buyer_prestige / 500.0) + rng.uniform(0.0, 0.10)
    wage_offer = round(max(current_wage * wage_bump, 1000.0), 2)

    # Contract Duration
    bdate = player.birth_date
    age = evaluation_date.year - bdate.year - ((evaluation_date.month, evaluation_date.day) < (bdate.month, bdate.day))
    if age <= 23:
        years = rng.choice((4, 5))
    elif age <= 29:
        years = rng.choice((3, 4, 5))
    elif age <= 32:
        years = rng.choice((2, 3))
    else:
        years = rng.choice((1, 2))

    # Structured reason
    reason = _determine_structured_reason(player, buying_club, selling_club, contract, evaluation_date)

    offer_id = f"offer_{seed_hash[:12]}"

    return TransferOffer(
        id=offer_id,
        player_id=player.id,
        selling_club_id=candidate.selling_club_id,
        buying_club_id=candidate.buying_club_id,
        transfer_fee=final_fee,
        wage_offer=wage_offer,
        contract_years=years,
        structured_reason=reason,
        seed=seed_hash[:16],
    )


def generate_transfer_offers(
    selling_clubs: list[Club],
    buying_clubs: list[Club],
    players: list[Player],
    contracts: dict[str, ContractState] | None = None,
    evaluation_date: date = date(2025, 7, 1),
    window: TransferWindow = TransferWindow.SUMMER_WINDOW,
    seed: str = "global_transfer_seed",
    rules: dict | None = None,
) -> list[TransferOffer]:
    """Coordinates generation of transfer offers across clubs and players deterministically."""
    if rules is None:
        rules = _load_transfer_rules()

    if not is_transfer_window_active(evaluation_date, window=window, rules=rules):
        return []

    if contracts is None:
        contracts = {}

    og_rules = rules.get("offer_generation", {})
    max_offers_per_player = og_rules.get("max_offers_per_player", 3)
    max_targets_per_club = og_rules.get("max_targets_per_club", 5)

    buyer_map = {getattr(c, "id", getattr(c, "name", idx)): c for idx, c in enumerate(buying_clubs)}
    seller_map = {getattr(c, "id", getattr(c, "name", idx)): c for idx, c in enumerate(selling_clubs)}
    player_map = {p.id: p for p in players}

    # Map player to selling club
    player_seller_map: dict[str, int | str] = {}
    for seller_id, club in seller_map.items():
        if club.squad:
            for p in club.squad:
                player_seller_map[p.id] = seller_id

    # Build candidates pool deterministically
    candidates: list[TransferCandidate] = []

    sorted_buyer_ids = sorted(buyer_map.keys(), key=lambda x: str(x))
    sorted_player_ids = sorted(player_map.keys(), key=lambda x: str(x))

    for buyer_id in sorted_buyer_ids:
        buyer = buyer_map[buyer_id]
        buyer_prestige = max(1.0, min(100.0, getattr(buyer, "prestige", 50.0)))

        for player_id in sorted_player_ids:
            seller_id = player_seller_map.get(player_id)
            if seller_id is None or seller_id == buyer_id:
                continue

            player = player_map[player_id]
            contract = contracts.get(player_id)
            mv = calculate_market_value(player, contract=contract, club=seller_map.get(seller_id), evaluation_date=evaluation_date, rules=rules)

            # Check financial / prestige feasibility
            if mv.value > (buyer_prestige * 3000000.0) + 15000000.0:
                continue

            # Calculate deterministic interest & priority
            p_ovr = position_ovr(player, player.primary_position)
            target_q = 45.0 + (buyer_prestige * 0.45)
            fit_score = max(0.0, min(100.0, 100.0 - abs(p_ovr - target_q) * 2.0))

            cand_seed = f"{seed}:{buyer_id}:{seller_id}:{player_id}"
            cand_hash = hashlib.sha256(cand_seed.encode("utf-8")).hexdigest()
            rng = Random(int(cand_hash[:16], 16))

            interest_score = max(0.0, min(100.0, fit_score * 0.8 + rng.uniform(0.0, 20.0)))
            priority_score = max(0.0, min(100.0, interest_score * 0.9 + (p_ovr / 2.0)))

            if interest_score >= og_rules.get("min_interest_score", 40.0):
                candidate = TransferCandidate(
                    player_id=player_id,
                    selling_club_id=seller_id,
                    buying_club_id=buyer_id,
                    market_value=mv.value,
                    fit_score=round(fit_score, 2),
                    interest_score=round(interest_score, 2),
                    priority_score=round(priority_score, 2),
                )
                candidates.append(candidate)

    # Sort candidates deterministically: priority_score DESC, interest_score DESC, player_id ASC, buying_club_id ASC
    candidates.sort(key=lambda c: (-c.priority_score, -c.interest_score, str(c.player_id), str(c.buying_club_id)))

    # Generate offers respecting limits
    player_offer_counts: dict[str, int] = {}
    club_target_counts: dict[str | int, int] = {}
    generated_offers: list[TransferOffer] = []
    seen_pairs: set[tuple[str | int, str]] = set()

    for cand in candidates:
        buyer_id = cand.buying_club_id
        p_id = cand.player_id

        if (buyer_id, p_id) in seen_pairs:
            continue
        if club_target_counts.get(buyer_id, 0) >= max_targets_per_club:
            continue
        if player_offer_counts.get(p_id, 0) >= max_offers_per_player:
            continue

        player = player_map[p_id]
        buyer = buyer_map[buyer_id]
        seller = seller_map[cand.selling_club_id]
        contract = contracts.get(p_id)

        offer_seed = f"{seed}:{buyer_id}:{cand.selling_club_id}:{p_id}"
        offer = generate_transfer_offer(
            candidate=cand,
            buying_club=buyer,
            selling_club=seller,
            player=player,
            contract=contract,
            evaluation_date=evaluation_date,
            seed=offer_seed,
            rules=rules,
        )

        generated_offers.append(offer)
        seen_pairs.add((buyer_id, p_id))
        club_target_counts[buyer_id] = club_target_counts.get(buyer_id, 0) + 1
        player_offer_counts[p_id] = player_offer_counts.get(p_id, 0) + 1

    # Sort final generated offers deterministically: transfer_fee DESC, player_id ASC, buying_club_id ASC
    generated_offers.sort(key=lambda o: (-o.transfer_fee, str(o.player_id), str(o.buying_club_id)))

    return generated_offers
