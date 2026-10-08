---
name: credential-inventory
description: "Maintain a project CREDENTIALS.md register that records every credential, API key, token, env var, and secret-backed configuration the project needs: variable name, service, purpose, environments, where the value is stored, owner, and rotation, never the value itself. Use when adding an integration that needs API keys or tokens, onboarding a developer who asks which env vars or environment variables they need to run the project, auditing which secrets a project depends on, or before a release. Not for storing secret values, generating or rotating keys, or reviewing application security."
version: 1.0.0
level: L2
produces: CREDENTIALS.md
---

# Credential Inventory

## Purpose

Keep one authoritative, committed register (`CREDENTIALS.md`) of every credential a project depends on, so a developer or agent can answer "what do I need, where do I get it, and where does it live" without reading the whole codebase or asking around. The register holds metadata only. Values stay in the project's secret store (`.env`, a password manager, a cloud secret manager, CI secrets).

## When to Use

- A new integration, SDK, database, or third-party service is added and needs API keys, tokens, a connection string, or a certificate.
- A developer or agent asks which env vars or environment variables the project needs to run locally, in CI, or in production.
- An existing credential changes owner, scope, environment, storage location, or is rotated or retired.
- Before a release or handover, to confirm every referenced secret is documented and every documented secret is still used.
- Onboarding: generating or refreshing `.env.example` from the register.

## When Not to Use

- Do not use to store, paste, or transmit secret values; `CREDENTIALS.md` never contains a value, even a "test" or "temporary" one.
- Do not use to generate, sign, or rotate keys; do that in the owning service and record the outcome here.
- Do not use as a substitute for `security-engineer` when the question is whether secret handling in code is safe (logging, exposure, injection).
- Do not use for personal data or user records; those are not credentials.

## Role / Responsibilities

Act as the project's secret registrar: discover what the code needs, record it, keep the record and the code in sync, and block secret values from entering the register. The agent owns discovery and judgement (what a variable is for, who owns it); `scripts/credentials_check.py` owns validation.

## Inputs

Required:
- project root

Discoverable from the repository:
- existing `CREDENTIALS.md` (if any)
- `.env.example`, `.env.sample`, `.env.template`
- environment variable references in code (`process.env.X`, `os.environ["X"]`, `os.getenv("X")`, `System.getenv("X")`, `ENV["X"]`, `env::var("X")`, `${X}` in compose/CI files)
- CI and deployment configuration that names secrets

Optional (ask only when it cannot be inferred):
- owner or team for a credential
- where the value is stored (secret manager path, vault item, CI secret name)
- rotation policy

## Outputs

- `CREDENTIALS.md` at the project root, in the format of `templates/CREDENTIALS.md`
- optionally an updated `.env.example` listing every variable with an empty or placeholder value
- a check report from `scripts/credentials_check.py` (exit 0) recorded as verification evidence

## Register Format

One table, one row per credential. Columns are fixed so the checker can parse them:

| Column | Meaning |
| --- | --- |
| `Variable` | Environment variable or config key name, `UPPER_SNAKE_CASE` |
| `Service` | System that issues or consumes it (Stripe, Postgres, GitHub Actions) |
| `Purpose` | What the project does with it, one line |
| `Environments` | Comma-separated: `local`, `ci`, `staging`, `production`, or `all` |
| `Source` | Where a person obtains a value (dashboard URL, team, runbook) |
| `Storage` | Where the value lives per environment (`.env` local, `1Password: Project/Stripe`, `GH secret STRIPE_KEY`, `AWS SM /prod/stripe`) |
| `Owner` | Person or team accountable for it |
| `Rotation` | Policy or cadence (`90d`, `on offboarding`, `none: public key`) |
| `Status` | `active`, `pending`, `deprecated`, `retired` |

Storage entries name a location, never a value. Public identifiers (a publishable key, a client ID) still get a row, with `Rotation` noting they are non-secret, so onboarding is complete.

## Workflow

```text
INSPECT → RECONCILE → RECORD → CHECK → REPORT
```

1. **Inspect.** Run `python skills/credential-inventory/scripts/credentials_check.py --root <project> --code-scan --json`. It lists variables found in code and env templates, variables already registered, and the difference. If `CREDENTIALS.md` is missing, create it first: `e2e template copy CREDENTIALS`, or copy this skill's `templates/CREDENTIALS.md` to the project root.
2. **Reconcile.** For each variable in code but not in the register: find the reference, read enough surrounding code to state its purpose and service, and add a row. For each registered variable no longer in code: confirm with a repository search, then set `Status` to `retired` (keep the row for one release so the removal is visible) or delete it if the user prefers.
3. **Record.** Fill every column. Where owner, storage, or rotation cannot be determined from the repository, write `unknown` and list the variable in the report as needing input; do not invent a team or path.
4. **Check.** Run the checker again without `--json`. It must exit 0. It fails on: a secret-like value anywhere in the file, a malformed table, a missing required column, an empty `Variable`/`Service`/`Purpose`/`Storage` cell, or a variable name that is not `UPPER_SNAKE_CASE`. With `--strict` it also fails on drift (undocumented or unused variables).
5. **Report.** State what was added, changed, or retired; which rows contain `unknown`; and paste the checker's summary line as evidence.

