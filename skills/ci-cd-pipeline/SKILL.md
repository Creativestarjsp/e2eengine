---
name: ci-cd-pipeline
description: "Set up and maintain CI/CD pipelines with GitHub Actions: continuous integration on every pull request, automated preview deployment, and a production deployment gated by approval. Use when adding or repairing a CI workflow, automating a deployment, adding a pipeline quality gate, or auditing GitHub Actions workflows for unsafe patterns."
version: 1.0.0
level: L2
consumes: DEPLOYMENT.md
---

# CI/CD Pipeline

## Purpose

Turn the verification and deployment steps a project already performs by hand into a pipeline that runs them the same way every time: every change is verified before merge, the verified artifact is the one deployed, preview is automatic, and production waits for a person.

## When to Use

- Adding continuous integration that runs on every pull request.
- Automating a deployment that has already been performed by hand and recorded in `DEPLOYMENT.md`.
- Adding a pipeline quality gate.
- Repairing a broken or unreliable CI workflow run.
- Auditing GitHub Actions workflows for unsafe patterns.

## When Not to Use

- Not a substitute for `app-deployment` or `mobile-release`: those decide the target and prove the first deploy by hand; this skill automates what they recorded in `DEPLOYMENT.md`.
- Not a substitute for `qa-engineer` when the tests themselves need designing.
- Not a substitute for `security-engineer` for a full review of the pipeline's trust boundaries.

## Inputs

Required:
- the repository and its build, test, and lint commands

Discoverable from the repository:
- existing `.github/workflows/*.yml`
- language and package manager (lockfiles), runtime versions
- `DEPLOYMENT.md`: targets, build, smoke test, and which environment needs approval
- `CREDENTIALS.md`: which pipeline secrets exist and where they are stored

Ask when it cannot be inferred: which branch is production, and who may approve a production deploy.

## Outputs

- Workflow files under `.github/workflows/`
- The `## Pipeline` section of `DEPLOYMENT.md`: triggers, stages, gates, approvers
- New pipeline secrets registered by name in `CREDENTIALS.md`
- `workflow_lint.py` passing, and a link or log of one successful run as evidence

## Pipeline Shape

```text
pull request → install (cached) → lint + type check → test → build → deploy preview → smoke test
merge to main → build once → [approval] → migrate → deploy production → smoke test → (roll back on failure)
```

- **CI** (`templates/ci.yml`): runs on every pull request and on the main branch. It is the required check for merging.
- **Preview deploy**: after CI passes, deploy and smoke test. The preview URL is posted on the pull request.
- **Production deploy**: a separate job bound to a protected `production` environment, so the platform enforces the approval.

## Workflow

```text
INSPECT → DESIGN → WRITE → LINT → RUN → RECORD
```

1. **Inspect.** Read existing workflows and `DEPLOYMENT.md`. Find the project's real commands in its manifest; do not invent script names.
2. **Design.** List the jobs, what each needs, and what gates the next. Keep CI under a few minutes with dependency caching and by running independent jobs in parallel.
3. **Write.** Start from `templates/ci.yml`. For deploy jobs, follow the authentication and steps for the target in `references/github-actions.md`.
4. **Lint.** Run `python skills/ci-cd-pipeline/scripts/workflow_lint.py --root <project>`. It must exit 0.
5. **Run.** Push to a branch and watch the run. A workflow that has never run is not done.
6. **Record.** Update `DEPLOYMENT.md` and `CREDENTIALS.md`. Tell the user which repository settings they must apply by hand: required checks, environment approvers, secrets.

## Rules / Constraints

- Declare `permissions:` in every workflow and grant the least each job needs. Default to `contents: read`.
- Pin third-party actions to a released version tag or a commit SHA, never a branch. Check the action's releases for the current version instead of copying a number from memory.
- Use federated identity (OpenID Connect) for cloud credentials where the target supports it. Long-lived keys are the fallback and are registered in `CREDENTIALS.md` with a rotation policy.
- Never print a secret, and never interpolate `${{ secrets.* }}` or untrusted event fields (titles, branch names, comment bodies) directly inside a `run:` script. Pass them through `env:`.
- Do not use `pull_request_target` to build or run code from a pull request.
- Production deploy jobs declare `environment: production` and a `concurrency` group so two releases cannot overlap.
- Build once and deploy that artifact. Do not rebuild between preview and production.
- Every job has a `timeout-minutes`.
- A failing check is fixed or the change is reverted. Do not make a check pass by skipping it, deleting tests, or adding `continue-on-error`.
- Pipeline changes that affect production deploys need the release owner's review.

## Error Handling

| Failure | Action |
| --- | --- |
| Workflow lint fails | Fix each error; warnings are reviewed and either fixed or justified in the report. |
| Job fails only in CI | Compare tool versions, environment variables by name, and missing services with the local run. |
| Flaky job | Find the nondeterminism (timing, order, shared state, network). Retries hide it; use them only for external network steps. |
| Secret not available | Check it exists for that environment and that the job declares the environment. Report the name, never ask for the value in chat. |
| Deploy job cannot authenticate | Check the trust policy or federated credential for the repository, branch, and environment it allows. |
| Production deploy failed mid-way | Run the rollback in `DEPLOYMENT.md`, then diagnose. |

Two consecutive failures with the same cause is a stop: report evidence instead of re-running.

## Validation

- `workflow_lint.py` exits 0.
- One successful pull-request run and, for deploy workflows, one successful preview deploy with a passing smoke test.
- The production job waits for approval when triggered.
- No secret appears in workflow files or run logs.

## Examples

`templates/ci.yml` is a starting CI workflow. `references/github-actions.md` lists, for each target, how the deploy job authenticates and which steps it runs.

## Definition of Done

Every pull request is tested before merge; preview deploys and is smoke tested automatically; production requires an approval enforced by the platform; credentials are short-lived or registered; the workflow has run successfully and the lint passes.

## Security Considerations

A pipeline can read every secret and deploy to production, so it is a primary attack surface. The common failures are: a compromised or moving third-party action, code from an untrusted pull request running with secrets, script injection through event fields, and over-broad tokens. The rules above and `workflow_lint.py` address each. Treat workflow files as production code and review their changes.

## Limitations

- Templates and references target GitHub Actions. The pipeline shape and rules apply to other CI systems, but no templates are provided for them.
- `workflow_lint.py` is line-based. It catches the common unsafe patterns, not every one; it is not a replacement for a security review.
- Repository settings (branch protection, environment approvers, secrets) cannot be set from workflow files and must be applied by someone with access.
