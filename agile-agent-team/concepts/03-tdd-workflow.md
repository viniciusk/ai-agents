# Concept 03 — TDD Workflow in Agentic Systems

Test-Driven Development (TDD) is powerful in human teams. In agentic systems, it becomes even more important — because tests are the only reliable constraint you can put on an AI agent's implementation.

---

## Why TDD Matters for AI Agents

When a human developer writes code without tests, at least they have intuition, experience, and a mental model of "is this right?" An AI agent implementing code without tests can produce something that looks syntactically correct, appears to follow the architecture, but silently does the wrong thing.

**Tests are the specification.** If a test passes, the agent has demonstrably met a requirement. If it fails, the agent has clear, unambiguous feedback. This is far more reliable than asking an agent to "make sure the feature works correctly."

---

## The Red-Green-Refactor Loop in Agents

Traditional TDD has three phases:

1. **Red** — Write a failing test
2. **Green** — Write the minimum code to make the test pass
3. **Refactor** — Clean up without breaking the tests

In the agent system:

1. **Red (QA Agent)** — QA writes tests based on acceptance criteria. These tests fail because no implementation exists yet.
2. **Green (Dev Agent)** — Dev reads failing tests and writes code to make them pass. Dev does not add functionality beyond what tests require.
3. **Refactor (Dev Agent, optional)** — Dev cleans up code. Runs tests to confirm they still pass.
4. **Verify (QA Agent)** — QA runs the full test suite and produces the sign-off.

---

## What the QA Agent Writes

For each acceptance criterion, QA produces at least one test at the appropriate level:

### Unit Tests
Test individual functions or classes in isolation.

```
Acceptance Criterion: "Password reset tokens must expire after 24 hours"
Unit Test: test_token_expiry_after_24_hours()
  → Creates a token with a timestamp 25 hours in the past
  → Asserts the token is considered invalid
  → Asserts the appropriate error is raised
```

### Integration Tests
Test how components work together.

```
Acceptance Criterion: "Sending a reset email must update the user record"
Integration Test: test_reset_email_updates_user_record()
  → Calls the reset email service with a valid user
  → Asserts the user record has a reset_token and reset_token_expires_at
  → Asserts an email was dispatched (using a test email backend)
```

### End-to-End Tests
Test the full user journey.

```
Acceptance Criterion: "User can reset password via the email link"
E2E Test: test_full_password_reset_flow()
  → User requests reset
  → Clicks link in email
  → Sets new password
  → Logs in with new password
  → Assert login succeeds
```

---

## The Test File Structure QA Produces

QA organizes tests to match the Architect's task breakdown:

```
tests/
  unit/
    test_token_generation.py
    test_token_validation.py
    test_email_formatting.py
  integration/
    test_reset_email_service.py
    test_database_updates.py
  e2e/
    test_full_reset_flow.py
  conftest.py (or equivalent setup file)
  run_tests.sh  ← Script the Dev agent uses to run all tests
```

The `run_tests.sh` file is critical — it gives the Dev agent a single command to verify all tests pass.

---

## Instructions QA Includes for Dev

At the end of the QA phase, QA produces a `dev-handoff.md` inside the tests folder:

```markdown
## For the Developer

All tests in this folder are currently FAILING because no implementation exists.
Your goal: make all tests pass without modifying any test files.

Setup:
  1. Install dependencies: `pip install -r requirements.txt`
  2. Run tests: `./run_tests.sh`

Test order (start here):
  1. unit/test_token_generation.py — start here, fewest dependencies
  2. unit/test_token_validation.py
  3. integration/test_reset_email_service.py
  4. integration/test_database_updates.py
  5. e2e/test_full_reset_flow.py — run this last

If a test is ambiguous, consult the acceptance criteria in:
  artifacts/po/acceptance-criteria.md

Do NOT modify test files. If a test seems wrong, escalate to QA.
```

---

## The "No Test Modification" Rule

This is the most important rule in the TDD workflow:

> **The Dev agent must never modify test files to make tests pass.**

This rule prevents the most common failure mode: an agent that "solves" a failing test by weakening the assertion rather than fixing the implementation.

In the skills for both the Dev agent and the QA verification phase, this rule is explicit and reinforced. The Orchestrator can optionally enforce it by diffing the test files between phases — if test files changed, the Dev agent is flagged.

---

## When Tests and Requirements Conflict

Sometimes a test is genuinely wrong — the QA agent misunderstood an acceptance criterion. In this case:

1. Dev produces an escalation artifact: `test-conflict-report.md`
2. Orchestrator routes this to QA
3. QA reviews the conflict and either:
   - Fixes the test (most common) and sends back to Dev
   - Confirms the test is correct and Dev needs to fix the implementation
4. If there's still disagreement → Orchestrator routes to Architect who makes the final call on the API contract

This process is explicit and auditable. No silent "I'll just change the test to match what I wrote."

---

## Monitoring Test Progress

During the Green phase, the Dev agent should report progress incrementally:

```
Task 1/5: Implement token generation
  → Running: ./run_tests.sh tests/unit/test_token_generation.py
  → Result: 3/3 passing ✓

Task 2/5: Implement token validation
  → Running: ./run_tests.sh tests/unit/test_token_validation.py
  → Result: 2/4 passing — debugging test_expired_token_raises...
  → Fixed: was checking wrong field. Now 4/4 passing ✓
```

This output becomes part of `implementation-notes.md` — a useful record of where the agent got stuck and how it resolved it.
