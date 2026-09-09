---
name: database-abstraction
description: "Design a stable data-access boundary so persistence technology can change without leaking storage details into application code. Use for repository architecture, database portability, swapping engines or ORMs, testing persistence in isolation, or adding a database adapter."
---

# Database Abstraction

## Purpose
Design a stable data-access boundary between application/domain code and database-specific implementations so persistence technology can evolve without leaking storage details through the application.

## Use When
Use for repository/data-access architecture, persistence boundaries, database portability, swapping database engines or ORMs/ODMs, testing persistence independently, or introducing a new database adapter.

Do not add an abstraction merely because a database exists. Add one when it protects a meaningful boundary, enables multiple implementations, improves testability, or isolates vendor-specific behavior.

## Inputs

Required:
- domain/application use cases
- current persistence implementation
- data ownership and invariants
- transaction requirements

Useful:
- expected database engines
- consistency requirements
- query complexity
- caching strategy
- migration constraints
- operational limits

Never assume portability. Inspect the actual database capabilities first.

## Architecture

```text
Domain / Application
        |
        v
Persistence Port / Repository Contract
        |
        +-------------------+
        |                   |
        v                   v
Database Adapter       Test / Fake Adapter
        |
        v
Driver / ORM / ODM
        |
        v
Database
```

## Workflow

```text
DISCOVER → DEFINE CONTRACT → MODEL CAPABILITIES → ADAPT → TEST → VERIFY
```

1. Inspect current domain services, queries, models, transactions, and database-specific behavior.
2. Identify the smallest stable persistence contract required by application use cases.
3. Keep domain-facing types and errors independent of vendor-specific APIs where practical.
4. Put database-specific schemas, query syntax, serialization, indexes, sessions, and driver behavior inside the adapter.
5. Make transaction boundaries explicit; do not hide distributed or database-specific semantics behind a misleading generic API.
6. Define capability differences when databases cannot provide equivalent behavior.
7. Provide deterministic unit-test seams and integration tests against the real database behavior.
8. Verify query correctness, consistency, performance, migrations, and failure behavior at the adapter boundary.

## Decision Framework

Prefer an abstraction when:
- application logic should survive a persistence implementation change
- multiple persistence implementations are real requirements
- tests need a controlled persistence boundary
- vendor-specific behavior is spreading into services/controllers

Avoid an abstraction when:
- it only renames CRUD operations
- the application intentionally depends on database-native features
- it creates a lowest-common-denominator API that hides important guarantees
- the abstraction adds indirection without reducing coupling

Use capability-oriented contracts for features such as transactions, atomic updates, optimistic concurrency, full-text search, geospatial queries, or database-native aggregation when those capabilities materially affect correctness.

## Layering Rules

- Controllers/API handlers must not construct database queries directly.
- Domain services should depend on persistence contracts, not Mongoose models, SQL clients, or raw driver objects.
- Database adapters own vendor-specific mapping and query construction.
- Database migrations/index definitions remain explicit and operationally visible.
- Do not leak persistence documents/entities into external API contracts.
- Do not convert every database feature into a generic interface; preserve intentional escape hatches with explicit boundaries.

## Quality Bar
A database abstraction should provide:

- a small use-case-driven contract
- explicit ownership of mapping and persistence concerns
- explicit transaction/capability semantics
- testability without weakening production guarantees
- a clear path for database-specific optimizations
- observable performance and failure behavior

## Anti-Patterns
Avoid:

- generic `BaseRepository<T>` abstractions with dozens of unused methods
- leaking ORM/ODM documents into domain logic
- hiding transaction boundaries
- pretending incompatible database guarantees are equivalent
- putting business rules in database adapters
- putting database queries in controllers
- creating an abstraction before understanding access patterns

## Verification
Verify:

- contract tests for every adapter
- integration tests against the real database
- transaction and concurrency semantics
- serialization/deserialization behavior
- error mapping
- index/query behavior
- migration compatibility
- application behavior without direct database coupling

## Composition
Typically compose with:

- `database-engineer` for schema, indexes, integrity, migrations, and performance
- a database-specific skill such as `mongoose-developer` for implementation details
- `backend-developer` for service/application integration
- `qa-engineer` for contract and integration coverage
- `security-engineer` for secrets, authorization, and sensitive-data boundaries

## Output
Return:

- persistence contract
- adapter boundary
- mapping strategy
- capability/transaction model
- migration/index implications
- test strategy
- integration evidence
- remaining portability or vendor-coupling risks

## Definition of Done
Application code depends on a justified persistence boundary, database-specific behavior is isolated in adapters, important database capabilities remain explicit, and contract plus integration verification demonstrates that the boundary preserves correctness.
