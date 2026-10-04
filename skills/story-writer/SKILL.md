---
name: story-writer
description: "Turn a PRD, feature request, or backlog item into user stories with verifiable acceptance criteria, platforms, and dependencies, one file per story under stories/. Use when breaking a product or feature into stories, writing or rewriting acceptance criteria, ordering a backlog by dependency, or recording the evidence that closes a story."
version: 1.0.0
level: L2
consumes: PRD.md
produces: stories/
---

# Story Writer

## Purpose

Turn product requirements into small, independently verifiable user stories. Each story states who wants what and why, the acceptance criteria that define done, the platforms it covers, and the stories it depends on. SD2 hands workers one story at a time, and SD3 verifies against its acceptance criteria.

## When to Use

- A PRD or feature request must be broken into stories before design or implementation starts.
- A story is too large, vague, or unverifiable and needs splitting or sharper acceptance criteria.
- A backlog needs ordering by dependency so work can start on stories that are ready.
- A finished story needs its evidence recorded and its status moved to `done`.
- A blueprint is in its `define` phase and `stories/` does not exist yet.

## When Not to Use

- Not a substitute for a PRD: if goals, users, and scope are unknown, write `PRD.md` first (`e2e template copy PRD`).
- Not a substitute for `software-architect`, `api-developer`, or `ui-ux-designer`: a story says what the user can do, never which tables, endpoints, or components deliver it.
- Not a substitute for `qa-engineer`: this skill defines what must be proven; QA designs and runs the tests that prove it.

## Inputs

Required:
- `PRD.md`, or a feature request detailed enough to name the user and the outcome

Discoverable from the repository:
- existing `stories/` files and the highest story number in use
- `DESIGN.md`, `API-CONTRACT.md`, `ARCHITECTURE.md` when they already exist
- which platforms the product ships on (web, mobile, api)

Ask only when it cannot be inferred: who the user is, or what outcome they need.

## Outputs

- One file per story: `stories/STORY-<nnn>-<slug>.md`, created with `e2e story new "<title>"` from the STORY template
- `e2e story check` passing
- A short report: stories written, their dependency order, and any assumptions made

## Story Format

```markdown
# STORY-012: Sign in with email

Status: todo
Platforms: web, mobile
Depends on: STORY-003

As a returning user, I want to sign in with my email and password, so that I can see my data.

## Acceptance Criteria

- AC1: Valid credentials open the home screen.
- AC2: A wrong password shows an error and does not sign the user in.

## Evidence

- AC1:
- AC2:
```

The engine parses these lines exactly: the `# STORY-<n>: <title>` heading, `Status`, `Platforms`, `Depends on`, and `- AC<n>: <text>` under the two headings. Status is one of `todo`, `in-progress`, `done`.

## Workflow

```text
READ → SLICE → WRITE → ORDER → CHECK → REPORT
```

1. **Read.** Read the PRD and any existing stories. Create each new story with `e2e story new "<title>"`, which assigns the next number and file name; never renumber or reuse an id.
2. **Slice.** Split by user outcome, not by layer. "Sign in with email" is a story; "create users table" is a task inside one. A story should be buildable and verifiable on its own in one SD2 plan. Split when a story has more than about six acceptance criteria or mixes unrelated outcomes.
3. **Write.** For each story fill the template. Every acceptance criterion describes something observable: what the user does, what the system shows or stores. Include at least one failure or edge case where the feature has one.
4. **Order.** Set `Depends on` only for real prerequisites (the story cannot be verified until the other is done). Fewer dependencies means more parallel work.
5. **Check.** Run `e2e story check`. It must pass. Fix every error; review every warning.
6. **Report.** List the stories in dependency order (`e2e story next` shows what can start now), and state assumptions made where the PRD was silent.

### Closing a story

A story moves to `done` only when each acceptance criterion has evidence written beside it: a test name and result, a screenshot path, or a command and its output. Then run `e2e story check`; it fails a `done` story with a criterion that has no evidence, or one whose dependency is not done.

## Rules / Constraints

- Acceptance criteria are testable statements. Reject "works well", "is fast", "looks good"; write the measurable form instead ("responds within 2 seconds on a 4G connection").
- One story covers every platform it names with the same criteria, so web and mobile do not drift. Use a platform-specific criterion only for a platform-specific behaviour.
- Do not invent requirements. Where the PRD is silent, write the assumption in `## Notes` and list it in the report.
- Do not write implementation detail into a story.
- Do not mark a story `done` or write evidence for work that was not verified.
- Do not edit a `done` story's criteria. A changed requirement is a new story.
- Never put credentials, tokens, or personal data in a story or its evidence.

## Error Handling

| Situation | Action |
| --- | --- |
| PRD missing or too thin to name users and outcomes | Stop story writing, report the gap, and offer to draft the PRD (`e2e template copy PRD`). |
| `e2e story check` reports a dependency cycle | Find the story that does not truly need the other and remove that dependency, or split the shared part into its own story. |
| A criterion cannot be made testable | Ask what observable result would satisfy it; if unanswered, move it to `## Notes` as an open question. |
| Story is `done` but check reports missing evidence | Set status back to `in-progress` unless the evidence exists and can be recorded now. |
| Two stories describe the same outcome | Merge into the lower-numbered story and delete the other only if it is still `todo`. |

## Validation

- `e2e story check` exits 0.
- Every story has a narrative, at least one acceptance criterion, a status, and platforms.
- Every PRD goal in scope maps to at least one story; state any that do not.
- No story depends on a story that does not exist.

## Examples

`examples/` holds a three-story set for a sign-in feature: one `done` with evidence, one ready, one waiting on a dependency. `e2e story check` passes on it and `e2e story next` returns only the ready story.

## Definition of Done

Stories exist for every in-scope PRD goal, each with testable acceptance criteria; dependencies are real and acyclic; `e2e story check` passes; assumptions are reported.

## Security Considerations

Stories are committed and widely read. Keep secrets, real user data, and internal hostnames out of narratives, criteria, and evidence; reference `CREDENTIALS.md` variable names instead of values.

## Limitations

- The checker validates structure and traceability, not whether a criterion is a good one or whether evidence is truthful; SD3 judges that.
- Story size is a judgement call; the six-criteria guide is a heuristic.
