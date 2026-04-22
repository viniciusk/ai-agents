---
name: scope-refiner
description: Refines raw user requirements into actionable backlogs. Use this at the start of a feature request to explore side-effects and technical consequences.
---

# Feature Refiner Skill

1. **Identify Mission:** Ensure you are working in `./.agent-missions/mission-{{ID}}/`. Verify `MISSION_STATE.md` exists; if not, Phase 0 was skipped — halt and ask.
2. **Instantiate Template:** Copy `.agent/templates/BACKLOG.md` into the mission folder. You are filling a contract, not writing prose.
3. **Interactive Probe:** Ask 3–5 clarifying questions that map directly onto Job Story fields (see below).
4. **Fill the Artifact:** Complete every section of `BACKLOG.md`, especially the Job Story, Context Fields, Clarifying Questions table, Acceptance Criteria (Gherkin), and Out of Scope.
5. **Update State:** Append a Phase 1 entry to `MISSION_STATE.md → Phase Log` and set **Status** to `awaiting-approval`.

## Goal

To produce a `BACKLOG.md` whose structure the architect can rely on in Phase 2, and whose Gherkin scenarios the tdd-specialist can translate one-to-one into feature tests in Phase 3. The format is **Job Story**, not User Story — front-load the triggering situation, not the persona.

## The Job Story Format (what you are filling)

```
When {triggering situation},
the user (role: X) wants to {motivation},
so they can {observable outcome}.
```

Why Job Stories: the `When` clause here doubles as the Gherkin `When` in Acceptance Criteria. The persona becomes a qualifier rather than a mandatory prefix — write `"the user"` when the role is irrelevant and name a role only when permissions or UI variants depend on it. "Success signal" is a separate field from "motivation" so agents downstream can test for observable outcomes directly.

## Interactive Probe (question templates)

Your 3–5 questions should collectively surface enough to fill the Job Story sentence AND the Context Fields block. Use or adapt the questions below. Do not ask more than 5; if you need more, prioritize.

1. **Trigger** — "What event or state in the system causes this feature to matter? (e.g. 'user clicks Notifications in the topbar', 'admin imports a CSV', 'a scheduled job fires nightly')"
2. **Success signal** — "After this works, what can the user see, touch, or confirm that tells them it worked?"
3. **Actor specificity** — "Does this apply to everyone, or only users with a specific role/permission? (ignore if persona is irrelevant)"
4. **Persistence** — "Should this persist in the DB, session-only, or client-side only?"
5. **UI surface** — "Is this an Inertia modal, a full-page transition, a background side-effect, or an embedded component?"
6. **Failure modes** — "What's the non-obvious way this could break an existing user's experience?"
7. **Boundary** — "What's the nearest thing this is NOT — i.e. a feature it might be confused with but we're not building?"

Record every question and the user's verbatim answer in the Clarifying Questions table — that table is the source-of-truth for intent. When you write the Job Story sentence and Context Fields, you are compressing answers from this table, not inventing content.

## Gherkin Alignment

Acceptance Criteria MUST be valid Gherkin (`Feature / Scenario / Given / When / Then`). Reuse phrasing from Context Fields verbatim where possible:

- `Given` clauses ← **Preconditions** field
- `When` clauses ← **Triggering event** field
- `Then` clauses ← **Success signal** field

If you cannot reuse the Context Fields in Gherkin without paraphrasing heavily, your Context Fields are probably wrong — revise them first.

## Rejection Handling

If the user rejects the backlog at Gate 1, edit `BACKLOG.md` in place. Append new clarifying questions to the existing table — do not delete rows. Log the rejection in `MISSION_STATE.md → Revision History`.

## Constraints

- Do not assume default Laravel behavior if multiple options exist.
- Focus on the "Side-Effects" of changing existing system behavior.
- Do not skip template sections, even with "N/A" — write `none` explicitly so the architect knows it was considered.
- Do not revert to "As a X, I want Y, so that Z" phrasing. The template uses Job Stories deliberately.
