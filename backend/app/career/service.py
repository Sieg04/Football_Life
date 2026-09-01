from typing import Dict
from app.career.domain import (
    CareerAdvanceResult,
    CareerSession,
    CareerSessionStatus,
    CareerSetupRequest,
)
from app.career.engine import CareerSessionEngine
from app.career.exceptions import CareerSessionNotFoundException
from app.event.career_domain import CareerEvent
from app.event.presentation_domain import CareerPresentation


class CareerSessionService:
    """
    In-memory application service for Phase 14 career session state.
    Provides clean thread-safe operations.
    """

    _sessions: Dict[str, CareerSession] = {}

    @classmethod
    def create_career(cls, request: CareerSetupRequest) -> CareerSession:
        session = CareerSessionEngine.create_session(request)
        cls._sessions[session.career_id] = session
        return session

    @classmethod
    def get_session(cls, career_id: str) -> CareerSession:
        if career_id not in cls._sessions:
            raise CareerSessionNotFoundException(career_id)
        return cls._sessions[career_id]

    @classmethod
    def advance_career(cls, career_id: str) -> CareerAdvanceResult:
        session = cls.get_session(career_id)
        advance_res = CareerSessionEngine.advance_season(session)

        # Apply advance result to stored session
        updated_session = CareerSession(
            career_id=session.career_id,
            player_id=session.player_id,
            current_season=advance_res.current_season,
            simulation_position=session.simulation_position + 1,
            status=advance_res.status,
            career=advance_res.updated_career or session.career,
            career_record=advance_res.updated_record or session.career_record,
            presentation=advance_res.presentation or session.presentation,
            pending_decision=advance_res.pending_decision,
            pending_events=session.pending_events + advance_res.processed_events,
            notifications=session.notifications + advance_res.new_notifications,
            last_processed_event_id=advance_res.processed_events[-1].event_id if advance_res.processed_events else session.last_processed_event_id,
            seed=session.seed,
            season_summary=advance_res.season_summary,
        )

        cls._sessions[career_id] = updated_session
        return advance_res

    @classmethod
    def resolve_decision(cls, career_id: str, decision_id: str, option_id: str) -> CareerSession:
        session = cls.get_session(career_id)
        updated_session, _ = CareerSessionEngine.resolve_session_decision(session, option_id)
        cls._sessions[career_id] = updated_session
        return updated_session

    @classmethod
    def resolve_transfer(cls, career_id: str, offer_id: str, action: str) -> CareerSession:
        session = cls.get_session(career_id)
        updated_session = CareerSessionEngine.resolve_transfer_choice(session, offer_id, action)
        cls._sessions[career_id] = updated_session
        return updated_session

    @classmethod
    def pause_session(cls, career_id: str) -> CareerSession:
        session = cls.get_session(career_id)
        paused_session = CareerSession(
            career_id=session.career_id,
            player_id=session.player_id,
            current_season=session.current_season,
            simulation_position=session.simulation_position,
            status=CareerSessionStatus.PAUSED,
            career=session.career,
            career_record=session.career_record,
            presentation=session.presentation,
            pending_decision=session.pending_decision,
            pending_events=session.pending_events,
            notifications=session.notifications,
            last_processed_event_id=session.last_processed_event_id,
            seed=session.seed,
            season_summary=session.season_summary,
        )
        cls._sessions[career_id] = paused_session
        return paused_session

    @classmethod
    def get_events(cls, career_id: str) -> tuple[CareerEvent, ...]:
        session = cls.get_session(career_id)
        return session.career_record.events

    @classmethod
    def get_presentation(cls, career_id: str) -> CareerPresentation:
        session = cls.get_session(career_id)
        return session.presentation

    @classmethod
    def clear_all_sessions(cls) -> None:
        cls._sessions.clear()
