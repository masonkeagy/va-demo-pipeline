#!/bin/bash

# ============================================
# Unit Tests Script
# ============================================
# Purpose: Run unit tests with coverage reporting
# Usage: bash run-unit-tests.sh --python-version 3.11
# ============================================

set -e

PYTHON_VERSION="3.11"
MIN_COVERAGE=80

while [[ $# -gt 0 ]]; do
  case $1 in
    --python-version)
      PYTHON_VERSION="$2"
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
echo "Stage 2: Unit Tests"
echo "============================================"
echo "Python Version: $PYTHON_VERSION"
echo "Min Coverage: $MIN_COVERAGE%"
echo ""

# Install dependencies
echo "[1/3] Installing dependencies..."
pip install pytest pandas numpy pytest-cov matplotlib openpyxl --quiet
echo "✓ Dependencies installed"
echo ""

# Run unit tests
echo "[2/3] Running unit tests..."
pytest tests/test_pipeline.py -v --tb=short
TESTS_EXIT_CODE=$?
echo "✓ Unit tests completed"
echo ""

# Run coverage
echo "[3/3] Running coverage analysis..."
pytest tests/test_pipeline.py \
  -v \
  --tb=short \
  --cov=read_data \
  --cov-report=term-missing \
  --cov-report=html \
  --cov-fail-under=$MIN_COVERAGE
COVERAGE_EXIT_CODE=$?

if [ $COVERAGE_EXIT_CODE -eq 0 ]; then
  echo "✓ Coverage threshold met: $MIN_COVERAGE%"
else
  echo "✗ Coverage below threshold"
  exit 1
fi

if [ $TESTS_EXIT_CODE -ne 0 ]; then
  exit 1
fi

echo ""
echo "============================================"
echo "✓ Unit Tests Complete"
echo "============================================"