#!/bin/bash

echo "============================================================"
echo "E2E RAG Test - Full Stack Verification (via curl)"
echo "============================================================"

BASE_URL="http://127.0.0.1:8000"

# Step 1: Create first incident
echo ""
echo "📝 Step 1: Creating first incident 'I can't login'"
RESPONSE1=$(curl -s -X POST "$BASE_URL/trigger/incident" \
  -H "Content-Type: application/json" \
  -d '{"description": "I cant login"}')

echo "   Response: $RESPONSE1"

if [[ $RESPONSE1 == "[]" ]]; then
  echo "   ✅ Success: Returned empty list"
else
  echo "   ❌ FAILED: Expected [], got $RESPONSE1"
  exit 1
fi

# Step 2: Update incident with resolution
echo ""
echo "🔄 Step 2: Updating incident with resolution 'Try harder'"
RESPONSE2=$(curl -s -X PUT "$BASE_URL/triggers/incident" \
  -H "Content-Type: application/json" \
  -d '{"description": "I cant login", "resolution": "Try harder"}')

echo "   Response: $RESPONSE2"

if [[ $RESPONSE2 == *'"status":"success"'* ]]; then
  echo "   ✅ Success: Incident updated"
else
  echo "   ❌ FAILED: Expected success, got $RESPONSE2"
  exit 1
fi

# Wait for embedding
echo ""
echo "⏳ Waiting 4 seconds for embedding to be stored..."
sleep 4

# Step 3: Create second incident
echo ""
echo "📝 Step 3: Creating incident 'Logging in does not work'"
RESPONSE3=$(curl -s -X POST "$BASE_URL/trigger/incident" \
  -H "Content-Type: application/json" \
  -d '{"description": "Logging in does not work"}')

echo "   Response: $RESPONSE3"

if [[ $RESPONSE3 == *"Try harder"* ]]; then
  echo "   ✅ Success: Found resolution 'Try harder' via RAG!"
else
  echo "   ❌ FAILED: Expected ['Try harder'], got $RESPONSE3"
  exit 1
fi

echo ""
echo "============================================================"
echo "🎉 ALL E2E RAG TESTS PASSED!"
echo "============================================================"
echo ""
echo "Verified:"
echo "  ✓ New incidents return empty list"
echo "  ✓ Incidents can be updated with resolutions"
echo "  ✓ Similar incidents return relevant resolutions via RAG"
echo "  ✓ Gemini API integration working"
echo "  ✓ pgvector similarity search working"
echo "  ✓ Full stack integration successful"
echo ""
