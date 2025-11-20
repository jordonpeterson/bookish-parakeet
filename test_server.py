#!/usr/bin/env python3
"""
Tests for the fast-startup webserver.
"""
import json
import unittest
import time
from http.client import HTTPConnection
from threading import Thread


class TestIncidentServer(unittest.TestCase):
    """Test cases for the incident resolution server."""

    @classmethod
    def setUpClass(cls):
        """Start the server before running tests."""
        from server import run_server
        
        cls.server_thread = Thread(target=run_server, daemon=True)
        cls.server_thread.start()
        # Give the server time to start
        time.sleep(0.5)

    def _make_request(self, method, path, body=None):
        """Helper method to make HTTP requests."""
        conn = HTTPConnection('localhost', 8000, timeout=5)
        headers = {'Content-Type': 'application/json'} if body else {}
        
        if body:
            body = json.dumps(body)
        
        conn.request(method, path, body=body, headers=headers)
        response = conn.getresponse()
        data = response.read().decode()
        
        return response.status, json.loads(data) if data else None

    def test_health_endpoint(self):
        """Test the health check endpoint."""
        status, data = self._make_request('GET', '/health')
        self.assertEqual(status, 200)
        self.assertEqual(data['status'], 'healthy')
        self.assertEqual(data['service'], 'incident-resolver')

    def test_root_endpoint(self):
        """Test the root endpoint."""
        status, data = self._make_request('GET', '/')
        self.assertEqual(status, 200)
        self.assertIn('message', data)
        self.assertIn('endpoints', data)
        self.assertIsInstance(data['endpoints'], list)

    def test_list_incidents(self):
        """Test listing incidents."""
        status, data = self._make_request('GET', '/incidents')
        self.assertEqual(status, 200)
        self.assertIn('incidents', data)
        self.assertIsInstance(data['incidents'], list)

    def test_create_incident(self):
        """Test creating an incident."""
        incident_data = {
            'title': 'Test incident',
            'severity': 'medium'
        }
        status, data = self._make_request('POST', '/incidents', incident_data)
        self.assertEqual(status, 201)
        self.assertIn('incident_id', data)
        self.assertEqual(data['data']['title'], incident_data['title'])

    def test_not_found(self):
        """Test 404 response."""
        status, data = self._make_request('GET', '/nonexistent')
        self.assertEqual(status, 404)
        self.assertIn('error', data)


class TestStartupTime(unittest.TestCase):
    """Test server startup performance."""

    def test_import_time(self):
        """Test that module imports quickly."""
        start = time.time()
        import server
        import_time = time.time() - start
        
        # Should import in less than 0.1 seconds
        self.assertLess(import_time, 0.1, 
                       f"Import took {import_time:.4f}s, should be < 0.1s")


if __name__ == '__main__':
    unittest.main()
