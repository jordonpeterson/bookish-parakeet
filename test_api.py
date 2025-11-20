import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_make_incident_returns_200():
    """Test that /trigger/incident endpoint returns 200 status code."""
    response = client.post(
        "/trigger/incident",
        json={"description": "Test incident from API test"}
    )

    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_make_incident_creates_record():
    """Test that the incident endpoint returns a list."""
    response = client.post(
        "/trigger/incident",
        json={"description": "Another test incident"}
    )

    assert response.status_code == 200
    result = response.json()
    assert isinstance(result, list)


def test_update_incident_returns_200():
    """Test that PUT /triggers/incident returns 200 status code."""
    # First, create an incident
    create_response = client.post(
        "/trigger/incident",
        json={"description": "Incident to update"}
    )

    # Now update it by matching the description
    update_response = client.put(
        "/triggers/incident",
        json={
            "description": "Incident to update",
            "resolution": "Issue resolved by restarting service"
        }
    )

    assert update_response.status_code == 200
    assert update_response.json()["status"] == "success"
    assert "data" in update_response.json()


def test_update_incident_updates_record():
    """Test that the incident is actually updated in the database."""
    # First, create an incident
    create_response = client.post(
        "/trigger/incident",
        json={"description": "Original description"}
    )

    # Update it by matching the description
    update_response = client.put(
        "/triggers/incident",
        json={
            "description": "Original description",
            "resolution": "Fixed the problem"
        }
    )

    assert update_response.status_code == 200
    data = update_response.json()["data"]
    assert len(data) > 0
    assert data[0]["description"] == "Original description"
    assert data[0]["resolution"] == "Fixed the problem"


def test_update_nonexistent_incident():
    """Test that updating a non-existent incident returns an error."""
    response = client.put(
        "/triggers/incident",
        json={
            "description": "This description does not exist in the database",
            "resolution": "Some resolution"
        }
    )

    assert response.status_code == 200
    assert response.json()["status"] == "error"
    assert response.json()["message"] == "Incident not found"
