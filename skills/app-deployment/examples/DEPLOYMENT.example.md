# Deployment

## Targets

| Component | Platform/Host | Environment | URL or Identifier |
| --- | --- | --- | --- |
| Web (Next.js) | Vercel | preview | per-PR URL from the Git integration |
| Web (Next.js) | Vercel | production | https://shop.example.com |
| API (Node, container) | Railway | preview | PR environment `pr-<number>` |
| API (Node, container) | Railway | production | https://api.shop.example.com |
| Database, auth, storage | Supabase | preview | branch per PR |
| Database, auth, storage | Supabase | production | project `shop-prod` |

Chosen because the web app is Next.js (Vercel builds it without configuration), the API holds WebSocket connections (needs a server process, so Railway rather than functions), and the product needs Postgres with row-level security and auth (Supabase).

## Environments

- **Preview:** one per pull request on all three platforms. Uses the Supabase branch database; never production data.
- **Production:** deployed from `main` after approval.

Differences: preview uses Stripe test keys and sends no email.

## Build

- Web: `npm ci && npm run build` (Node 22).
- API: `Dockerfile` at `api/Dockerfile`, image tagged with the commit SHA.

## Configuration

Variable names only; values live where `CREDENTIALS.md` says.

- Web: `NEXT_PUBLIC_SUPABASE_URL`, `NEXT_PUBLIC_SUPABASE_ANON_KEY`, `NEXT_PUBLIC_API_URL`
- API: `DATABASE_URL`, `SUPABASE_SERVICE_ROLE_KEY`, `STRIPE_SECRET_KEY`, `JWT_SECRET`

## Pipeline

Pull request: CI runs tests, platforms build previews, CI runs the smoke test against the preview URLs. Merge to `main`: production deploy job waits for approval in the `production` environment.

## Database Migrations

`supabase db push` runs in the production job before the API and web deploys. Migrations are additive; column removals ship one release after the code stops using them.

## Mobile Release

Not applicable to this component; see the mobile app's own record.

## Smoke Test

```sh
python skills/app-deployment/scripts/smoke_test.py --url <api-url> --path /health --path /api/version --contains ok
python skills/app-deployment/scripts/smoke_test.py --url <web-url> --path / --path /login
```

Expected: every check passes within three attempts.

## Rollback

- **Web:** `vercel rollback <previous-deployment-url>`; confirm with the web smoke test.
- **API:** Railway dashboard → service → Deployments → roll back to the previous deployment; confirm `/health`.
- **Database:** migrations are forward-only. Push a reverting migration. For data loss, restore from point-in-time recovery; the release owner decides.
- Trigger: production smoke test fails, or error rate stays above 2% for five minutes after release.

## Evidence

Latest preview deploy: 2026-10-06, commit `4f2a9c1`, PR 42.

```text
PASS    /health 200 in 184 ms
PASS    /api/version 200 in 97 ms
smoke_test: OK (2/2 checks) https://api-pr-42.example.com
```
