# Choosing a Target

Use what the project already uses. Choose a new target only for a new project or when asked to move.

## By application shape

| The project is… | Good first choice | Also fits |
| --- | --- | --- |
| Static site or single-page app | Vercel, Firebase Hosting | Azure Static Web Apps, AWS S3 + CloudFront |
| Next.js or another SSR framework | Vercel | Firebase App Hosting, GCP Cloud Run, AWS Amplify Hosting |
| Containerized API or worker | Railway, GCP Cloud Run | Azure Container Apps, AWS ECS on Fargate, VPS |
| Backend needing Postgres + auth + storage with little server code | Supabase | Firebase (document database, auth, storage) |
| Realtime/mobile backend on Google's stack | Firebase | Supabase |
| Long-running processes, WebSockets, background jobs | Railway, VPS | Cloud Run (with limits), Container Apps, ECS |
| Organization already standardized on one cloud | That cloud (AWS / GCP / Azure) | — |
| Lowest fixed cost, full control, team can operate servers | VPS | — |

## Questions that decide it

1. **Does anything already exist?** An existing cloud account, database, or domain usually settles the choice.
2. **Does the app need a server process?** Static and serverless options are simpler to operate and roll back.
3. **Where is the data?** Put compute in the same region and, where possible, the same provider as the database.
4. **Who operates it?** A VPS needs someone to patch, back up, and monitor it. Managed platforms trade cost for that work.
5. **What must preview look like?** Per-pull-request previews are built in on Vercel, Firebase Hosting channels, Railway, Azure Static Web Apps, and Supabase branching; on the big clouds they are something you build.
6. **Any compliance or region constraint?** Check data residency before choosing.

## Common combinations

- Web on Vercel + API on Railway + database on Supabase
- Web on Firebase Hosting + Cloud Run API + Firestore
- Everything in containers on one VPS behind a reverse proxy
- Mobile app (see `mobile-release`) + Supabase or Firebase backend

State the choice and the reason in `DEPLOYMENT.md`. Pricing and free-tier limits change often; check the vendor's current pricing page rather than relying on memory.
