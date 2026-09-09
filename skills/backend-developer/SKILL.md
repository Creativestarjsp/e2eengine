---
name: backend-developer
description: "Implement backend services, business logic, validation, authentication, authorization, persistence and failure handling. Use for server-side implementation, service boundaries and backend tests. Not for database architecture, infrastructure or frontend work."
---

# Backend Developer

## Purpose
Design and implement reliable backend services, APIs, business logic, validation, authentication, authorization, persistence, and failure handling.

## Use When
Use for server-side implementation, business logic, service boundaries, API behavior, authentication/authorization integration, and backend tests.

Do not use as the primary skill for database architecture, infrastructure, or frontend UX.

## Inputs

Required:
- task requirements
- existing backend architecture and conventions
- relevant API/data contracts

Useful:
- performance expectations
- security requirements
- migration constraints
- acceptance criteria

Never invent undocumented business rules or data behavior.

## Workflow

```text
UNDERSTAND → INSPECT → TRACE → PLAN → IMPLEMENT → TEST → SECURITY REVIEW → VERIFY
```

1. Inspect the repository, service boundaries, configuration, dependencies, tests, and existing conventions.
2. Trace the request, authorization, business logic, and data flow.
3. Identify validation boundaries, invariants, failure paths, and compatibility constraints.
4. Design the smallest compatible change.
5. Implement with clear separation between transport, business logic, and persistence concerns.
6. Add or update tests for success, invalid input, authorization, and important failures.
7. Review authentication, authorization, sensitive data handling, and abuse cases.
8. Run relevant tests, type checks, linting, and build checks.
9. Review for correctness, performance, maintainability, and unnecessary complexity.

## Decision Rules

- Validate untrusted input at system boundaries.
- Enforce authorization server-side.
- Keep domain logic independent from transport concerns where practical.
- Prefer explicit contracts and predictable errors.
- Preserve compatibility unless a deliberate breaking change is approved.
- Make idempotency and retry behavior explicit when relevant.
- Use the simplest architecture that satisfies actual requirements.

## Quality Bar
A completed backend change should have:

- correct business behavior
- explicit validation
- correct authorization
- deterministic error handling
- appropriate observability
- relevant automated tests
- safe data handling
- acceptable performance for the expected workload
- backward compatibility where required

## Anti-Patterns
Avoid:

- trusting client-side validation
- authorization hidden only in UI logic
- leaking stack traces or sensitive internals
- hardcoded secrets
- business logic scattered through controllers
- swallowing exceptions
- unnecessary abstractions
- premature distributed architecture
- changing unrelated services

## Verification
Where applicable verify:

- unit tests
- integration/API tests
- type checks
- linting
- authentication and authorization cases
- validation failures
- not-found/conflict/server-error paths
- idempotency or retry behavior
- backward compatibility

State what was actually executed.

## Security
Never request, expose, or commit credentials. Treat input, uploaded files, external responses, and persisted data according to their trust level. Apply least privilege and avoid sensitive information in logs.

## Output
Return:

- implementation summary
- affected endpoints/services
- business and security decisions
- tests/checks performed
- migration or compatibility notes
- remaining risks

## Definition of Done
The behavior is implemented, validated, authorized, tested, observable where appropriate, compatible with affected consumers, and verified against the relevant failure paths.
