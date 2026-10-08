# Blueprints and Stories

## Purpose

Carry a product from requirements to a deployed, operable release with every
step gated by an artifact, instead of relying on the wording of each task to
pick the right specialists.

Three pieces work together:

| Piece | Answers | Lives in | Engine module |
|---|---|---|---|
| Skill contract | What does this skill read and leave behind? | `consumes:` / `produces:` in `SKILL.md` frontmatter | `e2e/skills.py` |
| Blueprint | Which phases does this product type go through, and what ends each? | `workflows/<name>.json` | `e2e/blueprints.py` |
| Story | What is one feature, and what proves it is done? | `stories/STORY-<n>-<slug>.md` | `e2e/stories.py` |

## Lifecycle

```text
PRD.md
  → define        story-writer                      → stories/
  → architecture  software-architect                → ARCHITECTURE.md
  → contracts     database-engineer → api-developer → DATA-MODEL.md, API-CONTRACT.md
                  ui-ux-designer                    → DESIGN.md
  → build         backend ∥ web ∥ mobile ∥ qa       → every story done, with evidence
  → harden        security, code review, credentials, → CREDENTIALS.md, UX-REVIEW.md
                  UX review of the built screens
  → preview       app-deployment → ci-cd-pipeline,  → DEPLOYMENT.md, RELEASE-CHECKLIST.md
                  mobile-release
  → release       app-deployment → mobile-release,  → RUNBOOK.md
                  observability (owner approval)
```

A phase may start only when the phases it depends on are complete and the
blueprint's inputs exist. A phase is complete when its artifacts exist and, for
the build phase, every story is `done`.

## Skill Contracts

```yaml
consumes: ARCHITECTURE.md, DATA-MODEL.md
produces: API-CONTRACT.md
```

