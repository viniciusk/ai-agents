---
name: mission-quota-usage-estimator
description: Estimate token usage and costs for AI agents during missions.
---

# Mission Quota Usage Estimator Skill

1. **Record Telemetry:** Every time an agent completes a phase or hands over to another agent, they MUST execute:
   `python3 ./.agent/scripts/quotestimator.py --agent <agent_name> --model <model_name> --turns <N> --read <file1> <file2> --modified <file3> <file4>`

2. **Summarize Telemetry:** At the end of the mission, run:
   `python3 ./.agent/scripts/quotestimator.py --summarize --mission <MISSION_ID>`
