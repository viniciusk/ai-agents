# animist.solutions.ai-agents

A collection of multi-agent development team skeletons, configurations, and workflows designed to be copied into new projects and adapted for AI-driven development.

## Included Agent Teams

- **[`laravel-fullstack-team`](./laravel-fullstack-team)**: A structured multi-agent team tailored for Laravel 12, Inertia v3, and Vue 3 feature work. It features a strict 6-phase workflow (from backlog generation to implementation and automated test verification), drift reviews, and an integrated LLM token quota estimator.
- **[`agile-agent-team`](./agile-agent-team)**: An agile-focused AI agent team structure.

## Core Philosophy

These directories aren't just collections of prompts. They enforce structured, phase-based workflows where AI agents produce predictable, strictly formatted artifacts (contracts, templates, and logs) rather than freeform prose.

Inside each team folder, you'll generally find:

- Pre-defined agent **skills** dictating their responsibilities and system boundaries.
- **Workflows** that orchestrate handoffs and user-approval gates between different agents.
- **State management** scripts and rules to persist the agents' memory and context across sessions.
