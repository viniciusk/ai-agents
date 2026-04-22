#!/usr/bin/env bash
# run-tests.sh — wrap `php artisan test` so output can be pasted directly into
# TEST_REPORT_RED.md (Phase 3) or FINAL_REVIEW.md (Phase 5) without reformatting.
#
# Usage:
#   ./.agent/scripts/run-tests.sh red   <mission-id>   # run suite, EXPECT failures (Phase 3)
#   ./.agent/scripts/run-tests.sh green <mission-id>   # run suite, EXPECT all pass  (Phase 5)
#
# The script prints a block that mirrors the template's "Run Metadata" + "Full Test
# Output" sections. It does NOT edit the mission's markdown file — paste the output
# yourself so the agent remains the author of the artifact.
#
# Exit codes:
#   0 — outcome matches mode (red: tests failed, green: tests passed)
#   1 — outcome contradicts mode (paste output, investigate)
#   2 — usage error or Laravel project not detected

set -uo pipefail

# Script lives at dev-team/.agent/scripts/ — climb two levels to reach dev-team/.
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"

if [[ $# -lt 2 ]]; then
  echo "usage: $0 <red|green> <mission-id>" >&2
  exit 2
fi

MODE="$1"
MISSION_ID="$2"

case "$MODE" in
  red|green) ;;
  *) echo "error: mode must be 'red' or 'green' (got '$MODE')" >&2; exit 2 ;;
esac

# Locate the Laravel project root. Convention: it lives as a sibling of dev-team/,
# but allow the user to override with DEV_TEAM_LARAVEL_ROOT.
LARAVEL_ROOT="${DEV_TEAM_LARAVEL_ROOT:-$ROOT_DIR/..}"
if [[ ! -f "$LARAVEL_ROOT/artisan" ]]; then
  echo "error: could not find artisan at $LARAVEL_ROOT/artisan" >&2
  echo "hint:  export DEV_TEAM_LARAVEL_ROOT=/path/to/your/laravel/project" >&2
  exit 2
fi

ISO_NOW="$(date +%Y-%m-%dT%H:%M:%S%z | sed -E 's/([+-][0-9]{2})([0-9]{2})$/\1:\2/')"
PHP_VERSION="$(php -v 2>/dev/null | head -n 1 || echo 'unknown')"
LARAVEL_VERSION="$(cd "$LARAVEL_ROOT" && php artisan --version 2>/dev/null || echo 'unknown')"

echo "---"
echo "mission: $MISSION_ID"
echo "mode:    $MODE"
echo "ran_at:  $ISO_NOW"
echo "php:     $PHP_VERSION"
echo "laravel: $LARAVEL_VERSION"
echo "---"
echo

TMP_OUT="$(mktemp)"
trap 'rm -f "$TMP_OUT"' EXIT

(cd "$LARAVEL_ROOT" && php artisan test) 2>&1 | tee "$TMP_OUT"
TEST_EXIT=${PIPESTATUS[0]}

echo
echo "---"
case "$MODE" in
  red)
    if [[ $TEST_EXIT -ne 0 ]]; then
      echo "outcome: RED (tests failed as expected) ✅"
      exit 0
    else
      echo "outcome: tests unexpectedly PASSED while in RED mode ❌" >&2
      echo "         either the tests are wrong, or code already implements the feature." >&2
      exit 1
    fi
    ;;
  green)
    if [[ $TEST_EXIT -eq 0 ]]; then
      echo "outcome: GREEN (all tests passed) ✅"
      exit 0
    else
      echo "outcome: tests FAILED while in GREEN mode ❌" >&2
      echo "         implementation is not complete — inspect output above." >&2
      exit 1
    fi
    ;;
esac
