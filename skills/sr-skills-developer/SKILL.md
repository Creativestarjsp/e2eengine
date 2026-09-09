---
name: sr-skills-developer
description: "Design, implement, review and maintain AI-agent skills to the E2E Skill System standards. Use when creating a new skill, upgrading an existing one, reviewing skill quality, or maintaining the skill library."
---

# SR Skills Developer

## Purpose
Design, implement, validate, review, document, and maintain production-quality AI-agent skills that follow the E2E Skill System standards.

## Use When
Use when creating a new skill, upgrading an existing skill, reviewing skill quality, designing skill references/tools, or maintaining the skill library.

## Do Not Use For
Do not use this as a substitute for a domain specialist when the task is primarily product, frontend, backend, database, security, or DevOps work. Use the relevant specialist skill and this skill only for the skill-engineering layer.

## Inputs

Required:
- target repository
- target skill or capability
- desired behavior

Useful:
- reference implementations
- domain requirements
- examples
- validation requirements

Inspect the repository instead of requiring information that can be discovered there.

## Core Standard

Every skill must follow:

```text
Purpose
→ Trigger
→ Scope
→ Inputs/Outputs
→ Workflow
→ Decisions
→ Anti-Patterns
→ Quality Bar
→ Verification
→ Failure Handling
→ Security/Safety
→ Maintenance
```

Production skills target **L2 minimum**. Core/reference skills target **L3** according to `standards/SKILL-AUTHORING-STANDARD.md`.

## Workflow

```text
INSPECT → DEFINE → DESIGN → IMPLEMENT → SCORE → REVIEW → REFINE → APPROVE
```

### 1. Inspect

Inspect existing skills, standards, repository conventions, related implementations, and available tooling before modifying anything.

### 2. Define

Document:

- purpose
- triggers
- non-triggers
- scope
- inputs
- outputs
- non-goals
- acceptance criteria
- dependencies

### 3. Design

Choose the smallest maintainable structure.

Use supporting files only when they improve reliability:

```text
skills/<skill-name>/
├── SKILL.md
├── references/
├── examples/
└── scripts/
```

### 4. Implement

Write direct, executable instructions. Include domain-specific decision rules, anti-patterns, verification, and failure behavior.

### 5. Score

Use `standards/SKILL-QUALITY-SCORECARD.md`.

A production skill should score at least **22/30** and pass all mandatory gates.

### 6. Review

Review the skill as an independent agent with no hidden context.

Check:

- trigger precision
- scope
- workflow completeness
- decision quality
- anti-pattern coverage
- output usefulness
- verification
- security
- maintainability
- consistency with repository standards

### 7. Refine

Fix findings, remove contradictory instructions, update examples/references, and re-score after material changes.

### 8. Approve

Use the review workflow in `standards/SKILL-REVIEW-WORKFLOW.md`. Core skills should be reviewed toward L3 quality.

## Instruction Quality

Prefer:

> Inspect the existing implementation before creating a new pattern.

Over vague language such as:

> Consider possibly checking the existing implementation.

Use explicit verbs:

- Inspect
- Compare
- Decide
- Implement
- Verify
- Document
- Escalate

Define ambiguous words such as `optimize`, `improve`, or `best` when they are necessary.

## Trigger Design

Triggers should describe task intent and boundaries. Avoid broad triggers that cause accidental activation.

## Input Design

Define minimum required context. Do not require information that can reliably be discovered from the repository.

Never silently fabricate critical missing information.

## Output Design

Outputs must be concrete and reviewable, such as:

- files changed
- skill behavior
- validation results
- scorecard
- examples/references
- known limitations

## Anti-Patterns
Avoid:

- prompt dumps
- giant general-purpose skills
- duplicated rules
- vague motivational language
- hidden assumptions
- contradictory instructions
- examples that disagree with the skill
- unnecessary supporting files
- instructions that depend on temporary project details without saying so

## Tooling

Use deterministic tools when they materially improve reliability.

```text
Skill → Tool/Script → Verified output
```

Tool behavior must be documented and failures must be handled explicitly.

## Security

Never include secrets, credentials, private tokens, or instructions to bypass access controls. Consider secret handling, input validation, authorization, dependency risk, and unsafe command execution when applicable.

## Validation by Skill Type

### Documentation skill
Check structure, links, examples, consistency, and formatting.

### Code-generation skill
Check generated code, tests, type checks, build behavior, and repository conventions.

### Workflow/agent skill
Check triggers, sequencing, outputs, tool assumptions, failure handling, and delegation behavior.

When automation is unavailable, perform a structured manual review and state the limitation.

## Maintenance

When changing a skill:

1. Read the current version.
2. Preserve intentional behavior.
3. Update related examples/references.
4. Re-run the quality scorecard.
5. Re-run applicable validation.
6. Record material changes.

## Definition of Done

A skill is complete when its purpose and triggers are clear, scope is controlled, workflow is executable, decisions are explicit, anti-patterns are covered, quality is defined, verification and failure behavior are present, security is considered, supporting material is consistent, and the skill passes the applicable quality gate.
