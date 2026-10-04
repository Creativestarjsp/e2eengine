# E2E Engineering Rules

This repository is the canonical, runtime-neutral engineering system for AI-assisted software development.

## Mission

Build skills and agent infrastructure that are focused, executable, verifiable, secure, maintainable, and reusable across supported runtimes.

## System Model

```text
Context + Rules
      ↓
CodeBrain
      ↓
SD3 Supervisor
      ↓
SD2 Orchestrator
      ↓
SD1 Workers
      ↓
Specialist Skills
      ↓
Tools / Implementation
      ↓
Verification
```

## Before Changing Anything

1. Inspect the repository.
2. Read relevant standards, architecture documents, and affected skills.
3. Reuse existing conventions.
4. Identify affected files and dependencies.
5. Define the smallest safe change.
6. Define verification before implementation.

Never invent repository facts when they can be inspected.

## Skill Rules

- Preserve existing skills unless a deliberate migration is approved.
- Keep each skill focused on one capability.
- Avoid unnecessary duplication.
- Define purpose, triggers, scope, inputs, outputs, workflow, quality bar, verification, failure handling, and security considerations.
- Shared skill knowledge must remain runtime-neutral.
- Claude/Codex-specific behavior belongs in runtime adapters.
- Use the skill registry/composition model when routing work.

## SD Rules

- SD1 executes assigned work.
- SD2 decomposes, routes, sequences, parallelizes safe work, integrates, and escalates.
- SD3 independently verifies requirements, implementation, security, testing, and integration.
- Default maximum active SD1 workers: 4.
- Do not create unsafe concurrent edits.
- Do not retry failures indefinitely.

## Context and CodeBrain

Use `architecture/CONTEXT-AND-RULES.md` for context precedence and bounded context packages.

Use `architecture/CODEBRAIN.md` for repository graph, symbol, dependency, retrieval, and impact-analysis contracts. CodeBrain facts must have provenance and incomplete coverage must be reported.

## Blueprints and Stories

Use `architecture/BLUEPRINTS-AND-STORIES.md` when building a product or feature end to end. Follow the blueprint's current phase, build one story at a time, and never mark a story `done` without evidence for every acceptance criterion.

## Verification

Use `architecture/VERIFICATION.md`. Completion claims require evidence. Distinguish facts, inspected evidence, assumptions, and unknowns.

## Hooks, Security, and Memory

Follow:

- `architecture/HOOKS-AND-GUARDRAILS.md`
- `architecture/MEMORY.md`
- `architecture/RELEASE-GATES.md`

Never embed secrets or credentials. Never use rules or memory to bypass safety controls.

## Workflow

UNDERSTAND → INSPECT → DEFINE → DESIGN → IMPLEMENT → VALIDATE → REVIEW → VERIFY → DOCUMENT

## Completion

A change is complete only after relevant validation has been performed, evidence has been recorded, and affected documentation/contracts are synchronized.
