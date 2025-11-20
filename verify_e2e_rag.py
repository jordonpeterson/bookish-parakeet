#!/usr/bin/env python3
"""
Standalone E2E test for RAG functionality.
This script makes real HTTP requests to a running FastAPI server.

Usage:
1. Start the server: uvicorn main:app --reload --port 8000
2. Run this script: python3 verify_e2e_rag.py
"""

import requests
import time
import sys
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

BASE_URL = "http://127.0.0.1:8000"


def test_e2e_rag_flow():
    """
    Test the complete RAG workflow:
    1. Create incident "I can't login" -> returns empty list (no similar incidents)
    2. Update incident with resolution "Try harder" -> returns 200
    3. Create incident "Logging in does not work" -> returns ["Try harder"]
    """

    # Check if GEMINI_API_KEY is set
    if not os.getenv("GEMINI_API_KEY"):
        print("❌ GEMINI_API_KEY not set in environment")
        print("Please set GEMINI_API_KEY in your .env file")
        return False

    print("\n" + "="*60)
    print("E2E RAG Test - Full Stack Verification")
    print("="*60)

    try:
        # Step 1: Create first incident with description "I can't login"
        print("\n📝 Step 1: Creating first incident 'I can't login'")
        response1 = requests.post(
            f"{BASE_URL}/trigger/incident",
            json={"description": "I can't login"}
        )

        print(f"   Status: {response1.status_code}")
        print(f"   Response: {response1.json()}")

        if response1.status_code != 200:
            print(f"❌ FAILED: Expected 200, got {response1.status_code}")
            return False

        result1 = response1.json()
        if not isinstance(result1, list):
            print(f"❌ FAILED: Expected list, got {type(result1)}")
            return False

        if result1 != []:
            print(f"❌ FAILED: Expected empty list, got {result1}")
            return False

        print("   ✅ Success: Returned empty list (no similar incidents)")

        # Step 2: Update the incident with resolution "Try harder"
        print("\n🔄 Step 2: Updating incident with resolution 'Try harder'")
        response2 = requests.put(
            f"{BASE_URL}/triggers/incident",
            json={
                "description": "I can't login",
                "resolution": "Try harder"
            }
        )

        print(f"   Status: {response2.status_code}")
        print(f"   Response: {response2.json()}")

        if response2.status_code != 200:
            print(f"❌ FAILED: Expected 200, got {response2.status_code}")
            return False

        result2 = response2.json()
        if result2.get("status") != "success":
            print(f"❌ FAILED: Expected success status, got {result2}")
            return False

        print("   ✅ Success: Incident updated with resolution")

        # Wait for embedding to be generated and stored
        print("\n⏳ Waiting 3 seconds for embedding to be stored...")
        time.sleep(3)

        # Step 3: Create second incident with similar description
        print("\n📝 Step 3: Creating incident 'Logging in does not work'")
        response3 = requests.post(
            f"{BASE_URL}/trigger/incident",
            json={"description": "Logging in does not work"}
        )

        print(f"   Status: {response3.status_code}")
        print(f"   Response: {response3.json()}")

        if response3.status_code != 200:
            print(f"❌ FAILED: Expected 200, got {response3.status_code}")
            return False

        result3 = response3.json()
        if not isinstance(result3, list):
            print(f"❌ FAILED: Expected list, got {type(result3)}")
            return False

        if len(result3) == 0:
            print(f"❌ FAILED: Expected non-empty list, got empty list")
            print("   This means RAG did not find the similar incident")
            return False

        if "Try harder" not in result3:
            print(f"❌ FAILED: Expected 'Try harder' in {result3}")
            return False

        print(f"   ✅ Success: Found similar incident with resolution: {result3}")

        print("\n" + "="*60)
        print("🎉 ALL E2E RAG TESTS PASSED!")
        print("="*60)
        print("\nVerified:")
        print("  ✓ New incidents return empty list (no similar incidents)")
        print("  ✓ Incidents can be updated with resolutions")
        print("  ✓ Similar incidents return relevant resolutions via RAG")
        print("  ✓ Gemini API integration working")
        print("  ✓ pgvector similarity search working")
        print("  ✓ Full stack integration successful")
        print()
        return True

    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: Could not connect to FastAPI server")
        print(f"Make sure the server is running: uvicorn main:app --reload --port 8000")
        return False
    except Exception as e:
        print(f"\n❌ ERROR: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_e2e_rag_flow()
    sys.exit(0 if success else 1)
