---
trigger: always_on
---

# Rule: Knowledge Management

## Context

Agents in this workspace are part of a long-running software development lifecycle. Cross-session architectural knowledge and domain terminology must be persisted in a way that is easily accessible to both humans and AI agents. This information lives in the `docs/` folder, which is committed to version control.

## Mandatory Actions

1. **Architectural Decisions:** Every time an architectural or logic choice is made that will outlive the current mission (cross-cutting conventions, stack-level choices, persisted data shapes), append an entry to `docs/architecture/decisions.md`.
2. **Domain Terminology:** If a new core domain concept or term is introduced, add it to `docs/glossary.md` to ensure ubiquitous language.
3. **Reference Before Acting:** Before designing new features or making architectural decisions, read `docs/architecture/decisions.md` and `docs/glossary.md` to ensure consistency with existing patterns.
