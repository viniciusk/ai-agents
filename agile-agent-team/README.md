# Agile Agent Team — Skeleton & Learning Guide

> Build a team of AI agents that collaborates like a real software development squad.

---

## What You're Building

An **autonomous multi-agent system** where you provide a business goal (e.g., "Add OAuth login") and a team of specialized AI agents collaborates to plan, design, test, and implement it — mirroring how a real agile team works.

```
You (Business Goal)
        │
        ▼
┌───────────────────┐
│   Product Owner   │  ← Understands the "why", writes user stories
└────────┬──────────┘
         │ User Stories + Acceptance Criteria
         ▼
┌───────────────────┐
│ Software Architect│  ← Defines the "how", designs for scale & resilience
└────────┬──────────┘
         │ Architecture Decision Records (ADRs) + Task Breakdown
         ▼
┌──────────┐  ┌──────────┐
│  QA Agent│  │Full Stack│  ← QA writes tests FIRST (TDD), then Dev implements
│  (Tests) │  │Developer │
└────┬─────┘  └────┬─────┘
     │              │
     └──────┬───────┘
            ▼
     All agents review
     Artifacts + Handoff
```

---

## Project Structure

```
agile-agent-team/
├── README.md                           ← You are here
├── concepts/
│   ├── 00-architecture-overview.md    ← Mental model: how agents think and collaborate
│   ├── 01-agent-roles.md              ← Detailed role definitions and responsibilities
│   ├── 02-collaboration-flow.md       ← The handoff protocol between agents
│   └── 03-tdd-workflow.md             ← QA-first TDD pattern in agentic systems
├── claude/
│   ├── README.md                       ← Claude implementation walkthrough
│   ├── skills/
│   │   ├── product-owner/SKILL.md     ← PO agent skill (Claude format)
│   │   ├── software-architect/SKILL.md
│   │   ├── full-stack-developer/SKILL.md
│   │   └── qa-engineer/SKILL.md
│   ├── orchestrator.py                ← Python orchestration (Claude Agent SDK)
│   └── orchestrator.ts                ← TypeScript orchestration (Claude Agent SDK)
└── antigravity/
    ├── README.md                       ← Google Antigravity implementation walkthrough
    ├── mission-config.json             ← Squad blueprint (reference / sync target)
    └── .agent/                         ← Antigravity workspace config (required path)
        ├── agents.md                   ← Agent catalog (human reference)
        ├── skills/
        │   ├── po/SKILL.md             ← PO agent skill
        │   ├── architect/SKILL.md
        │   ├── developer/SKILL.md
        │   └── qa/SKILL.md
        └── workflows/
            ├── full-mission.md         ← /mission slash command
            └── fix.md                  ← /fix slash command
```

Per-mission outputs are written to `.agent-missions/mission-{timestamp}/` (created by Step 0 of the `/mission` workflow) — never inside `.agent/` itself.

---

## Start Here

**If you're new to multi-agent systems**, read the concepts in order:
1. `concepts/00-architecture-overview.md` — understand the mental model
2. `concepts/01-agent-roles.md` — learn what each agent does
3. `concepts/02-collaboration-flow.md` — understand how agents hand off work
4. `concepts/03-tdd-workflow.md` — understand QA-first development

**Then pick your platform:**
- `claude/README.md` — build with Claude Agent SDK + Skills
- `antigravity/README.md` — build with Google Antigravity + Skills

---

## Key Concepts You'll Learn

| Concept | What it means |
|---|---|
| **Orchestrator** | The "manager" agent that assigns work to specialists |
| **Subagents** | Specialist agents (PO, Architect, Dev, QA) that do focused work |
| **Skills** | Markdown files that give an agent its persona, rules, and expertise |
| **Artifacts** | Structured outputs agents produce (user stories, ADRs, tests, code) |
| **Handoff Protocol** | The structured format agents use to pass work to each other |
| **TDD Loop** | QA writes tests → Dev implements → QA verifies → repeat |

---

## Platform Comparison

| Feature | Claude Agent SDK | Google Antigravity |
|---|---|---|
| Skills format | Markdown (`SKILL.md`) | Markdown (`SKILL.md`) |
| Agent definition | `AgentDefinition` in code | Workspace + Skill config |
| Parallel agents | Via `Agent` tool | Up to 5 parallel workspaces |
| Orchestration | Python/TypeScript SDK | Manager View (GUI + API) |
| IDE integration | Works with any editor | Built-in IDE (like Cursor) |
| Model | Claude (all variants) | Gemini, Claude, GPT-OSS |
| MCP support | Yes | Yes (since early 2026) |
| Artifacts | Text/file outputs | Structured visual Artifacts |
