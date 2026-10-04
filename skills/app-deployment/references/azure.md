# Azure

Confirm commands with `az <group> --help` on the installed CLI; this file is a map, not a transcript.

## Fits

Organizations on Microsoft's cloud, and apps using Azure databases or identity.

## Pick the service by shape

| Shape | Service |
| --- | --- |
| Static site or SPA, optionally with a small API | Static Web Apps |
| Web app or API from code or a container | App Service |
| Containerized API or worker with scale-to-zero | Container Apps |
| Event-driven function | Azure Functions |
| Single server you manage | Virtual Machine; follow `vps.md` |

## Authentication

- Local: `az login`, `az account set --subscription <id>`.
- CI: the official login action with OpenID Connect and a federated credential on an app registration or managed identity. Avoid client secrets in CI.
- Scope the role assignment to the resource group being deployed.

## Configuration and secrets

Key Vault for secrets. App Service and Container Apps can reference Key Vault entries from app settings, so values stay out of configuration files.

## Preview deploy

- **Static Web Apps:** the official GitHub Action creates a preview environment per pull request and removes it when the PR closes. Routing lives in `staticwebapp.config.json`.
- **App Service:** deploy to a `staging` deployment slot and test the slot's URL.
- **Container Apps:** in multiple-revision mode, deploy a new revision at 0% traffic and test its revision URL.

## Production deploy

- **Static Web Apps:** merge to the production branch.
- **App Service:** `az webapp deployment slot swap --resource-group <rg> --name <app> --slot staging --target-slot production`.
- **Container Apps:** `az containerapp update --name <app> --resource-group <rg> --image <image>`, then `az containerapp ingress traffic set` to move weight to the new revision.

## Rollback

- App Service: swap the slots back; the previous version is still in the staging slot.
- Container Apps: `az containerapp revision list`, then set traffic back to the previous revision.
- Static Web Apps: redeploy the previous commit.

## Logs

`az webapp log tail --name <app> --resource-group <rg>`; `az containerapp logs show --name <app> --resource-group <rg> --follow`; Application Insights for traces and errors.

## CI notes

Slot swap and revision traffic-shifting both give a tested artifact in production without a rebuild. Prefer them to deploying straight to the production slot.

## Gotchas

- Mark environment-specific app settings as slot settings, or a swap carries staging configuration into production.
- Always-on and minimum-replica settings affect cold starts and cost.
- Resource names are often globally unique; keep them in configuration, not scattered through scripts.
