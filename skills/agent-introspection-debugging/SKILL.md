---
name: agent-introspection-debugging
description: "Diagnose failed or looping agent runs before retrying, separating model, context, tool, environment and repository causes. Use when a worker times out or repeatedly fails, the same correction is attempted twice, tool calls loop without progress, or context drift is suspected."
---

# Agent Introspection Debugging

## Purpose
Diagnose failed or looping agent runs before retrying, using captured state and evidence to distinguish model, context, tool, environment, and repository failures.

## Use When
- A worker times out or repeatedly fails.
- The same correction is attempted more than once.
- Tool calls loop without progress.
- Context drift or environment mismatch is suspected.

## Workflow
1. Capture the run ID, task, runtime, worker, phase, duration, return code, stdout/stderr, tool audit, and repository state.
2. Classify the failure: task interpretation, context, code, test, tool, permission, environment, integration, or architectural.
3. Identify the smallest reproducible failure signature.
4. Apply one contained corrective action.
5. Re-run only the affected verification.
6. Escalate to SD3 when the failure is architectural, security-sensitive, or persists after bounded correction.

## Anti-Patterns
- Blindly retrying the same prompt.
- Hiding failed evidence.
- Increasing timeouts as the first response.
- Giving a worker broader permissions to compensate for an unknown failure.

## Output
Produce an introspection report with failure class, evidence, likely root cause, corrective action, confidence, and escalation decision.

## Composition
Used by SD2 after worker failures and by SD3 when evaluating repeated correction loops.

## Claude/Codex Compatibility
Runtime-neutral and shared across Claude Code and Codex.
