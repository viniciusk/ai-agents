---
name: native-mission-telemetry
description: A zero-dependency macOS script to estimate the token footprint and cost of the current mission.
---

# Skill: Mission Quota Usage Estimator

## Goal

Estimate the token footprint of the files read and modified during this mission and append a cost receipt to the final Artifact.

## Instructions

1. Identify all the file paths you have **read or analyzed** for context during this mission.
2. Identify all the file paths you have **created or modified** during this mission.
3. Open the Antigravity integrated terminal and run the python estimator. Separate the files using the respective flags. Example:
   `python3 ./.agent/scripts/quotestimator.py --read app/Models/User.php --modified app/Http/Controllers/AuthController.php`
4. Read the markdown table output.
5. Append the output table to the absolute bottom of the `FINAL_REVIEW.md` artifact you are finalizing for mission {{MISSION_ID}}
