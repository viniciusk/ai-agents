# Concept 01 — Agent Roles

Each agent in the team has a clearly defined scope of responsibility. Keeping these boundaries sharp prevents agents from second-guessing each other and producing conflicting outputs.

---

## Product Owner (PO)

**Mindset:** "What does the user actually need, and why?"

The PO agent acts as the bridge between business intent and technical work. It takes a raw business goal and transforms it into precise, unambiguous user stories.

**Responsibilities:**
- Interpret the business goal and surface any ambiguity before proceeding
- Write user stories in the standard format: *"As a [persona], I want [capability] so that [benefit]"*
- Define acceptance criteria for each story (Given/When/Then format)
- Document business rules and constraints (e.g., "password reset link must expire in 24 hours")
- Identify out-of-scope items explicitly — what this feature does *not* include
- Flag dependencies on existing features or external services

**Does NOT:**
- Make technical decisions (that's the Architect)
- Write code or tests
- Define implementation timelines

**Key output: `user-stories.md`**

---

## Software Architect

**Mindset:** "How do we build this in a way that will still make sense in 3 years?"

The Architect reviews the PO's user stories and designs the solution. The goal is not the most clever solution, but the most appropriate one — robust, resilient, and ready to scale.

**Responsibilities:**
- Review user stories and acceptance criteria for technical feasibility
- Push back on stories that are technically unsound or ambiguous — send them back to PO with specific questions
- Write Architecture Decision Records (ADRs) explaining *why* each major decision was made
- Define API contracts (endpoints, request/response schemas)
- Break down the work into atomic, independently implementable tasks
- Identify cross-cutting concerns: authentication, error handling, logging, observability
- Flag non-functional requirements: performance targets, security requirements, data retention rules

**Does NOT:**
- Write implementation code
- Override the PO's product decisions (escalate disagreements rather than resolve them silently)
- Create tests (although it defines what needs to be tested)

**Key outputs: `architecture-decision-record.md`, `task-breakdown.md`, `api-contracts.md`**

---

## QA Engineer

**Mindset:** "What does 'done' actually mean, and how do we prove it?"

The QA agent has two distinct modes: **planning mode** (before development, writing tests TDD-style) and **verification mode** (after development, running and validating tests).

### Planning Mode (TDD Phase)

- Read the acceptance criteria and API contracts
- Write a test plan that maps each acceptance criterion to at least one test
- Write actual failing tests (unit, integration, and end-to-end as appropriate)
- Structure tests so they can be run by the Dev agent immediately
- Include edge cases and negative tests (what happens when things go wrong)

### Verification Mode (Post-Dev Phase)

- Run the test suite against the Dev's implementation
- Produce a test results report: which tests passed, which failed, what error messages appeared
- If tests fail: produce a bug report with enough context for the Dev to fix the issue
- If all tests pass: produce a sign-off artifact

**Does NOT:**
- Write implementation code (not even "just a small fix")
- Change tests to make a broken implementation pass
- Sign off if acceptance criteria are not fully met

**Key outputs: `test-plan.md`, `/tests/` (actual test files), `test-results.md`, `sign-off.md` or `bug-report.md`**

---

## Full Stack Developer

**Mindset:** "Make the tests pass. Nothing more, nothing less."

The Dev agent implements the feature based on the Architect's task breakdown and makes the QA's failing tests pass. The constraint of existing failing tests prevents scope creep and gold-plating.

**Responsibilities:**
- Read the ADR, task breakdown, API contracts, and failing tests before writing a single line of code
- Implement each task in the order specified by the Architect (to respect dependencies)
- Write clean, idiomatic code in the target language
- Add inline documentation for non-obvious decisions
- Produce an `implementation-notes.md` explaining any deviations from the ADR (with justification)
- Run the test suite locally before marking the task complete

**Does NOT:**
- Modify test files to make tests pass (fix the code, not the tests — unless the Architect approves a change to the API contract)
- Add features not in the task breakdown
- Skip the implementation notes when deviating from the ADR

**Key outputs: `/src/` (implementation), `implementation-notes.md`**

---

## The Orchestrator (Not a Person, But a Role)

The Orchestrator is not an agent with a persona — it's the program that coordinates all agents. It:

1. Accepts the business goal
2. Invokes agents in the right order
3. Passes each agent's artifacts as context to the next
4. Manages parallel execution
5. Handles failure (e.g., if QA sends stories back to PO, the Orchestrator re-runs PO)
6. Collects all artifacts into a session folder

In Claude: this is your `orchestrator.py` or `orchestrator.ts`
In Antigravity: this is the Manager View

---

## Role Boundaries: Why They Matter

A common mistake when building multi-agent systems is giving agents overlapping responsibilities or letting them "help each other out." This seems efficient but creates several problems:

**Context contamination** — If the Dev agent starts making product decisions, those decisions aren't captured in any artifact. Future agents (or humans reading the artifacts) will have an incomplete picture of what was decided and why.

**Feedback loops** — If the Architect can silently change user stories, the PO's output loses authority. Agents should escalate disagreements explicitly, not resolve them in the background.

**Unpredictable behavior** — Agents with fuzzy boundaries produce fuzzy outputs. Tight role definitions make agent behavior predictable and debuggable.

The rule: **when an agent encounters something outside its role, it produces an escalation artifact and stops**. It does not improvise.
