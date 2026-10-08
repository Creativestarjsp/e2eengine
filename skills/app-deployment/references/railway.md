# Railway

Confirm commands with `railway --help` on the installed CLI; this file is a map, not a transcript.

## Fits

Containerized APIs, workers, and full-stack apps that need a server process, with managed databases alongside. Good when the app needs WebSockets, background jobs, or a persistent process. Less suited to large static sites.

## Project files

`railway.json` or `railway.toml` (config as code: build command, start command, health check path, restart policy, pre-deploy command), and a `Dockerfile` if you do not use the platform's builder.

## Authentication

- Local: `railway login`, then `railway link` to select the project and environment.
- CI: a project token in `RAILWAY_TOKEN`, scoped to one environment.

## Environment variables

Set per service and per environment in the dashboard or with `railway variables`. Reference another service's values with reference variables instead of copying them. `railway run <command>` runs a local command with the environment's variables injected.

## Preview deploy

- With the Git integration, enable pull-request environments: each PR gets an isolated copy of the environment that is removed when the PR closes.
- CLI: `railway up --environment <name> --service <name>` deploys the current directory to a non-production environment.

## Production deploy

- Git integration: merge to the branch the production environment watches.
- CLI: `railway up --environment production --service <name>`; in CI add the flag that streams build logs and exits with the build result.

Set a health check path in config. The platform waits for it to return success before switching traffic to the new deployment, which prevents a broken build from going live.

## Rollback

From the dashboard: open the service's deployments and roll back to an earlier one. That restores the earlier image and its variables. Database changes are not reverted.

## Logs

`railway logs` for the linked service, or the dashboard's build and deploy logs.

## CI notes

Choose one deploy path: the Git integration, or `railway up` from CI. Running both deploys every commit twice.

## Gotchas

- The app must listen on the port in the `PORT` variable and bind to `0.0.0.0`.
- Filesystem writes are lost on redeploy unless a volume is attached.
- Run migrations as a pre-deploy command so a failed migration stops the deploy.
