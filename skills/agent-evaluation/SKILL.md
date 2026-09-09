---
name: agent-evaluation
description: "Judge SD1/SD2/SD3 work on evidence rather than effort or self-reported success. Use after a non-trivial worker run, when SD3 is deciding whether work is acceptable, when comparing runtime or model variants, or when investigating reliability regressions."
---

# Agent Evaluation

## Purpose
Evaluate SD1/SD2/SD3 work independently using evidence rather than effort or self-reported success.

## Use When
- A non-trivial worker run completes.
- SD3 is deciding whether work is acceptable.
- Comparing runtime, model, or workflow variants.
- Investigating reliability regressions.

## Evaluation Axes
Score 0-5 with evidence for every score below 5:
1. Accuracy — claims match repository evidence.
2. Completeness — requested requirements and relevant regressions are covered.
3. Correctness — implementation and tests behave as intended.
4. Security — trust boundaries and sensitive-data handling remain intact.
5. Integration — changes fit existing architecture and interfaces.
6. Evidence quality — commands, tests, files, and outcomes are reproducible.
7. Efficiency — unnecessary changes, retries, and tool usage are minimized.

## Workflow
1. Capture the task and completion criteria.
2. Inspect actual repository state.
3. Compare changed files against the task and plan.
4. Run deterministic checks where practical.
5. Record failures and concrete evidence.
6. Produce scores and corrective actions.

## Rules
Do not re-perform the task. Do not give a perfect score without evidence. Do not penalize missing features that were not requested. Security and data-integrity failures are blocking regardless of aggregate score.

## Output
Return structured evaluation data with scores, evidence, failed checks, risks, and recommended next actions.

## Composition
SD3 uses this skill after SD1 execution. The evaluator is independent from the worker and should use a fresh context when runtime support exists.

## Claude/Codex Compatibility
Runtime-neutral and shared across Claude Code and Codex.
