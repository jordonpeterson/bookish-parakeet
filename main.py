from fastapi import FastAPI
from pydantic import BaseModel
from supabase import create_client, Client
import os
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables from .env file
load_dotenv()

app = FastAPI()

# Supabase configuration
SUPABASE_URL = os.getenv("SUPABASE_URL", "http://127.0.0.1:54321")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZS1kZW1vIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImV4cCI6MTk4MzgxMjk5Nn0.EGIM96RAZx35lJzdJsyH-qQwv8Hdp7fsn3W0YpN81IU")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Gemini API configuration
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)


class IncidentRequest(BaseModel):
    description: str


class IncidentUpdateRequest(BaseModel):
    description: str
    resolution: str

def queryRag(description: str) -> list[int]:
    """Query RAG database for incidents similar to the given description.

    Args:
        description: The incident description to search for

    Returns:
        List of incident IDs that are similar to the description
    """
    if not GEMINI_API_KEY or not description:
        return []

    try:
        # Generate embedding for the query description using Gemini
        result = genai.embed_content(
            model="models/embedding-001",
            content=description,
            task_type="retrieval_query",
            output_dimensionality=768
        )
        query_embedding = result['embedding']

        # Convert embedding list to PostgreSQL vector format
        embedding_str = "[" + ",".join(map(str, query_embedding)) + "]"

        # Query database for similar embeddings using cosine distance
        # The <=> operator computes cosine distance (lower = more similar)
        response = supabase.rpc(
            'match_incident_embeddings',
            {
                'query_embedding': embedding_str,
                'match_threshold': 0.5,
                'match_count': 5
            }
        ).execute()

        # Extract incident IDs from the results
        incident_ids = [row['incident_id'] for row in response.data]
        return incident_ids

    except Exception as e:
        print(f"Error querying RAG: {e}")
        return []


def getMatchingIncidents(description: str) -> list[str]:
    # Access RAG to get matching incidents from description
    incident_ids = queryRag(description)

    if not incident_ids:
        return []

    # Query database for the resolutions of matching incidents
    result = supabase.table("incidents").select("resolution").in_("id", incident_ids).execute()

    # Extract resolution strings from the results
    resolutions = [incident["resolution"] for incident in result.data if incident.get("resolution")]
    return resolutions


@app.post("/trigger/incident")
async def make_incident(incident: IncidentRequest):
    """Create a new incident with the provided description."""
    result = supabase.table("incidents").insert({
        "description": incident.description
    }).execute()

    # Return list of strings (to be populated later)
    return getMatchingIncidents(incident.description)

def update_memory(description: str, resolution: str) -> list[int]:
    """Store embeddings for an incident in the RAG database.

    Args:
        description: The incident description
        resolution: The incident resolution

    Returns:
        List of incident IDs that were updated with embeddings
    """
    if not GEMINI_API_KEY or not description:
        return []

    try:
        # Find the incident ID by description
        result = supabase.table("incidents").select("id").eq("description", description).execute()

        if not result.data:
            print(f"No incident found with description: {description}")
            return []

        incident_id = result.data[0]["id"]

        # Generate embedding for the description using Gemini
        # Use task_type="retrieval_document" for storing documents
        embedding_result = genai.embed_content(
            model="models/embedding-001",
            content=description,
            task_type="retrieval_document",
            output_dimensionality=768
        )
        embedding = embedding_result['embedding']

        # Convert embedding list to PostgreSQL vector format
        embedding_str = "[" + ",".join(map(str, embedding)) + "]"

        # Upsert the embedding into the incident_embeddings table
        # Use upsert to handle cases where embedding already exists
        upsert_result = supabase.table("incident_embeddings").upsert({
            "incident_id": incident_id,
            "embedding": embedding_str
        }, on_conflict="incident_id").execute()

        print(f"Successfully stored embedding for incident {incident_id}")
        return [incident_id]

    except Exception as e:
        print(f"Error updating memory: {e}")
        return []


@app.put("/triggers/incident")
async def update_incident(incident: IncidentUpdateRequest):
    """Update an existing incident by finding it via description and adding a resolution."""
    result = supabase.table("incidents").update({
        "resolution": incident.resolution
    }).eq("description", incident.description).execute()

    update_memory(incident.description, incident.resolution)

    if not result.data:
        return {"status": "error", "message": "Incident not found"}

    return {"status": "success", "data": result.data}


@app.get("/")
async def root():
    return {"message": "FastAPI + Supabase Local"}
