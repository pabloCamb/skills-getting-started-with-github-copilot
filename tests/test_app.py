from copy import deepcopy
from urllib.parse import quote

import pytest
from fastapi.testclient import TestClient

from src import app as app_module

client = TestClient(app_module.app)


@pytest.fixture(autouse=True)
def reset_activities():
    """Restore in-memory activity data before and after each test."""
    original = deepcopy(app_module.activities)

    app_module.activities.clear()
    app_module.activities.update(deepcopy(original))

    yield

    app_module.activities.clear()
    app_module.activities.update(deepcopy(original))


def test_get_activities_returns_activity_data():
    # Arrange
    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    payload = response.json()
    assert isinstance(payload, dict)
    assert "Chess Club" in payload
    assert "participants" in payload["Chess Club"]


def test_signup_registers_valid_participant():
    # Arrange
    activity_name = "Soccer Club"
    email = "new-player@mergington.edu"

    # Act
    response = client.post(
        f"/activities/{quote(activity_name)}/signup?email={quote(email)}"
    )

    # Assert
    assert response.status_code == 200
    body = response.json()
    assert body["message"] == f"Signed up {email} for {activity_name}"
    assert email in app_module.activities[activity_name]["participants"]


def test_signup_rejects_duplicate_participant():
    # Arrange
    activity_name = "Chess Club"
    email = "michael@mergington.edu"

    # Act
    response = client.post(
        f"/activities/{quote(activity_name)}/signup?email={quote(email)}"
    )

    # Assert
    assert response.status_code == 400
    assert "already" in response.json()["detail"].lower()


def test_unregister_removes_participant():
    # Arrange
    activity_name = "Programming Class"
    email = "remove-me@mergington.edu"
    signup_response = client.post(
        f"/activities/{quote(activity_name)}/signup?email={quote(email)}"
    )
    assert signup_response.status_code == 200

    # Act
    response = client.delete(
        f"/activities/{quote(activity_name)}/unregister?email={quote(email)}"
    )

    # Assert
    assert response.status_code == 200
    body = response.json()
    assert email not in body["participants"]
    assert email not in app_module.activities[activity_name]["participants"]


def test_signup_unknown_activity_returns_404():
    # Arrange
    activity_name = "Nonexistent Activity"
    email = "student@mergington.edu"

    # Act
    response = client.post(
        f"/activities/{quote(activity_name)}/signup?email={quote(email)}"
    )

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_unregister_unknown_activity_returns_404():
    # Arrange
    activity_name = "Nonexistent Activity"
    email = "student@mergington.edu"

    # Act
    response = client.delete(
        f"/activities/{quote(activity_name)}/unregister?email={quote(email)}"
    )

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_unregister_unregistered_participant_returns_404():
    # Arrange
    activity_name = "Track and Field"
    email = "not-registered@mergington.edu"

    # Act
    response = client.delete(
        f"/activities/{quote(activity_name)}/unregister?email={quote(email)}"
    )

    # Assert
    assert response.status_code == 404
    assert "not registered" in response.json()["detail"].lower()
