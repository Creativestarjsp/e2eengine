# app-deployment

Deploy a web app, API, or worker and prove it works. One workflow for every
target; target specifics in `references/`. See `SKILL.md`.

Requirements: Python 3.9+, git, no third-party packages. The target's own CLI
is needed only to run its deploy commands.

```text
scripts/deploy_preflight.py   is the project fit to deploy? (--env preview|production)
scripts/smoke_test.py         does the deployment answer? (--url … --path /health)
references/choosing-a-target.md
references/vercel.md  firebase.md  supabase.md  railway.md  aws.md  gcp.md  azure.md  vps.md
examples/DEPLOYMENT.example.md
```

```sh
python skills/app-deployment/scripts/deploy_preflight.py --root . --env preview
python skills/app-deployment/scripts/smoke_test.py --url https://<preview-url> --path /health
```