When a new credential is introduced by the current change, do steps 2–4 in the same change so the register never lags the code.

## Rules / Constraints

- Never write a secret value into `CREDENTIALS.md`, an example file, a commit message, a report, or chat output. If a value is encountered while inspecting (for example in a stray `.env`), do not repeat it; report the file path and recommend rotation.
- `.env`, `.env.local`, `.env.production`, and private key files are protected paths (see `e2e/hooks.py`); read them only if the user explicitly asks, and never copy their contents.
- The register is committed; secret stores are not. Do not add `CREDENTIALS.md` to `.gitignore`.
- Keep the fixed column set. Add project-specific detail inside `Purpose` or `Storage`, not as new columns, so the checker keeps working across projects.
- Do not invent owners, storage paths, or rotation policies. `unknown` is a valid, honest cell.
- Do not rename variables in code to make them match the register; document what the code actually uses.

## Error Handling

| Failure | Action |
| --- | --- |
| Checker reports a secret-like value in `CREDENTIALS.md` | Remove the value, replace with a storage location, re-run. Recommend rotation if the value was ever committed. |
| Variable in code with no identifiable purpose | Add the row with `Purpose: unknown: referenced in <file>` and flag it in the report. Do not guess. |
| Register lists a variable not found in code | Search the repo including CI/deploy config. If truly absent, mark `retired`. If used only in infrastructure, note that in `Purpose`. |
| Checker cannot parse the table | Restore the header from `templates/CREDENTIALS.md`; do not reformat rows by hand without re-running the check. |
| `--code-scan` misses a language's env access pattern | Record the variable manually and report the missed pattern so the checker can be extended. |

Do not loop on the checker. Two failing runs with the same finding means the finding needs a human decision; report it.

## Validation

- `python skills/credential-inventory/scripts/credentials_check.py --root <project>` exits 0.
- `--code-scan` shows no undocumented variables, or each one is listed in the report with a reason.
- Repository secret scan (`e2e/hooks.py: secret_scan`) still passes on the project.
- `.env.example`, if regenerated, contains every `active`/`pending` variable and no values.

## Examples

See `examples/CREDENTIALS.example.md` for a filled register for a Next.js + Postgres + Stripe project, and `examples/check-output.txt` for the checker's output on it.

Adding a credential mid-task:

```text
Change: add SendGrid email sending.
1. Code reads process.env.SENDGRID_API_KEY in lib/email.ts.
2. Add row: SENDGRID_API_KEY | SendGrid | Send transactional email | staging, production |
   SendGrid dashboard > Settings > API Keys (team: platform) |
   local: .env; staging/prod: GH secret SENDGRID_API_KEY | platform | 90d | active
3. Add SENDGRID_API_KEY= to .env.example.
4. Run checker: "credentials_check: OK (9 registered, 0 undocumented, 0 unused, 0 secret-like values)".
```

## Definition of Done

- `CREDENTIALS.md` exists at the project root in the fixed format.
- Every environment variable referenced in code or env templates has a row, or is explicitly listed as an exception in the report.
- No row contains a secret value; the checker exits 0.
- Rows with `unknown` cells are listed for the user to complete.
- The checker summary is recorded as evidence.

## Security Considerations

The register is a map of where secrets live, which makes it useful to an attacker who already has repository access. It does not raise the risk beyond what the codebase already reveals (the code names the same variables), and it lowers the more common risk of secrets being pasted into README files, chat, or tickets because there was no sanctioned place to record them. Storage entries should name a location, not a retrieval command that embeds a token. Personal data, customer records, and internal hostnames that are themselves sensitive do not belong in the register.

## Limitations

- The code scanner is regex-based and covers common env access idioms in JavaScript/TypeScript, Python, Ruby, Go, Java/Kotlin, Rust, shell, YAML, and Docker Compose. Framework-specific config loaders (for example Pydantic settings fields, Spring `@Value`) are not detected; add those rows manually.
- The checker detects secret-like values by pattern; it cannot prove a file has none. Treat a passing check as necessary, not sufficient.
- Ownership and rotation are organisational facts the repository cannot supply; expect `unknown` cells on first run.
