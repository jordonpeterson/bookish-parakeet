#!/usr/bin/env python3
"""
Fast-startup Python webserver for incident resolution system.

Uses Python's built-in http.server for minimal dependencies and fast startup.
"""
import json
import time
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs


class IncidentHandler(BaseHTTPRequestHandler):
    """HTTP request handler for incident resolution endpoints."""

    def log_message(self, format, *args):
        """Override to provide cleaner log output."""
        pass  # Disable default logging for faster performance

    def _send_json_response(self, status_code, data):
        """Send a JSON response."""
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

    def do_GET(self):
        """Handle GET requests."""
        parsed_path = urlparse(self.path)
        path = parsed_path.path

        # Health check endpoint
        if path == '/health':
            self._send_json_response(200, {
                'status': 'healthy',
                'service': 'incident-resolver'
            })
            return

        # Root endpoint
        if path == '/':
            self._send_json_response(200, {
                'message': 'Incident Resolution API',
                'version': '1.0.0',
                'endpoints': [
                    '/health',
                    '/incidents',
                    '/incidents/<id>',
                    '/incidents/search'
                ]
            })
            return

        # List incidents endpoint
        if path == '/incidents':
            query_params = parse_qs(parsed_path.query)
            self._send_json_response(200, {
                'incidents': [],
                'total': 0,
                'message': 'No incidents found'
            })
            return

        # Not found
        self._send_json_response(404, {
            'error': 'Not Found',
            'path': path
        })

    def do_POST(self):
        """Handle POST requests."""
        parsed_path = urlparse(self.path)
        path = parsed_path.path

        # Create incident endpoint
        if path == '/incidents':
            content_length = int(self.headers.get('Content-Length', 0))
            if content_length > 0:
                body = self.rfile.read(content_length)
                try:
                    data = json.loads(body.decode())
                    self._send_json_response(201, {
                        'message': 'Incident created',
                        'incident_id': 'placeholder-id',
                        'data': data
                    })
                    return
                except json.JSONDecodeError:
                    self._send_json_response(400, {
                        'error': 'Invalid JSON'
                    })
                    return

        # Not found
        self._send_json_response(404, {
            'error': 'Not Found',
            'path': path
        })

    def do_OPTIONS(self):
        """Handle OPTIONS requests for CORS."""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()


def run_server(host='0.0.0.0', port=8000):
    """Start the web server."""
    server_address = (host, port)
    httpd = HTTPServer(server_address, IncidentHandler)
    print(f'Server running on http://{host}:{port}')
    print('Press Ctrl+C to stop')
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print('\nShutting down server...')
        httpd.shutdown()


if __name__ == '__main__':
    start_time = time.time()
    run_server()
    startup_time = time.time() - start_time
    print(f'Startup time: {startup_time:.3f} seconds')
