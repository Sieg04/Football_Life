import pytest
from types import MappingProxyType

from app.event.career_domain import CareerRecord
from app.event.presentation_domain import CareerPresentation, CareerStatus, VisualPriority
from app.event.presentation_engine import build_career_presentation
from app.event.replay_domain import (
    CaptureFrame,
    CapturePreset,
    CapturePresetType,
    CareerReplay,
    ContentScene,
    ContentStory,
    ReplayErrorCode,
    ReplayMoment,
    ReplayMomentType,
    ReplayProcessingException,
    ReplaySeason,
    ScenePriority,
    SceneType,
)
from app.event.replay_engine import (
    build_capture_frame,
    build_career_replay,
    build_content_scene,
    build_content_story,
    build_replay_seasons,
    identify_replay_moments,
    reorder_content_scenes,
    validate_career_replay,
    validate_content_story,
)


def test_replay_season_construction_valid() -> None:
    season = ReplaySeason(
        season_id="2026/27",
        season_label="Season 2026/27",
        season_index=1,
        club_id="club_01",
        club_name="FC Barcelona",
        appearances=30,
        goals=15,
        assists=8,
        trophies=("La Liga",),
        ovr=82,
        moment_ids=("m_1", "m_2"),
    )
    assert season.season_id == "2026/27"
    assert season.goals == 15
    assert isinstance(season.trophies, tuple)
    assert isinstance(season.source_references, MappingProxyType)


def test_replay_season_construction_invalid() -> None:
    with pytest.raises(ValueError):
        ReplaySeason(
            season_id="",
            season_label="Season 1",
            season_index=1,
            club_id="c1",
            club_name="Club",
            appearances=10,
            goals=5,
            assists=2,
            trophies=(),
            ovr=75,
            moment_ids=(),
        )


def test_replay_moment_construction_valid() -> None:
    moment = ReplayMoment(
        moment_id="mom_01",
        moment_type=ReplayMomentType.TRANSFER,
        title="Blockbuster Transfer to FC Barcelona",
        description="Completed record transfer move.",
        season_id="2026/27",
        priority=ScenePriority.CRITICAL,
        visual_priority=VisualPriority.CRITICAL,
    )
    assert moment.moment_id == "mom_01"
    assert moment.priority == ScenePriority.CRITICAL
    assert moment.moment_type == ReplayMomentType.TRANSFER


def test_career_replay_construction_and_immutability() -> None:
    season = ReplaySeason(
        season_id="2026/27",
        season_label="Season 2026/27",
        season_index=1,
        club_id="club_01",
        club_name="FC Barcelona",
        appearances=30,
        goals=15,
        assists=8,
        trophies=(),
        ovr=82,
        moment_ids=("mom_01",),
    )
    moment = ReplayMoment(
        moment_id="mom_01",
        moment_type=ReplayMomentType.DEBUT,
        title="Debut Goal",
        description="Scored on debut",
        season_id="2026/27",
        priority=ScenePriority.HIGH,
        visual_priority=VisualPriority.HIGH,
    )
    replay = CareerReplay(
        replay_id="rep_01",
        career_id="car_01",
        player_id="P_001",
        player_name="Adrian Martínez",
        career_status=CareerStatus.ACTIVE,
        seasons=(season,),
        moments=(moment,),
    )
    assert replay.career_id == "car_01"

    with pytest.raises(Exception):
        replay.player_name = "New Name"  # type: ignore[misc]


def test_build_career_replay_from_presentation() -> None:
    pres = build_career_presentation()
    res = build_career_replay(
        presentation=pres,
        career_id="test_car",
        player_id="P_TEST",
        player_name="Test Player",
    )
    assert res.success is True
    assert res.replay is not None
    assert len(res.replay.seasons) > 0
    assert len(res.replay.moments) > 0


def test_content_story_creation_and_reordering() -> None:
    pres = build_career_presentation()
    res_rep = build_career_replay(presentation=pres, career_id="car_story_test")
    assert res_rep.replay is not None

    story_res = build_content_story(replay=res_rep.replay, title="Test Story")
    assert story_res.success is True
    story = story_res.content_story
    assert story is not None
    assert len(story.scenes) > 0

    scene_ids = [s.scene_id for s in story.scenes]
    reversed_ids = list(reversed(scene_ids))

    reordered = reorder_content_scenes(story, reversed_ids)
    assert reordered.scenes[0].scene_id == reversed_ids[0]
    assert reordered.scenes[0].order_index == 0


def test_reorder_scenes_invalid_order_fails_atomically() -> None:
    pres = build_career_presentation()
    res_rep = build_career_replay(presentation=pres, career_id="car_story_test")
    assert res_rep.replay is not None
    story = build_content_story(replay=res_rep.replay).content_story
    assert story is not None

    invalid_ids = [s.scene_id for s in story.scenes][:-1]  # missing one ID
    with pytest.raises(ReplayProcessingException) as exc_info:
        reorder_content_scenes(story, invalid_ids)

    assert exc_info.value.error_code == ReplayErrorCode.INVALID_ORDER


def test_capture_frame_generation() -> None:
    pres = build_career_presentation()
    replay = build_career_replay(presentation=pres, career_id="car_cap").replay
    assert replay is not None

    story = build_content_story(replay=replay).content_story
    assert story is not None
    scene = story.scenes[0]

    frame = build_capture_frame(scene=scene, replay=replay, preset_type=CapturePresetType.CINEMATIC)
    assert frame.preset.width == 1920
    assert frame.preset.height == 1080
    assert frame.player_name == replay.player_name


def test_active_career_safety_no_fake_ending() -> None:
    pres = build_career_presentation()
    replay = build_career_replay(presentation=pres, career_id="car_active").replay
    assert replay is not None
    assert replay.career_status == CareerStatus.ACTIVE

    moments = identify_replay_moments(presentation=pres, career_id="car_active")
    end_moments = [m for m in moments if m.moment_type == ReplayMomentType.CAREER_END]
    assert len(end_moments) == 0, "Active career must not generate career end moment"
