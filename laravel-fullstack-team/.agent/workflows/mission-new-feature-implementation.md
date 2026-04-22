---
name: mission new feature implementation
description: A high-integrity TDD workflow for Laravel 12 / Inertia v3 features. Step-by-step implementation with two user-approval gates and explicit rollback paths.
trigger: /mission-new-feature-implementation
---

# Mission: Feature Implementation

## Artifacts & Their Templates

Every phase below produces an artifact in the mission folder (`./.agent-missions/mission-{{ID}}/`). Agents MUST instantiate these from the templates — they are not free-form documents.

| Artifact             | Template                              | Producer                                   | Phase  |
| -------------------- | ------------------------------------- | ------------------------------------------ | ------ |
| `MISSION_STATE.md`   | `.agent/templates/MISSION_STATE.md`   | System (Phase 0) + every agent on handover | 0, all |
| `BACKLOG.md`         | `.agent/templates/BACKLOG.md`         | `scope-refiner`                            | 1      |
| `DESIGN.md`          | `.agent/templates/DESIGN.md`          | `architect`                                | 2      |
| `TEST_REPORT_RED.md` | `.agent/templates/TEST_REPORT_RED.md` | `tdd-specialist`                           | 3      |
| `FINAL_REVIEW.md`    | `.agent/templates/FINAL_REVIEW.md`    | `tdd-specialist` + `architect`             | 5      |
| `HALT_REPORT.md`     | `.agent/templates/HALT_REPORT.md`     | Any agent via `halt-mission` skill         | any    |

## Phase 0: Initialization

- **Agent:** System
- **Action:** Run `./.agent/scripts/new-mission.sh {{feature-slug}}`. The script creates `./.agent-missions/mission-{{YYYYMMDD-hhmmss}}/`, instantiates `MISSION_STATE.md` from the template, and returns the mission ID on stdout.
- **Action:** Update `.agent/state/context.json` so `active_feature` is the new mission ID and `last_updated` is now. Validate with `./.agent/scripts/validate-state.sh`.
- **Output:** "Mission started. ID: mission-{{YYYYMMDD-hhmmss}}"

## Phase 1: Requirements Refinement

- **Agent:** `scope-refiner`
- **Context:** Read the user prompt + the repo-root `README.md`.
- **Action:** Copy `.agent/templates/BACKLOG.md` into the mission folder. Fill every `{{placeholder}}`. Conduct the 3–5-question interactive probe and record answers in the Clarifying Questions table.
- **Artifact:** `./.agent-missions/mission-{{ID}}/BACKLOG.md`.
- **Handover:** Append a Phase 1 entry to `MISSION_STATE.md → Phase Log` and set **Status** to `awaiting-approval`.
- **Gate:** **WAIT** for user approval. See _Rejection Handling_ below for loop-back behavior.

## Phase 2: Architectural Design

- **Agent:** `architect`
- **Context:** Read `./.agent-missions/mission-{{ID}}/BACKLOG.md`.
- **Action:** Copy `.agent/templates/DESIGN.md` into the mission folder. Fill every section, in particular the **File Paths Contract** and the **Testing Contract** — these are binding on Phases 3 and 4.
- **Rule:** Must include Inertia v3 prop definitions, `useForm` shape, and Tailwind v4 CSS variable strategy. Reject Repository Pattern unless justified in the **Explicit Non-Decisions** section.
- **Handover:** Append a Phase 2 entry to `MISSION_STATE.md → Phase Log`.
- **Gate:** **WAIT** for user approval.

## Phase 3: TDD (Test Generation)

- **Agent:** `tdd-specialist`
- **Context:** Read `DESIGN.md → Testing Contract` and `DESIGN.md → File Paths Contract`.
- **Action:** Generate failing PHPUnit/Inertia tests. Every row in the Testing Contract must become a real test method.
- **Verification:** Run `./.agent/scripts/run-tests.sh red {{MISSION_ID}}`. The script exits 0 only if tests fail as expected.
- **Artifact:** Copy `.agent/templates/TEST_REPORT_RED.md` into the mission folder and fill it with the run output and the coverage-vs-contract table.
- **Handover:** Append a Phase 3 entry to `MISSION_STATE.md → Phase Log`.

