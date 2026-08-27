from dataclasses import dataclass, replace
from datetime import date
from typing import Sequence

from app.player.domain import Player
from app.transfer.domain import (
    ContractState,
    OfferDecisionStatus,
    TransferApplication,
    TransferApplicationStatus,
    TransferDecision,
    TransferHistoryRecord,
    TransferOffer,
)
from app.world.entities import Club, ClubMembership, SquadRole


@dataclass(frozen=True)
class TransferApplicationResult:
    updated_clubs: dict[int | str, Club]
    updated_contracts: dict[str, ContractState]
    applications: tuple[TransferApplication, ...]
    history_records: tuple[TransferHistoryRecord, ...]


def create_transfer_application(
    decision: TransferDecision,
    offer: TransferOffer | None = None,
    season: int = 2025,
    application_id: str | None = None,
) -> TransferApplication:
    """Creates a TransferApplication from a Phase 7D TransferDecision (and optional TransferOffer)."""
    if offer is not None and offer.id != decision.offer_id:
        raise ValueError(f"offer.id ({offer.id}) does not match decision.offer_id ({decision.offer_id})")

    app_id = application_id or f"app_{decision.offer_id}"

    transfer_fee = offer.transfer_fee if offer is not None else 0.0
    wage = offer.wage_offer if offer is not None else 0.0
    contract_years = offer.contract_years if offer is not None else 3

    if decision.status == OfferDecisionStatus.ACCEPTED:
        initial_status = TransferApplicationStatus.PENDING
        reason = "Decision accepted"
    else:
        initial_status = TransferApplicationStatus.SKIPPED
        reason = f"Decision status is {decision.status}"

    return TransferApplication(
        application_id=app_id,
        transfer_decision_id=decision.offer_id,
        player_id=decision.player_id,
        seller_club_id=decision.selling_club_id,
        buyer_club_id=decision.buying_club_id,
        transfer_fee=transfer_fee,
        wage=wage,
        contract_years=contract_years,
        status=initial_status,
        season=season,
        reason=reason,
    )


