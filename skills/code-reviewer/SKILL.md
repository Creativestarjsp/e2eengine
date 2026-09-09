---
name: code-reviewer
description: "Review code independently for correctness, security, maintainability, performance, compatibility and regression risk, citing evidence. Use for pull-request review, change review, pre-release review and targeted implementation audits."
---

# Code Reviewer

## Purpose
Perform independent, evidence-based review of code for correctness, security, maintainability, performance, compatibility, and regression risk.

## Use When
Use for pull-request review, change review, pre-release review, and targeted implementation audits.

## Inputs

Required:
- actual changed code
- intended behavior or acceptance criteria

Useful:
- test results
- architecture documentation
- related issues
- performance/security requirements

Never review from assumptions when repository evidence is available.

## Workflow

```text
INSPECT → UNDERSTAND → TRACE → CHECK → CLASSIFY → RECOMMEND → VERIFY
```

1. Inspect the complete change and surrounding code needed for context.
2. Establish intended behavior from requirements and existing conventions.
3. Trace important execution and data paths.
4. Check correctness, edge cases, security, authorization, error handling, performance, compatibility, and tests.
5. Classify findings by severity and evidence.
6. Provide actionable recommendations tied to specific locations.
7. Verify whether tests actually prove important behavior.

## Severity

- **Critical:** severe security, data-loss, or production-breaking issue
- **High:** likely serious bug, security weakness, or major regression
- **Medium:** meaningful correctness, reliability, maintainability, or compatibility issue
- **Low:** minor improvement or style issue

Do not inflate severity to force a preferred implementation.

## Decision Rules

- Review actual behavior and evidence.
- Prioritize correctness and user impact over stylistic preferences.
- Distinguish confirmed defects from questions or speculative concerns.
- Avoid unrelated refactoring recommendations.
- Prefer consistency with established architecture unless there is evidence it is harmful.

## Anti-Patterns
Avoid:

- approving without inspecting relevant code
- reporting theoretical issues as confirmed vulnerabilities
- style-only nitpicks that obscure important findings
- demanding rewrites without evidence
- treating passing tests as proof that all behavior is correct

## Verification
Check relevant test evidence and, when practical, execute targeted checks. Record what was actually verified.

## Output
For each finding provide:

- severity
- location
- evidence/problem
- impact
- recommended fix

End with:

- verified strengths
- tests/checks reviewed
- remaining risks
- overall recommendation

## Definition of Done
The change has been reviewed against its intended behavior and relevant risk areas, findings are actionable and evidence-based, and verification status is explicit.
