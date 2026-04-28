# Antigravity's Quotestimator

A standalone extraction of the agent quota estimation script and its minimal `.agent` directory structure.

## Usage

This structure is designed to work out-of-the-box when copied into other projects. It uses the `.agent/scripts/quotestimator.py` to calculate API cost and token usage during agent operations.

### Estimating Cost

```bash
python3 ./.agent/scripts/quotestimator.py --agent my-agent --model gemini-3.1-pro --turns 2 --read src/main.py --modified src/feature.py
```

### Mission Summary

If you track a specific mission in `.agent/state/context.json`, you can summarize the mission's total usage:

```bash
python3 ./.agent/scripts/quotestimator.py --summarize
```

## Accuracy

It is a solid heuristic estimate, though not strictly exact:

- **Token Math:** The ~4 characters per token rule is a standard industry approximation.
- **Output Tracking:** Using git diff measures final generated code, but it inherently undercounts "thinking" tokens or code the agent generated but subsequently overwrote.
- **Pricing:** The hardcoded dictionary provides a good snapshot but requires manual maintenance.
