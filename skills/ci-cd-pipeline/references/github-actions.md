# GitHub Actions: Deploy Jobs by Target

Check each action's releases for its current version before pinning. Names below are the publishers' official actions as known when written; confirm they are still maintained.

## Job skeleton for any deploy

```yaml
deploy-production:
  needs: [test]
  if: github.ref == 'refs/heads/main'
  runs-on: ubuntu-latest
  timeout-minutes: 20
  environment: production            # approval is enforced by the environment's protection rules
  concurrency: deploy-production     # never two releases at once
  permissions:
    contents: read
    id-token: write                  # only when the job uses OpenID Connect
  steps:
    - uses: actions/checkout@<version>
    # authenticate → build or fetch artifact → migrate → deploy → smoke test
```

Environment secrets are available only to jobs that declare that environment, which keeps production credentials away from pull-request jobs.

## Authentication and steps per target

| Target | How the job authenticates | Deploy step |
| --- | --- | --- |
| Vercel | Token secret plus org and project ids as variables | `vercel pull`, `vercel build`, `vercel deploy --prebuilt` (add `--prod` for production); or let the Git integration deploy and only smoke test |
| Firebase | Service account through workload identity federation, or a key in a secret | The Firebase Hosting deploy action for channels and live; `firebase deploy --only …` for functions and rules |
| Supabase | Access token and database password secrets; project ref as a variable | The Supabase CLI setup action, then `supabase link`, `supabase db push`, `supabase functions deploy` |
| Railway | Project token secret scoped to one environment | Install the CLI, `railway up` for the service and environment in CI mode |
| AWS | OpenID Connect: the AWS credentials action assumes an IAM role | Push image to ECR and update the ECS service; or `aws s3 sync` and a CloudFront invalidation |
| GCP | OpenID Connect: the Google auth action with workload identity federation | The Cloud Run deploy action or `gcloud run deploy` with `--no-traffic --tag`, then shift traffic |
| Azure | OpenID Connect: the Azure login action with a federated credential | Static Web Apps deploy action; or deploy to a slot and swap; or `az containerapp update` |
| VPS | SSH deploy key in a secret, host key pinned in `known_hosts` | Build and push the image, then over SSH: pull and `docker compose up -d` |
| Expo (mobile) | Expo access token secret | The Expo setup action, then `eas build --non-interactive`, `eas submit`, or `eas update` |

## After every deploy step

```yaml
- name: Smoke test
  run: python skills/app-deployment/scripts/smoke_test.py --url "$DEPLOY_URL" --path /health
  env:
    DEPLOY_URL: ${{ steps.deploy.outputs.url }}
```

Pass values through `env:` as above. Do not write `${{ … }}` inside the script text.

## Quality gates worth adding

- `e2e deploy check --env preview` (or `production` in the production job): one command for the secret scan, story check, credential register, deploy preflight, mobile preflight, and workflow lint
- `e2e story check` when the project uses stories
- `python skills/credential-inventory/scripts/credentials_check.py --code-scan --strict`
- `e2e guardrails check --stage pre-merge` for the secret scan
- `python skills/ci-cd-pipeline/scripts/workflow_lint.py` on changes to `.github/workflows/`

## Pull requests from forks

Workflows triggered by `pull_request` from a fork receive no secrets and a read-only token. That is the safe default: run tests there, and deploy previews only for branches in the repository. Do not switch to `pull_request_target` to get secrets.

## Caching

Use the setup action's built-in dependency cache keyed on the lockfile. Cache dependencies, not build outputs that depend on secrets or environment.

## Settings to apply by hand

- Branch protection on the production branch: require the CI check and a review.
- Environment `production`: required reviewers; restrict to the production branch.
- Secrets and variables at environment scope, not repository scope, where they are environment-specific.
