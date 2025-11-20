# bookish-parakeet
Helps resolve incidents faster by summarizing relevant log data and linking to similar previous incidents.

## Fast-Startup Python Webserver

This project includes a lightweight Python webserver with minimal startup time, built using Python's standard library.

### Features
- **Fast startup**: Uses built-in `http.server` module (no external dependencies)
- **RESTful API**: JSON-based endpoints for incident management
- **CORS support**: Cross-origin requests enabled
- **Health check**: `/health` endpoint for monitoring

### Requirements
- Python 3.7 or higher
- No external dependencies

### Quick Start

```bash
# Run the server
python3 server.py

# Or make it executable and run directly
chmod +x server.py
./server.py
```

The server will start on `http://0.0.0.0:8000` by default.

### API Endpoints

- `GET /` - API information and available endpoints
- `GET /health` - Health check endpoint
- `GET /incidents` - List all incidents
- `POST /incidents` - Create a new incident

### Example Usage

```bash
# Check server health
curl http://localhost:8000/health

# Get API info
curl http://localhost:8000/

# List incidents
curl http://localhost:8000/incidents

# Create an incident
curl -X POST http://localhost:8000/incidents \
  -H "Content-Type: application/json" \
  -d '{"title": "Database connection issue", "severity": "high"}'
```

### Performance

The server is optimized for fast startup:
- No external dependencies to load
- Minimal imports from standard library
- Startup time typically < 0.1 seconds
