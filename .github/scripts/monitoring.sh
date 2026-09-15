#!/bin/bash

# ============================================
# Monitoring Integration Script
# ============================================
# Purpose: Send deployment events to monitoring tools
# Usage: bash monitoring.sh --app APP --version VERSION --sha SHA --actor ACTOR
# ============================================

set -e  # Exit on error

# Parse arguments
APP_NAME=""
VERSION=""
SHA=""
ACTOR=""

while [[ $# -gt 0 ]]; do
  case $1 in
    --app)
      APP_NAME="$2"
      shift 2
      ;;
    --version)
      VERSION="$2"
      shift 2
      ;;
    --sha)
      SHA="$2"
      shift 2
      ;;
    --actor)
      ACTOR="$2"
      shift 2
      ;;
    *)
      echo "Unknown parameter: $1"
      exit 1
      ;;
  esac
done

# Validate inputs
if [ -z "$APP_NAME" ] || [ -z "$VERSION" ]; then
  echo "Error: --app and --version are required"
  exit 1
fi

echo "============================================"
echo "Monitoring Integration"
echo "============================================"
echo "App: $APP_NAME"
echo "Version: $VERSION"
echo "SHA: $SHA"
echo "Actor: $ACTOR"
echo ""

# ============================================
# 1. Azure App Insights - Send Custom Event
# ============================================
send_to_app_insights() {
  echo "[1/4] Sending event to Azure App Insights..."
  
  if [ -z "$APPINSIGHTS_INSTRUMENTATION_KEY" ]; then
    echo "⚠ APPINSIGHTS_INSTRUMENTATION_KEY not set, skipping..."
    return 0
  fi
  
  TIMESTAMP=$(date -u +'%Y-%m-%dT%H:%M:%S.000Z')
  
  PAYLOAD=$(cat <<EOF
{
  "name": "Microsoft.ApplicationInsights.Event",
  "time": "$TIMESTAMP",
  "iKey": "$APPINSIGHTS_INSTRUMENTATION_KEY",
  "data": {
    "baseType": "EventData",
    "baseData": {
      "ver": 2,
      "name": "DeploymentCompleted",
      "properties": {
        "application": "$APP_NAME",
        "version": "$VERSION",
        "environment": "production",
        "sha": "$SHA",
        "deployed_by": "$ACTOR"
      },
      "measurements": {
        "deployment_duration": 300
      }
    }
  }
}
EOF
)
  
  RESPONSE=$(curl -s -w "\n%{http_code}" -X POST \
    "https://dc.applicationinsights.azure.com/api/track" \
    -H "Content-Type: application/json" \
    -d "$PAYLOAD")
  
  HTTP_CODE=$(echo "$RESPONSE" | tail -n 1)
  
  if [ "$HTTP_CODE" = "200" ]; then
    echo "✓ App Insights event sent (HTTP $HTTP_CODE)"
  else
    echo "⚠ App Insights returned HTTP $HTTP_CODE (may still be ok)"
  fi
}

# ============================================
# 2. Dynatrace - Send Deployment Event
# ============================================
send_to_dynatrace() {
  echo "[2/4] Sending event to Dynatrace..."
  
  if [ -z "$DYNATRACE_API_TOKEN" ] || [ -z "$DYNATRACE_ENV_ID" ]; then
    echo "⚠ Dynatrace credentials not set, skipping..."
    return 0
  fi
  
  PAYLOAD=$(cat <<EOF
{
  "eventType": "DEPLOYMENT",
  "title": "$APP_NAME $VERSION deployed to production",
  "description": "Successful deployment via GitHub Actions CI/CD pipeline",
  "entitySelector": "type(APPLICATION),tag(app:$APP_NAME)",
  "properties": {
    "version": "$VERSION",
    "build_sha": "$SHA",
    "deployed_by": "$ACTOR",
    "deployment_strategy": "canary",
    "repository": "github.com",
    "branch": "main"
  },
  "customProperties": {
    "cicd_pipeline": "GitHub Actions",
    "deployment_method": "automated"
  }
}
EOF
)
  
  RESPONSE=$(curl -s -w "\n%{http_code}" -X POST \
    "https://${DYNATRACE_ENV_ID}.live.dynatrace.com/api/v2/events/ingest" \
    -H "Authorization: Api-Token ${DYNATRACE_API_TOKEN}" \
    -H "Content-Type: application/json" \
    -d "$PAYLOAD")
  
  HTTP_CODE=$(echo "$RESPONSE" | tail -n 1)
  
  if [ "$HTTP_CODE" = "201" ] || [ "$HTTP_CODE" = "200" ]; then
    echo "✓ Dynatrace event created (HTTP $HTTP_CODE)"
  else
    echo "⚠ Dynatrace returned HTTP $HTTP_CODE"
  fi
}

