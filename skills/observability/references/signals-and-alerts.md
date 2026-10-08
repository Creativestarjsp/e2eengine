# Signals, Log Locations, and Alerts

## The minimum set

| Question | Signal | Where it comes from |
| --- | --- | --- |
| Is it up? | Health endpoint, external uptime check | The app; a checker outside the host |
| Is it failing? | Error rate, error tracking events, crash-free rate (mobile) | Platform metrics; error tracking SDK |
| Is it slow? | Latency percentiles (p50, p95, p99) | Platform metrics or app instrumentation |
| Is it running out? | Connections, memory, disk, queue depth | Platform or host metrics |
| What changed? | Release version on every log line and error | Build injects the commit or version |

## Health endpoints

- **Liveness** (`/healthz`): returns success if the process can answer. No dependency calls. Used to restart a stuck process.
- **Readiness** (`/readyz`): returns success only if required dependencies answer (database ping, cache). Used to decide whether to send traffic.
- Respond quickly, require no authentication, and return no detail beyond a status.

## Where logs live, by target

| Target | Built-in logs |
| --- | --- |
| Vercel | Runtime and build logs in the dashboard and `vercel logs`; short retention, so add a log drain for anything needed later |
| Firebase | Cloud Logging; `firebase functions:log` |
| Supabase | Log explorer in the dashboard for API, auth, database, and functions |
| Railway | Service logs in the dashboard and `railway logs` |
| AWS | CloudWatch Logs; `aws logs tail` |
| GCP | Cloud Logging; `gcloud run services logs read` |
| Azure | Log stream and Application Insights |
| VPS | `docker compose logs`, `journalctl`; ship off the server |

Retention on built-in logs is often short. Decide how long logs must be kept and export them if the platform's retention is shorter.

## Logging rules

- One JSON object per line: `timestamp`, `level`, `message`, `request_id`, `release`, plus context fields.
- Levels mean something: `error` needs attention, `warn` is unexpected but handled, `info` is a business event, `debug` is off in production.
- Redact authorization headers, cookies, tokens, passwords, and personal data at the logger.
- Propagate a request id from the edge through every service and into error reports.

## Error and crash tracking

- Backend: capture unhandled exceptions and rejected promises with request context.
- Web: capture runtime errors; upload source maps at build time and keep them private.
- Mobile: crash reporting with debug symbols uploaded per build (dSYM for iOS, mapping files for Android), plus the JavaScript bundle's source map for React Native.
- Tag every event with `release` and `environment` so a spike can be tied to a deploy.

## Alerts

Start with these and add only when an incident shows a gap:

| Alert | Condition | First action |
| --- | --- | --- |
| Down | External uptime check fails for 2 consecutive minutes | Check the latest deploy; roll back if it is recent |
| Errors | Error rate above the agreed threshold for 5 minutes | Open error tracking, compare first-seen with the last release |
| Slow | p95 latency above the agreed threshold for 10 minutes | Check dependency health and saturation |
| Saturation | Database connections, disk, or memory above 85% | Follow the runbook's capacity step |
| Mobile crashes | Crash-free sessions for the new version below the agreed level | Halt the staged rollout |
| Certificate or domain expiry | Fewer than 14 days left | Renew; check why automation did not |

Thresholds are agreed with the owner and written in the runbook; the numbers above are starting points, not standards.

## Reviewing alerts

After each incident and at least quarterly: remove alerts nobody acted on, and add one for any failure found by a user before it was found by monitoring.
