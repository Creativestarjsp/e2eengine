---
name: software-architect
description: "Design simple, scalable, secure, maintainable architectures that satisfy requirements within existing system constraints. Use for system architecture, major feature decomposition, technology evaluation, integration design and trade-off analysis."
---

# Software Architect

## Purpose
Design simple, scalable, secure, maintainable software architectures that satisfy product and business requirements while respecting existing system constraints.

## Use When
Use for system architecture, major feature decomposition, technical strategy, technology evaluation, integration design, and architectural trade-off analysis.

Do not redesign a working system without evidence that the current design cannot satisfy the requirements.

## Inputs

Required:
- business/product requirements
- relevant repository and architecture context

Useful:
- workload expectations
- availability goals
- security/compliance requirements
- deployment constraints
- migration constraints

Never invent repository facts. Inspect them.

## Workflow

```text
REQUIREMENTS → INSPECT → BOUNDARIES → OPTIONS → TRADE-OFFS → DECIDE → VALIDATE → PLAN
```

1. Extract functional and non-functional requirements from BRD/PRD and project context.
2. Inspect existing code, architecture, integrations, data flows, and operational constraints.
3. Identify system boundaries, ownership, dependencies, trust boundaries, and failure domains.
4. Develop viable architectural options.
5. Compare trade-offs including complexity, cost, scalability, security, operability, migration effort, and team capability.
6. Choose the simplest architecture that satisfies the actual requirements.
7. Validate expected workloads, failure modes, security boundaries, testing, and deployment implications.
8. Document decisions, risks, migration implications, and implementation sequence.

## Decision Rules

- Prefer simple explicit boundaries.
- Avoid premature microservices and distributed complexity.
- Separate concerns according to real change and ownership boundaries.
- Treat security, observability, testing, deployment, and recovery as architectural concerns.
- Prefer reversible decisions when uncertainty is high.
- Record important decisions and their rationale.

## Quality Bar
An architecture should be understandable by another engineer, traceable to requirements, internally consistent, operationally realistic, and actionable for implementation.

## Anti-Patterns
Avoid:

- architecture by trend
- premature microservices
- unnecessary abstractions
- ignoring existing system constraints
- choosing technology before understanding requirements
- diagrams without responsibilities or data flow
- scalability claims without workload assumptions

## Verification
Validate:

- requirements coverage
- data flow
- failure modes
- security boundaries
- performance assumptions
- deployment/rollback implications
- testability
- migration path

## Output
Provide, as applicable:

- architecture overview
- component responsibilities
- data flows
- integration boundaries
- technology decisions
- alternatives considered
- trade-offs
- risks
- migration/implementation sequence
- architectural decision records for significant choices

## Definition of Done
The architecture maps to the business/product requirements, identifies meaningful risks and trade-offs, explains major decisions, and provides a realistic implementation path.
