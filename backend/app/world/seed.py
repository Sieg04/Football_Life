import json
from datetime import date
from pathlib import Path

from sqlalchemy import delete
from sqlalchemy.orm import Session

from app.models import (
    ClubMembershipModel,
    ClubModel,
    CompetitionModel,
    CountryModel,
    LeagueModel,
    ManagerModel,
    PlayerModel,
    SourceValueModel,
)
from app.world.calculations import ROLE_WEIGHTS, club_current_strength
from app.world.data import generate_world
from app.world.entities import SquadRole


def load_definitions(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def seed_world(session: Session, definitions: dict, seed: int = 20260824) -> None:
    world = generate_world(seed, definitions)
    role_weights = {
        SquadRole(role): weight for role, weight in definitions.get("role_weights", {}).items()
    } or ROLE_WEIGHTS
    session.execute(delete(ClubMembershipModel))
    session.execute(delete(PlayerModel))
    session.execute(delete(SourceValueModel))
    session.execute(delete(ClubModel))
    session.execute(delete(ManagerModel))
    session.execute(delete(LeagueModel))
    session.execute(delete(CompetitionModel))
    session.execute(delete(CountryModel))

    session.add_all(CountryModel(**country.__dict__) for country in world.countries)
    session.flush()
    league_codes = {definition["name"]: definition["code"] for definition in definitions["leagues"]}
    session.add_all(
        LeagueModel(code=league_codes[league.name], **{key: value for key, value in league.__dict__.items() if key != "name"}, name=league.name)
        for league in world.leagues
    )
    session.add_all(
        ManagerModel(**manager.__dict__) for manager in world.managers
    )
    session.flush()
    manager_ids = {manager.name: manager.id for manager in session.query(ManagerModel).all()}
    session.add_all(
        ClubModel(
            name=club.name,
            country_code=club.country_code,
            league_code=club.league_code,
            manager_id=manager_ids[club.manager.name],
            current_strength=club_current_strength(club, role_weights),
            **{
                key: value
                for key, value in club.__dict__.items()
                if key not in {"name", "country_code", "league_code", "manager", "squad", "memberships"}
            },
        )
        for club in world.clubs
    )
    session.flush()
    club_ids = {club.name: club.id for club in session.query(ClubModel).all()}
    session.add_all(
        PlayerModel(
            id=player.id,
            name=player.name,
            surname=player.surname,
            nationality=player.nationality,
            birth_date=player.birth_date,
            height=player.height,
            weight=player.weight,
            preferred_foot=player.preferred_foot,
            primary_position=player.primary_position,
            secondary_positions=list(player.secondary_positions),
            internal_attributes=player.attributes.__dict__,
            current_ability=player.current_ability,
            potential=player.potential,
            development_rate=player.development_rate,
            development_profile=player.development_profile.value,
            role_familiarity=player.role_familiarity,
            traits=list(player.traits),
            personality=player.personality,
            archetype=player.archetype,
            **player.state.__dict__,
        )
        for club in world.clubs
        for player in club.squad
    )
    session.add_all(
        ClubMembershipModel(
            player_id=membership.player_id,
            club_id=club_ids[club.name],
            role=membership.role.value,
            start_date=membership.start_date,
            end_date=membership.end_date,
        )
        for club in world.clubs
        for membership in club.memberships
    )
    session.add_all(
        CompetitionModel(**competition.__dict__) for competition in world.competitions
    )
    for club in world.clubs:
        session.add(SourceValueModel(entity_type="club", entity_key=club.name, source="UEFA", source_date=date(2026, 1, 1), raw_value=club.uefa_coefficient_raw, normalized_value=club.uefa_coefficient_normalized))
    for country in world.countries:
        if country.fifa_points is not None and country.national_strength is not None:
            session.add(SourceValueModel(entity_type="country", entity_key=country.code, source="FIFA", source_date=date(2026, 1, 1), raw_value=country.fifa_points, normalized_value=country.national_strength))
    session.commit()
