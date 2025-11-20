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
  - Returns: List of strings (to be populated with relevant information)
  - Example:
    ```bash
    curl -X POST http://localhost:8000/trigger/incident \
      -H "Content-Type: application/json" \
      -d '{"description": "Database connection timeout"}'
    ```

- `PUT /triggers/incident` - Update an existing incident by finding it via description
  - Request body: `{"description": "string", "resolution": "string"}`
  - Finds the incident with matching description and adds the resolution
  - Example:
    ```bash
    curl -X PUT http://localhost:8000/triggers/incident \
      -H "Content-Type: application/json" \
      -d '{"description": "Database connection timeout", "resolution": "Restarted the database service"}'
    ```

### Testing

Run all tests with pytest:
```bash
python3 -m pytest test_api.py -v
```

Or simply:
```bash
pytest test_api.py -v
```

The `-v` flag enables verbose output showing each test result.

### Supabase Local Development

- Studio URL: http://127.0.0.1:54323
- API URL: http://127.0.0.1:54321
- DB URL: postgresql://postgres:postgres@127.0.0.1:54322/postgres

To stop Supabase:
```bash
supabase stop
```

## Production Deployment

### Prerequisites
- A Supabase account and project (https://supabase.com)
- Gemini API key (https://aistudio.google.com/app/apikey)

### Deployment Steps

1. **Get Supabase Credentials**
   - Go to your Supabase Dashboard → Project Settings → API
   - Copy your **Project URL** and **service_role key**

2. **Create `.env` file**
   ```bash
   cp .env.example .env
   ```

   Fill in your production credentials:
   ```env
   SUPABASE_URL=https://your-project-ref.supabase.co
   SUPABASE_KEY=your-supabase-service-role-key
   GEMINI_API_KEY=your-gemini-api-key
   ```

3. **Link to Production Supabase**
   ```bash
   supabase link --project-ref your-project-ref
   ```

4. **Push Database Migrations**
   ```bash
   supabase db push
   ```

   This will create:
   - `incidents` table
   - `incident_embeddings` table with pgvector extension
   - `match_incident_embeddings` RPC function

5. **Run the Application**
   ```bash
   uvicorn main:app --reload
   ```

### Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `SUPABASE_URL` | Your Supabase project URL | `https://xxxxx.supabase.co` |
| `SUPABASE_KEY` | Service role key (secret) | `eyJhbG...` |
| `GEMINI_API_KEY` | Google Gemini API key | `AIza...` |
