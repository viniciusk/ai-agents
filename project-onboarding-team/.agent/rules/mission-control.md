---
trigger: always_on
---

# Rule: Mission-Centric Persistence

## Goal

Ensure every task is part of a traceable, isolated "Mission" to maintain project state and auditability.

## Mandatory Standards

1. **Root Directory:** All work must originate from or be logged in `./.agent-missions/mission-{{ID}}/`.
2. **The Blackboard:** Every agent must check for the presence of `MISSION_STATE.md` before starting.
3. **Artifact Isolation:** Handovers (Backlogs, Designs, Test Reports) MUST be stored in the mission's folder.
4. **Context Updates:** Before concluding a turn, the active agent must update `MISSION_STATE.md` with:
   - Current Phase Status (e.g., "Refinement Complete").
   - Location of newly created artifacts.
   - Any architectural decisions that deviate from the initial plan.

## Enforcement

Do not write code or tests until a Mission ID is established in the session context.
