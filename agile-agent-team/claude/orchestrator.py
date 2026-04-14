"""
Agile Agent Team Orchestrator — Claude Agent SDK
=================================================

This orchestrator coordinates four specialized agents (Product Owner,
Software Architect, QA Engineer, Full Stack Developer) to take a business
goal through planning, design, TDD, implementation, and verification.

Prerequisites:
  pip install claude-agent-sdk

Usage:
  # Run from inside your actual project folder:
  python /path/to/agile-agent-team/claude/orchestrator.py "Add password reset via email"

  # Or with an explicit project path from anywhere:
  python orchestrator.py "Add password reset" --project-path /path/to/your/project

  # Force a full project re-scan (refreshes project.config.md):
  python orchestrator.py "Add password reset" --refresh-context

Env vars required:
  ANTHROPIC_API_KEY=your-api-key

Project context strategy:
  - On first run: scans the project and writes project.config.md (one-time cost)
  - On subsequent runs: reads project.config.md instantly (no scan)
  - After each mission: appends a small changelog entry (incremental update)
  - Use --refresh-context to force a full re-scan when the project changes significantly
"""

import argparse
import asyncio
import sys
from datetime import datetime
from pathlib import Path
from claude_agent_sdk import query, ClaudeAgentOptions


# ─────────────────────────────────────────────
# Configuration
# ─────────────────────────────────────────────

MAX_PO_ARCHITECT_CYCLES = 3     # Max times Architect can push back to PO
MAX_QA_DEV_CYCLES = 5           # Max times QA can send bugs back to Dev

# Model assignments per role.
#
# The guiding principle: match model capability to the cost of a mistake.
#
#   Opus   → Software Architect. Architecture decisions are the most expensive
#             mistakes in the pipeline — a bad ADR poisons every downstream agent.
#             Opus's deeper reasoning is worth the cost here.
#
#   Sonnet → Product Owner, QA Planning, Developer, Context Discovery.
#             Strong comprehension and judgment needed, but not pure abstract
#             reasoning. Sonnet handles story writing, test design, code generation,
#             and codebase analysis very well at a fraction of Opus cost.
#
#   Haiku  → Dev Setup, QA Verification. Mechanical tasks: create directory
#             structure, run a test command and read the output. No complex
#             reasoning required — Haiku is faster and much cheaper here.
#
# To tune: change any value below. The model string is passed directly to the
# Claude Agent SDK. No other code changes needed.

MODEL_CONFIG = {
    # One-time project scan — accuracy matters more than speed, runs rarely
    "context-discovery":  "claude-sonnet-4-6",

    # Planning phase — high quality reasoning throughout
    "product-owner":      "claude-sonnet-4-6",
    "software-architect": "claude-opus-4-6",    # Most critical — Opus justified
    "qa-planning":        "claude-sonnet-4-6",

    # Implementation phase — mechanical setup, strong code gen, mechanical verify
    "dev-setup":          "claude-haiku-4-5-20251001",
    "developer":          "claude-sonnet-4-6",
    "qa-verification":    "claude-haiku-4-5-20251001",
}

# The context file lives in the project root — created once, updated incrementally
PROJECT_CONFIG_FILENAME = "project.config.md"

# Path to skill files — relative to this orchestrator script
SKILLS_DIR = Path(__file__).parent / "skills"


# ─────────────────────────────────────────────
# Helper: Load skill prompt from SKILL.md
# ─────────────────────────────────────────────

def load_skill(skill_name: str) -> str:
    """Load a skill's SKILL.md content to use as system prompt."""
    skill_path = SKILLS_DIR / skill_name / "SKILL.md"
    if not skill_path.exists():
        raise FileNotFoundError(f"Skill not found: {skill_path}")
    return skill_path.read_text()


# ─────────────────────────────────────────────
# Project Context: lazy init + incremental update
# ─────────────────────────────────────────────

