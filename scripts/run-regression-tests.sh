#!/usr/bin/env bash

set -euo pipefail

UAT_URL="${UAT_URL:-}"
while [[ $# -gt 0 ]]; do
  case "$1" in
    --uat-url)
      if [[ $# -lt 2 ]]; then
        echo "ERROR: --uat-url requires a value" >&2
        exit 2
      fi
      UAT_URL="$2"
      shift 2
      ;;
    *)
      echo "ERROR: Unknown argument: $1" >&2
      exit 2
      ;;
  esac
done

if [[ -z "$UAT_URL" ]]; then
  echo "ERROR: Set UAT_URL or pass --uat-url https://<environment>.crm.dynamics.com" >&2
  exit 2
fi

mkdir -p regression-results

set +e
python -m pytest tests/regression \
  --junitxml=regression-results/junit.xml \
  -v \
  --tb=short
TEST_EXIT_CODE=$?
set -e

python - "$TEST_EXIT_CODE" <<'PY'
import json
import sys
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path

exit_code = int(sys.argv[1])
report = Path("regression-results/junit.xml")
if not report.exists():
    raise SystemExit("Pytest did not produce regression-results/junit.xml")

root = ET.parse(report).getroot()
if root.tag == "testsuites":
    totals = {name: sum(int(suite.get(name, 0)) for suite in root.findall("testsuite"))
              for name in ("tests", "failures", "errors", "skipped")}
else:
    totals = {name: int(root.get(name, 0)) for name in
              ("tests", "failures", "errors", "skipped")}

summary = {
    "status": "success" if exit_code == 0 else "failure",
    "functionalTests": totals["tests"],
    "failedTests": totals["failures"] + totals["errors"],
    "skippedTests": totals["skipped"],
    "environment": "UAT",
    "timestamp": datetime.now(timezone.utc).isoformat(),
}
Path("regression-results/regression-summary.json").write_text(
    json.dumps(summary, indent=2) + "\n", encoding="utf-8"
)
PY

cat regression-results/regression-summary.json
exit "$TEST_EXIT_CODE"
