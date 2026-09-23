from fastapi.testclient import TestClient

from src.app import app

client = TestClient(app)


def test_signup_rejects_duplicate_participant():
    activity_name = "Chess Club"
    email = "duplicate@mergington.edu"

    first = client.post(f"/activities/{activity_name}/signup?email={email}")
    assert first.status_code == 200

    second = client.post(f"/activities/{activity_name}/signup?email={email}")
    assert second.status_code == 400
    assert "already" in second.json()["detail"].lower()


def test_unregister_removes_participant():
    activity_name = "Programming Class"
    email = "remove-me@mergington.edu"

    signup = client.post(f"/activities/{activity_name}/signup?email={email}")
    assert signup.status_code == 200

    response = client.delete(f"/activities/{activity_name}/unregister?email={email}")
    assert response.status_code == 200
    assert email not in response.json()["participants"]
