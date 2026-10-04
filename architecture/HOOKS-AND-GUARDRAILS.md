# E2E Hooks and Guardrails

## Purpose

Hooks provide deterministic checks around agent actions. They complement skills; they do not replace judgment.

## Lifecycle

```text
pre-task
  ↓
pre-context
  ↓
pre-edit
  ↓
post-edit
  ↓
pre-test
  ↓
post-test
  ↓
pre-commit / release
  ↓
pre-deploy
  ↓
verification
```

## Guardrail Classes

### Safety

- secret detection
- destructive command confirmation
- protected file restrictions
- credential handling
- untrusted input boundaries

### Engineering

- formatting/lint checks
- type checks
- generated-file consistency
- migration safety
- API contract checks

### Verification

- required tests
- evidence collection
- changed-file review
- acceptance-criteria traceability

## Hook Contract

A hook should return:

```yaml
status: pass | warn | block
rule: "..."
evidence: []
message: "..."
remediation: "..."
```

Hooks must be deterministic where possible and must not silently mutate unrelated project state.

## Failure Policy

- `pass`: continue.
- `warn`: continue only when policy allows and record the warning.
- `block`: stop the affected action and route remediation through the responsible agent.

Security and data-loss protections should default to blocking when confidence is high.
