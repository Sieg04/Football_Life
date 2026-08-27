import hashlib
import math
from dataclasses import replace
from datetime import date
from random import Random

from app.player.domain import Player
from app.player.engine import position_ovr
from app.transfer.contracts import calculate_contract_pressure
from app.transfer.domain import (
    ClubDecision,
    ContractState,
    OfferDecisionStatus,
    PlayerDecision,
    StructuredReason,
    TransferDecision,
    TransferOffer,
)
from app.transfer.market import calculate_market_value
from app.transfer.offers import _load_transfer_rules
from app.world.entities import Club


def evaluate_player_decision(
    offer: TransferOffer,
    player: Player,
    buying_club: Club,
    selling_club: Club | None = None,
    contract: ContractState | None = None,
    evaluation_date: date = date(2025, 7, 1),
    rules: dict | None = None,
) -> PlayerDecision:
    """Evaluates whether a player accepts a transfer offer based on wage, prestige, playing time, and ambition."""
    if rules is None:
        rules = _load_transfer_rules()

    pd_rules = rules.get("player_decision", {})
    threshold = float(pd_rules.get("acceptance_threshold", 50.0))
    weights = pd_rules.get("weights", {})
    wage_w = float(weights.get("wage", 0.35))
    prestige_w = float(weights.get("prestige", 0.25))
    playing_time_w = float(weights.get("playing_time", 0.25))
    ambition_w = float(weights.get("ambition", 0.15))

    reasons: list[StructuredReason] = []

    # 1. Wage factor
    current_wage = contract.wage_band if contract else 2000.0
    wage_ratio = offer.wage_offer / max(1.0, current_wage)
    if wage_ratio >= 1.0:
        wage_score = min(100.0, 50.0 + (wage_ratio - 1.0) * 50.0)
    else:
        wage_score = max(0.0, wage_ratio * 50.0)

    if wage_score >= 60.0 or offer.wage_offer >= current_wage * 1.15:
        reasons.append(StructuredReason.PLAYER_WAGE)

    # 2. Destination prestige factor
    buying_prestige = float(getattr(buying_club, "prestige", 50.0))
    selling_prestige = float(getattr(selling_club, "prestige", 50.0)) if selling_club else 50.0
    prestige_diff = buying_prestige - selling_prestige
    prestige_score = max(0.0, min(100.0, 50.0 + prestige_diff * 1.0))

    if prestige_score >= 60.0 or prestige_diff >= 5.0:
        reasons.append(StructuredReason.DESTINATION_PRESTIGE)

    # 3. Playing time factor
    pos = player.primary_position
    p_ovr = position_ovr(player, pos)
    buyer_squad = list(buying_club.squad) if buying_club.squad else []
    pos_ovrs = [position_ovr(p, pos) for p in buyer_squad if p.primary_position == pos or pos in p.secondary_positions]

    if not pos_ovrs:
        playing_time_score = 90.0
    else:
        best_buyer_ovr = max(pos_ovrs)
        ovr_diff = p_ovr - best_buyer_ovr
        playing_time_score = max(0.0, min(100.0, 60.0 + ovr_diff * 5.0))

    if playing_time_score >= 60.0:
        reasons.append(StructuredReason.PLAYING_TIME)

    # 4. Ambition factor
    ambition_val = 50.0
    if hasattr(player, "personality") and isinstance(player.personality, dict):
        ambition_val = float(player.personality.get("ambition", 50.0))

    ambition_ratio = max(0.0, min(1.0, ambition_val / 100.0))
    ambition_score = (ambition_ratio * prestige_score) + ((1.0 - ambition_ratio) * wage_score)

    # Calculate total score
    total_score = (
        wage_score * wage_w
        + prestige_score * prestige_w
        + playing_time_score * playing_time_w
        + ambition_score * ambition_w
    )

    clamped_score = max(0.0, min(100.0, float(total_score)))
    if math.isnan(clamped_score) or math.isinf(clamped_score):
        clamped_score = 0.0

    accepted = clamped_score >= threshold

    # Sort reasons deterministically
    sorted_reasons = sorted(list(set(reasons)), key=lambda r: r.value)

    return PlayerDecision(
        accepted=accepted,
        score=round(clamped_score, 2),
        reasons=sorted_reasons,
    )


