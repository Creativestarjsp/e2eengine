# Supabase

Confirm commands with `supabase --help` on the installed CLI; this file is a map, not a transcript.

## Fits

A backend platform: Postgres, authentication, file storage, realtime, and edge functions. It does not host the web frontend; pair it with Vercel, Firebase Hosting, or another host. A natural backend for mobile apps.

## Project files

`supabase/config.toml`, `supabase/migrations/*.sql` (schema history, committed), `supabase/functions/<name>/`, and `supabase/seed.sql` for local data.

## Authentication

- Local: `supabase login`, then `supabase link --project-ref <ref>`.
- CI: `SUPABASE_ACCESS_TOKEN` and the database password as CI secrets, with the project ref as a plain variable.

## Keys and secrets

- The public (anon / publishable) key ships in client code. It is safe only when row-level security is enabled on every exposed table.
- The service-role (secret) key bypasses row-level security. Server-side only. Never in a web bundle, mobile binary, or public variable.
- Edge function secrets: `supabase secrets set <NAME>` reads values from the environment or a file kept out of git.

## Preview deploy

- Local stack: `supabase start` runs Postgres, auth, and storage in containers for development and tests.
- Preview branches: with branching enabled and the Git integration connected, each pull request gets an isolated database with migrations applied.
- Otherwise use a separate staging project and link to it by ref.

## Production deploy

1. Schema: write changes as migrations (`supabase migration new <name>`, or generate one with `supabase db diff`), review the SQL, then `supabase db push` to the linked project.
2. Edge functions: `supabase functions deploy <name>`.
3. Auth settings, storage buckets, and policies: keep them in migrations or config so preview and production match.

Run schema migrations before the application code that depends on them, and keep each migration compatible with the code still serving traffic.

## Rollback

- Schema: migrations run forward. Roll back by writing and pushing a new migration that reverses the change. Destructive changes (dropping a column or table) cannot be reversed without a backup.
- Data: restore from backups or point-in-time recovery, where the plan includes it. Confirm what is available before the first production release.
- Edge functions: redeploy the previous commit.

## Logs

The dashboard's log explorer for the API, auth, database, and functions. The CLI can serve functions locally with `supabase functions serve` for debugging.

## CI notes

Run migrations against a fresh local database in CI (`supabase start`, then `supabase db reset`) so a broken migration fails before it reaches a real project.

## Gotchas

- A table created without row-level security is readable and writable by anyone with the public key.
- Editing the schema in the dashboard creates drift from `supabase/migrations/`. Pull the change into a migration or it will be lost on the next environment.
- Serverless clients should use the pooled connection string, not a direct database connection.
