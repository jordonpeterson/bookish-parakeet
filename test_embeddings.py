import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from main import app, update_memory, queryRag
import os

client = TestClient(app)


class TestUpdateMemory:
    """Tests for the update_memory function."""

    @patch('main.genai.embed_content')
    @patch('main.supabase')
    def test_update_memory_success(self, mock_supabase, mock_embed):
        """Test that update_memory successfully generates and stores embeddings."""
        # Mock the database query to find incident
        mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value.data = [
            {"id": 1}
        ]

        # Mock the Gemini embedding response
        mock_embed.return_value = {
            'embedding': [0.1] * 768  # Mock 768-dimensional embedding
        }

        # Mock the upsert response
        mock_supabase.table.return_value.upsert.return_value.execute.return_value.data = [
            {"incident_id": 1, "embedding": "[0.1, 0.1, ...]"}
        ]

        # Mock GEMINI_API_KEY environment variable
        with patch('main.GEMINI_API_KEY', 'fake-api-key'):
            result = update_memory("Test incident", "Test resolution")

        # Verify result
        assert result == [1]

        # Verify Gemini API was called with correct parameters
        mock_embed.assert_called_once_with(
            model="models/embedding-001",
            content="Test incident",
            task_type="retrieval_document",
            output_dimensionality=768
        )

    @patch('main.supabase')
    def test_update_memory_no_incident_found(self, mock_supabase):
        """Test that update_memory returns empty list when incident not found."""
        # Mock the database query to return no results
        mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value.data = []

        with patch('main.GEMINI_API_KEY', 'fake-api-key'):
            result = update_memory("Nonexistent incident", "Resolution")

        assert result == []

    def test_update_memory_no_api_key(self):
        """Test that update_memory returns empty list when API key is missing."""
        with patch('main.GEMINI_API_KEY', None):
            result = update_memory("Test incident", "Test resolution")

        assert result == []

    def test_update_memory_empty_description(self):
        """Test that update_memory returns empty list for empty description."""
        with patch('main.GEMINI_API_KEY', 'fake-api-key'):
            result = update_memory("", "Test resolution")

        assert result == []

    @patch('main.genai.embed_content')
    @patch('main.supabase')
    def test_update_memory_api_error(self, mock_supabase, mock_embed):
        """Test that update_memory handles API errors gracefully."""
        # Mock the database query to find incident
        mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value.data = [
            {"id": 1}
        ]

        # Mock the Gemini API to raise an exception
        mock_embed.side_effect = Exception("API Error")

        with patch('main.GEMINI_API_KEY', 'fake-api-key'):
            result = update_memory("Test incident", "Test resolution")

        assert result == []


class TestQueryRag:
    """Tests for the queryRag function."""

    @patch('main.genai.embed_content')
    @patch('main.supabase')
    def test_query_rag_success(self, mock_supabase, mock_embed):
        """Test that queryRag successfully finds similar incidents."""
        # Mock the Gemini embedding response
        mock_embed.return_value = {
            'embedding': [0.2] * 768  # Mock 768-dimensional embedding
        }

        # Mock the RPC response with matching incidents
        mock_supabase.rpc.return_value.execute.return_value.data = [
            {"incident_id": 2, "similarity": 0.95},
            {"incident_id": 5, "similarity": 0.87}
        ]

        with patch('main.GEMINI_API_KEY', 'fake-api-key'):
            result = queryRag("Similar incident description")

        # Verify result
        assert result == [2, 5]

        # Verify Gemini API was called with correct parameters
        mock_embed.assert_called_once_with(
            model="models/embedding-001",
            content="Similar incident description",
            task_type="retrieval_query",
            output_dimensionality=768
        )

    def test_query_rag_no_api_key(self):
        """Test that queryRag returns empty list when API key is missing."""
        with patch('main.GEMINI_API_KEY', None):
            result = queryRag("Test description")

        assert result == []

    def test_query_rag_empty_description(self):
        """Test that queryRag returns empty list for empty description."""
        with patch('main.GEMINI_API_KEY', 'fake-api-key'):
            result = queryRag("")

        assert result == []

    @patch('main.genai.embed_content')
    @patch('main.supabase')
    def test_query_rag_no_matches(self, mock_supabase, mock_embed):
        """Test that queryRag returns empty list when no matches are found."""
        # Mock the Gemini embedding response
        mock_embed.return_value = {
            'embedding': [0.3] * 768
        }

        # Mock the RPC response with no matches
        mock_supabase.rpc.return_value.execute.return_value.data = []

        with patch('main.GEMINI_API_KEY', 'fake-api-key'):
            result = queryRag("Unique incident")

        assert result == []

    @patch('main.genai.embed_content')
    @patch('main.supabase')
    def test_query_rag_api_error(self, mock_supabase, mock_embed):
        """Test that queryRag handles API errors gracefully."""
        # Mock the Gemini API to raise an exception
        mock_embed.side_effect = Exception("API Error")

        with patch('main.GEMINI_API_KEY', 'fake-api-key'):
            result = queryRag("Test description")

        assert result == []


