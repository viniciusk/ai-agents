# Backlog — {{feature-slug}}

> Produced by `scope-refiner` in Phase 1. Must be approved by the user before Phase 2 begins. Revisions edit this file in place; do not create numbered copies.

## Source Prompt

> {{verbatim user prompt that started the mission}}

## Feature Intent (Job Story)

The Job Story format front-loads the triggering context (not the persona). This aligns with the Gherkin `When` clauses used in Acceptance Criteria below — the trigger written here should be re-usable verbatim, or near-verbatim, as the primary Gherkin `When`.

**When** {{triggering situation or context}},
**{{role — use "the user" if persona is not load-bearing; name a specific role only if permission-gated}}** wants to **{{motivation / capability}}**,
**so they can** {{observable outcome — what changes in their world when this works}}.

## Context Fields

Machine-parseable companion fields. Fill each explicitly — write `none` rather than leaving blank. Downstream agents (architect, tdd-specialist) rely on these fields individually.

- **Primary actor(s):** {{roles involved — only non-trivial if permission-gated; otherwise "the user"}}
- **Triggering event:** {{what in the real system causes this to happen — should match the Gherkin `When`}}
- **Preconditions:** {{state that must exist before the trigger — should match the Gherkin `Given`}}
- **Success signal:** {{what the user observes when it works — should match the Gherkin `Then`}}
- **Failure modes to prevent:** {{non-obvious failure scenarios the design must defend against, or "none"}}

## Clarifying Questions & Answers

Record the 3–5 questions the refiner asked and the user's answers. This is the source-of-truth for intent.

| # | Question | Answer |
|---|---|---|
| 1 | {{Q1}} | {{A1}} |
| 2 | {{Q2}} | {{A2}} |
| 3 | {{Q3}} | {{A3}} |

## Technical Constraints

Explicit constraints agreed with the user. If the architect wants to relax one of these, that's a scope change and it must loop back to Phase 1.

- **Persistence:** {{DB | session | client-side only | none}}
- **UI surface:** {{Inertia modal | full page | component embed | background}}
- **Permissions:** {{Spatie roles/permissions involved, or "none"}}
- **Existing code touched:** {{list of domains/models/middlewares that will be modified}}
- **Stack version locks:** Laravel 12, Inertia v3, Vue 3 `<script setup>`, Tailwind v4 (CSS variables).

## Side Effects & Risks

Non-obvious consequences of this change. One bullet each.

- {{e.g. "Existing users with no `notifications_preferences` row will need a backfill migration."}}

## Acceptance Criteria (Gherkin)

```gherkin
Feature: {{feature-slug}}

  Scenario: {{primary happy path}}
    Given {{precondition}}
    When {{action}}
    Then {{observable outcome}}

  Scenario: {{edge case or permission boundary}}
    Given {{precondition}}
    When {{action}}
    Then {{observable outcome}}
```

## Definition of Done

Bullet list the developer will be held to in Phase 4 and the tdd-specialist will verify in Phase 5.

- [ ] All Gherkin scenarios pass as feature tests.
- [ ] No regression in existing `php artisan test` suite.
- [ ] {{any mission-specific bar — e.g. "Lighthouse accessibility score ≥ 95 on the new page"}}.

## Out of Scope

Explicitly list what is NOT being built. This is the architect's and developer's reference when tempted to scope-creep.

- {{e.g. "No admin-side moderation queue — that is a follow-up mission."}}
