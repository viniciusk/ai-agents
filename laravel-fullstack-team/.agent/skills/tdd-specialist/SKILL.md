---
name: tdd-specialist
description: Writes failing PHPUnit and Inertia tests. Use this after a design is finalized but before any implementation code is written.
---

# TDD Specialist Skill

1. **Read Design:** Parse `DESIGN.md → Testing Contract` and `DESIGN.md → File Paths Contract` from the active mission folder. Every row in the Testing Contract must become a real test method; every test file must live under one of the paths declared in the File Paths Contract.
2. **Phase 3 (Red):**
   - Copy `.agent/templates/TEST_REPORT_RED.md` into the mission folder.
   - Write the tests. Use `Inertia::assertRender` and strict TypeScript prop validation.
   - Run `./.agent/scripts/run-tests.sh red {{MISSION_ID}}` — the script exits 0 only when the new tests fail as expected. Paste its output into the template's "Full Test Output" section.
3. **Phase 5 (Green):**
   - Open `FINAL_REVIEW.md` (instantiated from `.agent/templates/FINAL_REVIEW.md`) and fill **Part A — Green Verification**.
   - Run `./.agent/scripts/run-tests.sh green {{MISSION_ID}}`. Paste output; fill the Coverage vs. DESIGN Contract table.
4. **Update State:** Append a Phase 3 (or Phase 5) entry to `MISSION_STATE.md → Phase Log`.
5. **Record Telemetry:** Before handing over, run `python3 ./.agent/scripts/quotestimator.py --agent CURRENT_AGENT --model CURRENT_AGENT_MODEL --turns NUMBER_OF_TURNS_TAKEN --read EACH_FILE_READ --modified EACH_FILE_MODIFIED`.

## Goal

- **Phase 3:** establish a "Red" testing state whose shape matches DESIGN.md exactly, so the developer has a precise target.
- **Phase 5:** confirm "Green" and hand a coverage verdict to the architect for the drift review.

## Instructions

### Naming & File Placement

- **Feature tests:** `tests/Feature/{FeatureName}Test.php`. One class per user-facing route group.
- **Unit tests for Actions:** `tests/Unit/Actions/{ActionName}Test.php`. One class per Action.
- **Unit tests for domain services / value objects:** `tests/Unit/Domain/{ClassName}Test.php`.
- **Test method naming:** `test_{behavior_under_condition}` (snake_case) or `it_{behavior}` with the `#[Test]` attribute — be consistent with the existing suite; grep before deciding.

### Phase 3 — Red

1. **Read Design:** parse the Testing Contract table first; it is authoritative.
2. **Feature Tests:** create one test method per Gherkin scenario in `BACKLOG.md → Acceptance Criteria`, crossed-referenced with the DESIGN Testing Contract. Use:
   - `Inertia::assertRender()` to verify the correct Vue component.
   - `assertInertia(fn ($page) => ...)` to validate props/TypeScript data structures.
3. **Unit Tests:** for Service/Action classes, ensure 100% path coverage.
4. **Validation:** run `./.agent/scripts/run-tests.sh red {{MISSION_ID}}`. Exit 0 = red as expected. Exit 1 = unexpected pass → investigate; either the test is wrong or code already exists.
5. **Fill `TEST_REPORT_RED.md`:** every row of the Tests Created table must map back to a DESIGN section reference. If a Testing Contract row has no test, you are not done.

### Phase 5 — Green

1. Run `./.agent/scripts/run-tests.sh green {{MISSION_ID}}`. Exit 0 required.
2. Fill Part A of `FINAL_REVIEW.md`. Hand off to architect for Part B.

## Constraints

- **Strictly No Implementation:** do not create Models, Controllers, or Vue files in Phase 3.
- Only use existing interfaces/factories. If they don't exist, mock them or define the expected signature in the test.
- **Do not truncate test output** in the artifact — the full block is the audit trail.
- **Do not invent tests outside the Testing Contract.** If coverage feels thin, flag it to the architect; Phase 2 revises, then Phase 3 resumes.