async def get_project_context(project_path: Path, force_refresh: bool = False) -> str:
    """
    Load or create project.config.md.

    Strategy:
      - If config exists and force_refresh=False → read and return it instantly.
      - If config doesn't exist (or force_refresh=True) → run a discovery agent,
        write the result to project.config.md, and return it.

    This means the expensive scan runs exactly once per project (or on demand).
    """

    config_path = project_path / PROJECT_CONFIG_FILENAME

    if config_path.exists() and not force_refresh:
        print(f"📖 Reading existing project context from {PROJECT_CONFIG_FILENAME}")
        return config_path.read_text()

    action = "Refreshing" if force_refresh else "Creating"
    print(f"🔍 {action} project context — scanning codebase (one-time cost)...")

    context = await run_context_discovery(project_path)

    config_path.write_text(context)
    print(f"✅ Project context saved to {config_path}")
    print(f"   Future runs will read this file directly — no re-scan needed.")

    return context


async def run_context_discovery(project_path: Path) -> str:
    """
    Run a discovery agent to scan the project and produce project.config.md.

    Uses Sonnet (not Haiku) because accuracy matters here — this file is the
    foundation every subsequent agent builds on. A misread convention or missed
    pattern will propagate into every mission until the file is refreshed.
    Token cost: one-time per project (or on --refresh-context).
    """

    prompt = f"""
Scan the project at: {project_path}

Your job: produce a project.config.md that future AI agents can read to
immediately understand this codebase WITHOUT scanning it themselves.

Read the following (use Glob and Read tools):
  - README files (README.md, docs/*.md)
  - Any existing CLAUDE.md or .claude/ files
  - Package/dependency files (package.json, requirements.txt, pyproject.toml,
    go.mod, Cargo.toml, pom.xml, build.gradle, composer.json — whatever exists)
  - A sample of source files to understand patterns (read 2-3 files per
    major folder, don't read every file)
  - Test files (to understand the testing setup)
  - Config files (.env.example, docker-compose.yml, etc.)

Produce a file with this exact structure:

---
# Project Context
_Generated: {datetime.now().strftime("%Y-%m-%d %H:%M")} | Run with --refresh-context to regenerate_

## Tech Stack
[Languages, frameworks, major libraries — be specific with versions if visible]

## Project Structure
[Key directories and what they contain — 1 line each, only the important ones]

## Conventions & Patterns
[How this codebase does things: naming conventions, error handling approach,
logging, config management, authentication patterns — whatever is observable]

## Testing Setup
- Framework: [e.g., pytest, Jest, RSpec]
- Test location: [e.g., tests/, __tests__/, spec/]
- Run command: [e.g., pytest, npm test, bundle exec rspec]
- Coverage command: [if available]

## How to Run the Project
[Dev server command, build command, any required env vars]

## Recent Changes
_This section is updated automatically after each agent mission._
[Empty on first creation]
---

Write the file to: {project_path / PROJECT_CONFIG_FILENAME}
Then output a one-line summary of what you found (for the log).
"""

    result_text = ""
    async for message in query(
        prompt=prompt,
        options=ClaudeAgentOptions(
            model=MODEL_CONFIG["context-discovery"],
            allowed_tools=["Read", "Glob", "Grep"],   # Read-only — no side effects
            permission_mode="acceptEdits",
        )
    ):
        if hasattr(message, "result"):
            result_text = message.result

    # Read back the written file (agent wrote it directly to project_path)
    config_path = project_path / PROJECT_CONFIG_FILENAME
    if config_path.exists():
        return config_path.read_text()

    # Fallback: use whatever the agent returned as text
    return result_text or "# Project Context\n[Discovery failed — add context manually]\n"


async def update_project_context(project_path: Path, mission_summary: str) -> None:
    """
    After a mission completes, append a small changelog entry to project.config.md.

    This is intentionally lightweight — no re-scanning, no agent involved.
    Just a structured append that keeps the config current over time.
    """

    config_path = project_path / PROJECT_CONFIG_FILENAME
    if not config_path.exists():
        return  # Nothing to update

    entry = (
        f"\n### {datetime.now().strftime('%Y-%m-%d')} — {mission_summary}\n"
    )

    content = config_path.read_text()

    # Append the entry under the "## Recent Changes" section
    if "## Recent Changes" in content:
        content = content.replace(
            "## Recent Changes",
            f"## Recent Changes{entry}",
            1  # Replace only the first occurrence
        )
    else:
        content += f"\n## Recent Changes{entry}"

    config_path.write_text(content)
    print(f"📝 Project context updated with mission summary.")


# ─────────────────────────────────────────────
# Helper: Set up mission folder
# ─────────────────────────────────────────────