def evaluate_club_decision(
    offer: TransferOffer,
    player: Player,
    selling_club: Club,
    contract: ContractState | None = None,
    evaluation_date: date = date(2025, 7, 1),
    rules: dict | None = None,
) -> ClubDecision:
    """Evaluates whether the selling club accepts a transfer offer based on transfer fee, player importance, contract pressure, and squad depth."""
    if rules is None:
        rules = _load_transfer_rules()

    cd_rules = rules.get("club_decision", {})
    threshold = float(cd_rules.get("acceptance_threshold", 50.0))
    weights = cd_rules.get("weights", {})
    fee_w = float(weights.get("fee_vs_value", 0.45))
    importance_w = float(weights.get("player_importance", 0.25))
    contract_w = float(weights.get("contract_pressure", 0.20))
    depth_w = float(weights.get("squad_depth", 0.10))

    reasons: list[StructuredReason] = []

    # 1. Release clause trigger check
    if contract and contract.release_clause is not None and offer.transfer_fee >= contract.release_clause:
        return ClubDecision(
            accepted=True,
            score=100.0,
            reasons=[StructuredReason.CONTRACT_PRESSURE, StructuredReason.TRANSFER_FEE],
        )

    # 2. Offer fee vs Market Value
    mv = calculate_market_value(player, contract=contract, club=selling_club, evaluation_date=evaluation_date, rules=rules)
    market_val = max(1.0, mv.value)
    fee_ratio = offer.transfer_fee / market_val

    if fee_ratio >= 1.0:
        fee_score = min(100.0, 50.0 + (fee_ratio - 1.0) * 50.0)
    else:
        fee_score = max(0.0, fee_ratio * 50.0)

    if fee_score >= 60.0 or fee_ratio >= 1.0:
        reasons.append(StructuredReason.TRANSFER_FEE)
        reasons.append(StructuredReason.MARKET_VALUE)

    # 3. Player Importance factor
    p_ovr = position_ovr(player, player.primary_position)
    seller_squad = list(selling_club.squad) if selling_club.squad else []
    seller_ovrs = [position_ovr(p, p.primary_position) for p in seller_squad]
    avg_seller_ovr = (sum(seller_ovrs) / len(seller_ovrs)) if seller_ovrs else 60.0

    importance_diff = p_ovr - avg_seller_ovr
    importance_penalty = max(0.0, importance_diff * 2.5)
    importance_score = max(0.0, min(100.0, 70.0 - importance_penalty))

    if importance_diff >= 3.0:
        reasons.append(StructuredReason.PLAYER_IMPORTANCE)

    # 4. Contract Pressure factor
    pressure = calculate_contract_pressure(contract.contract_end, evaluation_date) if contract else 0.0
    contract_score = max(0.0, min(100.0, 30.0 + pressure * 0.7))

    if pressure >= 50.0:
        reasons.append(StructuredReason.CONTRACT_PRESSURE)

    # 5. Squad Depth factor
    pos = player.primary_position
    pos_count = len([p for p in seller_squad if p.primary_position == pos])
    if pos_count >= 3:
        depth_score = 80.0
        reasons.append(StructuredReason.DEPTH)
    elif pos_count == 2:
        depth_score = 50.0
    else:
        depth_score = 20.0

    # Calculate total score
    total_score = (
        fee_score * fee_w
        + importance_score * importance_w
        + contract_score * contract_w
        + depth_score * depth_w
    )

    clamped_score = max(0.0, min(100.0, float(total_score)))
    if math.isnan(clamped_score) or math.isinf(clamped_score):
        clamped_score = 0.0

    accepted = clamped_score >= threshold

    # Sort reasons deterministically
    sorted_reasons = sorted(list(set(reasons)), key=lambda r: r.value)

    return ClubDecision(
        accepted=accepted,
        score=round(clamped_score, 2),
        reasons=sorted_reasons,
    )


def resolve_transfer_offer(
    offer: TransferOffer,
    player: Player,
    buying_club: Club,
    selling_club: Club,
    contract: ContractState | None = None,
    evaluation_date: date = date(2025, 7, 1),
    rules: dict | None = None,
) -> TransferDecision:
    """Resolves a single transfer offer into a TransferDecision."""
    if offer.buying_club_id == offer.selling_club_id:
        raise ValueError("buying_club_id and selling_club_id must be different")

    player_dec = evaluate_player_decision(
        offer=offer,
        player=player,
        buying_club=buying_club,
        selling_club=selling_club,
        contract=contract,
        evaluation_date=evaluation_date,
        rules=rules,
    )

    club_dec = evaluate_club_decision(
        offer=offer,
        player=player,
        selling_club=selling_club,
        contract=contract,
        evaluation_date=evaluation_date,
        rules=rules,
    )

    if player_dec.accepted and club_dec.accepted:
        status = OfferDecisionStatus.ACCEPTED
    elif not player_dec.accepted and club_dec.accepted:
        status = OfferDecisionStatus.PLAYER_REJECTED
    elif player_dec.accepted and not club_dec.accepted:
        status = OfferDecisionStatus.CLUB_REJECTED
    else:
        status = OfferDecisionStatus.BOTH_REJECTED

    return TransferDecision(
        offer_id=offer.id,
        player_id=player.id,
        buying_club_id=offer.buying_club_id,
        selling_club_id=offer.selling_club_id,
        status=status,
        player_decision=player_dec,
        club_decision=club_dec,
    )