- Artifact names are paths relative to the project root; a trailing `/` means a directory.
- Each produced document has a template in `templates/` (the credential register's lives with its skill).
- Contracts are enforced when a blueprint is used. Outside a blueprint they are
  advisory: a skill asked to add one endpoint does not need an architecture document.
- `e2e blueprint check` fails when a phase needs an artifact that no input,
  earlier phase, or skill in the same phase provides, or when a phase claims an
  artifact none of its skills produces.

## Blueprints

Schema and commands: `workflows/README.md`.

SD2 behaviour with `--blueprint`:

1. The first ready phase supplies the skills. Task text no longer selects them.
2. Inside the phase, workers are ordered by contract: a skill that consumes what
   another produces waits for it. Everything else runs in parallel, up to the
   worker limit; skills beyond the limit are reported as deferred.
3. Missing inputs, a completed blueprint, or no ready phase are reported as
   `blockers`, and no worker is launched.
4. A phase marked `approval: owner` sets `owner_approval_required` on the SD3
   gate. The engine reports the requirement; it never grants the approval.

## Stories

Format: `templates/STORY.md`. Authoring method: `skills/story-writer/SKILL.md`.

- `Status`: `todo`, `in-progress`, `done`.
- `Depends on`: stories that must be `done` first. SD2 will not start a story with unmet dependencies.
- `Platforms`: a web-only story does not launch mobile workers, and the reverse.
- Acceptance criteria (`- AC1: …`) are handed to the workers and to SD3. The SD3
  gate gains the `acceptance-traceability` check and the criteria themselves.
- A story is `done` only when every criterion has evidence. `e2e story check`
  fails otherwise.

Inside a blueprint, a story can be planned only in the phase that sets
`requires_stories_done`; asking earlier yields a blocker naming the phase that
must finish first.

## Design Quality

Three things raise the quality of what gets designed and built:

- **Screen patterns.** `ui-ux-designer` starts each screen from a proven pattern (`skills/ui-ux-designer/references/screen-patterns.md`) and records deviations in `DESIGN.md`.
- **Illustration.** `vector-illustration` decides whether a view needs artwork at all, produces original SVG, validates it (`svg_check.py`), and renders it for review (`render_preview.py`). When generated artwork is not good enough, a person downloads a replacement from unDraw; the agent never crawls or downloads from that site.
- **Motion.** `lottie-animation` authors loaders, success feedback, and microinteractions as Lottie files, using the vendored `text-to-lottie` method (MIT, from diffusionstudio/lottie) with our own checker (`lottie_check.py`) and a CanvasKit/Skottie frame renderer (`lottie_preview.mjs`), so a browser player is not needed to verify them.
- **Motion in components.** `ui-motion` specifies and implements transitions, feedback, enter/exit, layout and gesture motion with CSS and Motion on web and Reanimated on React Native; reduced motion is mandatory and `motion_check.py` fails a project that animates without handling it.
- **Visual review.** In the `harden` phase `ux-laws` captures every built screen at a phone and a desktop width (`capture_screens.py`), looks at the images, and writes `UX-REVIEW.md`. Critical and High findings go back to the developer skills before release.

These checks need a browser to render. Without one the scripts say so, and the review must state that the screens were not looked at.

## Deployment Phases

Four skills run the last two phases. Each checks its own preconditions with a script, so a deploy cannot rest on a copied template:

| Skill | Does | Script |
|---|---|---|
| `app-deployment` | Deploys web and backend components to Vercel, Firebase, Supabase, Railway, AWS, GCP, Azure, or a VPS; writes `DEPLOYMENT.md` and `RELEASE-CHECKLIST.md` | `deploy_preflight.py`, `smoke_test.py` |
| `ci-cd-pipeline` | Automates the recorded deploy in GitHub Actions | `workflow_lint.py` |
| `mobile-release` | Builds, distributes to testers, submits to the stores, publishes OTA updates | `mobile_preflight.py` |
| `observability` | Health checks, logs, error tracking, alerts; writes `RUNBOOK.md` | uses `smoke_test.py` |

In `preview`, the app is deployed first; the pipeline and the mobile build wait for it because they consume `DEPLOYMENT.md`. In `release`, production is promoted first, then monitoring is verified and the mobile app submitted. `deploy_preflight.py --env production` fails unless `DEPLOYMENT.md` has real targets, smoke test, rollback, and evidence, and `RELEASE-CHECKLIST.md` names the release owner and approval date.

## Using the System in Another Project

Skills, blueprints, and templates live together in this repository. A project adopts them with one command:

```sh
e2e init --skills-path <path-to-this-repo>/skills
```

`init` records the skills path and, when `workflows/` and `templates/` sit beside it, records those too (`blueprints_paths`, `templates_paths` in `e2e.json`). Override with `--blueprints-path` / `--templates-path`, or with `E2E_BLUEPRINTS_PATH` / `E2E_TEMPLATES_PATH`. The project's own `workflows/`, `.e2e/workflows/`, `templates/`, and `.e2e/templates/` are searched first, so a project can override a shared blueprint or template by name.

Lifecycle documents start from templates the project can always reach:

```sh
e2e template list
e2e template copy PRD            # never overwrites; never writes outside the project
e2e story new "Sign in with email"   # next number, file name, and heading from the STORY template
```

## Commands

```sh
e2e story list | check | next | new "<title>"
e2e template list | copy <name> [destination]
e2e blueprint list | check | status <name>
e2e orchestrate "<task>" --blueprint <name> [--story STORY-<n>]
e2e execute     "<task>" --blueprint <name> [--story STORY-<n>]
e2e deploy check --env preview|production [--test "<command>"]
e2e deploy status
```

Without `--blueprint` and `--story`, planning behaves exactly as before.

## Limits

- Artifact checks test presence, not quality. A copied, unfilled template
  completes a phase as far as the engine can tell; SD3 judges the content.
- Only the first ready phase is planned, even when two phases could run side by side.
- Evidence is recorded text. The engine does not run the test it names.
- The engine decides whether a deploy capability may be used (`architecture/TOOL-SYSTEM.md`,
  Deploy gate) but does not run the platform's deploy command itself; an agent
  with unrestricted shell access is bound by the skill rules, not by the gate.