def create_mission_folder(project_path: Path, business_goal: str) -> Path:
    """Create a timestamped folder inside the project for this mission's artifacts."""

    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    mission_id = f"mission-{timestamp}"

    # Missions live inside the project, in a .agent-missions/ folder
    # (add this to .gitignore if you don't want to commit mission artifacts)
    mission_dir = project_path / ".agent-missions" / mission_id

    for subdir in ["artifacts/po", "artifacts/architect", "artifacts/qa",
                   "artifacts/dev", "handoffs", "tests"]:
        (mission_dir / subdir).mkdir(parents=True, exist_ok=True)

    (mission_dir / "mission.md").write_text(
        f"# Mission: {mission_id}\n\n"
        f"**Started:** {datetime.now().isoformat()}\n"
        f"**Project:** {project_path}\n"
        f"**Business Goal:**\n\n{business_goal}\n"
    )

    print(f"\n📁 Mission folder: {mission_dir}")
    return mission_dir


# ─────────────────────────────────────────────
# Helper: Run an agent with project context injected
# ─────────────────────────────────────────────

async def run_agent(role: str, prompt: str, mission_dir: Path,
                    project_context: str,
                    model_key: str | None = None,
                    allowed_tools: list[str] | None = None) -> str:
    """
    Run a single specialized agent.

    Args:
        role:          Skill name to load (e.g. "qa-engineer"). Controls persona.
        model_key:     Key into MODEL_CONFIG (e.g. "qa-verification"). Controls
                       which model is used. Defaults to `role` if not provided,
                       so callers only need to specify it when the same skill is
                       used in multiple modes with different model requirements
                       (e.g. QA planning vs QA verification, Dev setup vs Dev impl).
        project_context: Injected into every prompt — no per-agent re-scanning.
    """

    system_prompt = load_skill(role)
    tools = allowed_tools or ["Read", "Write", "Edit", "Bash", "Glob", "Grep",
                               "AskUserQuestion"]

    # model_key lets callers pick the right MODEL_CONFIG entry when the same
    # skill is used in different modes (e.g. "dev-setup" vs "developer").
    # Falls back to role name, then to Sonnet if neither is in MODEL_CONFIG.
    lookup_key = model_key or role
    model = MODEL_CONFIG.get(lookup_key, "claude-sonnet-4-6")

    # Inject project context as a preamble — agents read this before their task
    full_prompt = f"""
PROJECT CONTEXT (from project.config.md — read-only reference):
{project_context}

─────────────────────────────────────────────────────────────
YOUR TASK:
{prompt}
"""

    label = role.replace('-', ' ').title()
    mode_label = f" ({model_key})" if model_key and model_key != role else ""
    print(f"\n{'='*60}")
    print(f"🤖 Agent: {label}{mode_label}  [{model}]")
    print(f"{'='*60}")

    result_text = ""
    async for message in query(
        prompt=full_prompt,
        options=ClaudeAgentOptions(
            model=model,
            system_prompt=system_prompt,
            allowed_tools=tools,
            cwd=str(mission_dir),
            permission_mode="acceptEdits",
        )
    ):
        if hasattr(message, "content"):
            for block in message.content:
                if hasattr(block, "text"):
                    print(block.text, end="", flush=True)
        if hasattr(message, "result"):
            result_text = message.result

    return result_text


# ─────────────────────────────────────────────
# Helper: Parse handoff status
# ─────────────────────────────────────────────

def read_handoff_status(mission_dir: Path, handoff_filename: str) -> str:
    """Read the STATUS field from a handoff artifact."""
    handoff_path = mission_dir / "handoffs" / handoff_filename
    if not handoff_path.exists():
        return "MISSING"
    content = handoff_path.read_text()
    for line in content.splitlines():
        if line.strip().startswith("STATUS:"):
            return line.split(":", 1)[1].strip().split()[0]
    return "UNKNOWN"


# ─────────────────────────────────────────────
# Phase runners (context-aware)
# ─────────────────────────────────────────────

