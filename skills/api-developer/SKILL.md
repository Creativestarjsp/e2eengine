---
name: api-developer
description: "Design and implement APIs with explicit contracts, validation, error behavior and compatibility guarantees. Use for REST/HTTP endpoint design and implementation, request/response schemas, versioning, integration behavior and API tests."
---

# API Developer

## Purpose
Design and implement consistent, secure, predictable APIs and integrations with explicit contracts, validation, error behavior, and compatibility guarantees.

## Use When
Use for REST/HTTP API design, endpoint implementation, API contracts, request/response schemas, versioning, integration behavior, and API tests.

## Inputs

Required:
- product requirements
- existing API conventions
- consumer/client expectations

Useful:
- authentication model
- data contracts
- compatibility requirements
- rate limits
- performance expectations

## Workflow

```text
UNDERSTAND → INSPECT → CONTRACT → IMPLEMENT → TEST → DOCUMENT → VERIFY
```

1. Inspect existing routes, schemas, status codes, error shapes, authentication, middleware, and documentation.
2. Define resource semantics, request/response contracts, validation, authorization, and failure behavior.
3. Check compatibility with existing consumers.
4. Decide versioning, pagination, filtering, retry, and idempotency behavior where relevant.
5. Implement endpoint and service integration.
6. Test success, validation, authentication, authorization, not-found, conflict, rate-limit, and server-error paths as applicable.
7. Document the contract and examples.
8. Review security, observability, compatibility, and unnecessary complexity.

## Decision Rules

- Treat API contracts as public interfaces.
- Prefer consistent behavior with the existing API.
- Use explicit status and error semantics.
- Validate all untrusted input.
- Enforce authorization server-side.
- Make idempotency and retry semantics explicit where retries can occur.
- Prefer additive compatible changes when possible.

## Quality Bar
An API change must be:

- predictable
- validated
- authorized
- documented
- testable
- compatible with affected consumers
- explicit about failure behavior
- free of sensitive information leakage

## Anti-Patterns
Avoid:

- inconsistent error shapes
- arbitrary status codes
- undocumented breaking changes
- leaking database or stack internals
- trusting client-provided authorization claims
- ambiguous null/empty semantics
- endpoints that mix unrelated responsibilities
- changing API style without migration justification

## Verification
Verify:

- request validation
- response schema
- status codes
- authentication/authorization
- important failure paths
- idempotency where relevant
- backward compatibility
- API documentation

## Security
Do not expose credentials, tokens, internal stack traces, or unnecessary sensitive fields. Validate and authorize every protected operation.

## Output
Return:

- endpoint/contract changes
- request and response behavior
- compatibility/versioning decisions
- security considerations
- tests performed
- documentation changes
- remaining risks

## Definition of Done
The endpoint is implemented, secured, validated, tested across important paths, documented, and compatible with the intended consumers.
