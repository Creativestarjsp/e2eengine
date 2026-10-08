# E2E Engineering Rules — Codex Runtime

Use the shared E2E system under `skills/`, `standards/`, `architecture/`, and `runtime/`.

## Execution

Context + Rules → CodeBrain → SD3 → SD2 → SD1 → Skills → Tools → Verification → SD3 approval.

## Runtime

- Shared skills are the source of truth.
- Codex-specific behavior belongs under `.codex/`.
- Use `python -m e2e` or the installed `e2e` command for runtime inspection.
- Never bypass hooks, verification, or security controls.

## Blueprints and Stories

Use `architecture/BLUEPRINTS-AND-STORIES.md` when building a product or feature end to end. Follow the blueprint's current phase, build one story at a time, and never mark a story `done` without evidence for every acceptance criterion.

## Minimality

Before adding code: need → reuse → stdlib → native → installed dependency → simple implementation → custom abstraction.

Minimality never overrides security, validation, accessibility, data integrity, or acceptance criteria.

## Evidence

Do not claim tests, CodeBrain coverage, or verification that was not actually executed. Report limitations explicitly.
