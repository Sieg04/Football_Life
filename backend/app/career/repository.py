from sqlalchemy.orm import Session as SQLAlchemySession

from app.career.domain import (
    Career,
    CareerPhase,
    Season,
    SeasonalEnvironmentInput,
    SeasonalPerformanceInput,
    SeasonalPlayingTimeInput,
    SeasonSnapshot,
)
from app.models.career import CareerModel, SeasonModel, SeasonSnapshotModel
from app.player.domain import Player


def season_to_model(season: Season, career_id: str) -> SeasonModel:
    return SeasonModel(
        career_id=career_id,
        season_number=season.season_number,
        season_label=season.season_label,
        start_date=season.start_date,
        end_date=season.end_date,
        player_id=season.player_id,
        club_id=season.club_id,
        starting_age=season.starting_age,
        ending_age=season.ending_age,
        starting_position=season.starting_position,
        ending_position=season.ending_position,
        starting_ability=season.starting_ability,
        ending_ability=season.ending_ability,
        starting_ovr=season.starting_ovr,
        ending_ovr=season.ending_ovr,
        career_phase_at_start=season.career_phase_at_start.value,
        career_phase_at_end=season.career_phase_at_end.value,
        playing_time_input=vars(season.playing_time_input),
        performance_input=vars(season.performance_input),
        environment_input=vars(season.environment_input),
        development_budget=season.development_budget,
        development_summary=season.development_summary,
        attribute_changes=season.attribute_changes,
        season_seed=season.season_seed,
        is_completed=season.is_completed,
    )


def season_from_model(model: SeasonModel) -> Season:
    return Season(
        season_number=model.season_number,
        season_label=model.season_label,
        start_date=model.start_date,
        end_date=model.end_date,
        player_id=model.player_id,
        club_id=model.club_id,
        starting_age=model.starting_age,
        ending_age=model.ending_age,
        starting_position=model.starting_position,
        ending_position=model.ending_position,
        starting_ability=model.starting_ability,
        ending_ability=model.ending_ability,
        starting_ovr=model.starting_ovr,
        ending_ovr=model.ending_ovr,
        career_phase_at_start=CareerPhase(model.career_phase_at_start),
        career_phase_at_end=CareerPhase(model.career_phase_at_end),
        playing_time_input=SeasonalPlayingTimeInput(**model.playing_time_input),
        performance_input=SeasonalPerformanceInput(**model.performance_input),
        environment_input=SeasonalEnvironmentInput(**model.environment_input),
        development_budget=model.development_budget,
        development_summary=model.development_summary,
        attribute_changes=model.attribute_changes,
        season_seed=model.season_seed,
        is_completed=model.is_completed,
    )


def snapshot_to_model(snapshot: SeasonSnapshot, career_id: str) -> SeasonSnapshotModel:
    return SeasonSnapshotModel(
        career_id=career_id,
        season_number=snapshot.season_number,
        season_label=snapshot.season_label,
        starting_age=snapshot.starting_age,
        ending_age=snapshot.ending_age,
        club_id=snapshot.club_id,
        starting_position=snapshot.starting_position,
        ending_position=snapshot.ending_position,
        starting_ability=snapshot.starting_ability,
        ending_ability=snapshot.ending_ability,
        starting_ovr=snapshot.starting_ovr,
        ending_ovr=snapshot.ending_ovr,
        career_phase_at_start=snapshot.career_phase_at_start.value,
        career_phase_at_end=snapshot.career_phase_at_end.value,
        playing_time_input=vars(snapshot.playing_time_input),
        performance_input=vars(snapshot.performance_input),
        environment_input=vars(snapshot.environment_input),
        development_budget=snapshot.development_budget,
        development_summary=snapshot.development_summary,
        attribute_changes=snapshot.attribute_changes,
        season_seed=snapshot.season_seed,
    )


def snapshot_from_model(model: SeasonSnapshotModel) -> SeasonSnapshot:
    return SeasonSnapshot(
        season_number=model.season_number,
        season_label=model.season_label,
        starting_age=model.starting_age,
        ending_age=model.ending_age,
        club_id=model.club_id,
        starting_position=model.starting_position,
        ending_position=model.ending_position,
        starting_ability=model.starting_ability,
        ending_ability=model.ending_ability,
        starting_ovr=model.starting_ovr,
        ending_ovr=model.ending_ovr,
        career_phase_at_start=CareerPhase(model.career_phase_at_start),
        career_phase_at_end=CareerPhase(model.career_phase_at_end),
        playing_time_input=SeasonalPlayingTimeInput(**model.playing_time_input),
        performance_input=SeasonalPerformanceInput(**model.performance_input),
        environment_input=SeasonalEnvironmentInput(**model.environment_input),
        development_budget=model.development_budget,
        development_summary=model.development_summary,
        attribute_changes=model.attribute_changes,
        season_seed=model.season_seed,
    )


def career_to_model(career: Career) -> CareerModel:
    return CareerModel(
        id=career.id,
        player_id=career.player.id,
        start_date=career.start_date,
        end_date=career.end_date,
        current_season_number=career.current_season_number,
        current_season_label=career.current_season_label,
        current_club_id=career.current_club_id,
        career_phase=career.career_phase.value,
        peak_ability=career.peak_ability,
        peak_ovr=career.peak_ovr,
        peak_age=career.peak_age,
        peak_position=career.peak_position,
        peak_club_id=career.peak_club_id,
        seed=career.seed,
        seasons=[season_to_model(s, career.id) for s in career.seasons],
        snapshots=[snapshot_to_model(sn, career.id) for sn in career.snapshots],
    )


def career_from_model(model: CareerModel, player: Player) -> Career:
    return Career(
        id=model.id,
        player=player,
        start_date=model.start_date,
        end_date=model.end_date,
        current_season_number=model.current_season_number,
        current_season_label=model.current_season_label,
        current_club_id=model.current_club_id,
        career_phase=CareerPhase(model.career_phase),
        peak_ability=model.peak_ability,
        peak_ovr=model.peak_ovr,
        peak_age=model.peak_age,
        peak_position=model.peak_position,
        peak_club_id=model.peak_club_id,
        seasons=[season_from_model(sm) for sm in model.seasons],
        snapshots=[snapshot_from_model(snm) for snm in model.snapshots],
        seed=model.seed,
    )


class CareerRepository:
    def __init__(self, session: SQLAlchemySession) -> None:
        self.session = session

    def save(self, career: Career) -> None:
        model = self.session.query(CareerModel).filter_by(id=career.id).first()
        if model:
            self.session.delete(model)
            self.session.flush()

        new_model = career_to_model(career)
        self.session.add(new_model)
        self.session.commit()

    def get_by_id(self, career_id: str, player: Player) -> Career | None:
        model = self.session.query(CareerModel).filter_by(id=career_id).first()
        if not model:
            return None
        return career_from_model(model, player)
