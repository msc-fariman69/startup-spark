---
name: validating-startup-ideas
description: Generate practical startup validation experiments. Use when the user asks how to test, validate, de-risk, or prove demand for a startup idea. Do not use for writing landing page copy or investor pitch.
version: 1.0.0
allowed-tools: [score_startup_idea, create_validation_experiments]
---

# Validating Startup Ideas

## When to use

Use this skill to create validation experiments for a startup idea.

## Workflow

1. Identify the riskiest assumption.
2. Suggest 3 practical experiments.
3. For each experiment, include goal, action, success signal, and time box.
4. Score the idea using the `score_startup_idea` tool when useful.
5. Be honest about risks.

## Output format

```markdown
## Validation Plan

### Riskiest Assumption

### Experiments

#### Experiment 1
- Goal:
- Action:
- Success signal:
- Time box:

#### Experiment 2
- Goal:
- Action:
- Success signal:
- Time box:

#### Experiment 3
- Goal:
- Action:
- Success signal:
- Time box:

### Validation Score
```
