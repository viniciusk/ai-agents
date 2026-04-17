---
description: Targeted fix — re-run only the affected phases on an existing mission. Choose where to re-enter (developer, qa-planning, or qa-verification). Reuses the existing ADR, tests, and task breakdown from the original mission folder under .agent-missions/mission-{timestamp}/.
---

# Fix Workflow (`/fix`)

Re-run only the phases needed to address a bug or a missing test, without restarting the full pipeline.

**Expected invocation (from the chat):**

> Execute the `/fix` workflow defined in `.agent/workflows/fix.md` on mission `mission-{timestamp}`. Fix description: "{short specific description}". From phase: {developer | qa-planning | qa-verification}.

You are the **orchestrator**. Resolve the target mission, then re-enter the pipeline at the chosen phase.

---

## Parameters

Prompt the user for any that are missing:

- **`MISSION_ID`** — which mission to fix. Default: contents of `.agent-missions/current-mission`. If that file is missing, list the folders under `.agent-missions/` and ask the user to pick one.
- **`fix_description`** — what to fix (short, specific — this goes directly into the sub-agent's prompt).
- **`from_phase`** — one of:
  - `developer` *(default)* — re-run Dev → QA verify (implementation bug)
  - `qa-planning` — re-run QA planning → Dev → QA verify (tests need rewriting)
  - `qa-verification` — re-run QA verify only (Dev fixed it manually, just need sign-off)

---

## Step 0 — Resolve Mission and Sanity-Check

Confirm the mission folder exists and contains the expected prior artifacts:

// turbo
```bash
MISSION_ID="${MISSION_ID:-$(cat .agent-missions/current-mission 2>/dev/null)}"
MISSION_DIR=".agent-missions/${MISSION_ID}"

if [ ! -d "${MISSION_DIR}" ]; then
  echo "ERROR: mission folder not found: ${MISSION_DIR}"
  echo "Available missions:"
  ls -1 .agent-missions/ 2>/dev/null | grep -v '^current-mission$'
  exit 1
fi

echo "Fixing mission: ${MISSION_ID}"
echo "From phase:   ${from_phase:-developer}"
echo "Fix:          ${fix_description}"

# Update the current-mission pointer so downstream steps stay consistent.
echo "${MISSION_ID}" > .agent-missions/current-mission
```

Stop and surface to the user if the mission folder is missing, or if the required prior artifacts (`artifacts/architect/task-breakdown.md`, `tests/run_tests.sh`) are absent.

---

## Step 1 — QA Re-Plan *(only if `from_phase == "qa-planning"`)*

- **Agent / skill:** `qa`
- **Model:** `claude-sonnet-4-6`

Skip this step unless `from_phase == "qa-planning"`.

Task:

> You are in **PLANNING MODE** — rewriting or adding tests for a fix.
>
> **FIX REQUEST:** `{fix_description}`
>
> Read the existing `.agent-missions/${MISSION_ID}/artifacts/po/acceptance-criteria.md`, `.agent-missions/${MISSION_ID}/artifacts/architect/api-contracts.yaml`, and `.agent-missions/${MISSION_ID}/artifacts/architect/task-breakdown.md`. Rewrite or add failing tests as needed under `.agent-missions/${MISSION_ID}/tests/`. Update `.agent-missions/${MISSION_ID}/tests/DEV_HANDOFF.md` and `.agent-missions/${MISSION_ID}/artifacts/qa/test-plan.md`. Save the handoff to `.agent-missions/${MISSION_ID}/handoffs/qa-to-dev.md`.

**On blocked:** surface to user.

---

## Step 2 — Developer Implements the Fix *(runs if `from_phase` is `developer` or `qa-planning`)*

- **Agent / skill:** `developer`
- **Model:** `claude-sonnet-4-6`

Skip this step if `from_phase == "qa-verification"`.

Task:

> You are in **IMPLEMENTATION MODE**.
>
> **FIX REQUEST (address this specifically):** `{fix_description}`
>
> Read `.agent-missions/${MISSION_ID}/tests/DEV_HANDOFF.md`, `.agent-missions/${MISSION_ID}/artifacts/architect/task-breakdown.md`, and `.agent-missions/${MISSION_ID}/artifacts/architect/architecture-decision-record.md`. Run `./.agent-missions/${MISSION_ID}/tests/run_tests.sh` to see the current state. Fix the issue described above until every test passes. **Do NOT modify any test files.** Write `.agent-missions/${MISSION_ID}/artifacts/dev/implementation-notes.md` and save the handoff to `.agent-missions/${MISSION_ID}/handoffs/dev-to-qa.md`.

**On blocked:** surface to user.

---

## Step 3 — QA Verifies the Fix *(always runs)*

- **Agent / skill:** `qa`
- **Model:** `gemini-3-flash`

This is the final gate regardless of `from_phase`.

Task:

> You are in **VERIFICATION MODE**. Read `.agent-missions/${MISSION_ID}/handoffs/dev-to-qa.md` and the implementation notes. Run `./.agent-missions/${MISSION_ID}/tests/run_tests.sh` and capture the full output.
>
> **If ALL tests pass:** save `.agent-missions/${MISSION_ID}/artifacts/qa/test-results.md`, `.agent-missions/${MISSION_ID}/artifacts/qa/sign-off.md`, and `.agent-missions/${MISSION_ID}/handoffs/qa-signoff.md` with `STATUS: COMPLETE`.
>
> **If any tests fail:** save `.agent-missions/${MISSION_ID}/artifacts/qa/test-results.md`, `.agent-missions/${MISSION_ID}/artifacts/qa/bug-report.md`, and `.agent-missions/${MISSION_ID}/handoffs/qa-to-dev-cycle.md` with `STATUS: BLOCKED`.

**On blocked:** route back to Step 2 with the new bug report, up to `max_qa_dev_cycles: 5` total Dev↔QA loops.

**On complete:** mission fix complete. Announce the sign-off artifact and `${MISSION_DIR}/`.
