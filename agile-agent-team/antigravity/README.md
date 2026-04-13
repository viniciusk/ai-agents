# Google Antigravity Implementation Guide

Build the same agile agent team using **Google Antigravity** — the agent-first IDE.

---

## What is Antigravity?

Google Antigravity (launched November 2025) is an IDE built around autonomous agents. Instead of a chatbot in a sidebar, you dispatch agents that work independently in their own workspaces — each with access to an editor, terminal, and browser.

Key features relevant to this system:
- **Manager View** — Mission Control where you define the goal and dispatch agents
- **Workspaces** — Each agent works in an isolated environment (up to 5 in parallel)
- **Skills** — Markdown files (same format as Claude) that give agents specialized expertise
- **Artifacts** — Structured outputs agents produce that you can review and comment on
- **Multi-model** — Assign different models to different agents (Gemini 3.1 Pro, Claude Sonnet, etc.)
- **MCP support** — Connect to GitHub, Jira, databases, etc.

---

## How the Agile Team Maps to Antigravity

| Agile Agent | Antigravity concept |
|---|---|
| Orchestrator | You, using Manager View + this mission config |
| Product Owner agent | Workspace 1 with product-owner Skill |
| Software Architect agent | Workspace 2 with software-architect Skill |
| QA Engineer agent | Workspace 3 with qa-engineer Skill |
| Full Stack Developer agent | Workspace 4 with full-stack-developer Skill |
| Parallel execution | Workspaces 3 and 4 running simultaneously |

### On "Squads"

In Antigravity's community and documentation, "Squads" is sometimes used informally to describe a pre-configured group of Workspaces + Skills that work together on a domain. It's functionally the same as what Claude calls a "skill team" — a bundle of specialized skills designed to collaborate.

When you save `mission-config.json` (below) as a reusable template, that template is effectively your Squad.

---

## Prerequisites

1. Install Google Antigravity (free public preview at [antigravity.google](https://antigravity.google))
2. Sign in with your Google account
3. Copy the Skills in `antigravity/skills/` to your Antigravity project's `.antigravity/skills/` folder

---

## Setting Up the Skills

Antigravity Skills live in `.antigravity/skills/` in your project root, in the same format as Claude skills (a folder with a `SKILL.md` file):

```bash
your-project/
  .antigravity/
    skills/
      product-owner/
        SKILL.md        ← copy from antigravity/skills/product-owner/SKILL.md
      software-architect/
        SKILL.md
      qa-engineer/
        SKILL.md
      full-stack-developer/
        SKILL.md
```

Skills are loaded by agents automatically when you assign them in the Manager View.

---

## Running the Agile Team in Manager View

### Step 1: Open Manager View

In Antigravity, click the **Manager** tab (top of the interface). This is your mission control.

### Step 2: Define Your Mission

Click **New Mission** and describe your business goal:

```
Add password reset via email to our application.

Users should be able to request a reset link, receive it by email, 
click the link, and set a new password. Links expire after 24 hours.
```

### Step 3: Dispatch Agents in Sequence (Phase 1 & 2)

First, dispatch the PO agent:
1. Click **Add Workspace**
2. Name it: `product-owner`
3. Assign model: Gemini 3.1 Pro (or Claude Sonnet 4.6)
4. Assign skill: `product-owner`
5. Task: *"Read the mission and produce user stories with acceptance criteria. Save artifacts to artifacts/po/"*
6. Click **Dispatch**

Watch the PO agent work in its workspace. When the `po-to-architect.md` handoff appears in the `handoffs/` folder, dispatch the Architect:

1. Click **Add Workspace**
2. Name it: `software-architect`
3. Assign model: Gemini 3.1 Pro High (for complex reasoning)
4. Assign skill: `software-architect`
5. Task: *"Read artifacts/po/ and produce the architecture. Save to artifacts/architect/"*
6. Click **Dispatch**

### Step 4: Dispatch Parallel Phase (Phase 3)

When Architect produces its handoffs, dispatch BOTH simultaneously:

**Workspace 3 (QA Planning):**
- Name: `qa-planning`
- Skill: `qa-engineer`
- Task: *"PLANNING MODE: Write failing tests for all acceptance criteria. Use api-contracts.yaml as ground truth."*

**Workspace 4 (Dev Setup):**
- Name: `dev-setup`
- Skill: `full-stack-developer`
- Task: *"SETUP MODE: Create project structure per ADR. Install dependencies. No implementation code yet."*

This is where Antigravity's parallel execution shines — both workspaces run simultaneously.

### Step 5: Implementation Loop (Phase 4 & 5)

When QA planning is complete, dispatch the Dev agent for implementation:

**Workspace 4 (reuse or new):**
- Task: *"IMPLEMENTATION MODE: Read tests/DEV_HANDOFF.md. Make all failing tests pass. Do not modify test files."*

When Dev completes, dispatch QA verification:

**Workspace 3 (reuse):**
- Task: *"VERIFICATION MODE: Run ./tests/run_tests.sh. Produce sign-off.md if passing, bug-report.md if failing."*

If QA finds bugs: re-dispatch Dev with the bug report as context. Repeat until sign-off.

---

## Using mission-config.json

The `mission-config.json` file in this folder is a reusable template for the mission. Load it in Manager View to pre-configure all four workspaces with the right skills, models, and tasks.

This config is your reusable **Squad** — a saved multi-agent configuration you can invoke for any new feature.

---

## Key Differences vs. Claude Agent SDK

| Aspect | Claude Agent SDK | Google Antigravity |
|---|---|---|
| Orchestration | You write the loop in Python/TS | You manage it in the GUI (or API) |
| Parallel agents | `asyncio.gather()` | Dispatch workspaces simultaneously |
| Visibility | Terminal output | Visual workspace dashboards |
| Artifact review | Read files | View Artifacts panel with comments |
| Feedback | Edit prompts and re-run | Google-Doc-style comments on Artifacts |
| Reproducibility | Code in version control | `mission-config.json` template |
| CI/CD | Native (it's code) | Needs Antigravity API (in preview) |
| Local files | Yes | Yes (via workspace filesystem) |

**When to use Antigravity:** You want visual oversight, interactive feedback on artifacts, and you don't need to embed this in a CI/CD pipeline.

**When to use Claude Agent SDK:** You want programmable, reproducible orchestration that runs in CI/CD, or you need fine-grained control over the flow.