class TestEndToEndRAG:
    """End-to-end tests for the RAG functionality."""

    @patch('main.genai.embed_content')
    @patch('main.supabase')
    @patch('main.GEMINI_API_KEY', 'fake-api-key')
    def test_full_rag_flow(self, mock_supabase, mock_embed):
        """Test the complete flow: create incident -> update with resolution -> query similar."""
        # Setup mock responses for creating an incident
        mock_supabase.table.return_value.insert.return_value.execute.return_value.data = [
            {"id": 10, "description": "Database connection timeout"}
        ]

        # Mock queryRag to return no similar incidents initially
        mock_embed.return_value = {'embedding': [0.5] * 768}
        mock_supabase.rpc.return_value.execute.return_value.data = []
        mock_supabase.table.return_value.select.return_value.in_.return_value.execute.return_value.data = []

        # Create an incident
        response = client.post(
            "/trigger/incident",
            json={"description": "Database connection timeout"}
        )
        assert response.status_code == 200
        assert isinstance(response.json(), list)

        # Now update the incident with a resolution
        # Mock the select query for update_memory
        mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value.data = [
            {"id": 10}
        ]

        # Mock the update query
        mock_supabase.table.return_value.update.return_value.eq.return_value.execute.return_value.data = [
            {
                "id": 10,
                "description": "Database connection timeout",
                "resolution": "Increased connection pool size"
            }
        ]

        # Mock the upsert for embeddings
        mock_supabase.table.return_value.upsert.return_value.execute.return_value.data = [
            {"incident_id": 10}
        ]

        update_response = client.put(
            "/triggers/incident",
            json={
                "description": "Database connection timeout",
                "resolution": "Increased connection pool size"
            }
        )
        assert update_response.status_code == 200
        assert update_response.json()["status"] == "success"

        # Now query for similar incidents
        # Mock the RPC to return the incident we just created
        mock_supabase.rpc.return_value.execute.return_value.data = [
            {"incident_id": 10, "similarity": 0.99}
        ]

        # Mock the select query to get resolutions
        mock_supabase.table.return_value.select.return_value.in_.return_value.execute.return_value.data = [
            {
                "id": 10,
                "description": "Database connection timeout",
                "resolution": "Increased connection pool size"
            }
        ]

        # Query for similar incidents
        similar_response = client.post(
            "/trigger/incident",
            json={"description": "DB timeout issue"}
        )
        assert similar_response.status_code == 200
        # Should find the previously created incident with similar description

    @patch('main.genai.embed_content')
    @patch('main.supabase')
    @patch('main.GEMINI_API_KEY', 'fake-api-key')
    def test_rag_with_multiple_similar_incidents(self, mock_supabase, mock_embed):
        """Test that RAG returns multiple similar incidents when they exist."""
        # Mock embedding generation
        mock_embed.return_value = {'embedding': [0.4] * 768}

        # Mock RPC to return multiple similar incidents
        mock_supabase.rpc.return_value.execute.return_value.data = [
            {"incident_id": 1, "similarity": 0.95},
            {"incident_id": 3, "similarity": 0.90},
            {"incident_id": 7, "similarity": 0.85}
        ]

        # Mock select to return resolutions for all incidents
        mock_supabase.table.return_value.select.return_value.in_.return_value.execute.return_value.data = [
            {"id": 1, "resolution": "Resolution 1"},
            {"id": 3, "resolution": "Resolution 3"},
            {"id": 7, "resolution": "Resolution 7"}
        ]

        # Mock insert for new incident
        mock_supabase.table.return_value.insert.return_value.execute.return_value.data = [
            {"id": 99, "description": "Test incident"}
        ]

        response = client.post(
            "/trigger/incident",
            json={"description": "Test incident"}
        )

        assert response.status_code == 200
        resolutions = response.json()
        assert len(resolutions) == 3
        assert "Resolution 1" in resolutions
        assert "Resolution 3" in resolutions
        assert "Resolution 7" in resolutions


class TestEdgeCases:
    """Test edge cases and error handling."""

    @patch('main.GEMINI_API_KEY', None)
    def test_endpoints_without_api_key(self):
        """Test that endpoints work gracefully without API key (no RAG features)."""
        with patch('main.supabase') as mock_supabase:
            # Mock insert
            mock_supabase.table.return_value.insert.return_value.execute.return_value.data = [
                {"id": 1, "description": "Test"}
            ]

            response = client.post(
                "/trigger/incident",
                json={"description": "Test incident"}
            )

            # Should still work but return empty list (no RAG functionality)
            assert response.status_code == 200
            assert response.json() == []

    @patch('main.genai.embed_content')
    @patch('main.supabase')
    @patch('main.GEMINI_API_KEY', 'fake-api-key')
    def test_special_characters_in_description(self, mock_supabase, mock_embed):
        """Test that special characters in descriptions are handled correctly."""
        description = "Error with 'quotes' and \"double quotes\" and \n newlines"

        # Mock embedding
        mock_embed.return_value = {'embedding': [0.6] * 768}

        # Mock database responses
        mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value.data = [
            {"id": 1}
        ]
        mock_supabase.table.return_value.upsert.return_value.execute.return_value.data = [
            {"incident_id": 1}
        ]

        result = update_memory(description, "Fixed the issue")
        assert result == [1]

        # Verify the embedding was called with the description as-is
        mock_embed.assert_called_once()
        call_args = mock_embed.call_args[1]
        assert call_args['content'] == description
