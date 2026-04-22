#!/usr/bin/env bash
# archive-mission.sh — Phase 6 of the mission workflow.
#
# Moves a completed mission folder to ./.agent-missions/_archive/ and records
# the closure reason in a sibling ARCHIVE.md at the archive root.
#
# Usage:
#   ./.agent/scripts/archive-mission.sh <mission-id> [reason]
#
# Examples:
#   ./.agent/scripts/archive-mission.sh mission-20260421-131600 "closed-approved"
#   ./.agent/scripts/archive-mission.sh mission-20260421-131600 "abandoned: scope changed"

set -euo pipefail

# Script lives at dev-team/.agent/scripts/ — climb two levels to reach dev-team/.
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
MISSIONS_DIR="$ROOT_DIR/.agent-missions"
ARCHIVE_DIR="$MISSIONS_DIR/_archive"

if [[ $# -lt 1 ]]; then
  echo "usage: $0 <mission-id> [reason]" >&2
  exit 2
fi

MISSION_ID="$1"
REASON="${2:-closed-approved}"
SRC="$MISSIONS_DIR/$MISSION_ID"

if [[ ! -d "$SRC" ]]; then
  echo "error: mission folder not found: $SRC" >&2
  exit 1
fi

mkdir -p "$ARCHIVE_DIR"
DEST="$ARCHIVE_DIR/$MISSION_ID"

if [[ -e "$DEST" ]]; then
  echo "error: archive destination already exists: $DEST" >&2
  exit 1
fi

mv "$SRC" "$DEST"

ISO_NOW="$(date +%Y-%m-%dT%H:%M:%S%z | sed -E 's/([+-][0-9]{2})([0-9]{2})$/\1:\2/')"
LEDGER="$ARCHIVE_DIR/ARCHIVE.md"

if [[ ! -f "$LEDGER" ]]; then
  cat > "$LEDGER" <<'HEADER'
# Archived Missions

| Mission ID | Archived At | Reason |
|---|---|---|
HEADER
fi

printf '| %s | %s | %s |\n' "$MISSION_ID" "$ISO_NOW" "$REASON" >> "$LEDGER"

echo "Archived $MISSION_ID → $DEST"
echo "Ledger updated: $LEDGER"
