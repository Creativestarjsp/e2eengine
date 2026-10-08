# Release Checklist

Release:
Commit:
Date:

Each item needs evidence (command output, link, or file path), not a tick alone.

## Scope

- [ ] Every story in this release is `done` with evidence — `e2e story check`:

## Quality

- [ ] Tests pass:
- [ ] Web end-to-end checks pass:
- [ ] Mobile end-to-end checks pass:
- [ ] Code review complete:

## Security

- [ ] Security review complete, no open critical/high findings:
- [ ] Secret scan passes:
- [ ] `CREDENTIALS.md` passes `credentials_check.py --code-scan --strict`:

## Deployment

- [ ] Preview deploy succeeded and smoke test passed:
- [ ] Database migrations tested and reversible:
- [ ] Rollback steps tested or reviewed:

## Approval

- SD3 decision:
- Release owner:
- Approved on:
