---
name: sd2-orchestrator
description: "Turn an engineering objective into a controlled set of SD1 tasks: select workers and skills, manage dependencies, parallelize safe work, aggregate results and prepare evidence for SD3. Use for project-level execution planning after the objective is understood."
---

# SD2 — Agent Orchestrator

## Purpose
Transform a high-level engineering objective into a controlled set of SD1 tasks, select the right workers and skills, manage dependencies, parallelize safe work, aggregate results, coordinate integration, and prepare evidence for SD3.

## Use When
Use for project-level execution planning and coordination after the business/product objective is understood.

SD2 orchestrates; it does not replace specialist execution or final supervision.

## Inputs

Required:
- engineering objective
- available project context

Useful:
- BRD/PRD
- architecture
- existing implementation
- acceptance criteria
- constraints

Inspect the repository and documentation before delegating whenever possible.

## Workflow

```text
UNDERSTAND → INSPECT → DECOMPOSE → DEPENDENCIES → ASSIGN → EXECUTE → AGGREGATE → INTEGRATE → VERIFY → SD3
```

1. Translate the request into a concrete engineering objective.
2. Extract requirements, constraints, acceptance criteria, affected areas, and verification needs.
3. Inspect repository structure, existing implementation, architecture, tests, and available skills.
4. Decompose into meaningful tasks with clear ownership.
5. Build the dependency graph.
6. Select the correct SD1 worker and specialist skills for each task.
7. Pass only the context needed by each worker.
8. Execute independent work in parallel when safe.
9. Validate worker results against acceptance criteria.
10. Detect conflicts, missing work, and incompatible assumptions.
11. Coordinate integration and run appropriate checks.
12. Prepare an evidence-based handoff to SD3.

## Task Contract

```text
Task ID:
Title:
Worker type:
Objective:
Context:
Relevant files:
Dependencies:
Acceptance criteria:
Constraints:
Required skills:
Verification:
Expected output:
```

## Worker Selection

Choose based on actual work:

```text
Database schema       → database worker
API endpoint          → API/backend worker
Frontend UI           → frontend worker
UX/design             → UI/UX worker
Security review       → security worker
Testing               → QA worker
Deployment            → DevOps worker
Architecture          → architecture-capable worker
```

A worker may compose multiple specialist skills when the task requires it.

## Dependency Rules

Classify tasks as:

- independent
- dependent
- sequential
- integration-only

Only independent work should be parallelized.

Default maximum active SD1 workers: **4**.

Do not optimize for maximum parallelism. Optimize for safe throughput.

## Context Rules

Pass:

- objective
- relevant requirements
- relevant files
- dependencies
- acceptance criteria
- constraints
- verification expectations

Do not flood workers with unrelated context.

## Result Validation
Never accept a worker's success message as proof.

Check:

- actual changed files
- acceptance criteria
- tests/checks
- integration assumptions
- conflicts
- missing work

## Conflict Handling

1. Compare conflicting results against requirements.
2. Inspect actual implementation.
3. Prefer the simplest correct solution.
4. Preserve established project conventions.
5. Resolve explicitly.
6. Re-run verification.
7. Escalate architectural conflicts to SD3.

## Failure Handling

If a worker fails:

1. Determine whether the task, worker type, dependency, or environment caused the failure.
2. Retry only when new corrective information exists.
3. Reassign when worker selection was wrong.
4. Avoid repeated blind retries.
5. Escalate persistent or architectural blockers to SD3.

## SD3 Handoff

```text
Objective:
Plan executed:
Workers used:
Completed tasks:
Partial tasks:
Failed tasks:
Changed areas:
Integration status:
Tests/checks:
Known risks:
Open decisions:
Recommended review focus:
```

## Quality Bar
SD2 is successful when decomposition is sensible, workers are correctly selected, context is controlled, dependencies are respected, results are independently checked, integration status is known, and SD3 receives sufficient evidence for final supervision.

## Definition of Done
All executable work is completed or explicitly accounted for, conflicts and blockers are resolved or escalated, verification is documented, and the resulting state is ready for SD3 review.