async def run_product_owner(mission_dir: Path, project_context: str,
                             architect_feedback: str = "") -> str:
    mission_brief = (mission_dir / "mission.md").read_text()
    feedback_block = f"ARCHITECT FEEDBACK (respond to these before proceeding):\n{architect_feedback}" if architect_feedback else ""
    # Explicit absolute paths — prevents agents writing to project root
    po_dir       = mission_dir / "artifacts" / "po"
    handoffs_dir = mission_dir / "handoffs"
    prompt = f"""
MISSION BRIEF:
{mission_brief}

{feedback_block}

Follow your skill instructions:
1. Analyze the business goal in the context of the existing project
2. Surface any ambiguities (use AskUserQuestion if needed)
3. Write user stories and acceptance criteria
4. Save ALL artifacts to: {po_dir}/
   - {po_dir}/user-stories.md
   - {po_dir}/acceptance-criteria.md
   - {po_dir}/out-of-scope.md
5. Save handoff to: {handoffs_dir}/po-to-architect.md
"""
    return await run_agent("product-owner", prompt, mission_dir, project_context)


async def run_architect(mission_dir: Path, project_context: str) -> str:
    po_dir        = mission_dir / "artifacts" / "po"
    arch_dir      = mission_dir / "artifacts" / "architect"
    handoffs_dir  = mission_dir / "handoffs"
    prompt = f"""
Read these files:
  - {po_dir}/user-stories.md
  - {po_dir}/acceptance-criteria.md
  - {po_dir}/out-of-scope.md
  - {handoffs_dir}/po-to-architect.md

The PROJECT CONTEXT above tells you the existing tech stack and patterns.
Design your architecture to fit the existing project — don't introduce
new frameworks or patterns unless the existing ones are insufficient.

Follow your skill instructions:
1. Review PO artifacts for technical feasibility
2. If unclear: write {handoffs_dir}/architect-blocks-po.md with STATUS: BLOCKED, then stop
3. If sound: produce architecture fitting the existing codebase
4. Save ALL artifacts to: {arch_dir}/
   - {arch_dir}/architecture-decision-record.md
   - {arch_dir}/task-breakdown.md
   - {arch_dir}/api-contracts.yaml
   - {arch_dir}/non-functional-requirements.md
5. Save handoffs to:
   - {handoffs_dir}/architect-to-qa.md
   - {handoffs_dir}/architect-to-dev.md
"""
    return await run_agent("software-architect", prompt, mission_dir, project_context)


async def run_qa_planning(mission_dir: Path, project_context: str) -> str:
    po_dir       = mission_dir / "artifacts" / "po"
    arch_dir     = mission_dir / "artifacts" / "architect"
    qa_dir       = mission_dir / "artifacts" / "qa"
    tests_dir    = mission_dir / "tests"
    handoffs_dir = mission_dir / "handoffs"
    prompt = f"""
You are in PLANNING MODE.

The PROJECT CONTEXT above tells you the testing framework already in use.
Use the same framework — don't introduce a new test runner.

Read these files:
  - {po_dir}/acceptance-criteria.md
  - {arch_dir}/architecture-decision-record.md
  - {arch_dir}/api-contracts.yaml
  - {arch_dir}/task-breakdown.md
  - {handoffs_dir}/architect-to-qa.md

Follow your skill instructions:
1. Write failing tests using the project's existing test framework
2. Save tests to:
   - {tests_dir}/unit/
   - {tests_dir}/integration/
   - {tests_dir}/e2e/
3. Create {tests_dir}/run_tests.sh  (single command to run all tests)
4. Create {tests_dir}/DEV_HANDOFF.md  (setup and ordering instructions for Dev)
5. Save test plan to: {qa_dir}/test-plan.md
6. Save handoff to: {handoffs_dir}/qa-to-dev.md
"""
    return await run_agent("qa-engineer", prompt, mission_dir, project_context,
                           model_key="qa-planning")


async def run_dev_setup(mission_dir: Path, project_context: str) -> str:
    arch_dir     = mission_dir / "artifacts" / "architect"
    handoffs_dir = mission_dir / "handoffs"
    prompt = f"""
You are in SETUP MODE. Create the project structure per the architecture.
Do NOT write implementation code yet.

The PROJECT CONTEXT above shows the existing project structure.
New source files should follow the same conventions and live in the correct
locations WITHIN THE ACTUAL PROJECT (not inside the mission folder).

Read these files:
  - {arch_dir}/architecture-decision-record.md
  - {arch_dir}/task-breakdown.md
  - {handoffs_dir}/architect-to-dev.md

Then:
1. Create placeholder source files in the project (matching existing structure)
2. Install any new dependencies into the project's existing dependency file
3. Verify no dependency conflicts
4. Save handoff to: {handoffs_dir}/dev-setup-complete.md
"""
    return await run_agent("full-stack-developer", prompt, mission_dir, project_context,
                           model_key="dev-setup")


