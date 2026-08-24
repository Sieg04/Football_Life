from datetime import date

from sqlalchemy import Date, Float, ForeignKey, Integer, JSON, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class CountryModel(Base):
    __tablename__ = "countries"

    code: Mapped[str] = mapped_column(String(16), primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    fifa_rank: Mapped[int | None] = mapped_column(Integer)
    fifa_points: Mapped[float | None] = mapped_column(Float)
    national_strength: Mapped[float | None] = mapped_column(Float)


class LeagueModel(Base):
    __tablename__ = "leagues"

    code: Mapped[str] = mapped_column(String(16), primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    country_code: Mapped[str] = mapped_column(ForeignKey("countries.code"), nullable=False)
    tier: Mapped[int] = mapped_column(Integer, nullable=False)
    current_strength: Mapped[float] = mapped_column(Float, nullable=False)
    prestige: Mapped[float] = mapped_column(Float, nullable=False)
    financial_strength: Mapped[float] = mapped_column(Float, nullable=False)
    european_performance: Mapped[float] = mapped_column(Float, nullable=False)
    global_reputation: Mapped[float] = mapped_column(Float, nullable=False)


class ManagerModel(Base):
    __tablename__ = "managers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    tactical_quality: Mapped[float] = mapped_column(Float, nullable=False)
    player_development: Mapped[float] = mapped_column(Float, nullable=False)
    game_management: Mapped[float] = mapped_column(Float, nullable=False)
    rotation: Mapped[float] = mapped_column(Float, nullable=False)
    adaptability: Mapped[float] = mapped_column(Float, nullable=False)
    tactical_style: Mapped[str] = mapped_column(String(50), nullable=False)
    youth_preference: Mapped[float] = mapped_column(Float, nullable=False)
    discipline: Mapped[float] = mapped_column(Float, nullable=False)


class ClubModel(Base):
    __tablename__ = "clubs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    country_code: Mapped[str] = mapped_column(ForeignKey("countries.code"), nullable=False)
    league_code: Mapped[str] = mapped_column(ForeignKey("leagues.code"), nullable=False)
    manager_id: Mapped[int] = mapped_column(ForeignKey("managers.id"), nullable=False)
    current_strength: Mapped[float] = mapped_column(Float, nullable=False)
    prestige: Mapped[float] = mapped_column(Float, nullable=False)
    financial_power: Mapped[float] = mapped_column(Float, nullable=False)
    academy_quality: Mapped[float] = mapped_column(Float, nullable=False)
    facilities: Mapped[float] = mapped_column(Float, nullable=False)
    fan_pressure: Mapped[float] = mapped_column(Float, nullable=False)
    squad_depth: Mapped[float] = mapped_column(Float, nullable=False)
    uefa_coefficient_raw: Mapped[float] = mapped_column(Float, nullable=False)
    uefa_coefficient_normalized: Mapped[float] = mapped_column(Float, nullable=False)
    domestic_reputation: Mapped[float] = mapped_column(Float, nullable=False)
    international_reputation: Mapped[float] = mapped_column(Float, nullable=False)
    momentum: Mapped[float] = mapped_column(Float, nullable=False)
    memberships: Mapped[list["ClubMembershipModel"]] = relationship(back_populates="club", cascade="all, delete-orphan")


class PlayerModel(Base):
    __tablename__ = "players"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    surname: Mapped[str] = mapped_column(String(100), nullable=False)
    nationality: Mapped[str] = mapped_column(String(16), nullable=False)
    birth_date: Mapped[date] = mapped_column(Date, nullable=False)
    height: Mapped[float] = mapped_column(Float, nullable=False)
    weight: Mapped[float] = mapped_column(Float, nullable=False)
    preferred_foot: Mapped[str] = mapped_column(String(8), nullable=False)
    primary_position: Mapped[str] = mapped_column(String(3), nullable=False)
    secondary_positions: Mapped[list[str]] = mapped_column(JSON, nullable=False)
    internal_attributes: Mapped[dict[str, float]] = mapped_column(JSON, nullable=False)
    current_ability: Mapped[float] = mapped_column(Float, nullable=False)
    potential: Mapped[float] = mapped_column(Float, nullable=False)
    development_rate: Mapped[float] = mapped_column(Float, nullable=False)
    development_profile: Mapped[str] = mapped_column(String(20), nullable=False)
    role_familiarity: Mapped[dict[str, float]] = mapped_column(JSON, nullable=False)
    traits: Mapped[list[str]] = mapped_column(JSON, nullable=False)
    personality: Mapped[dict[str, float]] = mapped_column(JSON, nullable=False)
    archetype: Mapped[str] = mapped_column(String(32), nullable=False, default="BALANCED", server_default="BALANCED")
    confidence: Mapped[float] = mapped_column(Float, nullable=False)
    morale: Mapped[float] = mapped_column(Float, nullable=False)
    form: Mapped[float] = mapped_column(Float, nullable=False)
    fitness: Mapped[float] = mapped_column(Float, nullable=False)
    fatigue: Mapped[float] = mapped_column(Float, nullable=False)
    happiness: Mapped[float] = mapped_column(Float, nullable=False)
    reputation: Mapped[float] = mapped_column(Float, nullable=False)
    memberships: Mapped[list["ClubMembershipModel"]] = relationship(back_populates="player", cascade="all, delete-orphan")


class ClubMembershipModel(Base):
    __tablename__ = "club_memberships"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    player_id: Mapped[str] = mapped_column(ForeignKey("players.id", ondelete="CASCADE"), nullable=False)
    club_id: Mapped[int] = mapped_column(ForeignKey("clubs.id", ondelete="CASCADE"), nullable=False)
    role: Mapped[str] = mapped_column(String(16), nullable=False)
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date | None] = mapped_column(Date)
    player: Mapped[PlayerModel] = relationship(back_populates="memberships")
    club: Mapped[ClubModel] = relationship(back_populates="memberships")


class SourceValueModel(Base):
    __tablename__ = "source_values"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    entity_type: Mapped[str] = mapped_column(String(32), nullable=False)
    entity_key: Mapped[str] = mapped_column(String(100), nullable=False)
    source: Mapped[str] = mapped_column(String(32), nullable=False)
    source_date: Mapped[date] = mapped_column(Date, nullable=False)
    raw_value: Mapped[float] = mapped_column(Float, nullable=False)
    normalized_value: Mapped[float] = mapped_column(Float, nullable=False)
