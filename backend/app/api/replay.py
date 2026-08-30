from dataclasses import is_dataclass
from typing import Any
from fastapi import APIRouter, HTTPException, Query, status
from pydantic import BaseModel, Field

from app.career.exceptions import CareerSessionNotFoundException
from app.career.service import CareerSessionService
from app.event.presentation_engine import build_career_presentation
from app.event.replay_domain import (
    CapturePresetType,
    ContentStory,
    ReplayMomentType,
    ReplayProcessingException,
    ScenePriority,
)
from app.event.replay_engine import (
    build_capture_frame,
    build_career_replay,
    build_content_story,
    reorder_content_scenes,
)

router = APIRouter(prefix="/career", tags=["replay"])

_CONTENT_STORIES: dict[str, ContentStory] = {}


class CreateContentStorySchema(BaseModel):
    moment_ids: list[str] | None = Field(default=None)
    selected_moment_ids: list[str] | None = Field(default=None)
    title: str = Field(default="My Career Story")


class ReorderScenesSchema(BaseModel):
    scene_ids: list[str] | None = Field(default=None)
    scene_order: list[str] | None = Field(default=None)


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


def _get_or_build_replay(career_id: str) -> Any:
    try:
        session = CareerSessionService.get_session(career_id)
        res = build_career_replay(
            career_record=session.career_record,
            presentation=session.presentation,
            career_id=session.career_id,
            player_id=session.player_id,
            player_name=session.presentation.player.name if session.presentation and session.presentation.player else "Adrian Martínez",
        )
        if not res.success or not res.replay:
            raise Exception(res.errors[0] if res.errors else "Failed to build replay")
        return res.replay
    except CareerSessionNotFoundException:
        # Fallback for sample or direct testing if career_id not in in-memory service
        sample_pres = build_career_presentation()
        res = build_career_replay(
            presentation=sample_pres,
            career_id=career_id,
            player_id="P_SAMPLE",
            player_name=sample_pres.player.name if sample_pres.player else "Adrian Martínez",
        )
        if not res.success or not res.replay:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Career session '{career_id}' not found",
            )
        return res.replay


@router.get("/{career_id}/replay", response_model=None)
def get_career_replay(career_id: str) -> dict[str, Any]:
    try:
        replay = _get_or_build_replay(career_id)
        return _to_json_compatible(replay)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve career replay: {str(e)}",
        )


@router.get("/{career_id}/replay/moments", response_model=None)
def get_replay_moments(
    career_id: str,
    priority: str | None = Query(default=None),
    type: str | None = Query(default=None),
    moment_type: str | None = Query(default=None),
    season: str | None = Query(default=None),
) -> dict[str, Any]:
    try:
        replay = _get_or_build_replay(career_id)
        moments = list(replay.moments)

        if priority:
            p_upper = priority.upper()
            moments = [m for m in moments if m.priority.value == p_upper or m.priority == p_upper]
        t_filter = moment_type or type
        if t_filter:
            t_upper = t_filter.upper()
            moments = [m for m in moments if m.moment_type.value == t_upper or m.moment_type == t_upper]
        if season:
            moments = [m for m in moments if m.season_id == season]

        return {
            "career_id": career_id,
            "total": len(moments),
            "moments": _to_json_compatible(moments),
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve replay moments: {str(e)}",
        )


@router.post("/{career_id}/content-story", response_model=None)
def create_content_story(
    career_id: str, payload: CreateContentStorySchema
) -> dict[str, Any]:
    try:
        replay = _get_or_build_replay(career_id)
        effective_moment_ids = payload.selected_moment_ids if payload.selected_moment_ids is not None else payload.moment_ids
        res = build_content_story(
            replay=replay,
            moment_ids=effective_moment_ids,
            title=payload.title,
        )

        if not res.success or not res.content_story:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=res.errors[0] if res.errors else "Failed to create content story",
            )

        _CONTENT_STORIES[career_id] = res.content_story
        return _to_json_compatible(res.content_story)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create content story: {str(e)}",
        )


@router.get("/{career_id}/content-story", response_model=None)
def get_content_story(career_id: str) -> dict[str, Any]:
    try:
        if career_id in _CONTENT_STORIES:
            return _to_json_compatible(_CONTENT_STORIES[career_id])

        # Auto-create default content story if not already stored
        replay = _get_or_build_replay(career_id)
        res = build_content_story(replay=replay)
        if res.success and res.content_story:
            _CONTENT_STORIES[career_id] = res.content_story
            return _to_json_compatible(res.content_story)

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Content story for career '{career_id}' not found",
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve content story: {str(e)}",
        )


@router.put("/{career_id}/content-story/order", response_model=None)
def reorder_content_story_scenes(
    career_id: str, payload: ReorderScenesSchema
) -> dict[str, Any]:
    try:
        if career_id not in _CONTENT_STORIES:
            # Try to build default first
            replay = _get_or_build_replay(career_id)
            res = build_content_story(replay=replay)
            if res.success and res.content_story:
                _CONTENT_STORIES[career_id] = res.content_story
            else:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Content story for career '{career_id}' not found",
                )

        current_story = _CONTENT_STORIES[career_id]
        order_ids = payload.scene_ids or payload.scene_order

        if not order_ids:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="payload must include 'scene_ids' or 'scene_order'",
            )

        updated_story = reorder_content_scenes(current_story, order_ids)
        _CONTENT_STORIES[career_id] = updated_story
        return _to_json_compatible(updated_story)
    except ReplayProcessingException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=e.message,
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to reorder content story scenes: {str(e)}",
        )


@router.get("/{career_id}/capture/{scene_id}", response_model=None)
def get_capture_frame(
    career_id: str,
    scene_id: str,
    preset: str = Query(default="CINEMATIC"),
) -> dict[str, Any]:
    try:
        replay = _get_or_build_replay(career_id)

        # Retrieve scene from stored content story or build a scene
        matched_scene = None
        if career_id in _CONTENT_STORIES:
            matched_scene = next(
                (sc for sc in _CONTENT_STORIES[career_id].scenes if sc.scene_id == scene_id),
                None,
            )

        if not matched_scene:
            matched_moment = next(
                (m for m in replay.moments if m.moment_id == scene_id), None
            )
            if matched_moment:
                from app.event.replay_engine import build_content_scene

                matched_scene = build_content_scene(
                    moment=matched_moment,
                    title=matched_moment.title,
                    subtitle=f"Season {matched_moment.season_id}",
                    description=matched_moment.description,
                    order_index=0,
                    priority=matched_moment.priority,
                    season_id=matched_moment.season_id,
                )

        if not matched_scene:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Scene '{scene_id}' not found for career '{career_id}'",
            )

        p_type = preset.upper()
        frame = build_capture_frame(
            scene=matched_scene,
            replay=replay,
            preset_type=p_type,
        )
        return _to_json_compatible(frame)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate capture frame: {str(e)}",
        )
