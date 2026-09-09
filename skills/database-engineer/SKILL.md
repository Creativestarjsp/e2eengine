---
name: database-engineer
description: "Design correct, performant, migration-safe data models, queries, indexes and constraints. Use for schema design, migrations, query optimization, indexing, data integrity, persistence decisions and database testing."
---

# Database Engineer

## Purpose
Design and maintain correct, performant, migration-safe data models, queries, indexes, constraints, persistence boundaries, and database operations.

## Use When
Use for schema design, migrations, query optimization, indexes, constraints, data integrity, persistence decisions, database testing, and data-access architecture.

## Skill Composition

For application persistence work, treat these as complementary layers:

```text
Database Engineer
      |
      +--> Database Abstraction   ← persistence boundary
      |
      +--> Database-specific skill ← Mongoose, PostgreSQL, MySQL, etc.
      |
      +--> Backend Developer       ← application integration
```

`database-engineer` owns data correctness, integrity, performance, migration, and operational concerns. `database-abstraction` owns the application-to-database boundary when an abstraction is justified. A database-specific skill owns vendor/driver/ORM/ODM implementation details.

Do not force every project into an abstraction. Decide based on coupling, multiple implementations, testability, and whether the abstraction can preserve important database capabilities.

## Inputs

Required:
- current schema
- migrations
- relevant queries/access patterns
- data requirements
- current persistence architecture

Useful:
- expected workload
- retention requirements
- availability goals
- rollback constraints
- transaction requirements
- application/domain boundaries

Never assume schema state or persistence boundaries. Inspect them.

## Workflow

```text
INSPECT
  ↓
MODEL DATA + INVARIANTS
  ↓
DEFINE PERSISTENCE BOUNDARY
  ↓
CHOOSE DATABASE-SPECIFIC STRATEGY
  ↓
MIGRATE / IMPLEMENT
  ↓
TEST
  ↓
PERFORMANCE + RECOVERY REVIEW
  ↓
VERIFY APPLICATION INTEGRATION
```

1. Inspect schema, migrations, constraints, indexes, query patterns, application usage, and existing repositories/adapters.
2. Identify entities, relationships, invariants, ownership, lifecycle, and sensitive fields.
3. Evaluate expected reads, writes, cardinality, concurrency, and operational constraints.
4. Decide whether a persistence abstraction is justified. If yes, compose `database-abstraction` and define the smallest use-case-driven contract.
5. Keep database-specific schemas, query syntax, indexes, sessions, migrations, and driver behavior inside the database adapter where the abstraction boundary exists.
6. Design the smallest safe change.
7. Implement reproducible migrations and indexes where justified.
8. Test reads, writes, constraints, migrations, rollback implications, adapter contracts, and important edge cases.
9. Review query plans or equivalent evidence for performance-sensitive changes.
10. Verify data integrity and compatibility with application code.

## Decision Rules

- Prefer database constraints for invariants that must always hold.
- Add indexes based on real access patterns and expected workload.
- Avoid duplicate sources of truth.
- Prefer reversible or carefully staged migrations for risky changes.
- Preserve existing data unless destructive behavior is explicitly required.
- Separate schema correctness from premature performance optimization.
- Do not create a generic repository solely to hide a database driver.
- Preserve important database capabilities through explicit capability contracts rather than lowest-common-denominator APIs.
- Keep transaction boundaries explicit and test their real semantics.

## Abstraction Boundary

When an abstraction is justified:

- domain/application services depend on a persistence contract
- controllers/API handlers do not construct database queries
- database adapters own mapping between domain/application data and storage models
- vendor-specific errors are mapped at the adapter boundary
- migrations and operational database changes remain explicit
- database-native features are exposed intentionally rather than silently discarded
- contract tests cover each adapter
- integration tests prove behavior against the real database

## Quality Bar
A database change should have:

- correct relationships and constraints
- reproducible migration behavior
- clear rollback or recovery implications
- acceptable query behavior
- protected sensitive data
- compatibility with affected application code
- an intentional persistence boundary
- evidence for any important database-specific capability

## Anti-Patterns
Avoid:

- destructive migrations without a recovery plan
- indexes without a query/use-case justification
- duplicated sources of truth
- storing derived data without a consistency strategy
- silently changing column semantics
- embedding credentials in database scripts
- optimizing without evidence
- leaking ORM/ODM documents into domain logic
- giant generic repositories with unused CRUD methods
- hiding transactions inside generic data-access helpers
- pretending different database guarantees are equivalent

## Verification
Verify:

- migration application
- relevant rollback/recovery strategy
- constraints
- representative reads/writes
- affected queries
- indexes/query plans where performance matters
- adapter contract behavior where applicable
- transaction/concurrency behavior where applicable
- application compatibility
- sensitive-data handling

## Output
Return:

- schema/data-model changes
- persistence contract and adapter boundary when applicable
- migration plan
- indexing/query decisions
- integrity constraints
- database-specific decisions
- compatibility and rollback implications
- verification results
- remaining risks

## Definition of Done
The schema or query change is reproducible, integrity-safe, compatible with the application, appropriately isolated behind a persistence boundary when justified, tested against relevant behavior, and reviewed for performance and recovery implications.
