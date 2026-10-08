# Google Cloud (GCP)

Confirm commands with `gcloud <group> --help` on the installed CLI; this file is a map, not a transcript.

## Fits

Containerized APIs and web apps on Cloud Run, with Cloud SQL, Firestore, or other Google services. Use Firebase Hosting for static frontends (see `firebase.md`).

## Pick the service by shape

| Shape | Service |
| --- | --- |
| Containerized API, SSR app, or worker | Cloud Run |
| Static site or SPA | Firebase Hosting |
| Event-driven function | Cloud Run functions |
| Single server you manage | Compute Engine; follow `vps.md` |

## Authentication

- Local: `gcloud auth login`, `gcloud config set project <id>`.
- CI: workload identity federation with the official auth action, impersonating a deploy service account. Avoid downloaded service-account keys.
- Give the deploy service account only the roles needed to deploy that service.

## Configuration and secrets

Secret Manager. Mount secrets into Cloud Run with `--set-secrets=<ENV_NAME>=<secret>:<version>`; plain settings with `--set-env-vars`.

## Preview deploy

Deploy a revision that receives no traffic and reach it by tag:

`gcloud run deploy <service> --image <image> --region <region> --no-traffic --tag <tag>`

The command prints a tag-specific URL for the smoke test. Alternatively deploy a separate `<service>-staging` service or use a staging project.

## Production deploy

- New revision straight to traffic: `gcloud run deploy <service> --image <image> --region <region>`.
- Or shift traffic to the verified tagged revision: `gcloud run services update-traffic <service> --region <region> --to-tags <tag>=100`, optionally in steps for a gradual rollout.
- Build images with `gcloud builds submit --tag <image>` into Artifact Registry, tagged with the commit SHA.

## Rollback

`gcloud run revisions list --service <service> --region <region>`, then `gcloud run services update-traffic <service> --region <region> --to-revisions <previous-revision>=100`. Instant, and it does not rebuild.

## Logs

`gcloud run services logs read <service> --region <region>`, or Cloud Logging.

## CI notes

Authenticate, build and push the image, deploy with `--no-traffic --tag`, smoke test the tagged URL, then shift traffic. That sequence gives a verified promotion with a one-command rollback.

## Gotchas

- The container must listen on the port in `PORT`.
- Services are private unless deployed with unauthenticated access allowed; decide deliberately.
- Request timeouts and CPU-only-during-requests behaviour affect background work; use jobs or always-allocated CPU when needed.
- Cloud SQL needs the instance connection attached to the service and a pooled connection strategy.
