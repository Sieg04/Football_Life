from fastapi.testclient import TestClient

from app.main import app


def test_transfer_acceptance_returns_updated_career_and_current_club() -> None:
    client = TestClient(app)

    create_response = client.post(
        "/career/",
        json={
            "player_name": "Transfer QA",
            "position": "ST",
            "starting_club_id": "Real Madrid",
            "nationality": "Spain",
            "seed": "TRANSFER-API-REGRESSION",
        },
    )
    assert create_response.status_code == 201, create_response.text
    career_id = create_response.json()["career_id"]

    first_advance = client.post(f"/career/{career_id}/advance")
    assert first_advance.status_code == 200, first_advance.text
    session_after_advance = client.get(f"/career/{career_id}").json()
    assert session_after_advance["season_summary"] is not None

    offers_response = client.get(f"/career/{career_id}/offers")
    assert offers_response.status_code == 200, offers_response.text
    offers = offers_response.json()["available_offers"]
    assert offers, "Expected transfer offers to be generated"

    accept_response = client.post(
        f"/career/{career_id}/transfer",
        json={"offer_id": offers[0]["offer_id"], "action": "ACCEPT"},
    )
    assert accept_response.status_code == 200, accept_response.text

    session = accept_response.json()
    assert session["career"]["current_club_id"] == offers[0]["destination_club_name"]
    assert session["season_summary"] is not None
