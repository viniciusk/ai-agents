# Halt Report — {{MISSION_ID}}

> Produced by the `halt-mission` skill when an agent determines the mission cannot proceed without human intervention. This is a contract, not a prose note — every section must be filled. If a section genuinely does not apply, write `none` explicitly so the human auditor knows it was considered.

## Halt Metadata

- **Mission ID:** `{{MISSION_ID}}`
- **Halted at:** `{{ISO_8601_TIMESTAMP}}`
- **Halted by (agent):** `{{skill-name — e.g. architect, tdd-specialist, developer}}`
- **Phase at halt:** `{{N — e.g. 4 — Implementation}}`

## Point of Failure

The specific file, command, or decision where execution stopped. Be concrete — name the file path, the test method, or the contradictory claim.

- **File / command:** `{{path or command}}`
- **Triggering signal:** `{{e.g. "third consecutive red-test run with same assertion error", "DESIGN.md and BACKLOG.md contradict on persistence layer"}}`

## The "Why"

Explain the technical conflict in 3–8 lines. The goal is that the human reads this once and knows what is broken without opening every artifact.

{{e.g. "DESIGN.md → File Paths Contract requires a `NotificationService` class under `app/Services/`, but the Testing Contract in the same DESIGN.md expects `Notification::dispatch(...)` as a model static — those cannot both be true. No path through the BACKLOG disambiguates which surface is authoritative."}}

## Retry History

Summarize the failed attempts pulled from `MISSION_STATE.md → Retry Log`. Every attempt must be a row; if no retries were made before the halt, write `no retries — halt triggered on first-contact contradiction`.

| Attempt | Timestamp | What was tried | Outcome |
|---|---|---|---|
| 1 | `{{ISO}}` | `{{short description}}` | `{{red | error | contradicted}}` |
| 2 | `{{ISO}}` | `{{short description}}` | `{{red | error | contradicted}}` |
| 3 | `{{ISO}}` | `{{short description}}` | `{{red | error | contradicted}}` |

## Proposed Human Fix

At least two distinct resolution paths. Do not rank them — the human decides.

1. **Option A — {{short name}}:** {{2–3 lines. What the human would change, in which artifact, to unblock.}}
2. **Option B — {{short name}}:** {{2–3 lines. A meaningfully different path — different artifact, different tradeoff.}}

## Closure Path

Once the human resolves the blocker:

- If the fix is an artifact revision (BACKLOG, DESIGN): edit in place, log to `MISSION_STATE.md → Revision History`, reset `Status` to the appropriate phase, and resume.
- If the mission is being abandoned: run `./.agent/scripts/archive-mission.sh {{MISSION_ID}} "halted: <reason>"`.
- This report stays in the mission folder either way — it is the audit trail.
