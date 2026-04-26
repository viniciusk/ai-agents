# laravel-fullstack-team

A skeleton multi-agent development team for Laravel 12 / Inertia v3 / Vue 3 feature work. Designed to be copied into new projects and adapted — hence the emphasis on contracts, templates, and explicit phase boundaries over freeform prose.

## What lives here

```
laravel-fullstack-team/
├── README.md                          # this file
├── .agent/
│   ├── config.json                    # agents, tier/mode/temperature assignments
│   ├── state/
│   │   └── context.json               # cross-session state (runtime; not committed on fresh projects)
│   ├── rules/
│   │   ├── state-persistence.md       # always-on: how to read/write context.json
│   │   └── mission-control.md         # always-on: how missions isolate and audit work
│   ├── skills/
│   │   ├── scope-refiner/SKILL.md     # Phase 1 — turns a prompt into a BACKLOG
│   │   ├── architect/SKILL.md         # Phase 2 + 5 — designs and reviews drift
│   │   ├── tdd-specialist/SKILL.md    # Phase 3 + 5 — writes failing tests, verifies green
│   │   └── developer/SKILL.md         # Phase 4 — implements backend + frontend
│   ├── workflows/
│   │   └── mission-new-feature-implementation.md  # the 6-phase feature workflow
│   ├── templates/                     # fillable skeletons for every artifact
│   │   ├── MISSION_STATE.md
│   │   ├── BACKLOG.md
│   │   ├── DESIGN.md
│   │   ├── TEST_REPORT_RED.md
│   │   └── FINAL_REVIEW.md
│   └── scripts/                       # operational scripts — all agent-workflow scoped
│       ├── new-mission.sh             # Phase 0 — creates a mission folder
│       ├── archive-mission.sh         # Phase 6 — closes/abandons a mission
│       ├── validate-state.sh          # schema check for context.json + optional MISSION_STATE
│       ├── run-tests.sh               # wraps `php artisan test` with red/green mode
│       └── quotestimator.py           # calculates and tracks LLM token usage
└── .agent-missions/                   # runtime — created on first mission
    ├── mission-YYYYMMDD-HHMMSS/       # one folder per feature mission
    │   ├── MISSION_STATE.md
    │   ├── BACKLOG.md
    │   ├── DESIGN.md
    │   ├── TEST_REPORT_RED.md
    │   └── FINAL_REVIEW.md
    └── _archive/                      # closed/abandoned missions (plus ARCHIVE.md ledger)
```

## The core idea

Agents don't write freeform prose — they **fill contracts**. Every artifact (`BACKLOG`, `DESIGN`, `TEST_REPORT_RED`, `FINAL_REVIEW`, `MISSION_STATE`) starts as a template copy with named sections. This is what makes the system reusable across projects and swappable across models: the shape is fixed, only the contents vary.

Missions are isolated. Every feature gets its own folder under `.agent-missions/`. Agents never share scratch state across missions; cross-cutting persistence lives in `.agent/state/context.json` and is governed by a single rule.

## How to trigger the workflow

1. In the target Laravel project, ensure `laravel-fullstack-team/` is a sibling (or set `DEV_TEAM_LARAVEL_ROOT` to your project root before running `run-tests.sh`).
2. From the `laravel-fullstack-team/` root, issue the workflow trigger in your agent interface:
   ```
   /mission-new-feature-implementation
   ```
   The agent will run Phase 0 (via `.agent/scripts/new-mission.sh`) and prompt you for a feature slug.
3. Answer the scope-refiner's 3–5 clarifying questions. Approve or reject the BACKLOG.
4. Review the architect's DESIGN. Approve or reject.
5. Phases 3–4 run hands-off. Review the FINAL_REVIEW and approve to close.

## The 6 phases at a glance

| #   | Phase                       | Agent                          | Input               | Output                               | Gate     |
| --- | --------------------------- | ------------------------------ | ------------------- | ------------------------------------ | -------- |
| 0   | Initialization              | System (`new-mission.sh`)      | —                   | `MISSION_STATE.md`                   | —        |
| 1   | Requirements Refinement     | `scope-refiner`                | prompt + README     | `BACKLOG.md`                         | **User** |
| 2   | Architectural Design        | `architect`                    | `BACKLOG.md`        | `DESIGN.md`                          | **User** |
| 3   | TDD — Red                   | `tdd-specialist`               | `DESIGN.md`         | failing tests + `TEST_REPORT_RED.md` | —        |
| 4   | Implementation              | `developer`                    | `DESIGN.md` + tests | code                                 | —        |
| 5   | Verification + Drift Review | `tdd-specialist` + `architect` | everything          | `FINAL_REVIEW.md`                    | **User** |
| 6   | Closure                     | System (`archive-mission.sh`)  | —                   | archived mission                     | —        |

