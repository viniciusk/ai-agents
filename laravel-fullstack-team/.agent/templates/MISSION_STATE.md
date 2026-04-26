# Mission State — {{MISSION_ID}}

> The Blackboard. Every agent reads this before starting and updates it before ending its turn. Per `mission-control.md`, this file is the single source of truth for a mission.

## Mission Metadata

- **Mission ID:** `{{MISSION_ID}}`
- **Created:** `{{ISO_8601_TIMESTAMP}}`
- **Feature (short name):** `{{feature-slug}}`
- **Status:** `initialized` <!-- initialized | refining | designing | testing-red | implementing | verifying | awaiting-approval | closed | abandoned -->
- **Current Phase:** `0 — Initialization`

## Artifact Locations

| Artifact        | Path                   | Status      |
| --------------- | ---------------------- | ----------- |
| Backlog         | `./BACKLOG.md`         | not-started |
| Design          | `./DESIGN.md`          | not-started |
| Red Test Report | `./TEST_REPORT_RED.md` | not-started |
| Final Review    | `./FINAL_REVIEW.md`    | not-started |

## Phase Log

Append a new entry every time a phase starts, ends, is revised, or is rejected. Do not delete entries.

### Phase 0 — Initialization

- **Started:** `{{ISO_8601_TIMESTAMP}}`
- **Ended:** `{{ISO_8601_TIMESTAMP}}`
- **Outcome:** Mission folder created; state initialized.

<!-- Template for subsequent entries:

### Phase N — {Phase Name} (revision M)
- **Agent:** `{skill-name}`
- **Model:** `{tier} → {model-id resolved from .agent/config.json → tier_mapping}`
- **Started:** `{{ISO_8601_TIMESTAMP}}`
- **Ended:** `{{ISO_8601_TIMESTAMP}}`
- **Input:** `{path(s) to artifacts read}`
- **Output:** `{path(s) to artifacts produced or updated}`
- **Outcome:** `completed | rejected | superseded`
- **Notes:** `{1–3 lines}`

-->

## Retry Log

Every repeated attempt at the same action (failing test re-run, rejected design revision, developer fix-and-retest loop) gets a row. Do not delete rows.

| Attempt | Phase              | Timestamp                 | What was tried                           | Outcome                          |
| ------- | ------------------ | ------------------------- | ---------------------------------------- | -------------------------------- | --- | --- | --- | --- |
| <!-- 1  | 4 — Implementation | 2026-04-21T10:22:00+00:00 | Adjusted NotificationService return type | red (same assertion failure) --> |     |     |     |     |

## Deviations from Plan

Record any time execution deviates from `DESIGN.md` or `BACKLOG.md`. This is the drift log the architect reviews in Phase 5.

<!-- Example:
- Chose a plain Eloquent scope over an Action class for `listArchived` because the query is stateless and has no side effects. Approved by architect on {{timestamp}}.
-->

## Open Questions / Pending User Input

Use this section while waiting on a gate. Clear once the gate resolves.

<!-- Example:
- [ ] Confirm whether notifications should broadcast on the `private-user.{id}` or `presence-user.{id}` channel.
-->

## Revision History

Any time the user rejects a gate, log the rejection and the revision plan here.

<!-- Example:
- 2026-04-21 — Phase 2 design rejected. User requested removal of the event-sourcing layer. Architect to revise DESIGN.md in place (rev 2).
-->
