import pytest
from fastapi.testclient import TestClient
from main import app, GEMINI_API_KEY
import time

client = TestClient(app)


@pytest.mark.skipif(not GEMINI_API_KEY, reason="GEMINI_API_KEY not set in environment")
class TestE2ERAGFlow:
    """End-to-end test for RAG functionality with real API calls."""

    def test_full_rag_workflow(self):
        """
        Test the complete RAG workflow:
        1. Create incident "I can't login" -> returns empty list (no similar incidents)
        2. Update incident with resolution "Try harder" -> returns 200
        3. Create incident "Logging in does not work" -> returns ["Try harder"]
        """

        # Step 1: Create first incident with description "I can't login"
        print("\n=== Step 1: Creating first incident ===")
        response1 = client.post(
            "/trigger/incident",
            json={"description": "I can't login"}
        )

        print(f"Response status: {response1.status_code}")
        print(f"Response body: {response1.json()}")

        assert response1.status_code == 200, f"Expected 200, got {response1.status_code}"
        result1 = response1.json()
        assert isinstance(result1, list), "Expected a list response"
        assert result1 == [], f"Expected empty list, got {result1}"
        print("✓ First incident created, returned empty list as expected")

        # Step 2: Update the incident with resolution "Try harder"
        print("\n=== Step 2: Updating incident with resolution ===")
        response2 = client.put(
            "/triggers/incident",
            json={
                "description": "I can't login",
                "resolution": "Try harder"
            }
        )

        print(f"Response status: {response2.status_code}")
        print(f"Response body: {response2.json()}")

        assert response2.status_code == 200, f"Expected 200, got {response2.status_code}"
        result2 = response2.json()
        assert result2["status"] == "success", f"Expected success, got {result2}"
        assert "data" in result2, "Expected 'data' field in response"
        print("✓ Incident updated successfully with resolution")

        # Wait a moment to ensure embedding is stored
        print("\n=== Waiting for embedding to be stored ===")
        time.sleep(2)

        # Step 3: Create second incident with similar description
        print("\n=== Step 3: Creating second incident with similar description ===")
        response3 = client.post(
            "/trigger/incident",
            json={"description": "Logging in does not work"}
        )

        print(f"Response status: {response3.status_code}")
        print(f"Response body: {response3.json()}")

        assert response3.status_code == 200, f"Expected 200, got {response3.status_code}"
        result3 = response3.json()
        assert isinstance(result3, list), "Expected a list response"

        # Verify that we got the resolution from the similar incident
        assert len(result3) > 0, f"Expected at least one resolution, got empty list"
        assert "Try harder" in result3, f"Expected 'Try harder' in {result3}"
        print(f"✓ Found similar incident with resolution: {result3}")

        print("\n=== ✅ All E2E RAG tests passed! ===")


@pytest.mark.skipif(not GEMINI_API_KEY, reason="GEMINI_API_KEY not set in environment")
class TestE2ERAGWithMultipleIncidents:
    """Test RAG with multiple similar incidents."""

    def test_multiple_similar_incidents(self):
        """
        Test that RAG returns multiple resolutions when there are multiple similar incidents.
        """
        print("\n=== Testing multiple similar incidents ===")

        # Create and resolve first incident
        client.post("/trigger/incident", json={"description": "Database connection timeout"})
        client.put("/triggers/incident", json={
            "description": "Database connection timeout",
            "resolution": "Increase connection pool size"
        })

        # Create and resolve second similar incident
        client.post("/trigger/incident", json={"description": "DB connection fails"})
        client.put("/triggers/incident", json={
            "description": "DB connection fails",
            "resolution": "Check network firewall rules"
        })

        # Wait for embeddings to be stored
        time.sleep(2)

        # Query with similar description
        response = client.post(
            "/trigger/incident",
            json={"description": "Cannot connect to database"}
        )

        print(f"Response: {response.json()}")

        assert response.status_code == 200
        result = response.json()
        assert isinstance(result, list)

        # Should find at least one of the similar incidents
        assert len(result) > 0, "Expected to find similar incidents"

        # Check if we got the expected resolutions
        has_relevant_resolution = any(
            "connection" in r.lower() or "pool" in r.lower() or "firewall" in r.lower()
            for r in result
        )
        assert has_relevant_resolution, f"Expected relevant resolutions, got {result}"

        print(f"✓ Found {len(result)} similar incident(s) with resolutions: {result}")
