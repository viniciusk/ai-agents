# project-onboarding-team

A skeleton multi-agent auditing team designed to be dropped into any unknown, legacy, or "vibe-coded" codebase. This team is completely **language agnostic** and focuses on analyzing architecture, security, performance, and technical debt to produce an actionable Improvement Plan.

## What lives here

```
project-onboarding-team/
├── README.md                          # this file
├── .agent/
│   ├── config.json                    # agents, tier/mode/temperature assignments
│   ├── rules/
│   │   └── mission-control.md         # always-on: how missions isolate and audit work
│   ├── skills/
│   │   ├── discovery-agent/SKILL.md       # Phase 1 — maps the stack and produces GLOSSARY
│   │   ├── security-auditor/SKILL.md      # Phase 2 — finds vulnerabilities
│   │   ├── performance-expert/SKILL.md    # Phase 3 — finds bottlenecks
│   │   ├── architecture-reviewer/SKILL.md # Phase 4 — evaluates code quality & tech debt
│   │   └── planning-strategist/SKILL.md   # Phase 5 — synthesizes the IMPROVEMENT_PLAN
│   ├── workflows/
│   │   └── mission-project-onboarding.md  # the 5-phase onboarding workflow
│   ├── templates/                         # fillable skeletons for every artifact
│   │   ├── 01_MISSION_STATE.md
│   │   ├── 02_GLOSSARY.md
│   │   ├── 03_SECURITY_REVIEW.md
│   │   ├── 04_PERFORMANCE_REVIEW.md
│   │   ├── 05_ARCHITECTURE_REVIEW.md
│   │   ├── 06_TECH_DEBT_ASSESSMENT.md
│   │   ├── 07_IMPROVEMENT_PLAN.md
│   │   └── 08_FINAL_REVIEW.md
│   └── scripts/                       # operational scripts
│       ├── new-mission.sh             # Phase 0 — creates a mission folder
│       └── archive-mission.sh         # Phase 6 — closes/abandons a mission
└── .agent-missions/                   # runtime — created on first mission
```

## The core idea

Agents don't write freeform prose — they **fill contracts**. Every artifact (`GLOSSARY`, `SECURITY_REVIEW`, etc.) starts as a template copy with named sections. This ensures structured output that human engineers can actually read and act upon.

Missions are isolated. Every audit gets its own folder under `.agent-missions/`.

## How to trigger the workflow

1. In the target project you want to audit, ensure `project-onboarding-team/` is a sibling.
2. From the `project-onboarding-team/` root, issue the workflow trigger in your agent interface:
   ```
   /mission-project-onboarding
   ```
   The agent will run Phase 0 (via `.agent/scripts/new-mission.sh`) and prompt you for a project slug.
3. Review the `02_GLOSSARY.md` produced in Phase 1 to ensure the agent correctly mapped the business domain and tech stack. Approve or reject.
4. Phases 2–4 run hands-off as the specialized agents audit the code.
5. Review the `07_IMPROVEMENT_PLAN.md` and `08_FINAL_REVIEW.md` produced by the planning-strategist. Approve to close.

## The 5 phases at a glance

| #   | Phase                     | Agent                     | Output                                                    | Gate     |
| --- | ------------------------- | ------------------------- | --------------------------------------------------------- | -------- |
| 0   | Initialization            | System (`new-mission.sh`) | `01_MISSION_STATE.md`                                     | —        |
| 1   | Discovery                 | `discovery-agent`         | `02_GLOSSARY.md`                                          | **User** |
| 2   | Security Audit            | `security-auditor`        | `03_SECURITY_REVIEW.md`                                   | —        |
| 3   | Performance Audit         | `performance-expert`      | `04_PERFORMANCE_REVIEW.md`                                | —        |
| 4   | Architecture & Debt Audit | `architecture-reviewer`   | `05_ARCHITECTURE_REVIEW.md`, `06_TECH_DEBT_ASSESSMENT.md` | —        |
| 5   | Planning & Synthesis      | `planning-strategist`     | `07_IMPROVEMENT_PLAN.md`, `08_FINAL_REVIEW.md`            | **User** |

Full workflow spec: `.agent/workflows/mission-project-onboarding.md`.

## Important: Manual Model Switching

Because agents run inside your IDE's chat interface, **the system cannot automatically switch LLM models** (e.g., from Gemini Pro to Gemini Flash) mid-conversation just because `.agent/config.json` specifies it.

To actually respect the cost and speed optimizations in `config.json`, **you must manually act as the orchestrator**:

1. Before triggering a new phase, look at the required agent's tier in `config.json`.
2. Manually change the model dropdown in your IDE settings to match (e.g., switch to a faster/cheaper model before asking a lower-tier agent to work).
3. The agent will explicitly remind you of the required model at the start of each phase transition.

## Requirements

- A Bash environment (Mac/Linux/WSL).