async def run_developer(mission_dir: Path, project_context: str,
                         bug_report: str = "") -> str:
    arch_dir     = mission_dir / "artifacts" / "architect"
    dev_dir      = mission_dir / "artifacts" / "dev"
    tests_dir    = mission_dir / "tests"
    handoffs_dir = mission_dir / "handoffs"
    bug_block    = f"BUG REPORT FROM QA (fix these before anything else):\n{bug_report}" if bug_report else ""
    prompt = f"""
You are in IMPLEMENTATION MODE. Make all failing tests pass.

The PROJECT CONTEXT above shows conventions to follow (naming, error handling,
logging, etc.) — match the existing codebase style.

Read these files first:
  - {tests_dir}/DEV_HANDOFF.md  (setup and ordering instructions from QA)
  - {arch_dir}/task-breakdown.md
  - {arch_dir}/architecture-decision-record.md

{bug_block}

Then:
1. Verify tests are failing: run {tests_dir}/run_tests.sh
2. Implement tasks in order per the task breakdown
3. Run tests after each task to verify progress
4. When all tests pass, write: {dev_dir}/implementation-notes.md
5. Save handoff to: {handoffs_dir}/dev-to-qa.md
"""
    return await run_agent("full-stack-developer", prompt, mission_dir, project_context,
                           model_key="developer")


async def run_qa_verification(mission_dir: Path, project_context: str) -> str:
    dev_dir      = mission_dir / "artifacts" / "dev"
    qa_dir       = mission_dir / "artifacts" / "qa"
    tests_dir    = mission_dir / "tests"
    handoffs_dir = mission_dir / "handoffs"
    prompt = f"""
You are in VERIFICATION MODE.

Read these files:
  - {handoffs_dir}/dev-to-qa.md
  - {dev_dir}/implementation-notes.md

Then:
1. Run the test suite: {tests_dir}/run_tests.sh  (capture full output)
2. If ALL tests pass:
   - Save {qa_dir}/test-results.md
   - Save {qa_dir}/sign-off.md
   - Save {handoffs_dir}/qa-signoff.md  with STATUS: COMPLETE
3. If any tests fail:
   - Save {qa_dir}/test-results.md
   - Save {qa_dir}/bug-report.md  (actionable, per your skill instructions)
   - Save {handoffs_dir}/qa-to-dev-cycle.md  with STATUS: BLOCKED
"""
    return await run_agent("qa-engineer", prompt, mission_dir, project_context,
                           model_key="qa-verification")


# ─────────────────────────────────────────────
# Main Orchestration Loop
# ─────────────────────────────────────────────

def detect_resume_phase(mission_dir: Path) -> str:
    """
    Inspect an existing mission folder and return the name of the first
    incomplete phase. Used by --resume-mission to skip work already done.

    Phase completion is detected by the presence of the handoff each phase
    produces — if the handoff exists, that phase finished successfully.
    """
    handoffs = mission_dir / "handoffs"

    if not (handoffs / "po-to-architect.md").exists():
        return "po"
    if not (handoffs / "architect-to-qa.md").exists():
        return "architect"
    qa_done  = (handoffs / "qa-to-dev.md").exists()
    dev_done = (handoffs / "dev-setup-complete.md").exists()
    if not qa_done or not dev_done:
        return "parallel"
    if not (handoffs / "dev-to-qa.md").exists():
        return "developer"
    if not (handoffs / "qa-signoff.md").exists():
        return "qa-verification"
    return "complete"