def resolve_competing_offers(
    offers: list[TransferOffer],
    players: list[Player] | dict[str, Player],
    clubs: list[Club] | dict[str | int, Club],
    contracts: dict[str, ContractState] | None = None,
    evaluation_date: date = date(2025, 7, 1),
    rules: dict | None = None,
) -> list[TransferDecision]:
    """Resolves competing transfer offers across players deterministically."""
    if rules is None:
        rules = _load_transfer_rules()

    if contracts is None:
        contracts = {}

    player_map = players if isinstance(players, dict) else {p.id: p for p in players}
    if isinstance(clubs, dict):
        club_map = clubs
    else:
        club_map = {}
        for idx, c in enumerate(clubs):
            if hasattr(c, "id") and getattr(c, "id") is not None:
                club_map[c.id] = c
            if hasattr(c, "name") and getattr(c, "name") is not None:
                club_map[c.name] = c
            club_map[idx] = c

    offer_map: dict[str, TransferOffer] = {o.id: o for o in offers}
    decisions: list[TransferDecision] = []

    for offer in offers:
        player = player_map[offer.player_id]
        buyer = club_map[offer.buying_club_id]
        seller = club_map[offer.selling_club_id]
        contract = contracts.get(offer.player_id)

        dec = resolve_transfer_offer(
            offer=offer,
            player=player,
            buying_club=buyer,
            selling_club=seller,
            contract=contract,
            evaluation_date=evaluation_date,
            rules=rules,
        )
        decisions.append(dec)

    # Group decisions by player_id
    player_decisions: dict[str, list[TransferDecision]] = {}
    for dec in decisions:
        player_decisions.setdefault(dec.player_id, []).append(dec)

    comp_cfg = rules.get("competing_offers", {})
    comp_weights = comp_cfg.get("weights", {})
    fee_w = float(comp_weights.get("transfer_fee", 0.40))
    prestige_w = float(comp_weights.get("buyer_prestige", 0.30))
    wage_w = float(comp_weights.get("wage_offer", 0.20))
    fit_w = float(comp_weights.get("fit_score", 0.10))

    final_decisions: list[TransferDecision] = []

    # Sort player IDs deterministically for iteration
    for p_id in sorted(player_decisions.keys(), key=lambda x: str(x)):
        decs = player_decisions[p_id]
        accepted_decs = [d for d in decs if d.status == OfferDecisionStatus.ACCEPTED]

        if len(accepted_decs) <= 1:
            final_decisions.extend(decs)
            continue

        # Rank accepted offers
        ranked_accepted: list[tuple[float, TransferDecision]] = []
        for d in accepted_decs:
            off = offer_map[d.offer_id]
            buyer = club_map[d.buying_club_id]

            # Normalize values for competing offer ranking
            fee_val = off.transfer_fee / 1_000_000.0
            prestige_val = float(getattr(buyer, "prestige", 50.0))
            wage_val = off.wage_offer / 1_000.0
            player_score_val = d.player_decision.score

            score = (
                fee_val * fee_w
                + prestige_val * prestige_w
                + wage_val * wage_w
                + player_score_val * fit_w
            )
            ranked_accepted.append((score, d))

        # Sort by score DESC, offer_id ASC
        ranked_accepted.sort(key=lambda item: (-item[0], str(item[1].offer_id)))

        winning_dec = ranked_accepted[0][1]
        for d in decs:
            if d.status == OfferDecisionStatus.ACCEPTED and d.offer_id != winning_dec.offer_id:
                lost_dec = replace(d, status=OfferDecisionStatus.COMPETING_OFFER_LOST)
                final_decisions.append(lost_dec)
            else:
                final_decisions.append(d)

    # Sort final decisions in original offer order
    offer_order = {o.id: i for i, o in enumerate(offers)}
    final_decisions.sort(key=lambda d: offer_order.get(d.offer_id, 0))

    return final_decisions
