# Agile Agent Team

Four specialized agents that collaborate to take a business goal from requirements
through architecture, TDD, implementation, and verification.

All per-mission files live under `.agent-missions/mission-{timestamp}/`, created at
the start of each `/mission` run.

---

## Product Owner (`po`)

- **Goal**: Convert a business goal into structured user stories with measurable
  acceptance criteria. Clarify ambiguities before planning begins.
- **Skill**: `.agent/skills/po/SKILL.md`
- **Model**: `gemini-3.1-pro` or `claude-sonnet-4-6`
- **Triggers on**: mission brief in `.agent-missions/{MISSION_ID}/mission.md`
- **Produces**:
  - `.agent-missions/{MISSION_ID}/artifacts/po/user-stories.md`
  - `.agent-missions/{MISSION_ID}/artifacts/po/acceptance-criteria.md`
  - `.agent-missions/{MISSION_ID}/handoffs/po-to-architect.md`
- **Blocked?**: Surfaces to user — PO cannot proceed without clear requirements.

---

## Software Architect (`architect`)

- **Goal**: Design robust, scalable architecture from PO requirements.
  Produce the ADR, API contracts, and ordered task breakdown.
  Push back to PO if requirements are infeasible.
- **Skill**: `.agent/skills/architect/SKILL.md`
- **Model**: `gemini-3.1-pro-high` (high reasoning required — this phase is the most expensive mistake)
- **Triggers on**: `.agent-missions/{MISSION_ID}/handoffs/po-to-architect.md`
- **Produces**:
  - `.agent-missions/{MISSION_ID}/artifacts/architect/architecture-decision-record.md`
  - `.agent-missions/{MISSION_ID}/artifacts/architect/api-contracts.yaml`
  - `.agent-missions/{MISSION_ID}/artifacts/architect/task-breakdown.md`
  - `.agent-missions/{MISSION_ID}/handoffs/architect-to-qa.md`
  - `.agent-missions/{MISSION_ID}/handoffs/architect-to-dev.md`
- **Blocked?**: Routes back to Product Owner.

---

## QA Engineer (`qa`)

Runs in two distinct modes — never mix them in the same invocation.

- **Planning Mode**
  - **Goal**: Write failing tests before any implementation exists (TDD).
    Every acceptance criterion must have at least one test.
  - **Triggers on**: `.agent-missions/{MISSION_ID}/handoffs/architect-to-qa.md`
  - **Produces**:
    - `.agent-missions/{MISSION_ID}/tests/` (unit/, integration/, e2e/)
    - `.agent-missions/{MISSION_ID}/artifacts/qa/test-plan.md`
    - `.agent-missions/{MISSION_ID}/tests/DEV_HANDOFF.md`
    - `.agent-missions/{MISSION_ID}/handoffs/qa-to-dev.md`

- **Verification Mode**
  - **Goal**: Run the test suite against the finished implementation.
    Sign off only when all tests pass.
  - **Triggers on**: `.agent-missions/{MISSION_ID}/handoffs/dev-to-qa.md`
  - **Produces**:
    - `.agent-missions/{MISSION_ID}/artifacts/qa/sign-off.md` (pass) **or**
      `.agent-missions/{MISSION_ID}/artifacts/qa/bug-report.md` (fail)
    - `.agent-missions/{MISSION_ID}/handoffs/qa-signoff.md` **or**
      `.agent-missions/{MISSION_ID}/handoffs/qa-to-dev-cycle.md`

- **Skill**: `.agent/skills/qa/SKILL.md`
- **Model**: `claude-sonnet-4-6` (planning); `gemini-3-flash` (verification)

---

## Full Stack Developer (`developer`)

Runs in two distinct modes — never mix them in the same invocation.

- **Setup Mode**
  - **Goal**: Scaffold project structure and install dependencies based on the ADR.
    No implementation code — wait for QA to produce tests first.
  - **Triggers on**: `.agent-missions/{MISSION_ID}/handoffs/architect-to-dev.md`
  - **Produces**: `.agent-missions/{MISSION_ID}/handoffs/dev-setup-complete.md`

- **Implementation Mode**
  - **Goal**: Make all failing tests pass. Never modify test files.
    Implement task by task per the Architect's breakdown.
  - **Triggers on**: `.agent-missions/{MISSION_ID}/handoffs/qa-to-dev.md`
    AND `.agent-missions/{MISSION_ID}/handoffs/dev-setup-complete.md`
  - **Produces**:
    - `.agent-missions/{MISSION_ID}/src/`
    - `.agent-missions/{MISSION_ID}/artifacts/dev/implementation-notes.md`
    - `.agent-missions/{MISSION_ID}/handoffs/dev-to-qa.md`

- **Skill**: `.agent/skills/developer/SKILL.md`
- **Model**: `gemini-3-flash` (setup); `claude-sonnet-4-6` (implementation)
