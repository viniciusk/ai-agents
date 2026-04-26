#!/usr/bin/env bash
# new-mission.sh — Phase 0 of the mission workflow.
#
# Creates ./.agent-missions/mission-YYYYMMDD-HHMMSS/, copies the 01_MISSION_STATE.md
# template into it, and echoes the mission ID on stdout (so callers can capture it).
#
# Usage:
#   ./.agent/scripts/new-mission.sh [feature-slug]
#
# Example:
#   MISSION_ID=$(./.agent/scripts/new-mission.sh user-notifications)
#   echo "Started $MISSION_ID"

set -euo pipefail

# Resolve the dev-team root from this script's location, independent of caller cwd.
# Script lives at dev-team/.agent/scripts/ — climb two levels to reach dev-team/.
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"

MISSIONS_DIR="$ROOT_DIR/.agent-missions"
TEMPLATE="$ROOT_DIR/.agent/templates/01_MISSION_STATE.md"

if [[ ! -f "$TEMPLATE" ]]; then
  echo "error: 01_MISSION_STATE.md template not found at $TEMPLATE" >&2
  exit 1
fi

FEATURE_SLUG="${1:-unnamed}"
TIMESTAMP="$(date +%Y%m%d-%H%M%S)"
MISSION_ID="mission-${TIMESTAMP}"
MISSION_PATH="$MISSIONS_DIR/$MISSION_ID"

mkdir -p "$MISSION_PATH"

# Instantiate 01_MISSION_STATE.md from the template with placeholders filled in.
ISO_NOW="$(date +%Y-%m-%dT%H:%M:%S%z | sed -E 's/([+-][0-9]{2})([0-9]{2})$/\1:\2/')"
sed \
  -e "s|{{MISSION_ID}}|$MISSION_ID|g" \
  -e "s|{{ISO_8601_TIMESTAMP}}|$ISO_NOW|g" \
  -e "s|{{feature-slug}}|$FEATURE_SLUG|g" \
  "$TEMPLATE" > "$MISSION_PATH/01_MISSION_STATE.md"

# Stdout: the mission ID (machine-readable). Stderr: human-friendly confirmation.
echo "$MISSION_ID"
echo "Mission started at $MISSION_PATH" >&2
