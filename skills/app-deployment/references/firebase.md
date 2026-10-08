# Firebase

Confirm commands with `firebase --help` on the installed CLI; this file is a map, not a transcript.

## Fits

Static sites and SPAs (Hosting), SSR frameworks (App Hosting), serverless backends (Cloud Functions), document database (Firestore), auth, and file storage. A natural backend for mobile apps. Not for relational data or long-running servers; pair with Cloud Run for those (see `gcp.md`).

## Project files

`firebase.json` (what deploys from where), `.firebaserc` (project aliases such as `staging` and `production`), `firestore.rules`, `firestore.indexes.json`, `storage.rules`, `functions/`, and `apphosting.yaml` for App Hosting.

## Authentication

- Local: `firebase login`, then `firebase use <alias>`.
- CI: a service account through Application Default Credentials (`GOOGLE_APPLICATION_CREDENTIALS`), or workload identity federation from the CI provider. The older `login:ci` token flow is deprecated; do not introduce it.

## Environment variables and secrets

- Functions: secrets through `firebase functions:secrets:set <NAME>` (stored in Secret Manager) and bound to the functions that need them.
- Web client config (`apiKey`, `projectId`, …) identifies the project and is not secret. Data is protected by security rules and App Check, not by hiding that config.

## Preview deploy

- Hosting preview channel: `firebase hosting:channel:deploy <channel-id> --expires 7d` returns a temporary URL.
- The official GitHub Action for Hosting creates a channel per pull request.
- Use a separate Firebase project for staging when functions, rules, or data must be isolated; channels only preview Hosting content.

## Production deploy

Deploy only what changed: `firebase deploy --only hosting`, `--only functions:<name>`, `--only firestore:rules,firestore:indexes`, `--only storage`. A bare `firebase deploy` pushes everything in `firebase.json`, including rules.

App Hosting deploys from the connected Git repository through rollouts rather than `firebase deploy`.

## Rollback

- Hosting: roll back to an earlier release from the console's release history, or clone a known-good version onto live with `firebase hosting:clone <site>:<channel-or-version> <site>:live`.
- Functions and rules: redeploy the previous commit. There is no one-command rollback.
- Firestore data: restore from scheduled backups or point-in-time recovery if enabled. Enable it before the first production release.

## Logs

`firebase functions:log`, and Cloud Logging in the Google Cloud console.

## CI notes

Test rules and functions against the emulator suite (`firebase emulators:exec "<test command>"`) before deploying them.

## Gotchas

- Security rules deploy with the app. A permissive rule is a data breach, not a bug; test rules.
- Firestore indexes build asynchronously; queries fail until the index is ready.
- Function cold starts and region choice affect latency; keep functions in the same region as the database.
