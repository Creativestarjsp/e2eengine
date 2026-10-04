---
name: observability
description: "Make a deployed app observable and operable: health checks, structured logging, error and crash tracking, uptime checks, alert rules with a first action, and the runbook. Use when adding monitoring or error tracking, defining health checks or alerts, preparing an app for production, writing or updating RUNBOOK.md, or after an incident showed a gap in what could be seen."
version: 1.0.0
level: L2
consumes: DEPLOYMENT.md
produces: RUNBOOK.md
---

# Observability

## Purpose

Make sure that when a deployed app misbehaves, someone finds out quickly, can see why, and knows what to do. The outcome is a small set of signals covering availability, error rate, and latency, alerts that are worth waking for, and a runbook another engineer can follow.

## When to Use

- Preparing deployed components for production operation.
- Adding health checks, structured logs, error tracking, crash reporting, metrics, or uptime monitoring.
- Defining or pruning alerts.
- Writing or updating `RUNBOOK.md`.
- After an incident where the problem was found late or could not be diagnosed.
- A blueprint is in its `release` phase.

## When Not to Use

- Not a substitute for `app-deployment`: the app must be deployed and its rollback recorded there first.
- Not a substitute for `security-engineer` for audit logging requirements, intrusion detection, or compliance monitoring.
- Not a substitute for `qa-engineer`: monitoring finds problems in production; it does not replace testing before release.

## Inputs

Required:
- the deployed components and their targets (from `DEPLOYMENT.md`)

Discoverable from the repository:
- existing health routes, logging setup, error-tracking SDKs
- `ARCHITECTURE.md` for dependencies that can fail (database, queues, third-party APIs)
- `CREDENTIALS.md` for monitoring service keys

Ask when it cannot be inferred: who is on call and how they are reached, and what downtime is tolerable.

## Outputs

- Health endpoints implemented and listed
- Logging, error tracking, and uptime checks configured per component
- Alert rules, each with an owner and a first action
- `RUNBOOK.md` (from `templates/RUNBOOK.md`)
- A report: what is now visible, what is not, and evidence that one alert was tested

## Workflow

```text
INVENTORY → HEALTH → LOGS → ERRORS → METRICS → UPTIME → ALERTS → RUNBOOK → TEST
```

1. **Inventory.** List each component, its target, where its logs already go (`references/signals-and-alerts.md` has the per-target locations), and what it depends on.
2. **Health.** Give every service a liveness endpoint (the process answers) and a readiness endpoint (its dependencies answer). Wire the target's health check to them.
3. **Logs.** Structured (JSON) logs with timestamp, level, message, request id, and release version. Decide retention. Remove secrets and personal data from what is logged.
4. **Errors.** Add error tracking to the backend, web client, and mobile app, tagged with release and environment. Upload source maps and mobile debug symbols so stack traces are readable.
5. **Metrics.** Per service: request rate, error rate, latency percentiles; plus saturation of what it depends on (connections, queue depth, disk on a VPS).
6. **Uptime.** An external check on the public health URL and one key user path, from outside the hosting provider.
7. **Alerts.** Few, actionable, and tied to user impact. Each names an owner and the first action in the runbook.
8. **Runbook.** Fill `RUNBOOK.md`: overview, health, alerts, common operations, known failure modes, logs, escalation, recovery.
9. **Test.** Trigger one alert on purpose in a non-production environment, or verify the uptime check fails when the health endpoint is down. Record what happened.

## Rules / Constraints

- Never log secrets, tokens, passwords, full payment details, or personal data beyond what diagnosis needs. Redact at the logger, not by convention.
- Every alert has an owner and a first action. An alert nobody acts on is removed.
- Alert on symptoms users feel (errors, latency, downtime) before causes (CPU).
- Health endpoints reveal no internals: no versions of dependencies, no stack traces, no configuration.
- Monitoring credentials are registered in `CREDENTIALS.md`; client-side keys for error tracking are public by nature and must be scoped to ingest only.
- Do not add a monitoring vendor the project does not already use without stating the choice, its cost, and where data is sent.
- The runbook describes what is true now. Do not document procedures that have not been tried.

## Error Handling

| Situation | Action |
| --- | --- |
| No health endpoint exists | Add liveness first; readiness when dependencies are known. |
| Stack traces unreadable in production | Upload source maps or debug symbols as part of the build; verify with a test error. |
| Alert fires constantly | Fix the cause or change the threshold; never mute without a decision recorded in the runbook. |
| Logs contain sensitive data | Add redaction, then report that existing logs need purging and by whom. |
| Platform offers no metric that is needed | State the gap in the report rather than approximating it silently. |

## Validation

- Each service's health endpoint returns success when healthy and failure when a dependency is down.
- A deliberately thrown test error appears in error tracking with the right release and a readable stack trace.
- The uptime check detects a failed health endpoint.
- `python skills/app-deployment/scripts/smoke_test.py` passes against the health URLs.
- `RUNBOOK.md` has no empty section and its rollback steps match `DEPLOYMENT.md`.

## Examples

```text
Task: make the API production-ready.
1. Inventory: API on Railway (logs in platform log viewer), Postgres on Supabase, Stripe as external dependency.
2. /healthz (process) and /readyz (database ping) added; Railway health check path set to /readyz.
3. JSON logs with request id and release; authorization headers redacted.
4. Error tracking added with release tag; test error visible with readable stack.
5. External uptime check on /healthz every minute.
6. Alerts: uptime check failing 2 minutes → on-call, first action "check latest deploy, roll back";
   error rate above 2% for 5 minutes → on-call, first action "open error tracker, compare with release".
7. RUNBOOK.md written; uptime alert tested by stopping the preview service.
```

## Definition of Done

Health, logs, errors, and uptime are in place for every deployed component; alerts are few and each has an owner and first action; one alert was tested; `RUNBOOK.md` is complete and matches the real system.

## Security Considerations

Logs and error reports are a common place for secrets and personal data to leak, and they are often sent to a third party. Redact at source, restrict who can read them, and set retention. Keep dashboards and health details off the public internet unless they reveal nothing.

## Limitations

- Vendor-neutral by design: it names categories of tools, not a required product.
- Distributed tracing, service-level objectives with error budgets, and on-call rotation tooling are beyond this skill's default scope; add them when the system's size justifies it.
