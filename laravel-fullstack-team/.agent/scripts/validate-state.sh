#!/usr/bin/env bash
# validate-state.sh — schema check for context.json and, optionally, a mission's MISSION_STATE.md.
#
# Usage:
#   ./.agent/scripts/validate-state.sh                    # validate .agent/state/context.json
#   ./.agent/scripts/validate-state.sh <mission-id>       # also validate that mission's MISSION_STATE.md headings
#
# Exit codes:
#   0 — all checks passed
#   1 — validation failure (message on stderr)
#   2 — prerequisite missing (e.g. jq not installed)

set -euo pipefail

# Script lives at dev-team/.agent/scripts/ — climb two levels to reach dev-team/.
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
CONTEXT="$ROOT_DIR/.agent/state/context.json"

if ! command -v jq >/dev/null 2>&1; then
  echo "error: jq is required. Install via 'brew install jq' or 'apt-get install jq'." >&2
  exit 2
fi

fail() { echo "FAIL: $*" >&2; exit 1; }
ok()   { echo "ok: $*"; }

# ---- 1. context.json ----------------------------------------------------------

if [[ ! -f "$CONTEXT" ]]; then
  fail "context.json not found at $CONTEXT"
fi

if ! jq empty "$CONTEXT" >/dev/null 2>&1; then
  fail "context.json is not valid JSON"
fi

# Required keys: exactly this set.
REQUIRED_KEYS=(last_updated active_feature architectural_decisions pending_tasks)
ACTUAL_KEYS=$(jq -r 'keys_unsorted[]' "$CONTEXT" | sort)
EXPECTED_KEYS=$(printf '%s\n' "${REQUIRED_KEYS[@]}" | sort)

if [[ "$ACTUAL_KEYS" != "$EXPECTED_KEYS" ]]; then
  echo "expected keys:" >&2
  echo "$EXPECTED_KEYS" >&2
  echo "actual keys:" >&2
  echo "$ACTUAL_KEYS" >&2
  fail "context.json keys do not match schema in .agent/rules/state-persistence.md"
fi

# Type checks.
jq -e '.last_updated | type == "string"'            "$CONTEXT" >/dev/null || fail "last_updated must be a string"
jq -e '.active_feature | type == "string"'          "$CONTEXT" >/dev/null || fail "active_feature must be a string"
jq -e '.architectural_decisions | type == "array"'  "$CONTEXT" >/dev/null || fail "architectural_decisions must be an array"
jq -e '.pending_tasks | type == "array"'            "$CONTEXT" >/dev/null || fail "pending_tasks must be an array"

# Soft ISO 8601 check (YYYY-MM-DDThh:mm:ss with timezone).
TS=$(jq -r '.last_updated' "$CONTEXT")
if ! [[ "$TS" =~ ^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}([+-][0-9]{2}:?[0-9]{2}|Z)$ ]]; then
  fail "last_updated ($TS) is not ISO 8601 with a timezone"
fi

ok "context.json conforms to schema"

# ---- 2. MISSION_STATE.md (optional) ------------------------------------------

if [[ $# -ge 1 ]]; then
  MISSION_ID="$1"
  MSTATE="$ROOT_DIR/.agent-missions/$MISSION_ID/MISSION_STATE.md"
  if [[ ! -f "$MSTATE" ]]; then
    fail "MISSION_STATE.md not found for $MISSION_ID (looked at $MSTATE)"
  fi

  REQUIRED_SECTIONS=(
    "## Mission Metadata"
    "## Artifact Locations"
    "## Phase Log"
    "## Deviations from Plan"
    "## Open Questions"
    "## Revision History"
  )
  for sec in "${REQUIRED_SECTIONS[@]}"; do
    if ! grep -Fq "$sec" "$MSTATE"; then
      fail "MISSION_STATE.md for $MISSION_ID is missing required section: $sec"
    fi
  done
  ok "MISSION_STATE.md for $MISSION_ID has all required sections"
fi

echo "all checks passed."
