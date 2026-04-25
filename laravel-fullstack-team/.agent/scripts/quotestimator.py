import sys
import os
import argparse

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

def generate_receipt():
    parser = argparse.ArgumentParser(description="Estimate Antigravity Token Usage")
    parser.add_argument('--read', nargs='*', default=[], help='Files the agent read for context')
    parser.add_argument('--modified', nargs='*', default=[], help='Files the agent modified or created')
    args = parser.parse_args()

    read_files, read_tokens = estimate_tokens(args.read)
    mod_files, mod_tokens = estimate_tokens(args.modified)
    
    # Gemini 3.1 Pro baseline pricing equivalent ($2.00 per 1M input, $12.00 per 1M output)
    est_cost = (read_tokens / 1_000_000 * 2.00) + (mod_tokens / 1_000_000 * 12.00)
    
    print("### 📊 Mission Telemetry (Workspace Estimate)")
    print("| Metric | Value |")
    print("| :--- | :--- |")
    print(f"| **Files Read** | {read_files} |")
    print(f"| **Files Modified** | {mod_files} |")
    print(f"| **Est. Context Tokens** | ~{read_tokens:,} |")
    print(f"| **Est. Generated Tokens** | ~{mod_tokens:,} |")
    print(f"| **Est. API Equivalent Cost** | **${est_cost:.5f}** |")

if __name__ == "__main__":
    generate_receipt()