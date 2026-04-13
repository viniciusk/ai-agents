# Concept 02 — Collaboration Flow & Handoff Protocol

The most important engineering decision in a multi-agent system is not which model to use — it's **how agents communicate**. Poor handoffs create ambiguity. Ambiguity creates hallucination.

---

## The Handoff Protocol

Every agent-to-agent handoff follows the same structure:

```
HANDOFF ARTIFACT
─────────────────
FROM:    [Agent name]
TO:      [Next agent name]
STATUS:  [READY / BLOCKED / ESCALATION]
SESSION: [Unique session ID for this mission]

CONTEXT:
  [Summary of what was accomplished in this phase]

ARTIFACTS PRODUCED:
  - [filename]: [one-line description]
  - [filename]: [one-line description]

OPEN QUESTIONS (if STATUS = BLOCKED):
  - [Question 1 that must be answered before proceeding]
  - [Question 2]

NEXT AGENT INSTRUCTIONS:
  [Specific instruction for the next agent — what to read, what to produce]
```

This format means the Orchestrator can parse handoffs programmatically and decide what to do next without any ambiguity.

---

## The Full Flow in Detail

### Step 0: Mission Initialization

The Orchestrator receives the business goal and creates a **mission folder**:

```
sessions/
  mission-{timestamp}-{short-id}/
    mission.md          ← The original business goal + metadata
    handoffs/           ← All handoff artifacts
    artifacts/          ← All agent outputs
      po/
      architect/
      qa/
      dev/
```

Everything produced during the mission lives here. This makes the process fully auditable.

---

### Step 1: Product Owner Phase

**Input:** `mission.md` (business goal)

**The PO agent:**
1. Reads the mission
2. Identifies ambiguities — writes them as questions to the user
3. (Optional) Waits for user to answer via `AskUserQuestion` tool
4. Writes user stories + acceptance criteria
5. Produces handoff artifact with STATUS = READY

**Output artifacts:**
```
artifacts/po/
  user-stories.md
  acceptance-criteria.md
  out-of-scope.md
handoffs/
  po-to-architect.md
```

**Escalation condition:** If the business goal is fundamentally contradictory or impossible to scope, the PO produces STATUS = ESCALATION and stops. The Orchestrator surfaces this to the user.

---

### Step 2: Architect Phase

**Input:** `po-to-architect.md` + all PO artifacts

**The Architect agent:**
1. Reads all PO artifacts
2. Assesses technical feasibility
3. If a user story is ambiguous or technically unsound → produces STATUS = BLOCKED with specific questions, sends back to PO (Orchestrator re-runs PO phase with the questions as additional context)
4. If all stories are sound → designs the architecture
5. Breaks work into atomic tasks

**Output artifacts:**
```
artifacts/architect/
  architecture-decision-record.md
  task-breakdown.md
  api-contracts.md
  non-functional-requirements.md
handoffs/
  architect-to-qa.md
  architect-to-dev.md     ← sent simultaneously to both
```

---

### Step 3: Parallel Phase — QA + Dev Setup

This is where parallelism begins. Both agents start simultaneously:

**QA Agent receives:** `architect-to-qa.md` + all previous artifacts

QA writes the test plan and failing tests. This can take a while.

**Dev Agent receives:** `architect-to-dev.md` + all previous artifacts

Dev reads the architecture and sets up the project structure — file layout, dependencies, configuration — but writes NO implementation code yet.

**Why not have Dev wait for QA?** The setup work is independent. Dev can prepare the environment while QA writes tests. When QA is done, Dev immediately has a runnable test suite to work against.

---

### Step 4: Implementation Phase

**Input:** QA's failing tests + Dev's project structure + all previous artifacts

**The Dev agent:**
1. Reads the failing test files
2. Implements each task from the Architect's breakdown in order
3. Runs tests after each task to verify progress
4. Continues until all tests pass (or produces a BLOCKED artifact if stuck)

**Output artifacts:**
```
artifacts/dev/
  src/                     ← All implementation files
  implementation-notes.md
handoffs/
  dev-to-qa.md
```

---

### Step 5: Verification Phase

**Input:** `dev-to-qa.md` + all implementation files + original test suite

**The QA agent (verification mode):**
1. Runs the full test suite against the implementation
2. Produces test results report
3. If all tests pass → sign-off artifact
4. If tests fail → bug report with enough context for Dev to fix

**If bugs found:** Orchestrator re-runs Dev phase with the bug report as additional context. This loop repeats until sign-off.

---

## Handling Failures and Loops

The Orchestrator implements a **maximum iteration count** per phase to prevent infinite loops:

```python
MAX_PO_ARCHITECT_CYCLES = 3   # How many times Architect can push back to PO
MAX_QA_DEV_CYCLES = 5         # How many times QA can send bugs back to Dev
```

If a maximum is reached, the Orchestrator escalates to the user with a summary of what's blocking progress.

---

## Communication Rules

Agents communicate **only through artifacts** — never by calling each other directly. This is critical for:

**Auditability** — You can read every decision made during the mission
**Debuggability** — When something goes wrong, you can find exactly which agent produced the problematic output
**Replaceability** — You can swap out any agent (different model, different persona) without changing the others, as long as the artifact format stays the same

Think of artifacts the same way you'd think of git commits: they're the immutable record of what happened and why.
