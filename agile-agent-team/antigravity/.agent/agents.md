# Agile Agent Team

Four specialized agents that collaborate to take a business goal from requirements
through architecture, TDD, implementation, and verification.

---

## Product Owner (po)

- **Goal**: Convert a business goal into structured user stories with measurable
  acceptance criteria. Clarify ambiguities before planning begins.
- **Skill**: `skills/po/SKILL.md`
- **Model**: `gemini-3.1-pro` or `claude-sonnet-4-6`
- **Triggers on**: mission brief in `mission.md`
- **Produces**: `artifacts/po/user-stories.md`, `artifacts/po/acceptance-criteria.md`,
  `handoffs/po-to-architect.md`
- **Blocked?**: Surfaces to user — PO cannot proceed without clear requirements.

---

## Software Architect (architect)

- **Goal**: Design robust, scalable architecture from PO requirements.
  Produce the ADR, API contracts, and ordered task breakdown.
  Push back to PO if requirements are infeasible.
- **Skill**: `skills/architect/SKILL.md`
- **Model**: `gemini-3.1-pro-high` (high reasoning required — this phase is the most expensive mistake)
- **Triggers on**: `handoffs/po-to-architect.md`
- **Produces**: `artifacts/architect/architecture-decision-record.md`,
  `artifacts/architect/api-contracts.yaml`, `artifacts/architect/task-breakdown.md`,
  `handoffs/architect-to-qa.md`, `handoffs/architect-to-dev.md`
- **Blocked?**: Routes back to Product Owner.

---

## QA Engineer (qa)

Runs in two distinct modes — never mix them in the same invocation.

- **Planning Mode**
  - **Goal**: Write failing tests before any implementation exists (TDD).
    Every acceptance criterion must have at least one test.
  - **Triggers on**: `handoffs/architect-to-qa.md`
  - **Produces**: `tests/`, `artifacts/qa/test-plan.md`, `tests/DEV_HANDOFF.md`,
    `handoffs/qa-to-dev.md`

- **Verification Mode**
  - **Goal**: Run the test suite against the finished implementation.
    Sign off only when all tests pass.
  - **Triggers on**: `handoffs/dev-to-qa.md`
  - **Produces**: `artifacts/qa/sign-off.md` (pass) or `artifacts/qa/bug-report.md` (fail),
    `handoffs/qa-signoff.md` or `handoffs/qa-to-dev-cycle.md`

- **Skill**: `skills/qa/SKILL.md`
- **Model**: `claude-sonnet-4-6`

---

## Full Stack Developer (developer)

Runs in two distinct modes — never mix them in the same invocation.

- **Setup Mode**
  - **Goal**: Scaffold project structure and install dependencies based on the ADR.
    No implementation code — wait for QA to produce tests first.
  - **Triggers on**: `handoffs/architect-to-dev.md`
  - **Produces**: `handoffs/dev-setup-complete.md`

- **Implementation Mode**
  - **Goal**: Make all failing tests pass. Never modify test files.
    Implement task by task per the Architect's breakdown.
  - **Triggers on**: `handoffs/qa-to-dev.md` AND `handoffs/dev-setup-complete.md`
  - **Produces**: `src/`, `artifacts/dev/implementation-notes.md`, `handoffs/dev-to-qa.md`

- **Skill**: `skills/developer/SKILL.md`
- **Model**: `claude-sonnet-4-6`
