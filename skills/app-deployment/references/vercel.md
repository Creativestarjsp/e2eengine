# Vercel

Confirm commands with `vercel --help` on the installed CLI; this file is a map, not a transcript.

## Fits

Static sites, SPAs, and SSR frameworks (Next.js first). Serverless and edge functions. Not for long-running processes, background workers, or self-hosted databases.

## Project files

`vercel.json` (optional: routes, headers, function settings), `.vercel/` (local link state; keep out of git). Monorepos set the root directory in project settings.

## Authentication

- Local: `vercel login`, then `vercel link`.
- CI: a token passed with `--token`, plus `VERCEL_ORG_ID` and `VERCEL_PROJECT_ID` as environment variables. Scope the token to the team that owns the project.

## Environment variables

Managed per environment (development, preview, production) with `vercel env add | ls | rm` or the dashboard. `vercel env pull` writes a local env file; never commit it. Changing a variable does not affect existing deployments; redeploy.

Variables exposed to the browser (for example `NEXT_PUBLIC_*`) are public. Do not put secrets in them.

## Preview deploy

- Git integration: every push to a non-production branch gets a preview URL.
- CLI: `vercel pull --environment=preview`, `vercel build`, `vercel deploy --prebuilt`. The deployment URL is printed on stdout.

Previews may sit behind Deployment Protection. A smoke test that receives 401 should use the project's automation bypass, not disable protection.

## Production deploy

- Git integration: merge to the production branch.
- CLI: `vercel pull --environment=production`, `vercel build --prod`, `vercel deploy --prebuilt --prod`.
- Or promote an already-verified preview: `vercel promote <deployment-url>`.

## Rollback

`vercel rollback <previous-deployment-url>` or the dashboard's instant rollback. This repoints production at an earlier deployment; it does not revert environment variables or database changes.

## Logs and inspection

`vercel logs <deployment-url>`, `vercel inspect <deployment-url>`, and the dashboard's runtime logs.

## CI notes

Either let the Git integration deploy and have CI only run tests and the smoke test against the preview URL, or disable auto-deploy and run the three CLI steps in CI. Do not do both.

## Gotchas

- Function duration, memory, and payload limits depend on the plan; check before putting slow work in a function.
- Serverless functions open a new database connection per instance; use a pooled connection string.
- Build-time and runtime variables are different sets; a variable missing at build time fails the build, not the request.
