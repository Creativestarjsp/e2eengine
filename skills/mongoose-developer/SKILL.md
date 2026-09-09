---
name: mongoose-developer
description: "Implement MongoDB persistence with Mongoose while keeping database-specific behavior isolated and testable. Use for Mongoose schemas and models, validation, indexes, middleware, populate, discriminators, query design and transactions."
---

# Mongoose Developer

## Purpose
Implement production-grade MongoDB persistence with Mongoose while keeping database-specific behavior isolated, testable, observable, and compatible with the application's persistence boundary.

## Use When
Use for Mongoose schemas/models, validation, indexes, middleware, populate, discriminators, query design, transactions, MongoDB-specific persistence, and Mongoose compatibility work.

Mongoose provides schemas, models, validation, middleware, indexes, transactions, and other MongoDB integration capabilities. Use the current project-supported Mongoose version rather than assuming API behavior from older versions.

## Inputs

Required:
- existing persistence architecture
- domain/application use cases
- MongoDB collections and access patterns
- current Mongoose version

Useful:
- expected cardinality and workload
- transaction requirements
- indexing requirements
- migration strategy
- data retention and privacy constraints

## Architecture

```text
Application / Domain
        |
        v
Repository / Persistence Contract
        |
        v
Mongoose Adapter
   |            |
   v            v
Schema/Model   Query/Transaction Logic
        |
        v
MongoDB
```

## Workflow

```text
INSPECT → MODEL → SCHEMA → ADAPTER → INDEX → TEST → INTEGRATE → VERIFY
```

1. Inspect existing models, schemas, connections, repository contracts, queries, indexes, and application consumers.
2. Confirm the installed/supported Mongoose version and consult version-appropriate behavior before using advanced APIs.
3. Model documents around real access patterns and domain invariants.
4. Define schemas with explicit types, validation, timestamps, serialization behavior, and indexes where justified.
5. Keep Mongoose documents/models inside the persistence adapter when a database abstraction exists.
6. Use `lean()` deliberately for read paths that do not require hydrated documents.
7. Use populate, aggregation, discriminators, middleware, and plugins only when they solve a concrete requirement and their operational cost is understood.
8. Make transaction/session boundaries explicit for multi-document atomic workflows.
9. Test schema validation, queries, indexes, serialization, failure behavior, and transaction semantics against MongoDB where behavior cannot be faithfully mocked.
10. Verify application compatibility and regression impact before integration.

## Schema Rules

- Define schema shape explicitly.
- Validate data at the schema boundary, but do not put all business rules into schema validators.
- Treat indexes as workload decisions, not decoration.
- Avoid unbounded arrays and uncontrolled document growth.
- Choose embedding vs referencing based on read/write patterns, consistency, and cardinality.
- Make optionality and defaults intentional.
- Review `ObjectId` references and populate behavior for authorization and performance implications.
- Disable automatic production index creation when the project's operational policy requires controlled index deployment.

## Query Rules

- Prefer targeted projections for large documents.
- Verify query filters against indexes and actual access patterns.
- Avoid accidental collection scans on hot paths.
- Use pagination designed for the workload; do not assume `skip/limit` is appropriate at large offsets.
- Treat aggregation pipelines as production code and test important pipeline stages.
- Avoid N+1 populate/query patterns.
- Do not expose raw MongoDB/Mongoose query objects through API boundaries.

## Transaction Rules

Use transactions only when the business operation requires atomicity across multiple writes. Pass the session consistently through every participating operation. Do not hide transaction boundaries inside unrelated repository methods.

For workflows that can tolerate eventual consistency, prefer simpler idempotent operations over unnecessary multi-document transactions.

## Abstraction Rules

When `database-abstraction` is present:

- application/domain code depends on the persistence contract
- Mongoose models remain inside the Mongoose adapter
- vendor-specific errors are mapped at the adapter boundary
- MongoDB-native capabilities are exposed through explicit capability interfaces when required
- do not create a fake portable API that erases MongoDB semantics

If no abstraction is justified, document why direct Mongoose usage is intentionally allowed.

## Testing

Minimum relevant coverage:

- schema validation
- required/default fields
- serialization and deserialization
- representative reads and writes
- unique/index behavior
- query edge cases
- transaction behavior when used
- error mapping
- authorization-sensitive queries
- integration tests against MongoDB for behavior that mocks cannot prove

## Security

- Never hard-code MongoDB credentials or connection strings.
- Use least-privilege database credentials.
- Do not log full documents containing secrets or sensitive fields.
- Review projection and serialization for accidental data exposure.
- Validate authorization before resolving referenced documents.
- Treat user-controlled query input as untrusted.

## Performance

Measure before optimizing. Review:

- index selectivity
- query execution plans
- document size
- population cost
- aggregation complexity
- connection pool behavior
- transaction duration
- hot collections and write contention

## Anti-Patterns

Avoid:

- putting Mongoose models directly in controllers
- giant schemas containing unrelated domains
- unbounded populate chains
- indexes without query justification
- relying on validation alone for authorization
- hiding transactions inside generic CRUD methods
- mocking every MongoDB behavior and skipping integration tests
- assuming MongoDB and relational database guarantees are interchangeable

## Verification

Return evidence for:

- affected schemas/models
- repository/adapter changes
- index changes
- migrations or deployment steps
- query/test results
- transaction evidence where relevant
- performance evidence where relevant
- compatibility and regression risks

## Definition of Done
Mongoose behavior is isolated at the appropriate persistence boundary, schemas and indexes reflect real access patterns, validation and transactions are correct, sensitive data is protected, relevant MongoDB behavior is integration-tested, and application integration is verified.
