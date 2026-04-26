# Workflow: mission-project-onboarding

This workflow defines the sequential phases for auditing a legacy or "vibe-coded" codebase and generating an improvement plan.

## The Phases

| Phase | Agent                   | Input                                            | Output                                        | Gate     |
|-------|-------------------------|--------------------------------------------------|-----------------------------------------------|----------|
| 0     | System                  | `/mission-project-onboarding` trigger            | `01_MISSION_STATE.md` initialized                | —        |
| 1     | `discovery-agent`       | Source code                                      | `02_GLOSSARY.md`                                 | **User** |
| 2     | `security-auditor`      | Source code, `02_GLOSSARY.md`                       | `03_SECURITY_REVIEW.md`                          | —        |
| 3     | `performance-expert`    | Source code, `02_GLOSSARY.md`                       | `04_PERFORMANCE_REVIEW.md`                       | —        |
| 4     | `architecture-reviewer` | Source code, `02_GLOSSARY.md`                       | `05_ARCHITECTURE_REVIEW.md`, `06_TECH_DEBT_ASSESSMENT.md` | —        |
| 5     | `planning-strategist`   | All previous reports                             | `07_IMPROVEMENT_PLAN.md`, `08_FINAL_REVIEW.md`      | **User** |

## Rules of Engagement

1. **Model Enforcement Check:** At the very start of every phase (except Phase 0), the agent MUST remind the orchestrator (the user) to check their IDE model settings. Tell them exactly which model tier is recommended for the current agent based on `.agent/config.json` (e.g., "Please ensure you have switched to a `high` tier model like Gemini Pro before I proceed with the security audit.").
2. **Phase 1 (Discovery):** The `discovery-agent` maps out the core domains, technologies used, and terminology, producing `02_GLOSSARY.md`. The user must approve this glossary, as all subsequent agents will rely on its defined context to understand the application.
2. **Phase 2-4 (Parallelizable/Sequential Audit):** The security, performance, and architecture experts operate using the glossary and direct code review to assess the state of the system, identifying vulnerabilities, bottlenecks, and design flaws.
3. **Phase 5 (Synthesis):** The `planning-strategist` consumes the raw reports to produce an actionable `07_IMPROVEMENT_PLAN.md` and generates the `08_FINAL_REVIEW.md` for human approval.

## Rejection Handling

- If the **Discovery Phase** (`02_GLOSSARY.md`) is rejected, the `discovery-agent` re-runs to refine the project mapping.
- If the **Final Review** (`07_IMPROVEMENT_PLAN.md`) is rejected, the `planning-strategist` refines the strategy based on feedback, or delegates back to a specific auditor if missing information is identified.
