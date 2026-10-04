---
name: app-deployment
description: "Deploy a web app, API, or worker to a hosting target and prove the deploy works: choose the target, run preflight, deploy to preview, smoke test, record rollback, then promote to production with owner approval. Covers Vercel, Firebase, Supabase, Railway, AWS, GCP, Azure, and a self-managed VPS. Use when deploying or redeploying an app, choosing where to host, setting up preview and production environments, promoting a release, or rolling back."
version: 1.0.0
level: L2
consumes: ARCHITECTURE.md, CREDENTIALS.md
produces: DEPLOYMENT.md, RELEASE-CHECKLIST.md
---

# App Deployment

## Purpose

Take a built web app, API, or worker to a running, verified deployment on a chosen hosting target, with the rollback path known before the deploy happens. The same procedure applies to every target; target-specific commands live in `references/`.

## When to Use

- Deploying or redeploying a web app, API, or worker to Vercel, Firebase, Supabase, Railway, AWS, GCP, Azure, or a VPS.
- Choosing a hosting target for a new project, or moving between targets.
- Setting up preview, staging, and production environments.
- Promoting a verified preview to production, or rolling back a bad release.
- A blueprint is in its `preview` or `release` phase.

## When Not to Use

- Not a substitute for `mobile-release` when the deliverable is an iOS or Android binary, a store submission, or an over-the-air update.
- Not a substitute for `ci-cd-pipeline` when the work is the automation itself; this skill defines what a deploy must do, that skill wires it into a pipeline.
- Not a substitute for `observability` for logging, error tracking, alerting, and the runbook.
- Not a substitute for `database-engineer` when designing a migration; this skill only sequences when migrations run relative to the deploy.

## Inputs

Required:
- the component to deploy (web frontend, API, worker) and its build command
- the environment: `preview` or `production`

Discoverable from the repository:
- target configuration (`vercel.json`, `firebase.json`, `supabase/`, `railway.json`, `Dockerfile`, cloud config files); `scripts/deploy_preflight.py` detects these
- `ARCHITECTURE.md` (deployment shape), `CREDENTIALS.md` (which variables each environment needs and where values live)
- existing `DEPLOYMENT.md` and CI workflows

Ask when it cannot be inferred: the hosting target for a new project, and who the release owner is.

## Outputs

- A running deployment with a URL or identifier
- `DEPLOYMENT.md` (from `templates/DEPLOYMENT.md`): targets, environments, build, configuration by variable name, smoke test, rollback steps, and evidence of the latest deploy
- `RELEASE-CHECKLIST.md` (from `templates/RELEASE-CHECKLIST.md`) with evidence per item
- A report: what was deployed where, smoke-test result, rollback path, cost-bearing resources created, remaining risks

## Workflow

```text
INSPECT → CHOOSE → PREFLIGHT → CONFIGURE → DEPLOY PREVIEW → SMOKE TEST → RECORD → (APPROVAL) → PROMOTE → VERIFY
```

1. **Inspect.** Read `ARCHITECTURE.md`, `CREDENTIALS.md`, and any `DEPLOYMENT.md`. Run `python skills/app-deployment/scripts/deploy_preflight.py --root <project>` to see which targets are already configured.
2. **Choose.** If a target is already configured, use it. Otherwise pick one with `references/choosing-a-target.md` and state the reason. Do not migrate targets unless asked.
3. **Preflight.** Run `e2e deploy check --env preview` (add `--test "<test command>"`). It runs the secret scan, the story check, the credential register check, this skill's preflight, and the mobile and workflow checks where they apply, and records the result for the current commit. It must pass. Without the engine, run those checks individually.
4. **Configure.** Set each environment's variables in the target's secret store, by the names in `CREDENTIALS.md`. Keep preview and production values separate. Read the target's reference file before running any command.
5. **Deploy to preview.** Use the target's preview mechanism (preview URL, channel, branch environment, tagged revision, staging slot). Never make production the first place a change runs.
6. **Smoke test.** Run `python skills/app-deployment/scripts/smoke_test.py --url <preview-url> --path /health …`. A failing smoke test stops the workflow.
7. **Record.** Write `DEPLOYMENT.md`: target, environment, commit, URL, smoke-test output, and the exact rollback steps for this target. Fill `RELEASE-CHECKLIST.md`.
8. **Approval.** Production needs explicit approval from the release owner, recorded in `RELEASE-CHECKLIST.md`, and a passing `e2e deploy check --env production`. If the plan carries `owner_approval_required`, or no approval has been given in this task, stop here and report.
9. **Promote.** Run database migrations in the order `DEPLOYMENT.md` states, then promote using the target's production mechanism.
10. **Verify.** Smoke test production. If it fails, roll back using the recorded steps, confirm the rollback with the smoke test, and report.

