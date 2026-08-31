from dataclasses import is_dataclass
from typing import Any
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from app.career.domain import CareerSetupRequest
from app.career.context import build_club_context
from app.career.exceptions import (
    CareerCompletedException,
    CareerSessionNotFoundException,
    DecisionRequiredException,
    InvalidCareerStateException,
    InvalidDecisionOptionException,
)
from app.career.reputation import calculate_reputation
from app.career.service import CareerSessionService
from app.career.transfer import generate_transfer_offers

router = APIRouter(prefix="/career", tags=["career"])


class CreateCareerSchema(BaseModel):
    player_name: str = Field(..., min_length=2, max_length=100)
    position: str = Field(default="ST")
    starting_club_id: str = Field(default="club_1")
    nationality: str = Field(default="Spain")
    seed: str = Field(default="FL-CAREER-0001")


class ResolveDecisionSchema(BaseModel):
    decision_id: str
    option_id: str


class ResolveTransferSchema(BaseModel):
    offer_id: str
    action: str = Field(..., description="ACCEPT or REJECT or STAY")


def _to_json_compatible(obj: Any) -> Any:
    if is_dataclass(obj):
        return {k: _to_json_compatible(v) for k, v in obj.__dict__.items()}
    elif isinstance(obj, (tuple, list)):
        return [_to_json_compatible(item) for item in obj]
    elif isinstance(obj, dict):
        return {k: _to_json_compatible(v) for k, v in obj.items()}
    elif hasattr(obj, "items"):  # MappingProxyType
        return {k: _to_json_compatible(v) for k, v in obj.items()}
    elif hasattr(obj, "value"):  # StrEnum
        return obj.value
    return obj


@router.post("", response_model=None, status_code=status.HTTP_201_CREATED)
@router.post("/", response_model=None, status_code=status.HTTP_201_CREATED)
def create_career(payload: CreateCareerSchema) -> dict[str, Any]:
    try:
        req = CareerSetupRequest(
            player_name=payload.player_name,
            position=payload.position,
            starting_club_id=payload.starting_club_id,
            nationality=payload.nationality,
            seed=payload.seed,
        )
        session = CareerSessionService.create_career(req)
        return _to_json_compatible(session)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create career: {str(e)}",
        )


@router.get("/{career_id}", response_model=None)
def get_career_session(career_id: str) -> dict[str, Any]:
    try:
        session = CareerSessionService.get_session(career_id)
        return _to_json_compatible(session)
    except CareerSessionNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve career session: {str(e)}",
        )


@router.post("/{career_id}/advance", response_model=None)
def advance_career(career_id: str) -> dict[str, Any]:
    try:
        result = CareerSessionService.advance_career(career_id)
        return _to_json_compatible(result)
    except CareerSessionNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)
    except DecisionRequiredException as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=e.message)
    except CareerCompletedException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.message)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to advance career: {str(e)}",
        )


@router.get("/{career_id}/offers", response_model=None)
def get_transfer_offers(career_id: str) -> dict[str, Any]:
    try:
        session = CareerSessionService.get_session(career_id)
        player = session.career.player
        ctx = build_club_context(session.career.current_club_id)
        rep = calculate_reputation(
            player_ovr=player.current_ability,
            age=21 + session.career.current_season_number - 1,
            club_prestige=ctx.club_prestige,
            league_prestige=ctx.league_prestige,
        )
        offers_res = generate_transfer_offers(
            player_id=player.id,
            player_ovr=player.current_ability,
            age=21 + session.career.current_season_number - 1,
            position=player.primary_position,
            current_club_id=str(session.career.current_club_id),
            reputation=rep,
            season_number=session.career.current_season_number,
            seed=session.seed,
        )
        return _to_json_compatible(offers_res)
    except CareerSessionNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate transfer offers: {str(e)}",
        )


@router.post("/{career_id}/transfer", response_model=None)
def resolve_transfer(career_id: str, payload: ResolveTransferSchema) -> dict[str, Any]:
    try:
        session = CareerSessionService.resolve_transfer(career_id, payload.offer_id, payload.action)
        return _to_json_compatible(session)
    except CareerSessionNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to resolve transfer decision: {str(e)}",
        )


@router.post("/{career_id}/decision", response_model=None)
def resolve_decision(career_id: str, payload: ResolveDecisionSchema) -> dict[str, Any]:
    try:
        session = CareerSessionService.resolve_decision(career_id, payload.decision_id, payload.option_id)
        return _to_json_compatible(session)
    except CareerSessionNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)
    except InvalidDecisionOptionException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.message)
    except InvalidCareerStateException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.message)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to resolve decision: {str(e)}",
        )


@router.post("/{career_id}/pause", response_model=None)
def pause_career(career_id: str) -> dict[str, Any]:
    try:
        session = CareerSessionService.pause_session(career_id)
        return _to_json_compatible(session)
    except CareerSessionNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to pause career: {str(e)}",
        )


@router.get("/{career_id}/events", response_model=None)
def get_career_events(career_id: str) -> dict[str, Any]:
    try:
        events = CareerSessionService.get_events(career_id)
        return {"career_id": career_id, "events": _to_json_compatible(events)}
    except CareerSessionNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve events: {str(e)}",
        )


@router.get("/{career_id}/presentation", response_model=None)
def get_career_presentation(career_id: str) -> dict[str, Any]:
    try:
        presentation = CareerSessionService.get_presentation(career_id)
        return _to_json_compatible(presentation)
    except CareerSessionNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve presentation: {str(e)}",
        )
