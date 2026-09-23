#!/bin/bash

# ============================================
# Unit Tests Script
# ============================================
# Purpose: Run C# Plugin and TypeScript WebResource tests
# Usage: bash run-unit-tests.sh --min-coverage 80
# ============================================

set -e

MIN_COVERAGE=80
TESTS_FAILED=0

while [[ $# -gt 0 ]]; do
  case $1 in
    --python-version)
      # No longer needed - kept for backwards compatibility
      shift 2
      ;;
    --min-coverage)
      MIN_COVERAGE="$2"
      shift 2
      ;;
    *)
      shift
      ;;
  esac
done

echo "============================================"
echo "Stage 2: Unit Tests - D365 Customer Service"
echo "============================================"
echo "Min Coverage:  $MIN_COVERAGE%"
echo "Test Suites:   C# Plugins, TypeScript WebResources"
echo ""

# ============================================
# PART 1: C# PLUGIN TESTS
# ============================================
echo "--------------------------------------------"
echo "PART 1: C# Plugin Tests"
echo "--------------------------------------------"

if [ -d "tests/Plugins" ]; then
  echo "[1/4] Setting up .NET environment..."
  dotnet --version
  echo "✓ .NET available"
  echo ""

  echo "[2/4] Restoring NuGet packages..."
  dotnet restore tests/Plugins/
  echo "✓ Packages restored"
  echo ""

  echo "[3/4] Building test project..."
  dotnet build tests/Plugins/ --configuration Release --no-restore
  echo "✓ Build successful"
  echo ""

  echo "[4/4] Running Plugin tests..."
  mkdir -p test-results

  dotnet test tests/Plugins/ \
    --configuration Release \
    --no-build \
    --verbosity normal \
    --logger "trx;LogFileName=plugin-test-results.trx" \
    --results-directory test-results/ \
    --collect:"XPlat Code Coverage" \
    -- DataCollectionRunSettings.DataCollectors.DataCollector.Configuration.Format=cobertura

  PLUGIN_EXIT_CODE=$?

  if [ $PLUGIN_EXIT_CODE -eq 0 ]; then
    echo "✓ Plugin tests PASSED"
  else
    echo "✗ Plugin tests FAILED"
    TESTS_FAILED=1
  fi
else
  echo "⚠ No tests found in tests/Plugins/ - skipping"
fi

echo ""

# ============================================
# PART 2: TYPESCRIPT WEBRESOURCE TESTS
# ============================================
echo "--------------------------------------------"
echo "PART 2: TypeScript WebResource Tests"
echo "--------------------------------------------"

if [ -d "tests/WebResources" ]; then
  echo "[1/3] Setting up Node environment..."
  node --version
  npm --version
  echo "✓ Node available"
  echo ""

  echo "[2/3] Installing dependencies..."
  # Check if package.json exists in WebResources tests
  if [ -f "tests/WebResources/package.json" ]; then
    cd tests/WebResources
    npm install --silent
    echo "✓ Dependencies installed"
    echo ""

    echo "[3/3] Running WebResource tests..."
    mkdir -p ../../test-results

    npm test -- \
      --coverage \
      --coverageThreshold='{"global":{"lines":'"$MIN_COVERAGE"'}}' \
      --reporters=default \
      --reporters=jest-junit \
      --outputFile=../../test-results/webresource-test-results.xml 2>&1

    WR_EXIT_CODE=$?
    cd ../..

    if [ $WR_EXIT_CODE -eq 0 ]; then
      echo "✓ WebResource tests PASSED"
    else
      echo "✗ WebResource tests FAILED"
      TESTS_FAILED=1
    fi
  else
    echo "⚠ No package.json found in tests/WebResources/ - skipping"
  fi
else
  echo "⚠ No tests found in tests/WebResources/ - skipping"
fi

echo ""

# ============================================
# SUMMARY
# ============================================
echo "============================================"
echo "Unit Test Summary"
echo "============================================"
echo ""

if [ -d "test-results" ]; then
  echo "Test result files:"
  ls -la test-results/ 2>/dev/null || echo "  No result files generated yet"
fi

echo ""

if [ $TESTS_FAILED -eq 0 ]; then
  echo "✓ ALL TESTS PASSED"
  exit 0
else
  echo "✗ SOME TESTS FAILED - check output above"
  exit 1
fi