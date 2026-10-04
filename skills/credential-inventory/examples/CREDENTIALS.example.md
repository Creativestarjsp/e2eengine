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
| DATABASE_URL | Postgres | Primary application database connection string | all | local: `docker compose up db`; others: platform team | local: .env; ci: GH secret DATABASE_URL; staging/prod: AWS SM /shop/{env}/database-url | platform | on incident, on offboarding | active |
| STRIPE_SECRET_KEY | Stripe | Create checkout sessions and refunds | staging, production | Stripe dashboard > Developers > API keys (payments team) | staging: GH secret STRIPE_SECRET_KEY_TEST; prod: AWS SM /shop/prod/stripe-secret | payments | 90d | active |
| NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY | Stripe | Client-side Stripe.js initialisation | all | Stripe dashboard > Developers > API keys | local: .env; others: build env in deploy config | payments | none: public identifier | active |
| STRIPE_WEBHOOK_SECRET | Stripe | Verify webhook signatures in app/api/webhooks/stripe | staging, production | Stripe dashboard > Webhooks > endpoint signing secret | staging/prod: AWS SM /shop/{env}/stripe-webhook | payments | on endpoint change | active |
| NEXTAUTH_SECRET | NextAuth | Sign session JWTs | all | generate locally: `openssl rand -base64 32` | local: .env; ci: GH secret NEXTAUTH_SECRET; staging/prod: AWS SM /shop/{env}/nextauth | platform | 180d | active |
| GITHUB_CLIENT_ID | GitHub OAuth | Sign-in with GitHub, client identifier | all | GitHub org > Developer settings > OAuth Apps > shop-login | local: .env; others: deploy config | platform | none: public identifier | active |
| GITHUB_CLIENT_SECRET | GitHub OAuth | Sign-in with GitHub | all | same OAuth app as GITHUB_CLIENT_ID | local: .env; ci: GH secret GITHUB_CLIENT_SECRET; staging/prod: AWS SM /shop/{env}/github-oauth | platform | on offboarding | active |
| SENDGRID_API_KEY | SendGrid | Transactional email in lib/email.ts | staging, production | SendGrid > Settings > API Keys (platform team) | staging/prod: GH secret SENDGRID_API_KEY | platform | 90d | active |
| SENTRY_DSN | Sentry | Error reporting | staging, production | Sentry project settings > Client Keys | deploy config | platform | none: public identifier | active |
| LEGACY_MAILGUN_KEY | Mailgun | Replaced by SendGrid in v2.3 | none | unknown | unknown | unknown | unknown | retired |

## Notes

- Minimal local run needs only DATABASE_URL, NEXTAUTH_SECRET, and the two GITHUB_* values; Stripe and email are stubbed when their keys are absent.
- Stripe test-mode keys are used in staging; never put a live key in a GH secret.
