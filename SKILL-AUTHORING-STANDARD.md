# Skill Authoring Standard

## 1. Purpose

Every skill in this repository must be reliable, focused, discoverable, maintainable, and executable by an agent without hidden context.

A skill is an engineering artifact, not a prompt dump.

## 2. Required Structure

Every production skill must contain a `SKILL.md`.

Use supporting directories only when they add real value:

```text
skill-name/
├── SKILL.md
├── README.md              # optional
├── references/            # optional
├── examples/              # optional
├── scripts/               # optional
└── tests/                 # optional
```

Do not create empty or decorative directories.

## 3. SKILL.md Standard

A production `SKILL.md` should normally contain:

```markdown
# Skill Name

## Purpose
## When to Use
## When Not to Use
## Role / Responsibilities
## Inputs
## Outputs
## Workflow
## Rules / Constraints
## Error Handling
## Validation
## Examples
## Definition of Done
## Limitations
```

Sections may be omitted when genuinely irrelevant, but important behavior must not be left implicit.

## 4. Skill Scope

A skill must have one primary capability.

Good:

- API design
- database migration
- React UI implementation
- security review

Bad:

- general software development
- do everything
- improve the project

If a capability becomes too broad, split it into multiple skills.

## 5. Trigger Design

State precisely when the skill should be used.

Triggers should describe user intent or task characteristics.

Example:

```text
Use this skill when:
- designing a REST API
- reviewing an existing API contract
- adding a new endpoint
```

Also define important non-trigger cases.

Avoid overly broad triggers that cause unnecessary skill activation.

### Frontmatter, contracts, and routing vocabulary

Frontmatter keys, the `consumes` / `produces` artifact contract, and the rules for the words used in the description, Purpose, and trigger sections are defined in `standards/SKILL-AUTHORING-STANDARD.md` under "Frontmatter and Registry Integration". They are mandatory: the registry routes on that text, and a generic word there pulls the skill into unrelated tasks.

## 6. Inputs and Outputs

Define the minimum required information.

Inputs should distinguish:

- required
- optional
- discoverable from the repository

Outputs should be concrete and observable.

Avoid outputs such as "make it better" or "provide a good solution" without acceptance criteria.

## 7. Workflow Design

Workflows should be deterministic enough for another agent to execute.

Prefer:

```text
INSPECT → PLAN → IMPLEMENT → VERIFY → REPORT
```

over vague prose.

Use numbered steps for complex procedures.

For each important decision, define the condition that determines the path.

## 8. Repository Awareness

Before changing an existing project, inspect:

- relevant source files
- project documentation
- existing implementations
- configuration
- tests
- dependency conventions

Reuse existing patterns when appropriate.

Do not invent project conventions without evidence.

## 9. Instructions

Use direct, testable language.

Prefer:

> Run the relevant tests after modifying the authentication service.

Avoid:

> Make sure the authentication service is probably okay.

Avoid contradictory instructions, duplicated rules, and unnecessary narrative.

## 10. Evidence and Assumptions

Skills must distinguish:

- repository evidence
- verified results
- assumptions
- unverified claims

Agents must not fabricate files, APIs, test results, tool output, or project requirements.

If a critical fact cannot be established, stop or report the blocker.

## 11. Error Handling

Every non-trivial skill should define failure behavior.

Minimum pattern:

1. Detect the failure.
2. Identify its cause.
3. Attempt a safe in-scope correction.
4. Re-verify.
5. Report unresolved blockers explicitly.

Do not hide failures or repeatedly retry without new information.

## 12. Security

Never include secrets, API keys, credentials, passwords, private tokens, or personal data in a skill.

Skills that touch code or infrastructure should consider, where relevant:

- authentication
- authorization
- input validation
- injection risks
- secret management
- dependency risk
- unsafe command execution
- sensitive data exposure

## 13. Tooling

Use deterministic tools when they improve reliability.

A script is preferable to model-only reasoning when the task requires exact computation, parsing, validation, formatting, or repeatable checks.

Scripts should:

- have a clear purpose
- document inputs and outputs
- fail clearly
- avoid unnecessary dependencies
- never contain secrets

## 14. References

Move detailed domain knowledge into `references/` when keeping it in `SKILL.md` would make the operational instructions difficult to follow.

`SKILL.md` should explain **what to do**.

Reference material should explain **detailed knowledge needed to do it well**.

## 15. Examples

Examples must be realistic and consistent with the skill.

An example must not demonstrate behavior that the skill itself forbids.

Prefer complete examples over isolated fragments when the workflow is complex.

## 16. Validation

Every skill must have a validation strategy appropriate to its type.

### Documentation skill

Check:

- Markdown validity
- headings
- links
- examples
- internal consistency

### Code skill

Check:

- type checking/build
- tests
- linting where available
- generated structure
- edge cases

### Agent/workflow skill

Check:

- trigger conditions
- task decomposition
- input/output contracts
- failure paths
- tool assumptions
- completion criteria

Never report validation that was not actually performed.

## 17. Definition of Done

A skill is production-ready when:

- purpose is clear
- scope is focused
- trigger conditions are precise
- inputs and outputs are defined
- workflow is executable
- failure handling exists where needed
- security is considered
- examples match behavior
- validation has been performed
- documentation is understandable without hidden context
- it does not unnecessarily duplicate another skill

## 18. Naming

Use lowercase kebab-case for skill directories.

Examples:

```text
api-developer/
database-engineer/
security-engineer/
sd2-orchestrator/
```

Names should describe the capability rather than implementation details.

## 19. Skill Composition

Skills may use other skills when the host agent supports composition.

Do not copy large sections of another skill merely to reuse its behavior.

Reference or delegate to the existing capability instead.

For this repository's SD system:

```text
SD3 → supervises
SD2 → orchestrates
SD1 → executes
Skill → provides specialist method
Tool → provides deterministic execution
```

Keep these responsibilities separate.

## 20. Maintenance

When modifying a skill:

1. Read the existing skill first.
2. Preserve valid existing behavior unless intentionally changing it.
3. Update affected examples and references.
4. Re-run applicable validation.
5. Update documentation when behavior changes.

Avoid documentation drift.

## 21. Review Checklist

Before merging a skill, ask:

- Is the purpose obvious in 30 seconds?
- Is the trigger precise?
- Is the scope narrow enough?
- Could another agent execute it without guessing?
- Are inputs and outputs concrete?
- Are failure cases addressed?
- Are security implications considered?
- Are examples correct?
- Is validation reproducible?
- Does the skill duplicate existing capabilities?
- Does it follow repository conventions?
- Was routing compared before and after, with unrelated tasks unchanged?

## 22. Quality Levels

### L0 — Draft

Concept exists but is not validated.

### L1 — Usable

Clear instructions and basic examples exist.

### L2 — Production

Workflow, failure handling, validation, and documentation are complete.

### L3 — Mature

Production quality plus references, deterministic tooling where useful, tests, strong examples, and maintenance processes.

New skills should target **L2** at minimum. Important core skills should target **L3**.