## Phase 4: Implementation

- **Agent:** `developer`
- **Context:** Read `DESIGN.md` (binding) + `BACKLOG.md` (intent) + `TEST_REPORT_RED.md` (test list).
- **Action:** Implement backend + frontend. Create **only** the files listed in `DESIGN.md → File Paths Contract`. If a new file is truly needed, stop and flag a drift event (see _Rejection Handling_).
- **Constraint:** Update `MISSION_STATE.md → Artifact Locations` and `Phase Log` as files are created.
- **Done criterion:** `./.agent/scripts/run-tests.sh green {{MISSION_ID}}` exits 0.

## Phase 5: Verification & Architectural Review

- **Agent:** `tdd-specialist` → run `./.agent/scripts/run-tests.sh green {{MISSION_ID}}`. Fill **Part A — Green Verification** of `FINAL_REVIEW.md` (from template).
- **Agent:** `architect` → compare implementation against `DESIGN.md`. Fill **Part B — Architectural Drift Review**. Pick one verdict checkbox.
- **Artifact:** `./.agent-missions/mission-{{ID}}/FINAL_REVIEW.md`.
- **Gate:** **WAIT** for user approval.

## Phase 6: Mission Closure

- **Agent:** System
- **Action:** Summarize changes to the user (3 bullets, from `FINAL_REVIEW.md → Hand-off to User`).
- **Action:** Run `./.agent/scripts/archive-mission.sh {{MISSION_ID}} "closed-approved"`.
- **Action:** Reset `.agent/state/context.json`: `active_feature` → `"None"`; update `last_updated`; append any cross-cutting decisions to `architectural_decisions`.

---

## Rejection Handling (applies to Gates 1, 2, 5)

User approval gates can result in rejection. Agents MUST follow these rules — improvisation is a drift event.

1. **Edit in place, don't fork.** On rejection, the same artifact file is revised. Do not create `BACKLOG_v2.md`. Do not start a new mission.
2. **Log every revision.** Append an entry to `MISSION_STATE.md → Revision History` stating: which gate was rejected, the user's reason, and which phase will re-run.
3. **Loop-back targets by gate:**
   - **Gate 1 rejected (BACKLOG):** `scope-refiner` re-runs Phase 1. New clarifying questions go into the same table (append rows, don't delete).
   - **Gate 2 rejected (DESIGN):** decide whether the issue is scope or design.
     - If scope — loop back to Phase 1 (scope-refiner revises BACKLOG).
     - If design — `architect` revises DESIGN.md in place. Phases 3 and 4 do not start until approval.
   - **Gate 5 rejected (FINAL_REVIEW):** route by the verdict checkbox set in Part B — back to Phase 2, 3, or 4. Tests already written in Phase 3 stay; the tdd-specialist only adds or adjusts tests to cover new design changes.
4. **Drift events mid-phase** (e.g. Phase 4 developer needs a file not in the contract): the developer pauses, logs the drift to `MISSION_STATE.md → Deviations from Plan`, and loops back to Phase 2. The architect decides: amend DESIGN.md (approved drift) or instruct the developer to stay within the contract.
5. **Agent-initiated halt.** If an agent hits the triggers defined in `.agent/skills/halt-mission/SKILL.md → When to Invoke` (retry budget exhausted, irreconcilable artifact contradiction, or progress-free loop), it stops and runs the `halt-mission` skill. This produces `HALT_REPORT.md`, sets `MISSION_STATE.md → Status` to `halted`, and hands control to the human. The human either revises the offending artifact in place and resumes, or abandons per rule 6.
6. **Abandonment.** If the user abandons the mission rather than approving or revising, run `./.agent/scripts/archive-mission.sh {{MISSION_ID}} "abandoned: <reason>"` (or `"halted: <reason>"` if closing a halted mission). Do not delete the folder — the archive is the audit trail.

## Mission ID Format

- Format: `mission-YYYYMMDD-HHMMSS` (local time is fine as long as it matches `last_updated` in `context.json`).
- Generated by `./.agent/scripts/new-mission.sh` — do not hand-roll.
