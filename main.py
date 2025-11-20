from fastapi import FastAPI
from pydantic import BaseModel
from supabase import create_client, Client
import os

app = FastAPI()

# Supabase configuration
SUPABASE_URL = os.getenv("SUPABASE_URL", "http://127.0.0.1:54321")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZS1kZW1vIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImV4cCI6MTk4MzgxMjk5Nn0.EGIM96RAZx35lJzdJsyH-qQwv8Hdp7fsn3W0YpN81IU")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


class IncidentRequest(BaseModel):
    description: str


@app.post("/trigger/incident")
async def make_incident(incident: IncidentRequest):
    """Create a new incident with the provided description."""
    result = supabase.table("incidents").insert({
        "description": incident.description
    }).execute()

    return {"status": "success", "data": result.data}


@app.get("/")
async def root():
    return {"message": "FastAPI + Supabase Local"}