async def orchestrate(business_goal: str, project_path: Path,
                      force_refresh: bool = False,
                      resume_mission: Path | None = None):
    """
    Main orchestration function.

    Pass resume_mission=<path> to continue a run that was interrupted
    (e.g. by a credit limit hit). Completed phases are detected from
    their handoff files and skipped automatically.
    """

    # ── Resume or fresh start ────────────────────────────────────────
    if resume_mission:
        mission_dir = resume_mission.resolve()
        if not mission_dir.exists():
            print(f"❌ Mission folder not found: {mission_dir}")
            return
        resume_from = detect_resume_phase(mission_dir)
        if resume_from == "complete":
            print(f"✅ Mission already complete: {mission_dir}")
            return
        print(f"\n🔄 Resuming mission: {mission_dir.name}")
        print(f"📂 Project: {project_path}")
        print(f"⏩ Skipping to phase: {resume_from}\n")
        # Read the goal from the mission brief so we don't need --goal-file again
        mission_md = mission_dir / "mission.md"
        if not business_goal and mission_md.exists():
            business_goal = mission_md.read_text()
    else:
        resume_from = "po"
        print(f"\n🚀 Agile Agent Team")
        print(f"📋 Goal: {business_goal[:80]}{'...' if len(business_goal) > 80 else ''}")
        print(f"📂 Project: {project_path}\n")
        mission_dir = create_mission_folder(project_path, business_goal)

    # ── Load project context (cached after first run) ────────────────
    project_context = await get_project_context(project_path, force_refresh)

    # ── Phase 1 + 2: PO → Architect loop ────────────────────────────
    architect_feedback = ""
    for cycle in range(MAX_PO_ARCHITECT_CYCLES):

        if resume_from == "po":
            print(f"\n📌 Phase 1: Product Owner (cycle {cycle + 1})")
            print()  # blank line before agent work
            await run_product_owner(mission_dir, project_context, architect_feedback)
        else:
            print(f"\n⏩ Phase 1: Product Owner — skipped (already complete)")

        print()  # blank line between phases
        if resume_from in ("po", "architect"):
            print(f"📌 Phase 2: Software Architect (cycle {cycle + 1})")
            print()  # blank line before agent work
            await run_architect(mission_dir, project_context)
            resume_from = "po"  # re-enable both phases on subsequent cycles
        else:
            print(f"⏩ Phase 2: Software Architect — skipped (already complete)")

        print()  # blank line before status check
        status = read_handoff_status(mission_dir, "architect-blocks-po.md")
        if status == "BLOCKED":
            print(f"⚠️  Architect needs PO clarification — cycling back...")
            architect_feedback = (
                mission_dir / "handoffs" / "architect-blocks-po.md"
            ).read_text()
            resume_from = "po"
        else:
            print(f"✅ Architecture approved.")
            break
    else:
        print(f"\n❌ Max PO-Architect cycles reached.")
        print(f"   Review: {mission_dir}/handoffs/architect-blocks-po.md")
        return

    # ── Phase 3: Parallel — QA Planning + Dev Setup ──────────────────
    print()  # blank line before Phase 3
    handoffs = mission_dir / "handoffs"
    qa_done  = (handoffs / "qa-to-dev.md").exists()
    dev_done = (handoffs / "dev-setup-complete.md").exists()

    if qa_done and dev_done:
        print(f"⏩ Phase 3: QA Planning + Dev Setup — skipped (already complete)")
    else:
        tasks = []
        if not qa_done:
            tasks.append(run_qa_planning(mission_dir, project_context))
        else:
            print(f"⏩ Phase 3a: QA Planning — skipped")
        if not dev_done:
            tasks.append(run_dev_setup(mission_dir, project_context))
        else:
            print(f"⏩ Phase 3b: Dev Setup — skipped")

        if tasks:
            print()  # blank line before parallel execution
            print(f"📌 Phase 3: Running {len(tasks)} remaining task(s) in parallel")
            print()  # blank line before agent work
            await asyncio.gather(*tasks)
        print(f"\n✅ Tests written. Project structure ready.")

    # ── Phase 4 + 5: Dev → QA loop ───────────────────────────────────
    print()  # blank line before Phase 4
    bug_report = ""
    # Check for an existing bug report if resuming mid-cycle
    existing_bug = mission_dir / "artifacts" / "qa" / "bug-report.md"
    if existing_bug.exists():
        bug_report = existing_bug.read_text()

    for cycle in range(MAX_QA_DEV_CYCLES):
        dev_handoff = handoffs / "dev-to-qa.md"

        if resume_from == "qa-verification" and dev_handoff.exists():
            print(f"⏩ Phase 4: Implementation — skipped (already complete)")
            resume_from = "done"  # don't skip again on next cycle
        else:
            print(f"📌 Phase 4: Implementation (cycle {cycle + 1})")
            print()  # blank line before agent work
            await run_developer(mission_dir, project_context, bug_report)

        print()  # blank line between phases
        print(f"📌 Phase 5: QA Verification (cycle {cycle + 1})")
        print()  # blank line before agent work
        await run_qa_verification(mission_dir, project_context)

        print()  # blank line before result check
        status = read_handoff_status(mission_dir, "qa-signoff.md")
        if status == "COMPLETE":
            print(f"🎉 QA SIGN-OFF! Feature complete.")
            break

        print(f"\n⚠️  QA found issues — sending to Dev for fixes...")
        bug_path = mission_dir / "artifacts" / "qa" / "bug-report.md"
        if bug_path.exists():
            bug_report = bug_path.read_text()
    else:
        print(f"\n❌ Max Dev-QA cycles reached.")
        print(f"   Review: {mission_dir}/artifacts/qa/bug-report.md")
        return

    # ── Update project context with what was built ───────────────────
    await update_project_context(project_path, business_goal)

    # ── Mission Complete ─────────────────────────────────────────────
    print(f"\n{'='*60}")
    print(f"✅ MISSION COMPLETE")
    print(f"{'='*60}")
    print(f"📁 Artifacts:  {mission_dir}")
    print(f"📄 Stories:    {mission_dir}/artifacts/po/user-stories.md")
    print(f"📐 ADR:        {mission_dir}/artifacts/architect/architecture-decision-record.md")
    print(f"🧪 Tests:      {mission_dir}/tests/")
    print(f"✅ Sign-off:   {mission_dir}/artifacts/qa/sign-off.md")
    print(f"📝 Context:    {project_path / PROJECT_CONFIG_FILENAME} (updated)")


