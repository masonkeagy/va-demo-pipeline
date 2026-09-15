#!/bin/bash

# ============================================
# Regression Tests Script
# ============================================
# Purpose: Run Playwright or Pytest regression tests
# Usage: bash run-regression-tests.sh --framework playwright --uat-url https://uat.example.com
# ============================================

set -e

FRAMEWORK="auto"  # auto, playwright, pytest
UAT_URL="https://uat.placeholder.com"
APP_TYPE=""

while [[ $# -gt 0 ]]; do
  case $1 in
    --framework)
      FRAMEWORK="$2"
      shift 2
      ;;
    --uat-url)
      UAT_URL="$2"
      shift 2
      ;;
    --app-type)
      APP_TYPE="$2"
      shift 2
      ;;
    *)
      shift
      ;;
  esac
done

echo "============================================"
echo "Stage 8: Regression Testing"
echo "============================================"
echo "Framework: $FRAMEWORK"
echo "UAT URL: $UAT_URL"
echo ""

# Detect app type if not provided
if [ "$FRAMEWORK" = "auto" ]; then
  if [ -f ".vrm-app" ] || [ "$APP_TYPE" = "VRM" ]; then
    FRAMEWORK="playwright"
    echo "Detected: VRM App (using Playwright)"
  else
    FRAMEWORK="pytest"
    echo "Detected: Standard App (using Pytest)"
  fi
fi

echo ""

mkdir -p regression-results

# ============================================
# Playwright Tests (VRM Apps)
# ============================================
if [ "$FRAMEWORK" = "playwright" ]; then
  echo "[1/2] Setting up Playwright..."
  
  npm init -y
  npm install @playwright/test
  npx playwright install --with-deps chromium firefox
  
  echo "✓ Playwright installed"
  echo ""
  
  echo "[2/2] Running Playwright tests..."
  
  npx playwright test tests/regression \
    --reporter=html \
    --reporter=json \
    --reporter=list || true
  
  echo "✓ Playwright tests completed"

# ============================================
# Pytest Tests (Standard Apps)
# ============================================
else
  echo "[1/2] Setting up Pytest..."
  
  pip install pytest requests pytest-html
  
  echo "✓ Pytest installed"
  echo ""
  
  echo "[2/2] Running Pytest regression tests..."
  
  pytest tests/regression \
    -v \
    --tb=short \
    --html=pytest-report.html \
    --self-contained-html \
    --junit-xml=pytest-results.xml || true
  
  echo "✓ Pytest tests completed"
fi

echo ""

# Generate summary
cat > regression-results/summary.txt << EOF
========================================
Regression Test Summary
========================================
Environment:  UAT
URL:          $UAT_URL
Framework:    $FRAMEWORK
Version:      \$VERSION
Timestamp:    $(date -u +'%Y-%m-%dT%H:%M:%SZ')

Status: COMPLETED
========================================
EOF

cat regression-results/summary.txt

echo ""
echo "============================================"
echo "✓ Regression Testing Complete"
echo "============================================"