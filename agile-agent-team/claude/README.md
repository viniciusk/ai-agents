# Claude Implementation Guide

Build the agile agent team using the **Claude Agent SDK** and **Skills**.

---

## How It Works

Skills define each agent's persona and rules. The orchestrator (Python or TypeScript) loads those skills and runs agents in the right order, passing artifacts between them.

```
orchestrator.py
  │
  ├── loads skills/product-owner/SKILL.md → runs PO agent
  ├── loads skills/software-architect/SKILL.md → runs Architect agent
  ├── loads skills/qa-engineer/SKILL.md → runs QA agent (planning mode)
  ├── loads skills/full-stack-developer/SKILL.md → runs Dev agent (setup + impl)
  └── loads skills/qa-engineer/SKILL.md → runs QA agent (verification mode)
```

---

## Prerequisites

```bash
# Python 3.11+
pip install claude-agent-sdk

# Set your API key
export ANTHROPIC_API_KEY=your-api-key-here
```

---

## Running the System

```bash
# Basic usage
python orchestrator.py "Add password reset via email"

# More complex goal
python orchestrator.py "Add a shopping cart feature: users can add items, 
  update quantities, and proceed to checkout"
```

The orchestrator creates a timestamped mission folder under `sessions/`:

```
sessions/
  mission-20260413-142301/
    mission.md
    artifacts/
      po/            ← PO agent outputs
      architect/     ← Architect outputs
      qa/            ← QA outputs (test plan, results, sign-off)
      dev/           ← Dev outputs (notes)
    handoffs/        ← Agent-to-agent handoff artifacts
    tests/           ← Failing tests (written by QA, executed by Dev)
    src/             ← Implementation (written by Dev)
```

---

## Skills: The Core of Each Agent

A Skill is a Markdown file (`SKILL.md`) that becomes the agent's **system prompt** — its identity, rules, and instructions. The orchestrator reads the skill file and passes it to Claude via the `system_prompt` option.

### How Skills Work

```python
skill_content = Path("skills/product-owner/SKILL.md").read_text()

async for message in query(
    prompt="Analyze this business goal and write user stories...",
    options=ClaudeAgentOptions(
        system_prompt=skill_content,  # ← The SKILL.md becomes the system prompt
        allowed_tools=["Read", "Write", "AskUserQuestion"],
    )
):
    ...
```

### Customizing Skills

Each `SKILL.md` is just a text file — edit it to change agent behavior:

- **Add domain expertise:** "You specialize in financial services applications. Always consider regulatory compliance..."
- **Change output format:** Modify the artifact templates to use your team's standards
- **Add constraints:** "This project uses FastAPI for backend and React for frontend"
- **Add company context:** "Our database schema is documented at docs/schema.md"

---

## Using the Agent SDK: Key Patterns

### Pattern 1: Sequential Agents

```python
# Run PO, then pass output to Architect
po_result = await run_agent("product-owner", po_prompt, mission_dir)
arch_result = await run_agent("software-architect", arch_prompt, mission_dir)
```

### Pattern 2: Parallel Agents

```python
# QA planning and Dev setup run simultaneously
import asyncio
await asyncio.gather(
    run_qa_planning(mission_dir),
    run_dev_setup(mission_dir),
)
```

### Pattern 3: Conditional Loops

```python
for cycle in range(MAX_CYCLES):
    await run_agent(...)
    status = read_handoff_status(mission_dir, "handoff.md")
    if status == "READY":
        break
    # else: loop back with feedback
```

### Pattern 4: Named Subagents (Alternative Approach)

Instead of running separate processes, you can define all agents as subagents
of a single orchestrator agent:

```python
async for message in query(
    prompt="Orchestrate the agile team to build: [goal]",
    options=ClaudeAgentOptions(
        allowed_tools=["Read", "Write", "Agent"],  # Agent = spawn subagent
        agents={
            "product-owner": AgentDefinition(
                description="Writes user stories from business goals",
                prompt=load_skill("product-owner"),
                tools=["Read", "Write", "AskUserQuestion"],
            ),
            "software-architect": AgentDefinition(
                description="Designs technical architecture",
                prompt=load_skill("software-architect"),
                tools=["Read", "Write"],
            ),
            # ... etc
        },
    )
):
    ...
```

This approach lets Claude handle the orchestration logic itself. The tradeoff:
less control over the flow (Claude decides when to spawn agents) but less code.

---

## Extending the System

### Add a New Agent Role

1. Create `skills/your-role/SKILL.md` with the persona and rules
2. Add a `run_your_role()` function to `orchestrator.py`
3. Call it at the right point in the `orchestrate()` function

### Add a New Artifact Type

Define the artifact in the relevant SKILL.md (what it contains, what format it uses), then reference it in the downstream agent's skill (what to read and how to interpret it).

### Use a Different Model Per Agent

```python
options=ClaudeAgentOptions(
    model="claude-haiku-4-5-20251001",  # Cheaper model for simpler tasks
    ...
)
```

Consider: PO and Architect benefit most from the strongest model (Opus/Sonnet).
QA planning can use Sonnet. Dev implementation can use Sonnet. QA verification
can use Haiku (just running tests and reading output).

### Add MCP Integrations

```python
options=ClaudeAgentOptions(
    mcp_servers={
        "github": {"command": "npx", "args": ["@github/mcp-server"]},
        "jira": {"command": "npx", "args": ["@atlassian/jira-mcp"]},
    },
    ...
)
```

This lets agents create GitHub issues, update Jira tickets, open PRs, etc.

---

## Troubleshooting

**Agent doesn't write files to the right place:**
Make sure `cwd=str(mission_dir)` is set in ClaudeAgentOptions. The agent uses relative paths — the working directory determines where they land.

**Handoff parsing fails:**
Check that the agent is following the handoff format exactly as specified in SKILL.md. If you modify the format, update the `read_handoff_status()` function in orchestrator.py accordingly.

**Agent ignores skill instructions:**
The system_prompt parameter sets the persona. If the agent isn't following it, the task prompt may be overriding it. Keep task prompts focused on *what* to do and context — let the skill handle *how* to behave.

**Loop runs too many times:**
Increase `MAX_PO_ARCHITECT_CYCLES` or `MAX_QA_DEV_CYCLES` for complex features. Or look at the artifacts to understand what's blocking progress.
