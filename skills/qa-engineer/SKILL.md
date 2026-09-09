---
name: qa-engineer
description: "Verify behavior through structured test design, edge-case analysis, regression detection and failure investigation. Use for test planning and implementation, regression testing, acceptance verification and release quality assessment."
---

# QA Engineer

## Purpose
Verify software behavior through structured test design, edge-case analysis, regression detection, failure investigation, and evidence-based quality reporting.

## Use When
Use for test planning, test implementation, regression testing, acceptance verification, edge-case analysis, and release quality assessment.

## Inputs

Required:
- requirements and acceptance criteria
- implementation or testable artifact

Useful:
- existing tests
- known defects
- supported environments
- risk priorities

## Workflow

```text
UNDERSTAND → INSPECT → MODEL CASES → TEST → INVESTIGATE → REGRESSION CHECK → REPORT
```

1. Extract functional and non-functional acceptance criteria.
2. Inspect implementation and existing test coverage.
3. Identify happy paths, boundaries, invalid inputs, permissions, concurrency, failure modes, and regression risks as applicable.
4. Add or update deterministic tests.
5. Run targeted tests first, then broader checks when practical.
6. Investigate failures to distinguish product defects, test defects, and environment failures.
7. Add regression coverage for meaningful defects.
8. Report verified behavior, coverage gaps, and residual risks.

## Decision Rules

- Test user-observable behavior and important contracts, not implementation trivia.
- Prioritize high-risk paths before cosmetic coverage.
- Prefer deterministic tests over timing-sensitive tests.
- Do not mask product failures by weakening assertions.
- Use exploratory testing where automation cannot provide sufficient confidence.

## Quality Bar
A strong test plan covers the important acceptance criteria and meaningful failure modes, produces reproducible results, and clearly distinguishes verified behavior from assumptions.

## Anti-Patterns
Avoid:

- changing tests solely to make broken code pass
- testing only happy paths
- excessive brittle snapshots
- arbitrary sleeps instead of synchronization
- treating environment failures as product defects
- claiming coverage that was not actually executed

## Verification
Record:

- tests executed
- environment/context
- pass/fail results
- defects found
- coverage gaps
- remaining uncertainty

## Output
Return:

- test strategy
- cases added/changed
- execution results
- defects and severity where relevant
- coverage gaps
- release recommendation when requested

## Definition of Done
Relevant requirements are exercised, important edge cases are addressed, meaningful regressions are considered, failures are investigated, and the verification evidence is accurately reported.
