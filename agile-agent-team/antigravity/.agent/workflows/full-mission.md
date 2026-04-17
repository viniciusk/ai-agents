---
description: Full agile pipeline — PO writes stories, Architect designs, QA + Dev run in parallel, Dev implements, QA verifies. Creates a new mission folder under .agent-missions/mission-{timestamp}/ and orchestrates all six workspaces end to end.
---

# Full Mission Workflow (`/mission`)

Run the complete agile agent team pipeline end-to-end.

**Expected invocation (from the chat):**

> Execute the `/mission` workflow defined in `.agent/workflows/full-mission.md` using `@[docs/plans/{FILE_WITH_DEV_SCOPE.md}]` as the mission brief snippet. Act as the orchestrator and begin Phase 1: Product Owner.

You are the **orchestrator** for this workflow. Dispatch the sub-agents in order, wait for each handoff file, and route blocked states per the rules below.

---

## Flow

```
PO → Architect → (QA Planning + Dev Setup in parallel) → Dev → QA Verify
```

- Architect may push back to PO up to **3 times** (`max_po_architect_cycles: 3`)
- QA may loop back to Dev with bugs up to **5 times** (`max_qa_dev_cycles: 5`)

---

## Step 0 — Initialize Mission Folder

Generate a new mission id and scaffold the folder structure. **All subsequent steps read from and write to this folder.**

// turbo

```bash
MISSION_ID="mission-$(date +%Y%m%d-%H%M%S)"
MISSION_DIR=".agent-missions/${MISSION_ID}"

mkdir -p "${MISSION_DIR}/artifacts/po" \
         "${MISSION_DIR}/artifacts/architect" \
         "${MISSION_DIR}/artifacts/qa" \
         "${MISSION_DIR}/artifacts/dev" \
         "${MISSION_DIR}/handoffs" \
         "${MISSION_DIR}/tests/unit" \
         "${MISSION_DIR}/tests/integration" \
         "${MISSION_DIR}/tests/e2e" \
         "${MISSION_DIR}/src"

# Pointer to the active mission — later steps and the /fix workflow read this.
echo "${MISSION_ID}" > .agent-missions/current-mission

echo "Mission folder ready: ${MISSION_DIR}"
```

Then copy the mission brief into the mission folder:

- Read the file referenced by `@[docs/plans/{FILE_WITH_DEV_SCOPE.md}]` (or the brief the user pasted).
- Write it verbatim to `${MISSION_DIR}/mission.md`.

Confirm the folder exists and the brief is saved before continuing. If anything fails, surface to the user and stop.

---

## Step 1 — Product Owner (Phase 1)

- **Agent / skill:** `po`
- **Model:** `gemini-3.1-pro` (or `claude-sonnet-4-6`)
- **Wait for:** `${MISSION_DIR}/mission.md`

Dispatch a workspace with the `po` skill and this task:

> Read the mission brief in `.agent-missions/${MISSION_ID}/mission.md`. Follow your skill to produce user stories and acceptance criteria. Save all artifacts to `.agent-missions/${MISSION_ID}/artifacts/po/`. Save the handoff to `.agent-missions/${MISSION_ID}/handoffs/po-to-architect.md`.

**Expected outputs:**

- `${MISSION_DIR}/artifacts/po/user-stories.md`
- `${MISSION_DIR}/artifacts/po/acceptance-criteria.md`
- `${MISSION_DIR}/handoffs/po-to-architect.md` (`STATUS: READY` or `BLOCKED`)

**On blocked:** surface to the user. PO cannot proceed without clear requirements.

---

## Step 2 — Software Architect (Phase 2)

- **Agent / skill:** `architect`
- **Model:** `gemini-3.1-pro-high` (high reasoning — this phase is the most expensive mistake)
- **Wait for:** `${MISSION_DIR}/handoffs/po-to-architect.md` with `STATUS: READY`

Dispatch a workspace with the `architect` skill and this task:

> Read all PO artifacts in `.agent-missions/${MISSION_ID}/artifacts/po/` and the handoff in `.agent-missions/${MISSION_ID}/handoffs/po-to-architect.md`. Follow your skill to design the architecture. Save artifacts to `.agent-missions/${MISSION_ID}/artifacts/architect/`. Save both handoffs: `.agent-missions/${MISSION_ID}/handoffs/architect-to-qa.md` and `.agent-missions/${MISSION_ID}/handoffs/architect-to-dev.md`.

**Expected outputs:**

- `${MISSION_DIR}/artifacts/architect/architecture-decision-record.md`
- `${MISSION_DIR}/artifacts/architect/api-contracts.yaml`
- `${MISSION_DIR}/artifacts/architect/task-breakdown.md`
- `${MISSION_DIR}/handoffs/architect-to-qa.md`
- `${MISSION_DIR}/handoffs/architect-to-dev.md`

**On blocked:** route back to the PO workspace with the Architect's questions. Increment the PO↔Architect cycle counter; stop after 3 loops and surface to the user.

---

## Step 3 — QA Planning + Dev Setup (Phase 3, parallel)

Dispatch **both workspaces simultaneously** once the Architect handoffs exist. This is where Antigravity's parallel workspaces earn their keep.

### Step 3a — QA Planning

