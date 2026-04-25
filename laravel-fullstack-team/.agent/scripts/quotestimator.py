import sys
import os
import argparse

# Easily updatable expected costs (per 1M tokens)
# Values represent USD per 1,000,000 tokens
EXPECTED_COSTS = {
    "gemini-3.1-pro": {"input": 2.00, "output": 12.00},
    "gemini-3.1-pro-high": {"input": 2.00, "output": 12.00},
    "gemini-3.1-pro-low": {"input": 2.00, "output": 12.00},
    "gemini-3.0-flash": {"input": 0.075, "output": 0.30},
    "gemini-2.5-pro": {"input": 2.00, "output": 8.00},
    "gemini-2.5-flash": {"input": 0.075, "output": 0.30},
    "gemini-1.5-pro": {"input": 1.25, "output": 5.00},
    "gemini-1.5-flash": {"input": 0.075, "output": 0.30},
    "gpt-4o": {"input": 5.00, "output": 15.00},
    "gpt-4o-mini": {"input": 0.15, "output": 0.60},
    "claude-3-5-sonnet": {"input": 3.00, "output": 15.00},
    "claude-3-5-haiku": {"input": 1.00, "output": 5.00},
    "claude-3-7-sonnet": {"input": 3.00, "output": 15.00},
    "default": {"input": 2.00, "output": 12.00}
}

import json
import datetime

import subprocess

def estimate_tokens(file_paths):
    total_chars = 0
    total_files = 0
    
    for path in file_paths:
        if os.path.exists(path) and os.path.isfile(path):
            try:
                # Read the file natively, ignoring binary files
                with open(path, 'r', encoding='utf-8') as f:
                    total_chars += len(f.read())
                    total_files += 1
            except UnicodeDecodeError:
                pass 
                
    # Standard LLM heuristic: ~4 characters per token
    return total_files, total_chars // 4

def estimate_modified_tokens(file_paths):
    total_chars = 0
    total_files = 0
    
    for path in file_paths:
        if os.path.exists(path) and os.path.isfile(path):
            total_files += 1
            try:
                # Check if file is tracked by git
                status = subprocess.run(['git', 'ls-files', '--error-unmatch', path], 
                                        capture_output=True, text=True)
                if status.returncode != 0:
                    # Untracked file: count all characters
                    with open(path, 'r', encoding='utf-8') as f:
                        total_chars += len(f.read())
                else:
                    # Tracked file: count added characters in diff against HEAD
                    # 'HEAD' compares against the last commit, including staged and unstaged changes
                    diff = subprocess.run(['git', 'diff', 'HEAD', '-U0', '--', path], 
                                          capture_output=True, text=True, check=True)
                    for line in diff.stdout.splitlines():
                        if line.startswith('+') and not line.startswith('+++'):
                            # line[1:] is the added text
                            total_chars += len(line[1:])
            except Exception:
                # Fallback to whole file if git fails
                try:
                    with open(path, 'r', encoding='utf-8') as f:
                        total_chars += len(f.read())
                except:
                    pass
                    
    return total_files, total_chars // 4

def get_mission_id():
    try:
        with open('.agent/state/context.json', 'r') as f:
            data = json.load(f)
            mission = data.get('active_feature')
            if mission and mission != "None":
                return mission
    except Exception:
        pass
    return None

