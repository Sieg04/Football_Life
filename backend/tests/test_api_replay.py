import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_api_get_career_replay() -> None:
    response = client.get("/career/sample_car/replay")
    assert response.status_code == 200
    data = response.json()
    assert "replay_id" in data
    assert "seasons" in data
    assert "moments" in data


def test_api_get_replay_moments_with_filters() -> None:
    response = client.get("/career/sample_car/replay/moments?priority=CRITICAL")
    assert response.status_code == 200
    data = response.json()
    assert "moments" in data
    assert isinstance(data["moments"], list)


def test_api_create_and_get_content_story() -> None:
    # 1. Create content story
    res_moments = client.get("/career/sample_car/replay/moments")
    moments = res_moments.json()["moments"]
    m_ids = [m["moment_id"] for m in moments[:2]]

    res_create = client.post(
        "/career/sample_car/content-story",
        json={"moment_ids": m_ids, "title": "My Test Story"},
    )
    assert res_create.status_code == 200
    story_data = res_create.json()
    assert story_data["title"] == "My Test Story"
    assert len(story_data["scenes"]) == len(m_ids)

    # 2. Get content story
    res_get = client.get("/career/sample_car/content-story")
    assert res_get.status_code == 200
    assert res_get.json()["content_story_id"] == story_data["content_story_id"]


def test_api_reorder_content_story_scenes() -> None:
    # Create story
    res_create = client.post(
        "/career/sample_reorder/content-story",
        json={"title": "Reorder Story"},
    )
    assert res_create.status_code == 200
    story = res_create.json()
    scene_ids = [s["scene_id"] for s in story["scenes"]]
    reversed_ids = list(reversed(scene_ids))

    # Reorder
    res_order = client.put(
        "/career/sample_reorder/content-story/order",
        json={"scene_ids": reversed_ids},
    )
    assert res_order.status_code == 200
    updated = res_order.json()
    assert updated["scenes"][0]["scene_id"] == reversed_ids[0]


def test_api_reorder_invalid_scene_ids_returns_400() -> None:
    client.post("/career/sample_invalid/content-story", json={})
    res = client.put(
        "/career/sample_invalid/content-story/order",
        json={"scene_ids": ["invalid_sc_1", "invalid_sc_2"]},
    )
    assert res.status_code == 400


def test_api_get_capture_frame() -> None:
    res_get = client.get("/career/sample_cap/content-story")
    story = res_get.json()
    scene_id = story["scenes"][0]["scene_id"]

    res_cap = client.get(f"/career/sample_cap/capture/{scene_id}?preset=CINEMATIC")
    assert res_cap.status_code == 200
    frame = res_cap.json()
    assert frame["scene_id"] == scene_id
    assert frame["preset"]["preset_type"] == "CINEMATIC"
    assert frame["preset"]["width"] == 1920
