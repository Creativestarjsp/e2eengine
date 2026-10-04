# Skill Authoring Standard

## Purpose

This is the mandatory quality standard for every skill in E2E Skill System.

A skill is maintainable engineering knowledge, not a prompt dump. It must define behavior, boundaries, workflow, decision guidance, verification, and maintenance expectations.

## Runtime-Agnostic Principle

Domain skills are shared across supported coding-agent runtimes, including **Claude Code and Codex**.

Do not create duplicate domain skills merely because the runtime differs.

```text
Claude Code ──┐
              ├── Shared Skill ── Domain behavior
Codex ────────┘
```

Runtime-specific invocation, commands, adapters, or integration behavior belongs in the runtime adapter layer, not in the domain skill.

A skill must not depend on Claude-specific or Codex-specific behavior unless that dependency is explicitly documented and unavoidable.

## Required Skill Identity

Every `SKILL.md` must define:

- purpose
- intended user or agent
- trigger conditions
- non-trigger conditions
- scope
- expected outcomes

## Frontmatter and Registry Integration

Every `SKILL.md` starts with frontmatter. The registry reads it line by line, so each key stays on one line:

```yaml
---
name: skill-name            # kebab-case, identical to the directory name
description: "What the skill does and when to use it."
version: 1.0.0
level: L2
consumes: ARCHITECTURE.md, DATA-MODEL.md   # optional
produces: API-CONTRACT.md                  # optional
---
```

`name` and `description` are required. A skill without frontmatter does not load in runtimes that require it; `e2e skill diagnose` reports those.

### Artifact contract

Declare `consumes` and `produces` only when the skill takes part in a product lifecycle (`architecture/BLUEPRINTS-AND-STORIES.md`). Names are paths from the project root; a trailing `/` means a directory. Every produced document needs a template the project can copy (`e2e template list`), and a blueprint that uses the skill must still pass `e2e blueprint check`.

### Routing vocabulary

The registry selects skills by matching the words of a task against four places: the directory name, the `description`, the Purpose section, and the Use When / When to Use section. Words that few skills use carry the most weight. Therefore:

- Write those four places in the vocabulary of the skill's own domain. A generic word there ("fix", "slow", "build", "create", "test") will pull the skill into unrelated tasks.
- Do not name other skills in those places; their names count as this skill's vocabulary.
- State boundaries in When Not to Use as `Not a substitute for <skill> when …`. A plain "Do not use for X" removes the skill from every task that mentions X.
- After adding or rewording a skill, compare routing before and after for a set of related and unrelated tasks (`e2e context "<task>"` prints the matched skills). Unrelated tasks must not change.

## Scope and Boundaries

Every skill must explicitly define **Do** and **Do Not** responsibilities. Avoid accidental overlap unless skill composition is intentional and documented.

## Inputs and Outputs

Document required inputs, optional inputs, expected context, missing-information behavior, output format, and completion criteria. Never silently invent critical missing information.

## Triggering

Define when the skill should activate and when it should not. Prefer intent-based triggering over vague keyword matching.

## Workflow

A production skill must provide an actionable workflow. A common pattern is:

```text
UNDERSTAND → INSPECT → PLAN → EXECUTE → VERIFY → REVIEW
```

Adapt the workflow to the domain instead of forcing every skill into identical steps.

## Decision Framework

Explain important decisions rather than merely listing facts. Document decision factors, preferred defaults, tradeoffs, escalation conditions, and unacceptable choices.

## Domain Quality Bar

Define what high-quality work means for the domain. Use concrete acceptance criteria where practical. Avoid vague statements such as `make it good` or `use best practices` without defining them.

## Anti-Patterns

Every mature skill should document common failure modes and actively steer the agent away from generic solutions, unnecessary complexity, common implementation mistakes, unsafe behavior, misleading output, premature optimization, and unnecessary dependencies.

## Verification

Every meaningful skill must explain how work is verified. Depending on the domain this may include tests, linting, type checking, static analysis, visual review, schema validation, command output, acceptance criteria, or independent critique.