def print_summary():
    mission_id = get_mission_id()
    if not mission_id:
        print("No active mission found.")
        return
        
    mission_dir = f".agent-missions/{mission_id}"
    telemetry_file = os.path.join(mission_dir, "telemetry.jsonl")
    
    if not os.path.exists(telemetry_file):
        print("No telemetry data found for the current mission.")
        return
        
    total_read_files = 0
    total_read_tokens = 0
    total_modified_files = 0
    total_modified_tokens = 0
    total_turns = 0
    total_cost = 0.0
    
    with open(telemetry_file, 'r', encoding='utf-8') as f:
        for line in f:
            try:
                record = json.loads(line.strip())
                total_read_files += record.get("read_files", 0)
                total_read_tokens += record.get("read_tokens", 0)
                total_modified_files += record.get("modified_files", record.get("mod_files", 0))
                total_modified_tokens += record.get("modified_tokens", record.get("mod_tokens", 0))
                total_turns += record.get("turns", 1)
                total_cost += record.get("est_cost", 0.0)
            except Exception:
                pass
                
    print("### 📊 Mission Telemetry Summary")
    print("| Metric | Total Value |")
    print("| :--- | :--- |")
    print(f"| **Files Read** | {total_read_files} |")
    print(f"| **Files Modified** | {total_modified_files} |")
    print(f"| **Total Turns** | {total_turns} |")
    print(f"| **Est. Context Tokens** | ~{total_read_tokens:,} |")
    print(f"| **Est. Generated Tokens** | ~{total_modified_tokens:,} |")
    print(f"| **Est. Total API Cost** | **${total_cost:.5f}** |")

def generate_receipt():
    parser = argparse.ArgumentParser(description="Estimate Agent Token Usage")
    parser.add_argument('--agent', default='unknown-agent', help='The agent used (e.g. antigravity, cline)')
    parser.add_argument('--model', default='default', help='The model used by the agent (e.g. gemini-3.1-pro)')
    parser.add_argument('--read', nargs='*', default=[], help='Files the agent read for context')
    parser.add_argument('--modified', nargs='*', default=[], help='Files the agent modified or created')
    parser.add_argument('--turns', type=int, default=1, help='Number of conversation turns (multiplies input tokens)')
    parser.add_argument('--summarize', action='store_true', help='Print total summary for the active mission')
    args = parser.parse_args()

    if args.summarize:
        print_summary()
        return

    read_files, base_read_tokens = estimate_tokens(args.read)
    modified_files, modified_tokens = estimate_modified_tokens(args.modified)
    
    # Multiply input tokens by the number of turns
    read_tokens = base_read_tokens * args.turns
    
    # Retrieve costs
    # Normalize model string (e.g. "Gemini 3.1 Pro (High)" -> "gemini-3.1-pro-high")
    model_key = args.model.lower().replace(" ", "-").replace("-(", "-").replace("(", "").replace(")", "")
    rates = EXPECTED_COSTS.get(model_key, EXPECTED_COSTS["default"])
    
    est_cost = (read_tokens / 1_000_000 * rates["input"]) + (modified_tokens / 1_000_000 * rates["output"])
    
    # Store record
    mission_id = get_mission_id()
    if not mission_id:
        mission_id = "global"
    
    mission_dir = f".agent-missions/{mission_id}"
    if mission_id != "global" and os.path.isdir(mission_dir):
        telemetry_file = os.path.join(mission_dir, "telemetry.jsonl")
    else:
        telemetry_file = ".agent/state/telemetry.jsonl"
        
    record = {
        "timestamp": datetime.datetime.now().isoformat(),
        "agent": args.agent,
        "model": args.model,
        "read_files": read_files,
        "read_tokens": read_tokens,
        "modified_files": modified_files,
        "modified_tokens": modified_tokens,
        "turns": args.turns,
        "est_cost": est_cost
    }
    
    os.makedirs(os.path.dirname(telemetry_file), exist_ok=True)
    with open(telemetry_file, 'a', encoding='utf-8') as f:
        f.write(json.dumps(record) + "\n")
    
    print("### 📊 Mission Telemetry (Workspace Estimate)")
    print("| Metric | Value |")
    print("| :--- | :--- |")
    print(f"| **Agent** | {args.agent} |")
    print(f"| **Model** | {args.model} |")
    print(f"| **Files Read** | {read_files} |")
    print(f"| **Files Modified** | {modified_files} |")
    print(f"| **Turns Estimated** | {args.turns} |")
    print(f"| **Est. Context Tokens** | ~{read_tokens:,} |")
    print(f"| **Est. Generated Tokens** | ~{modified_tokens:,} |")
    print(f"| **Est. API Equivalent Cost** | **${est_cost:.5f}** |")

if __name__ == "__main__":
    generate_receipt()