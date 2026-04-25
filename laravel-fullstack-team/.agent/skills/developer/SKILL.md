---
name: developer
description: Implements features across the full Laravel 12 and Inertia v3 stack. Use this to turn designs and failing tests into working code.
---

# Stack Developer Skill

1. **Read the Contract:** Before writing any code, read `DESIGN.md → File Paths Contract` — you will create **only** these files — and `DESIGN.md → Testing Contract` — the tests already exist; you make them pass.
2. **Read the Tests:** `TEST_REPORT_RED.md` lists the failing tests. Treat them as the spec.
3. **Implementation:** Laravel 12 (PHP 8.2+), Vue 3 `<script setup>`, Tailwind v4.
4. **Persistence:** update `MISSION_STATE.md → Artifact Locations` and `Phase Log` as files are created.
5. **Record Telemetry:** Before handing over, run `python3 ./.agent/scripts/quotestimator.py --agent CURRENT_AGENT --model CURRENT_AGENT_MODEL --turns NUMBER_OF_TURNS_TAKEN --read EACH_FILE_READ --modified EACH_FILE_MODIFIED`.
6. **Verification:** run `./.agent/scripts/run-tests.sh green {{MISSION_ID}}` until it exits 0.

## Goal

Implement the backend and frontend logic required to turn tests from "Red" to "Green" — without creating a single file that isn't in the File Paths Contract.

## Instructions

1. **Backend (Laravel 12):**
   - Use **Action Classes** for business logic (SOLID). File location: `app/Actions/{{ActionName}}.php` (or as specified in DESIGN).
   - Use **Typed Properties** and constructor promotion (PHP 8.2+).
   - Implement Inertia controllers that return `Inertia::render()`. Controllers contain no logic beyond request parsing and Action invocation.
2. **Frontend (Vue 3 + TS):**
   - Use `<script setup>` and define props with TypeScript interfaces whose shape **exactly matches** the `Inertia::render()` payload declared in DESIGN.
   - Use Inertia `useForm` for data handling; initial values must match the `useForm` shape in DESIGN.
   - Apply **Tailwind v4** styles (using CSS variables where applicable). No ad-hoc CSS files unless listed in DESIGN.
3. **Database:** create Migrations and Seeders listed in `DESIGN.md → Data Layer`.
4. **Check Tests Frequently:** run `./.agent/scripts/run-tests.sh green {{MISSION_ID}}` after each logical unit of work, not only at the end.

## Drift Protocol

If you believe you must create a file **not** in the File Paths Contract, or change the shape of an Inertia prop contract:

1. Stop writing code.
2. Append a row to `MISSION_STATE.md → Deviations from Plan` describing the proposed drift and why it's necessary.
3. Flag back to the architect (loop to Phase 2). Do not continue implementation until DESIGN.md is amended.

This is not optional. Silent drift is the single biggest failure mode this workflow is designed to prevent.

## Constraints

- **Pass the Tests:** you are only done when `./.agent/scripts/run-tests.sh green {{MISSION_ID}}` exits 0.
- **Unified Logic:** prop names in the Controller MUST exactly match the Vue component's `defineProps` — verified in Phase 5.
- **No Files Outside Contract:** if it's not in `DESIGN.md → File Paths Contract`, you do not create it without amending DESIGN first.
- **Do not touch test files** written by the tdd-specialist except to fix genuine typos; tests are spec, not a draft.
