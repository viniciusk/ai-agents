---
name: quota-estimation
description: Workflow to track usage quotas.
---

# Quota Estimation Workflow

## Global Rules

1. **Telemetry Tracking:** Agents MUST execute the `quotestimator.py` script to track their API usage after significant tasks.

## Example Usage

- **Action:** Run `python3 ./.agent/scripts/quotestimator.py --agent dev-agent --model gemini-3.1-pro --turns 1 --read file.txt --modified out.txt`
