from dataclasses import asdict, is_dataclass
from typing import Any
from fastapi import APIRouter, HTTPException, status

from app.event.presentation_domain import CareerPresentation
from app.event.presentation_engine import build_career_presentation

router = APIRouter(prefix="/presentation", tags=["presentation"])


def _to_json_compatible(obj: Any) -> Any:
    if is_dataclass(obj):
        return {k: _to_json_compatible(v) for k, v in obj.__dict__.items()}
    elif isinstance(obj, (tuple, list)):
        return [_to_json_compatible(item) for item in obj]
    elif isinstance(obj, dict):
        return {k: _to_json_compatible(v) for k, v in obj.items()}
    elif hasattr(obj, "items"):  # handles MappingProxyType
        return {k: _to_json_compatible(v) for k, v in obj.items()}
    elif hasattr(obj, "value"):  # handles StrEnum
        return obj.value
    return obj


@router.get("/sample", response_model=None)
def get_sample_presentation() -> dict[str, Any]:
    try:
        presentation = build_career_presentation()
        # Override fields with non-zero default sample values if player_id is default sample
        player_dict = _to_json_compatible(presentation.player)
        player_dict.update({
            "name": "Adrian Martínez",
            "age": 24,
            "nationality": "Spain",
            "position": "CF",
            "overall_rating": 87,
            "current_club": "FC Barcelona",
            "market_value_eur": 74000000,
            "salary_eur": 180000,
            "primary_archetype": "Clinical Finisher",
        })

        overview_dict = _to_json_compatible(presentation.overview)
        overview_dict.update({
            "total_seasons": 6,
            "years_active": 6,
            "clubs_count": 2,
            "matches": 182,
            "goals": 96,
            "assists": 41,
            "trophies": 4,
            "trophies_count": 4,
            "milestones": 5,
            "turning_points": 3,
            "peak_rating": 87,
        })

        res = _to_json_compatible(presentation)
        res["player"] = player_dict
        res["overview"] = overview_dict
        return res
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate sample presentation: {str(e)}",
        )


@router.get("/{player_id}", response_model=None)
def get_player_presentation(player_id: str) -> dict[str, Any]:
    if not player_id or not player_id.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="player_id must be a non-empty string",
        )
    try:
        presentation = build_career_presentation()
        res = _to_json_compatible(presentation)
        res["player"]["player_id"] = player_id
        res["metadata"]["player_id"] = player_id
        return res
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to build presentation for player '{player_id}': {str(e)}",
        )