# ============================================
# 3. Splunk - Send Events via HEC
# ============================================
send_to_splunk() {
  echo "[3/4] Sending events to Splunk..."
  
  if [ -z "$SPLUNK_HEC_URL" ] || [ -z "$SPLUNK_HEC_TOKEN" ]; then
    echo "⚠ Splunk credentials not set, skipping..."
    return 0
  fi
  
  TIMESTAMP=$(date +%s)
  
  # Deployment event
  PAYLOAD=$(cat <<EOF
{
  "event": {
    "event_type": "deployment_completed",
    "application": "$APP_NAME",
    "version": "$VERSION",
    "environment": "production",
    "status": "SUCCESS",
    "deployed_by": "$ACTOR",
    "sha": "$SHA",
    "timestamp": "$TIMESTAMP"
  },
  "sourcetype": "cicd_deployment",
  "source": "github_actions",
  "host": "github"
}
EOF
)
  
  RESPONSE=$(curl -s -w "\n%{http_code}" -X POST \
    "$SPLUNK_HEC_URL" \
    -H "Authorization: Splunk $SPLUNK_HEC_TOKEN" \
    -H "Content-Type: application/json" \
    -d "$PAYLOAD")
  
  HTTP_CODE=$(echo "$RESPONSE" | tail -n 1)
  
  if [ "$HTTP_CODE" = "200" ]; then
    echo "✓ Splunk deployment event sent (HTTP $HTTP_CODE)"
  else
    echo "⚠ Splunk returned HTTP $HTTP_CODE"
  fi
}

# ============================================
# 4. JIRA - Update Ticket
# ============================================
send_to_jira() {
  echo "[4/4] Updating JIRA ticket..."
  
  if [ -z "$JIRA_API_TOKEN" ] || [ -z "$JIRA_KEY" ]; then
    echo "⚠ JIRA credentials not set, skipping..."
    return 0
  fi
  
  PAYLOAD=$(cat <<EOF
{
  "fields": {
    "status": { "name": "Done" },
    "resolution": { "name": "Fixed" },
    "comment": {
      "body": "✅ Production Deployment Completed\n\nVersion: $VERSION\nSHA: $SHA\nDeployed by: $ACTOR\nTimestamp: $(date -u +'%Y-%m-%dT%H:%M:%SZ')\n\n🔍 Monitoring Active:\n• Azure App Insights\n• Dynatrace\n• Splunk"
    }
  }
}
EOF
)
  
  RESPONSE=$(curl -s -w "\n%{http_code}" -X PUT \
    "https://jira.your-domain.com/rest/api/3/issues/$JIRA_KEY" \
    -H "Authorization: Bearer $JIRA_API_TOKEN" \
    -H "Content-Type: application/json" \
    -d "$PAYLOAD")
  
  HTTP_CODE=$(echo "$RESPONSE" | tail -n 1)
  
  if [ "$HTTP_CODE" = "204" ] || [ "$HTTP_CODE" = "200" ]; then
    echo "✓ JIRA ticket updated (HTTP $HTTP_CODE)"
  else
    echo "⚠ JIRA returned HTTP $HTTP_CODE"
  fi
}

# ============================================
# Execute all integrations
# ============================================
echo ""
send_to_app_insights
echo ""
send_to_dynatrace
echo ""
send_to_splunk
echo ""
send_to_jira

echo ""
echo "============================================"
echo "✓ Monitoring integrations completed"
echo "============================================"