---
name: halt-mission
description: Emergency stop for the agent workflow. Any agent invokes this when retries are exhausted, two artifacts contradict each other, or execution is looping without progress.
---

# Skill: Halt Mission (Emergency Brake)

## Goal

Gracefully terminate the current automated sequence and hand control back to the human with a **contract-shaped** diagnostic report (`HALT_REPORT.md`), so the root cause is legible without replaying the whole mission.

## When to Invoke

Invoke halt-mission when **any** of the following holds. Do not wait for all three.

1. **Retry budget exhausted.** Three entries have been appended to `MISSION_STATE.md → Retry Log` for the same action (same file, same test, same decision) with no progress between them. The third failed attempt is the trigger, not the fourth.
2. **Irreconcilable contradiction between artifacts.** Two binding artifacts make incompatible claims (e.g. `DESIGN.md → File Paths Contract` and `DESIGN.md → Testing Contract` disagree; `BACKLOG.md → Acceptance Criteria` and `DESIGN.md` disagree) and re-reading both does not resolve which is authoritative.
3. **Progress-free loop.** The same error signature has appeared twice after two different fix attempts — not a retry of the same fix, but two distinct attempts producing the same failure.

If you are the agent hitting any of these, stop your current work and run the steps below. Any agent may invoke this skill — it is not architect-exclusive.

## Instructions

1. **Stop execution.** Cease all file writes, terminal commands, and loop iterations. Do not attempt "one last fix."
2. **Instantiate the report.** Copy `.agent/templates/HALT_REPORT.md` into the mission folder `./.agent-missions/mission-{{ID}}/HALT_REPORT.md`. Fill every section — write `none` explicitly rather than leaving placeholders.
3. **Pull retry history from state.** The Retry History table in the report is a transcription of `MISSION_STATE.md → Retry Log` entries relevant to this halt — not a free-form summary.
4. **Update mission state.** In `MISSION_STATE.md`:
   - Set **Status** to `halted`.
   - Add an entry to **Artifact Locations** for `HALT_REPORT.md`.
   - Append a Phase Log entry noting the halt (which phase, which agent, pointer to the report).
5. **Notify the user.** Output the single line: `MISSION HALTED: Human Intervention Required. See ./.agent-missions/mission-{{ID}}/HALT_REPORT.md.` Do not add prose around it — the report is the communication.

## Closure Paths (what the human does next)

The skill does not choose between these — the human does, after reading the report. Your `HALT_REPORT.md → Proposed Human Fix` section should make both paths concrete enough to pick from.

- **Resolve and resume.** Human revises the offending artifact in place, logs the revision in `MISSION_STATE.md → Revision History`, resets **Status** to the appropriate phase, and the mission continues. The halt report stays in the folder as audit trail.
- **Abandon.** Human runs `./.agent/scripts/archive-mission.sh {{MISSION_ID}} "halted: <reason>"`. The folder moves to `_archive/` with the halt report intact.

## Constraints

- Do NOT delete the mission folder or any artifact — the halt report is only useful alongside the originals that caused it.
- Do NOT attempt autonomous recovery after invoking this skill. Halting *is* the action.
- Do NOT write free-form prose in place of the template. `HALT_REPORT.md` is a contract like every other artifact in this system.
- Do NOT invoke on a single failure. The triggers above require a pattern (three retries, contradiction, or repeat error) — a first failure is a retry, not a halt.