def apply_transfers(
    clubs: Sequence[Club] | dict[int | str, Club],
    contracts: dict[str, ContractState],
    applications: Sequence[TransferApplication],
    season: int = 2025,
    applied_date: date | None = None,
) -> TransferApplicationResult:
    """Deterministically applies accepted transfer applications to create next-season club rosters, contracts, and history.

     Guarantees input immutability (returns new dicts/tuples without modifying inputs).
    """
    if applied_date is None:
        applied_date = date(season, 7, 1)

    # Convert clubs input into a mutable dictionary mapping club_id to Club copy reference
    if isinstance(clubs, dict):
        club_map: dict[int | str, Club] = {k: v for k, v in clubs.items()}
    else:
        club_map = {}
        for idx, c in enumerate(clubs):
            c_id = getattr(c, "id", None)
            if c_id is not None:
                club_map[c_id] = c
            else:
                club_map[c.name] = c

    # Copy contracts map
    contract_map: dict[str, ContractState] = dict(contracts)

    # Sort applications deterministically according to spec:
    # 1. season
    # 2. player_id (str)
    # 3. seller_club_id (str)
    # 4. buyer_club_id (str)
    # 5. transfer_decision_id (str)
    sorted_apps = sorted(
        applications,
        key=lambda a: (
            a.season,
            str(a.player_id),
            str(a.seller_club_id),
            str(a.buyer_club_id),
            str(a.transfer_decision_id),
            str(a.application_id),
        ),
    )

    processed_apps: list[TransferApplication] = []
    history_records: list[TransferHistoryRecord] = []
    transferred_players_this_season: set[str] = set()

    # Track processed application IDs for duplicate detection
    processed_app_ids: set[str] = set()

    for app in sorted_apps:
        # Idempotency / Duplicate application check
        if app.application_id in processed_app_ids:
            dup_app = replace(app, status=TransferApplicationStatus.DUPLICATE, reason="Duplicate application ID")
            processed_apps.append(dup_app)
            continue
        processed_app_ids.add(app.application_id)

        # 1. Non-accepted status check
        if app.status == TransferApplicationStatus.SKIPPED or app.status != TransferApplicationStatus.PENDING:
            if app.status == TransferApplicationStatus.PENDING:
                # Should not be reached if created via helper, but handle cleanly
                skipped_app = replace(app, status=TransferApplicationStatus.SKIPPED, reason="Application not pending")
                processed_apps.append(skipped_app)
            else:
                processed_apps.append(app)
            continue

        # 2. Buyer == Seller check
        if app.seller_club_id == app.buyer_club_id:
            invalid_app = replace(app, status=TransferApplicationStatus.REJECTED_INVALID, reason="Buyer equals seller")
            processed_apps.append(invalid_app)
            continue

        # 3. Clubs existence check
        seller_club = club_map.get(app.seller_club_id)
        buyer_club = club_map.get(app.buyer_club_id)

        if seller_club is None or buyer_club is None:
            invalid_app = replace(app, status=TransferApplicationStatus.REJECTED_INVALID, reason="Seller or buyer club not found")
            processed_apps.append(invalid_app)
            continue

        # 4. Same player already transferred check (Conflict)
        if app.player_id in transferred_players_this_season:
            conflict_app = replace(app, status=TransferApplicationStatus.CONFLICT, reason="Player already transferred this window/season")
            processed_apps.append(conflict_app)
            continue

        # 5. Seller consistency check (Player must belong to seller squad)
        player_in_seller: Player | None = None
        for p in seller_club.squad:
            if p.id == app.player_id:
                player_in_seller = p
                break

        if player_in_seller is None:
            conflict_app = replace(app, status=TransferApplicationStatus.CONFLICT, reason="Player not found in seller squad")
            processed_apps.append(conflict_app)
            continue

        # 6. Check if player already in buyer squad
        if any(p.id == app.player_id for p in buyer_club.squad):
            conflict_app = replace(app, status=TransferApplicationStatus.CONFLICT, reason="Player already in buyer squad")
            processed_apps.append(conflict_app)
            continue

        # --- EXECUTE TRANSFER ---
        transferred_players_this_season.add(app.player_id)

        # Remove player from seller squad & memberships
        new_seller_squad = tuple(p for p in seller_club.squad if p.id != app.player_id)
        new_seller_memberships = tuple(m for m in seller_club.memberships if m.player_id != app.player_id)
        club_map[app.seller_club_id] = replace(
            seller_club,
            squad=new_seller_squad,
            memberships=new_seller_memberships,
        )

        # Add player to buyer squad & create new membership
        new_buyer_squad = buyer_club.squad + (player_in_seller,)
        new_membership = ClubMembership(
            player_id=app.player_id,
            club_id=app.buyer_club_id,
            role=SquadRole.STARTER,
            start_date=applied_date,
            end_date=date(applied_date.year + app.contract_years, 6, 30),
        )
        new_buyer_memberships = buyer_club.memberships + (new_membership,)
        club_map[app.buyer_club_id] = replace(
            buyer_club,
            squad=new_buyer_squad,
            memberships=new_buyer_memberships,
        )

        # Update contract state
        new_contract = ContractState(
            contract_start=applied_date,
            contract_end=date(applied_date.year + app.contract_years, 6, 30),
            wage_band=app.wage,
        )
        contract_map[app.player_id] = new_contract

        # Mark application as APPLIED
        applied_app = replace(app, status=TransferApplicationStatus.APPLIED, reason="Transfer applied successfully")
        processed_apps.append(applied_app)

        # Create immutable history record
        hist = TransferHistoryRecord(
            application_id=app.application_id,
            transfer_decision_id=app.transfer_decision_id,
            season=app.season,
            player_id=app.player_id,
            seller_club_id=app.seller_club_id,
            buyer_club_id=app.buyer_club_id,
            transfer_fee=app.transfer_fee,
            wage=app.wage,
            contract_years=app.contract_years,
            status=TransferApplicationStatus.APPLIED,
            applied_date=applied_date,
        )
        history_records.append(hist)

    return TransferApplicationResult(
        updated_clubs=club_map,
        updated_contracts=contract_map,
        applications=tuple(processed_apps),
        history_records=tuple(history_records),
    )