# ─────────────────────────────────────────────
# Entry Point
# ─────────────────────────────────────────────

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Agile Agent Team — autonomous feature development"
    )

    goal_group = parser.add_mutually_exclusive_group(required=True)
    goal_group.add_argument(
        "goal",
        nargs="?",
        help='Business goal in quotes, e.g. "Add password reset via email"'
    )
    goal_group.add_argument(
        "--goal-file",
        metavar="FILE",
        help="Path to a file containing the business goal (supports .md, .txt, any text file)"
    )

    parser.add_argument(
        "--project-path",
        default=".",
        help="Path to your project root (default: current directory)"
    )
    parser.add_argument(
        "--refresh-context",
        action="store_true",
        help="Force a full project re-scan and overwrite project.config.md"
    )
    parser.add_argument(
        "--resume-mission",
        metavar="MISSION_DIR",
        help=(
            "Resume an interrupted mission from where it left off. "
            "Pass the path to the mission folder, e.g. "
            ".agent-missions/mission-20260414-093417. "
            "Completed phases are detected automatically and skipped."
        )
    )

    args = parser.parse_args()

    # --resume-mission: goal is optional (read from mission.md if not given)
    if args.resume_mission:
        resume_path = Path(args.resume_mission)
        business_goal = ""  # will be read from mission.md inside orchestrate()
        if args.goal or args.goal_file:
            # Allow overriding the goal on resume (e.g. to add feedback)
            if args.goal_file:
                goal_path = Path(args.goal_file)
                if not goal_path.exists():
                    print(f"❌ Goal file not found: {goal_path}")
                    sys.exit(1)
                business_goal = goal_path.read_text().strip()
            else:
                business_goal = args.goal
    else:
        resume_path = None
        if args.goal_file:
            goal_path = Path(args.goal_file)
            if not goal_path.exists():
                print(f"❌ Goal file not found: {goal_path}")
                sys.exit(1)
            business_goal = goal_path.read_text().strip()
            print(f"📄 Goal loaded from: {goal_path} ({len(business_goal)} chars)")
        else:
            business_goal = args.goal

    project_path = Path(args.project_path).resolve()
    if not project_path.exists():
        print(f"❌ Project path not found: {project_path}")
        sys.exit(1)

    asyncio.run(orchestrate(
        business_goal=business_goal,
        project_path=project_path,
        force_refresh=args.refresh_context,
        resume_mission=resume_path,
    ))