Never claim successful execution without appropriate evidence.

## Self-Critique

Where judgment materially affects quality, include an explicit critique stage. For example:

```text
PLAN → CRITIQUE → BUILD → VERIFY → CRITIQUE
```

Critique must identify concrete weaknesses and corrective actions.

## Failure and Uncertainty

Define behavior for missing information, conflicting requirements, unavailable tools, failed implementation, failed validation, and ambiguous decisions. Prefer explicit escalation over fabricated certainty.

## Security and Safety

Consider applicable security and safety concerns, including sensitive information, secrets, authorization, untrusted input, unsafe commands, data exposure, and dependency risks. If a category is not materially relevant, state that briefly rather than adding meaningless boilerplate.

## Tooling

Use deterministic tools when they improve reliability:

```text
Skill → Tool / Script → Verified output
```

Tools should have clear inputs, outputs, failure behavior, and documentation.

## References

Move substantial domain knowledge out of `SKILL.md` when it would make the core instructions unnecessarily long. Use `references/` for durable supporting knowledge and explain when the reference should be used.

## Examples

Use examples when they improve execution quality. Examples should demonstrate decisions and behavior, not decorative snippets.

## Composition

A skill may use another skill when the dependency is meaningful. Document why it exists, when to invoke it, what context to pass, and what output is expected. Avoid circular dependencies.

## Agent Compatibility

Skills must work with the E2E hierarchy:

```text
SD3 Supervisor
    ↓
SD2 Orchestrator
    ↓
SD1 Worker
    ↓
Skill
```

A skill should not assume it is always called directly by a human. Its outputs should be usable by workers, orchestrators, and reviewers.

## Runtime Compatibility

When runtime behavior matters, test or reason about the skill through each supported adapter.

At minimum:

- shared domain instructions remain identical
- runtime-specific instructions are isolated
- file paths and commands are valid for the target runtime
- agent handoffs preserve the same task contract
- verification evidence is portable

## Maintainability

Keep instructions explicit, internally consistent, reasonably concise, free of duplicated rules, and independent of temporary project details unless intentionally project-specific.

## Recommended Structure

```text
skills/<skill-name>/
├── SKILL.md
├── references/
├── examples/
└── scripts/
```

Only create supporting directories when they provide real value.

Runtime-specific adapters should live outside the shared skill directory, for example:

```text
.claude/
.codex/
```

## Acceptance Checklist

A skill is ready only when all applicable items pass:

- [ ] purpose is clear
- [ ] triggers are clear
- [ ] frontmatter is complete and each key is on one line
- [ ] routing was compared before and after; unrelated tasks are unchanged
- [ ] artifact contract is declared when the skill takes part in a lifecycle
- [ ] scope is explicit
- [ ] inputs are defined
- [ ] outputs are defined
- [ ] workflow is actionable
- [ ] decisions are explained
- [ ] anti-patterns are documented
- [ ] quality bar is measurable
- [ ] verification is defined
- [ ] failure behavior is defined
- [ ] security/safety is considered
- [ ] references are separated when appropriate
- [ ] examples are useful when appropriate
- [ ] tooling is used where deterministic tooling helps
- [ ] composition dependencies are explicit
- [ ] SD1/SD2/SD3 compatibility is maintained
- [ ] Claude/Codex compatibility is maintained where supported
- [ ] runtime-specific behavior is isolated
- [ ] documentation is internally consistent

## Quality Levels

### L0 — Draft
Concept exists but has not passed the quality checklist.

### L1 — Usable
Clear scope and workflow; basic verification exists.

### L2 — Production
Strong decision framework, anti-patterns, verification, failure handling, and documentation.

### L3 — Reference Quality
Production quality plus strong examples, supporting references/tooling where useful, repeatable validation, and demonstrated reliability across supported runtimes.

New skills should target **L2 minimum**. Core skills should target **L3**.

## Final Principle

Do not optimize for the number of skills. Optimize for the probability that the correct skill produces the correct result consistently across supported agent runtimes.