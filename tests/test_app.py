import pytest
from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)

def test_get_activities():
    response = client.get("/activities")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data

def test_signup_for_activity_success():
    response = client.post("/activities/Chess Club/signup?email=tester@mergington.edu")
    assert response.status_code == 200
    assert "Signed up" in response.json().get("message", "")

    # Clean up: remove the test participant
    client.delete("/activities/Chess Club/unregister?email=tester@mergington.edu")

def test_signup_duplicate():
    email = "michael@mergington.edu"
    response = client.post(f"/activities/Chess Club/signup?email={email}")
    assert response.status_code == 400
    assert response.json()["detail"] == "Already signed up"

def test_signup_activity_full():
    # Simulate a full activity
    activity = "Tennis Club"
    for i in range(10):
        client.post(f"/activities/{activity}/signup?email=full{i}@mergington.edu")
    response = client.post(f"/activities/{activity}/signup?email=overflow@mergington.edu")
    assert response.status_code == 400
    assert response.json()["detail"] == "Activity is full"

    # Clean up
    for i in range(10):
        client.delete(f"/activities/{activity}/unregister?email=full{i}@mergington.edu")
    client.delete(f"/activities/{activity}/unregister?email=overflow@mergington.edu")

def test_unregister_participant():
    email = "remove@mergington.edu"
    client.post(f"/activities/Programming Class/signup?email={email}")
    response = client.delete(f"/activities/Programming Class/unregister?email={email}")
    assert response.status_code == 200
    assert "Unregistered" in response.json().get("message", "")

def test_unregister_not_found():
    response = client.delete("/activities/Programming Class/unregister?email=notfound@mergington.edu")
    assert response.status_code == 400
    assert response.json()["detail"] == "Participant not found"
