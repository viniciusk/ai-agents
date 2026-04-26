# Mission State — {{MISSION_ID}}

> The Blackboard. Every agent reads this before starting and updates it before ending its turn.

## Mission Metadata

- **Mission ID:** `{{MISSION_ID}}`
- **Created:** `{{ISO_8601_TIMESTAMP}}`
- **Target Project (short name):** `{{feature-slug}}`
- **Status:** `initialized` <!-- initialized | discovery | auditing | planning | awaiting-approval | closed | abandoned -->
- **Current Phase:** `0 — Initialization`

## Artifact Locations

| Artifact                   | Path                         | Status      |
| -------------------------- | ---------------------------- | ----------- |
| Glossary                   | `./02_GLOSSARY.md`              | not-started |
| Security Review            | `./03_SECURITY_REVIEW.md`       | not-started |
| Performance Review         | `./04_PERFORMANCE_REVIEW.md`    | not-started |
| Architecture Review        | `./05_ARCHITECTURE_REVIEW.md`   | not-started |
| Tech Debt Assessment       | `./06_TECH_DEBT_ASSESSMENT.md`  | not-started |
| Improvement Plan           | `./07_IMPROVEMENT_PLAN.md`      | not-started |
| Final Review               | `./08_FINAL_REVIEW.md`          | not-started |

## Phase Log

Append a new entry every time a phase starts, ends, is revised, or is rejected. Do not delete entries.

### Phase 0 — Initialization

- **Started:** `{{ISO_8601_TIMESTAMP}}`
- **Ended:** `{{ISO_8601_TIMESTAMP}}`
- **Outcome:** Mission folder created; state initialized.

<!-- Template for subsequent entries:

### Phase N — {Phase Name} (revision M)
- **Agent:** `{skill-name}`
- **Started:** `{{ISO_8601_TIMESTAMP}}`
- **Ended:** `{{ISO_8601_TIMESTAMP}}`
- **Output:** `{path(s) to artifacts produced or updated}`
- **Outcome:** `completed | rejected | superseded`
- **Notes:** `{1–3 lines}`

-->

## Open Questions / Pending User Input

Use this section while waiting on a gate. Clear once the gate resolves.

## Revision History

Any time the user rejects a gate, log the rejection and the revision plan here.
