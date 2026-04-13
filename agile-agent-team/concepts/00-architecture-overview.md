# Concept 00 — Architecture Overview

## The Core Mental Model

Think of this system the same way you'd think of a real agile team. You — the business stakeholder — walk in with a goal. The team takes that goal and, through a structured process of discovery, design, testing, and implementation, delivers working software.

The difference: **every "person" on this team is an AI agent**, and their collaboration happens through structured text artifacts rather than Slack messages and meetings.

---

## What is an Agent?

An agent is an AI model (like Claude or Gemini) given:

1. **A persona** — "You are a Senior Software Architect with 15 years of experience..."
2. **A set of tools** — what it can actually do (read files, run code, search the web)
3. **A task** — what it should accomplish right now
4. **Context** — the artifacts produced by previous agents

The agent then works **autonomously** — reasoning, using tools, producing output — until it completes the task.

---

## What is a Skill?

A Skill is a **Markdown file** (`SKILL.md`) that defines an agent's specialization. It contains:

- The agent's role and persona
- The rules it must follow
- The exact format of its output (so other agents can parse it)
- Examples of good and bad behavior

Skills are how you give an agent its "job description." Both Claude and Antigravity use this pattern.

---

## What is an Orchestrator?

The orchestrator is the "manager" — it doesn't do the technical work itself, but it:

1. Receives the business goal from you
2. Activates the right agents in the right order
3. Passes each agent's output as context to the next agent
4. Handles parallel work (e.g., QA and Dev working simultaneously)
5. Collects all artifacts into a final deliverable

In the Claude Agent SDK, the orchestrator is a Python or TypeScript program. In Antigravity, it's the Manager View (GUI).

---

## The Collaboration Flow (High Level)

```
INPUT:  Business Goal
        "Add a feature to let users reset their password via email"

PHASE 1: DISCOVERY (Product Owner)
  → Produces: User Stories, Acceptance Criteria, Business Rules

PHASE 2: DESIGN (Software Architect, reviews PO output)
  → Produces: Architecture Decision Record (ADR), Task List, API contracts

PHASE 3: TDD (QA Engineer, reviews Architect output)  [PARALLEL with Dev setup]
  → Produces: Failing tests (unit + integration + e2e)

PHASE 4: IMPLEMENTATION (Full Stack Dev, reviews ADR + failing tests)
  → Produces: Working code that makes the tests pass

PHASE 5: VERIFICATION (QA Engineer, reviews Dev output)
  → Produces: Test run results, bug reports if any, sign-off

OUTPUT: Passing tests + Implemented feature + All artifacts
```

---

## Why This Order Matters

**PO before Architect** — The Architect needs to know *what* to build before deciding *how* to build it. Skipping this creates "clever solutions to the wrong problem."

**Architect before Dev** — Without a design, developers make local decisions that don't compose well at scale. The ADR gives everyone a shared blueprint.

**QA before Dev (TDD)** — Writing tests before code forces clarity on what "done" means. It prevents the common pattern where tests are retrofitted to match whatever the code happens to do.

**QA verification at the end** — Closes the loop. The same agent who defined "done" verifies it.

---

## The Artifact Chain

Each agent produces a **structured artifact** that the next agent consumes. Think of artifacts as the "handoff documents" in the workflow.

```
Goal (string)
    ↓
[Product Owner]
    ↓ produces →  user-stories.md
                  acceptance-criteria.md

[Software Architect] ← reads user-stories.md + acceptance-criteria.md
    ↓ produces →  architecture-decision-record.md
                  task-breakdown.md
                  api-contracts.md

[QA Engineer] ← reads all above
    ↓ produces →  test-plan.md
                  /tests/ (actual failing test files)

[Full Stack Developer] ← reads all above + failing tests
    ↓ produces →  /src/ (implementation files)
                  implementation-notes.md

[QA Engineer] ← runs tests against implementation
    ↓ produces →  test-results.md
                  sign-off.md  OR  bug-report.md
```

---

## Parallelism

Not all phases need to be sequential. In a mature setup:

- While QA is writing tests, the Dev agent can be reading the ADR and setting up the project structure
- Multiple Dev agents can work on separate tasks from the task breakdown simultaneously
- The Architect can review PO output and start the ADR while the PO refines edge cases

Both Claude Agent SDK and Antigravity support parallel agent execution. The key constraint: **an agent cannot consume an artifact that hasn't been produced yet**.

---

## Key Design Decisions in This Skeleton

1. **Structured artifact formats** — Every artifact uses a consistent schema (defined in each SKILL.md) so agents can reliably parse each other's output.

2. **Explicit handoff instructions** — Each agent's skill tells it exactly what to look for in previous artifacts and what to produce.

3. **No implicit assumptions** — Agents should ask for clarification rather than guess. The PO agent, in particular, is instructed to surface ambiguity rather than resolve it silently.

4. **Fail-fast on design problems** — The Architect is explicitly instructed to reject technically unsound user stories and send them back to the PO with feedback.

5. **TDD as a constraint** — The Dev agent is instructed not to write a single line of implementation code before tests exist. This is enforced at the skill level.
