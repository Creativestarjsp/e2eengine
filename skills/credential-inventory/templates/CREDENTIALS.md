# Credentials

Register of every credential, key, token, and secret-backed setting this project needs.
This file records **where** values live and **who** owns them. It never contains a value.
Values belong in `.env` (local, git-ignored), CI secrets, or the secret manager named in `Storage`.

Maintained with the `credential-inventory` skill. Validate with:

```sh
python skills/credential-inventory/scripts/credentials_check.py --root . --code-scan
```

## Register

| Variable | Service | Purpose | Environments | Source | Storage | Owner | Rotation | Status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| EXAMPLE_API_KEY | Example | Replace this row | all | unknown | local: .env | unknown | unknown | pending |

## Conventions

- `Variable`: `UPPER_SNAKE_CASE`, exactly as the code reads it.
- `Environments`: comma-separated from `local`, `ci`, `staging`, `production`, or `all`.
- `Storage`: a location per environment, never a value. Examples: `local: .env`, `GH secret NAME`, `1Password: Vault/Item`, `AWS SM /prod/service/key`.
- `Rotation`: cadence or trigger (`90d`, `on offboarding`), or `none: public identifier` for non-secret keys.
- `Status`: `active`, `pending` (requested, not yet provisioned), `deprecated` (still works, do not use for new code), `retired` (removed from code; delete the row after one release).
- Write `unknown` rather than guessing.

## Notes

Free-form notes: which credentials are needed for a minimal local run, known gotchas, links to runbooks. No values.
