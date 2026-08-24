from datetime import date

from sqlalchemy import Boolean, Date, Float, ForeignKey, Integer, JSON, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class CareerModel(Base):
    __tablename__ = "careers"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    player_id: Mapped[str] = mapped_column(ForeignKey("players.id", ondelete="CASCADE"), nullable=False, index=True)
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date | None] = mapped_column(Date)
    current_season_number: Mapped[int] = mapped_column(Integer, nullable=False)
    current_season_label: Mapped[str] = mapped_column(String(16), nullable=False)
    current_club_id: Mapped[int] = mapped_column(ForeignKey("clubs.id"), nullable=False, index=True)
    career_phase: Mapped[str] = mapped_column(String(32), nullable=False)
    peak_ability: Mapped[float] = mapped_column(Float, nullable=False)
    peak_ovr: Mapped[float] = mapped_column(Float, nullable=False)
    peak_age: Mapped[int] = mapped_column(Integer, nullable=False)
    peak_position: Mapped[str] = mapped_column(String(8), nullable=False)
    peak_club_id: Mapped[int] = mapped_column(Integer, nullable=False)
    seed: Mapped[str] = mapped_column(String(64), nullable=False)

    seasons: Mapped[list["SeasonModel"]] = relationship(
        back_populates="career", cascade="all, delete-orphan", order_by="SeasonModel.season_number"
    )
    snapshots: Mapped[list["SeasonSnapshotModel"]] = relationship(
        back_populates="career", cascade="all, delete-orphan", order_by="SeasonSnapshotModel.season_number"
    )


class SeasonModel(Base):
    __tablename__ = "seasons"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    career_id: Mapped[str] = mapped_column(ForeignKey("careers.id", ondelete="CASCADE"), nullable=False, index=True)
    season_number: Mapped[int] = mapped_column(Integer, nullable=False)
    season_label: Mapped[str] = mapped_column(String(16), nullable=False)
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date] = mapped_column(Date, nullable=False)
    player_id: Mapped[str] = mapped_column(ForeignKey("players.id"), nullable=False, index=True)
    club_id: Mapped[int] = mapped_column(ForeignKey("clubs.id"), nullable=False, index=True)
    starting_age: Mapped[int] = mapped_column(Integer, nullable=False)
    ending_age: Mapped[int] = mapped_column(Integer, nullable=False)
    starting_position: Mapped[str] = mapped_column(String(8), nullable=False)
    ending_position: Mapped[str] = mapped_column(String(8), nullable=False)
    starting_ability: Mapped[float] = mapped_column(Float, nullable=False)
    ending_ability: Mapped[float] = mapped_column(Float, nullable=False)
    starting_ovr: Mapped[float] = mapped_column(Float, nullable=False)
    ending_ovr: Mapped[float] = mapped_column(Float, nullable=False)
    career_phase_at_start: Mapped[str] = mapped_column(String(32), nullable=False)
    career_phase_at_end: Mapped[str] = mapped_column(String(32), nullable=False)
    playing_time_input: Mapped[dict] = mapped_column(JSON, nullable=False)
    performance_input: Mapped[dict] = mapped_column(JSON, nullable=False)
    environment_input: Mapped[dict] = mapped_column(JSON, nullable=False)
    development_budget: Mapped[float] = mapped_column(Float, nullable=False)
    development_summary: Mapped[dict] = mapped_column(JSON, nullable=False)
    attribute_changes: Mapped[dict] = mapped_column(JSON, nullable=False)
    season_seed: Mapped[str] = mapped_column(String(128), nullable=False)
    is_completed: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    career: Mapped[CareerModel] = relationship(back_populates="seasons")


class SeasonSnapshotModel(Base):
    __tablename__ = "season_snapshots"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    career_id: Mapped[str] = mapped_column(ForeignKey("careers.id", ondelete="CASCADE"), nullable=False, index=True)
    season_number: Mapped[int] = mapped_column(Integer, nullable=False)
    season_label: Mapped[str] = mapped_column(String(16), nullable=False)
    starting_age: Mapped[int] = mapped_column(Integer, nullable=False)
    ending_age: Mapped[int] = mapped_column(Integer, nullable=False)
    club_id: Mapped[int] = mapped_column(ForeignKey("clubs.id"), nullable=False, index=True)
    starting_position: Mapped[str] = mapped_column(String(8), nullable=False)
    ending_position: Mapped[str] = mapped_column(String(8), nullable=False)
    starting_ability: Mapped[float] = mapped_column(Float, nullable=False)
    ending_ability: Mapped[float] = mapped_column(Float, nullable=False)
    starting_ovr: Mapped[float] = mapped_column(Float, nullable=False)
    ending_ovr: Mapped[float] = mapped_column(Float, nullable=False)
    career_phase_at_start: Mapped[str] = mapped_column(String(32), nullable=False)
    career_phase_at_end: Mapped[str] = mapped_column(String(32), nullable=False)
    playing_time_input: Mapped[dict] = mapped_column(JSON, nullable=False)
    performance_input: Mapped[dict] = mapped_column(JSON, nullable=False)
    environment_input: Mapped[dict] = mapped_column(JSON, nullable=False)
    development_budget: Mapped[float] = mapped_column(Float, nullable=False)
    development_summary: Mapped[dict] = mapped_column(JSON, nullable=False)
    attribute_changes: Mapped[dict] = mapped_column(JSON, nullable=False)
    season_seed: Mapped[str] = mapped_column(String(128), nullable=False)

    career: Mapped[CareerModel] = relationship(back_populates="snapshots")
