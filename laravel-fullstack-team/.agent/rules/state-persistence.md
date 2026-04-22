---
trigger: always_on
---

# Rule: Cognitive Continuity

## Context

Agents in this workspace are part of a long-running software development lifecycle. Cross-session context must be preserved in `.agent/state/context.json`. Per-mission state lives in `./.agent-missions/mission-{{ID}}/MISSION_STATE.md` and is governed by `mission-control.md`.

## Mandatory Actions

1. **Initial Sync:** Before starting any task, read `.agent/state/context.json`. If the file does not exist, create it using the schema below with empty/null values.
2. **Decision Logging:** Every time an architectural or logic choice is made that will outlive the current mission (cross-cutting conventions, stack-level choices, persisted data shapes), append an entry to `architectural_decisions`.
3. **Final Handover:** Before terminating a turn, update `last_updated` (ISO 8601 with timezone) and `active_feature` (set to the current mission ID, or `"None"` if idle).
4. **Schema:** `context.json` MUST conform to this shape exactly. No extra keys; no renamed keys.
   ```json
   {
     "last_updated": "2026-04-21T13:16:00+07:00",
     "active_feature": "mission-20260421-131600",
     "architectural_decisions": [
       "Maintain max 10 deleted items stack; persist via localStorage; append to list bottom strictly."
     ],
     "pending_tasks": []
   }
   ```

## Field Reference

- `last_updated` — ISO 8601 timestamp with timezone; updated on every handover.
- `active_feature` — mission ID (format `mission-YYYYMMDD-hhmmss`) currently in progress, or the string `"None"`.
- `architectural_decisions` — append-only list of durable decisions. Per-mission tactical decisions belong in that mission's `MISSION_STATE.md`, not here.
- `pending_tasks` — work identified during a mission that is intentionally deferred outside of it (e.g. cross-cutting refactors). Clear entries when addressed.

## Validation

Run `./.agent/scripts/validate-state.sh` to confirm `context.json` matches the schema before ending a session.
