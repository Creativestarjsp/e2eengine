# STORY-003: Reset a forgotten password

Status: todo
Platforms: web
Depends on: STORY-002

As a user who forgot my password, I want to reset it by email, so that I can get back into my account.

## Acceptance Criteria

- AC1: Requesting a reset for a registered email sends a link that expires after 30 minutes.
- AC2: Requesting a reset for an unknown email shows the same confirmation and sends nothing.
- AC3: Opening a valid link lets the user set a new password and signs them in.

## Evidence

- AC1:
- AC2:
- AC3:

## Notes

Assumption: reset is web-only for the first release; the mobile app opens the web flow.
