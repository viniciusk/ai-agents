# Google Antigravity Implementation Guide

Build the same agile agent team using **Google Antigravity** — the agent-first IDE.

---

## What is Antigravity?

Google Antigravity (launched November 2025) is an IDE built around autonomous agents. Instead of a chatbot in a sidebar, you dispatch agents that work independently in their own workspaces — each with access to an editor, terminal, and browser.

Key features relevant to this system:
- **Manager View** — Mission Control where you define the goal and dispatch agents
- **Workspaces** — Each agent works in an isolated environment (up to 5 in parallel)
- **Skills** — Markdown files (same format as Claude) that give agents specialized expertise, loaded from `.agent/skills/` in your workspace
- **Workflows** — Markdown files in `.agent/workflows/` that become slash commands (e.g. `/mission`, `/fix`)
- **Artifacts** — Structured outputs agents produce that you can review and comment on
- **Multi-model** — Assign different models to different agents (Gemini 3 Pro, Claude Sonnet 4.6, etc.)
- **MCP support** — Connect to GitHub, Jira, databases, etc.

---

## How the Agile Team Maps to Antigravity

| Agile Agent | Antigravity concept |
|---|---|
| Orchestrator | The `/mission` workflow + you in Manager View |
| Product Owner agent | Workspace with the `po` skill |
| Software Architect agent | Workspace with the `architect` skill |
| QA Engineer agent | Workspace with the `qa` skill (two modes) |
| Full Stack Developer agent | Workspace with the `developer` skill (two modes) |
| Parallel execution | QA Planning + Dev Setup dispatched simultaneously in Phase 3 |

### On "Squads"

In Antigravity's community and documentation, "Squads" is sometimes used informally to describe a pre-configured group of Workspaces + Skills that work together on a domain. Functionally it's the same as what Claude calls a "skill team" — a bundle of specialized skills designed to collaborate.

In this repo, `mission-config.json` is the reference blueprint of our Squad, and the `/mission` workflow is what actually executes it.

---

## Folder Layout

Antigravity reads workspace configuration from the `.agent/` folder at your project root:

```
agile-agent-team/antigravity/
├── README.md                  ← this file
├── mission-config.json        ← Squad blueprint (reference / sync target)
└── .agent/
    ├── agents.md              ← one-page agent catalog (human reference)
    ├── skills/
    │   ├── po/SKILL.md
    │   ├── architect/SKILL.md
    │   ├── qa/SKILL.md
    │   └── developer/SKILL.md
    └── workflows/
        ├── full-mission.md    ← /mission slash command
        └── fix.md             ← /fix slash command
```

Per-mission artifacts are written to `.agent-missions/mission-{timestamp}/` (created by Step 0 of the `/mission` workflow) — not inside `.agent/`.

---

## Prerequisites

1. Install Google Antigravity (free public preview at [antigravity.google](https://antigravity.google)).
2. Sign in with your Google account.
3. Open this repo as an Antigravity workspace, or copy the `.agent/` folder and `mission-config.json` into your own project root:

```bash
your-project/
  .agent/
    skills/
      po/SKILL.md
      architect/SKILL.md
      qa/SKILL.md
      developer/SKILL.md
    workflows/
      full-mission.md
      fix.md
    agents.md
  mission-config.json
```

Skills are loaded automatically. Workflows appear as slash commands (`/mission`, `/fix`) in the agent chat.

---

## Running the Agile Team

### Option A — Slash command (recommended)

In the Antigravity agent chat, paste:

> Execute the `/mission` workflow defined in `.agent/workflows/full-mission.md` using `@[docs/plans/{FILE_WITH_DEV_SCOPE.md}]` as the mission brief snippet. Act as the orchestrator and begin Phase 1: Product Owner.

Replace `{FILE_WITH_DEV_SCOPE.md}` with the actual filename of your scope document. The workflow will:

1. Create `.agent-missions/mission-{timestamp}/` with the full folder tree and write `mission.md` from your brief.
2. Dispatch the **Product Owner** workspace (Phase 1).
3. When the PO→Architect handoff appears, dispatch the **Architect** (Phase 2).
4. When the Architect's handoffs appear, dispatch **QA Planning** and **Dev Setup** in parallel (Phase 3).
5. When both Phase-3 handoffs arrive, dispatch the **Developer** in implementation mode (Phase 4).
6. When Dev signals ready, dispatch **QA Verification** (Phase 5). If bugs, loop back to Dev (max 5 cycles).

### Option B — Manager View, step by step

If you prefer to dispatch each workspace manually:

1. Open **Manager** and click **New Mission**.
2. Paste your business goal (e.g. "Add password reset via email, links expire after 24 hours.").
3. For each phase below, click **Add Workspace**, assign the matching skill and model, paste the task prompt from `mission-config.json`, and dispatch.
4. Before Phase 1, manually create the mission folder:
   ```bash
   MISSION_ID="mission-$(date +%Y%m%d-%H%M%S)"
   mkdir -p ".agent-missions/${MISSION_ID}"/{artifacts/{po,architect,qa,dev},handoffs,tests/{unit,integration,e2e},src}
   echo "${MISSION_ID}" > .agent-missions/current-mission
   ```

### Fixing a bug on an existing mission

In the agent chat, paste:

> Execute the `/fix` workflow defined in `.agent/workflows/fix.md` on mission `mission-{timestamp}`. Fix description: "{short specific description}". From phase: developer.

Set `From phase` to `qa-planning` if the tests themselves need rewriting, or `qa-verification` if you patched the implementation manually and just need sign-off. `/fix` reuses the existing mission folder — it does **not** create a new one.

---

## Key Differences vs. Claude Agent SDK

| Aspect | Claude Agent SDK | Google Antigravity |
|---|---|---|
| Orchestration | You write the loop in Python/TS | Driven by a markdown workflow (`/mission`) plus Manager View |
| Parallel agents | `asyncio.gather()` | Dispatch workspaces simultaneously |
| Visibility | Terminal output | Visual workspace dashboards |
| Artifact review | Read files | View Artifacts panel with comments |
| Feedback | Edit prompts and re-run | Google-Doc-style comments on Artifacts |
| Reproducibility | Code in version control | `.agent/workflows/` and `mission-config.json` in version control |
| CI/CD | Native (it's code) | Needs Antigravity API (in preview) |
| Local files | Yes | Yes (via workspace filesystem) |

**When to use Antigravity:** You want visual oversight, interactive feedback on artifacts, and you don't need to embed this in a CI/CD pipeline.

**When to use Claude Agent SDK:** You want programmable, reproducible orchestration that runs in CI/CD, or you need fine-grained control over the flow.
