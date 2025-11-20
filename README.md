# bookish-parakeet
Helps resolve incidents faster by summarizing relevant log data and linking to similar previous incidents.

## Setup

### Prerequisites
- Docker (for Supabase)
- Python 3.8+
- Supabase CLI

### Installation

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

2. Start Supabase locally:
```bash
supabase start
```

3. Run the FastAPI application:
```bash
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`

### API Endpoints

- `POST /trigger/incident` - Create a new incident
  - Request body: `{"description": "string"}`
  - Example:
    ```bash
    curl -X POST http://localhost:8000/trigger/incident \
      -H "Content-Type: application/json" \
      -d '{"description": "Database connection timeout"}'
    ```

### Supabase

- Studio URL: http://127.0.0.1:54323
- API URL: http://127.0.0.1:54321
- DB URL: postgresql://postgres:postgres@127.0.0.1:54322/postgres

To stop Supabase:
```bash
supabase stop
```
