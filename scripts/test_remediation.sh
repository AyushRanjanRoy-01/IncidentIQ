#!/bin/bash

# Test remediation actions script

set -e

API_URL="${API_URL:-http://localhost:8000}"
INCIDENT_ID="${1:-test-incident-001}"

echo "🧪 Testing remediation actions for incident: $INCIDENT_ID"

# Test remediation creation
echo "📝 Creating remediation action..."
REMEDIATION_RESPONSE=$(curl -s -X POST "$API_URL/api/v1/remediations" \
  -H "Content-Type: application/json" \
  -d "{
    \"incident_id\": \"$INCIDENT_ID\",
    \"action_type\": \"rollback\",
    \"description\": \"Rollback deployment to previous version\",
    \"confidence\": 0.9,
    \"requires_approval\": true
  }")

REMEDIATION_ID=$(echo "$REMEDIATION_RESPONSE" | jq -r '.remediation_id')
echo "✅ Created remediation: $REMEDIATION_ID"

# Test approval
echo "✅ Approving remediation..."
curl -s -X POST "$API_URL/api/v1/remediations/$REMEDIATION_ID/approve" \
  -H "Content-Type: application/json" \
  -d "{
    \"approved_by\": \"test-user\",
    \"approval_notes\": \"Test approval\"
  }" | jq '.'

# Test execution
echo "⚙️  Executing remediation..."
curl -s -X POST "$API_URL/api/v1/remediations/$REMEDIATION_ID/execute" \
  -H "Content-Type: application/json" | jq '.'

# Check status
echo "📊 Checking remediation status..."
curl -s "$API_URL/api/v1/remediations/$REMEDIATION_ID" | jq '.'

echo "✅ Remediation test complete!"
