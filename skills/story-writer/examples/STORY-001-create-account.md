# STORY-001: Create an account

Status: done
Platforms: web, mobile
Depends on:

As a new visitor, I want to create an account with my email and a password, so that my data is saved under my name.

## Acceptance Criteria

- AC1: Submitting a valid email and a password of 8+ characters creates the account and opens the home screen.
- AC2: An email that is already registered shows "Email already in use" and creates nothing.
- AC3: A password shorter than 8 characters is rejected before the form is sent.

## Evidence

- AC1: tests/auth/signup.test.ts "creates account and redirects" (pass); mobile: e2e/signup.yaml (pass)
- AC2: tests/auth/signup.test.ts "rejects duplicate email" (pass)
- AC3: tests/auth/signup-form.test.tsx "blocks short password" (pass)