Full workflow spec: `.agent/workflows/mission-new-feature-implementation.md`.

## Rejection handling (important)

There are three user-approval gates (after Phases 1, 2, 5). Rejection never starts a new mission and never creates versioned artifact copies — the same file is revised in place, and the revision is logged in `MISSION_STATE.md → Revision History`.

- **Gate 1 rejected** → Phase 1 re-runs (scope-refiner).
- **Gate 2 rejected** → Phase 2 re-runs, OR loop back to Phase 1 if the issue is scope.
- **Gate 5 rejected** → the architect's verdict checkbox in `FINAL_REVIEW.md → Part B` selects the loop-back target (Phase 2, 3, or 4).
- **Drift mid-Phase-4** → developer pauses, logs the drift, and loops back to Phase 2.
- **Abandoned** → run `.agent/scripts/archive-mission.sh MISSION_ID "abandoned: <reason>"`. The folder is preserved in `_archive/`.

Full rules: `.agent/workflows/mission-new-feature-implementation.md → Rejection Handling`.

## State: two levels

- **Cross-session, cross-mission:** `.agent/state/context.json`. Tracks `last_updated`, `active_feature`, durable `architectural_decisions`, and `pending_tasks`. Schema and rules live in `.agent/rules/state-persistence.md`. Validate with `.agent/scripts/validate-state.sh`.
- **Per-mission:** `MISSION_STATE.md` inside the mission folder. This is the blackboard — every agent reads it first and updates it on handover. Rules live in `.agent/rules/mission-control.md`.

Agents should resist the temptation to log mission-specific details in `context.json` — that pollutes the cross-session memory. If it's about _this_ feature, it goes in `MISSION_STATE.md`.

## Telemetry & Cost Tracking

The `quotestimator.py` script automatically runs at the end of each agent's phase to estimate token usage and API costs.

- It calculates **Input Tokens** by multiplying the read context by the number of conversational turns taken.
- It calculates **Output Tokens** efficiently by using `git diff` to count only the exact characters modified or added by the agent, avoiding overestimation.
- Telemetry records are stored in `.agent-missions/mission-{{ID}}/telemetry.jsonl`.
- At the end of the mission (Phase 6), a consolidated Markdown summary is appended directly to `FINAL_REVIEW.md`.

## Agent roster & why each one has the settings it does

From `.agent/config.json`:

- **architect** — tier `high`, temperature `0.15`. Cold, deterministic design; the contract must be stable across runs.
- **scope-refiner** — tier `balanced`, temperature `0.75`. Warm enough to explore side-effects and ask good questions.
- **tdd-specialist** — tier `turbo`, temperature `0`. Fast, deterministic, cheap; tests are mechanical translation of the Testing Contract.
- **developer** — tier `balanced`. Full-stack implementation; neither needs max reasoning nor pure speed.

## Extending this skeleton

When you copy `laravel-fullstack-team/` into a new project:

1. Edit `.agent/config.json → project_id` and tier mappings for your model provider.
2. Update the stack-specific language in each `SKILL.md` — the current skills name Laravel 12, Inertia v3, Vue 3, Tailwind v4 explicitly. Change those, and change the `DESIGN.md` template's TypeScript/Inertia sections accordingly.
3. Leave the rules, workflow shape, templates-as-contracts, and scripts alone unless you have a specific reason — those are the load-bearing parts of the skeleton.
4. Add new skills as separate folders under `.agent/skills/`. Add new workflows as separate files under `.agent/workflows/`. Existing pieces compose.

## Requirements

- `bash` (tested on macOS and Linux).
- `jq` for `validate-state.sh` (`brew install jq` / `apt-get install jq`).
- `python3` and `git` for `quotestimator.py` telemetry generation.
- `php` + a Laravel 12 project for `run-tests.sh`. Set `DEV_TEAM_LARAVEL_ROOT` if the Laravel project is not a sibling directory.