- **Agent / skill:** `qa`
- **Model:** `claude-sonnet-4-6`
- **Wait for:** `${MISSION_DIR}/handoffs/architect-to-qa.md`

Task:

> You are in **PLANNING MODE**. Read `.agent-missions/${MISSION_ID}/artifacts/po/acceptance-criteria.md` and `.agent-missions/${MISSION_ID}/artifacts/architect/api-contracts.yaml`. Write failing tests for every acceptance criterion. Save tests under `.agent-missions/${MISSION_ID}/tests/` (unit/, integration/, e2e/). Create `.agent-missions/${MISSION_ID}/tests/run_tests.sh` and `.agent-missions/${MISSION_ID}/tests/DEV_HANDOFF.md`. Save the test plan to `.agent-missions/${MISSION_ID}/artifacts/qa/test-plan.md`. Save the handoff to `.agent-missions/${MISSION_ID}/handoffs/qa-to-dev.md`.

**Expected outputs:**

- `${MISSION_DIR}/artifacts/qa/test-plan.md`
- `${MISSION_DIR}/tests/run_tests.sh`
- `${MISSION_DIR}/tests/DEV_HANDOFF.md`
- `${MISSION_DIR}/handoffs/qa-to-dev.md`

**On blocked:** surface to user.

### Step 3b — Dev Setup

- **Agent / skill:** `developer`
- **Model:** `gemini-3-flash`
- **Wait for:** `${MISSION_DIR}/handoffs/architect-to-dev.md`

Task:

> You are in **SETUP MODE**. Read `.agent-missions/${MISSION_ID}/artifacts/architect/architecture-decision-record.md` and `.agent-missions/${MISSION_ID}/artifacts/architect/task-breakdown.md`. Create the project directory structure and placeholder files under `.agent-missions/${MISSION_ID}/src/`. Install dependencies. **Do NOT write implementation code.** Save handoff to `.agent-missions/${MISSION_ID}/handoffs/dev-setup-complete.md`.

**Expected outputs:**

- `${MISSION_DIR}/src/` scaffolded
- `${MISSION_DIR}/handoffs/dev-setup-complete.md`

**On blocked:** surface to user.

Wait until **both** Step 3a and Step 3b have produced their handoffs before continuing.

---

## Step 4 — Developer Implementation (Phase 4)

- **Agent / skill:** `developer`
- **Model:** `claude-sonnet-4-6`
- **Wait for:** `${MISSION_DIR}/handoffs/qa-to-dev.md` AND `${MISSION_DIR}/handoffs/dev-setup-complete.md`

Task:

> You are in **IMPLEMENTATION MODE**. Read `.agent-missions/${MISSION_ID}/tests/DEV_HANDOFF.md` first, then the ADR and the task breakdown in `.agent-missions/${MISSION_ID}/artifacts/architect/`. Run `./.agent-missions/${MISSION_ID}/tests/run_tests.sh` and confirm all tests currently fail. Implement the task list in order. Run tests after each task. When all tests pass, write `.agent-missions/${MISSION_ID}/artifacts/dev/implementation-notes.md` and save the handoff to `.agent-missions/${MISSION_ID}/handoffs/dev-to-qa.md`. **Do NOT modify any test files.**

**Expected outputs:**

- `${MISSION_DIR}/src/` populated with implementation
- `${MISSION_DIR}/artifacts/dev/implementation-notes.md`
- `${MISSION_DIR}/handoffs/dev-to-qa.md`

**On blocked:** surface to user.

---

## Step 5 — QA Verification (Phase 5)

- **Agent / skill:** `qa`
- **Model:** `gemini-3-flash`
- **Wait for:** `${MISSION_DIR}/handoffs/dev-to-qa.md`

Task:

> You are in **VERIFICATION MODE**. Read `.agent-missions/${MISSION_ID}/handoffs/dev-to-qa.md` and the implementation notes. Run `./.agent-missions/${MISSION_ID}/tests/run_tests.sh` and capture the full output.
>
> **If ALL tests pass:** save `.agent-missions/${MISSION_ID}/artifacts/qa/test-results.md`, `.agent-missions/${MISSION_ID}/artifacts/qa/sign-off.md`, and `.agent-missions/${MISSION_ID}/handoffs/qa-signoff.md` with `STATUS: COMPLETE`.
>
> **If any tests fail:** save `.agent-missions/${MISSION_ID}/artifacts/qa/test-results.md`, `.agent-missions/${MISSION_ID}/artifacts/qa/bug-report.md` (expected vs actual, which test, which AC), and `.agent-missions/${MISSION_ID}/handoffs/qa-to-dev-cycle.md` with `STATUS: BLOCKED`.

**On blocked (bugs found):** route back to Step 4 (Developer) with the bug report. Increment the QA↔Dev cycle counter; stop after 5 loops and surface to the user.

**On complete:** mission complete. Announce the sign-off artifact and the location of `${MISSION_DIR}/`.

---

## Orchestrator Notes

- Always resolve `${MISSION_ID}` from `.agent-missions/current-mission` if the variable is not already bound in the shell session.
- Every dispatched sub-agent receives the `MISSION_ID` explicitly in its task prompt so it never has to guess.
- Do not merge modes in the same workspace invocation — QA Planning and QA Verification are distinct, as are Dev Setup and Dev Implementation.