## Rules / Constraints

- Preview before production, every time.
- The engine's tool policy enforces the gate: `deploy.preview` is refused until the preview gate has passed for the current tree, and `deploy.production` until the production gate has passed and approval is given. Any edit or new commit makes the gate stale. Do not work around a refusal; fix what the gate reports.
- Rollback (`deploy.rollback`) needs approval but no gate, so an incident is never blocked by a failing check.
- Never deploy to production, run a production migration, or change production configuration without the release owner's explicit approval for this release.
- Know the rollback before deploying. If a target has no rollback for a component (for example a destructive migration), say so and get approval that names that risk.
- Never print, log, commit, or paste a secret value. Refer to variables by name; values go straight from their store into the target's secret manager.
- In CI prefer short-lived credentials (OIDC / workload identity federation) over long-lived keys wherever the target supports them.
- Platform CLIs change. Before running a deploy command, confirm it against `<cli> --help` for the installed version; treat the reference files as a map, not a transcript.
- Destructive commands (deleting a service, project, database, bucket, or environment; disabling hosting; `destroy`) require separate explicit confirmation, even in preview.
- Report every resource created that can incur cost, and how to remove it.
- Do not change infrastructure unrelated to the task.
- Database migrations must be backward-compatible with the code version still serving traffic during the deploy.

## Error Handling

| Failure | Action |
| --- | --- |
| Preflight fails | Fix the reported item (tracked env file, missing `DEPLOYMENT.md` section) and re-run. Do not deploy around it. |
| Build fails on the target but passes locally | Compare runtime/tool versions and environment variables by name; fix the difference, not the symptom. |
| Preview smoke test fails | Do not promote. Read the target's logs, fix, redeploy preview, re-test. |
| Preview is behind platform authentication (401/403) | Use the target's automation bypass or an authenticated check; do not disable protection project-wide. |
| Production smoke test fails | Roll back immediately using `DEPLOYMENT.md`, confirm with the smoke test, then diagnose. |
| Missing credential or permission | Report the variable name or role needed. Do not request the value in chat; point to `CREDENTIALS.md` for where it lives. |
| CLI command differs from the reference | Trust `--help` and the vendor documentation; note the difference in the report. |

Two failed deploys with the same error is a stop: report the evidence instead of retrying.

## Validation

- `e2e deploy check --env <environment>` passes for the commit being deployed (`e2e deploy status` shows `current: true`).
- `smoke_test.py` exits 0 against the deployed URL, and its output is recorded in `DEPLOYMENT.md`.
- `DEPLOYMENT.md` names the rollback steps for every deployed component.
- No secret values appear in the repository, CI logs, or the report (`e2e guardrails check`).
- For production: approval is recorded in `RELEASE-CHECKLIST.md` with the owner's name and date.

## Examples

`examples/DEPLOYMENT.example.md` shows a filled deployment record for a web frontend on Vercel with an API on Railway and Supabase as the database.

```text
Task: deploy the API to preview.
1. Preflight: target detected `railway` (railway.json); CREDENTIALS.md present; exit 0.
2. Variables set in Railway's preview environment by name: DATABASE_URL, JWT_SECRET.
3. Deploy to the PR environment; URL reported by the platform.
4. smoke_test.py --url <preview-url> --path /health --path /api/version → "smoke_test: OK (2/2 checks)".
5. DEPLOYMENT.md updated with commit, URL, smoke output, and "Rollback: redeploy the previous deployment from the dashboard".
6. Stop: production needs owner approval.
```

## Definition of Done

The component is running on the chosen target; the smoke test passes and is recorded; rollback steps are written and specific to the target; secrets are in the target's store and nowhere else; production was touched only with recorded owner approval.

## Security Considerations

Deployment credentials are the most powerful secrets a project has. Scope tokens to one project and the least privilege that deploys; prefer federated identity in CI; never store them in the repository or echo them in logs. Keep preview environments from reaching production data. Public endpoints need the authentication the architecture specifies before they are exposed, including preview URLs.

## Limitations

- Reference files describe each platform as known when written; vendors change commands, limits, and product names. Verify against current documentation.
- The scripts check structure and reachability. They cannot confirm a platform is configured securely or that a rollback will succeed.
- Kubernetes, multi-region failover, and infrastructure-as-code authoring are out of scope here.
