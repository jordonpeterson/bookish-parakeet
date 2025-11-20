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
    assert response.json()["status"] == "success"
    assert "data" in response.json()


def test_make_incident_creates_record():
    """Test that the incident is actually created in the database."""
    response = client.post(
        "/trigger/incident",
        json={"description": "Another test incident"}
    )

    assert response.status_code == 200
    data = response.json()["data"]
    assert len(data) > 0
    assert data[0]["description"] == "Another test incident"
