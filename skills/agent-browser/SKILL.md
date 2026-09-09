---
name: agent-browser
description: "Drive a real browser for development, debugging, QA and end-to-end verification. Use when a task needs to navigate a site or local dev server, click/type/upload, verify a user journey, reproduce a UI bug, or confirm a change in the running application rather than in tests alone."
---

# Agent Browser

## Purpose

Operate real web browsers for development, debugging, QA, UI verification, and end-to-end workflows. This skill provides a shared browser capability for Claude Code, Codex, SD1 workers, SD2 orchestration, and SD3 verification.

The browser should be **visible by default for local development and verification** and may run **headless for CI/automation**.

## When to Use

Use when the task requires interacting with a real web application, including:

- navigating websites or local development servers
- clicking, typing, selecting, scrolling, uploading, and downloading
- verifying user journeys
- testing forms and authentication flows
- inspecting rendered UI
- collecting screenshots or video evidence
- accessibility inspection
- reproducing browser bugs
- visual QA and dogfooding
- validating a completed frontend feature

## When Not to Use

Do not use as the primary skill for:

- static source-code inspection that needs no browser
- backend-only implementation
- database-only work
- purely conceptual UI design
- native mobile device testing unless the browser is the actual target

## Browser Modes

### Visible Mode — Default for Development

Use visible/headed browser execution when a developer, reviewer, or QA engineer should be able to watch the agent operate the application.

```text
SD1
 ↓
Agent Browser
 ↓
Visible browser window
 ↓
Navigate → Click → Type → Inspect
 ↓
Screenshot / evidence
```

Default visible mode for:

- local development
- debugging
- UI review
- interactive QA
- developer demonstrations
- SD3 verification

### Headless Mode — CI / Automation

Use headless execution when a visible browser is unnecessary or unavailable.

```text
SD1
 ↓
Agent Browser
 ↓
Headless browser
 ↓
Logs / screenshots / video / test results
```

Use headless mode for:

- CI/CD
- scheduled tests
- repeatable automated regression suites
- environments without a display
- large-scale automated checks

Never claim that a developer visually observed the browser when execution was headless.

## Environment Requirement

Visible mode requires a browser runtime and display environment that supports headed execution. If the environment cannot display a browser, explicitly report that limitation and use headless mode only when appropriate.

## Workflow

```text
UNDERSTAND
→ INSPECT
→ OPEN
→ INTERACT
→ OBSERVE
→ VERIFY
→ CAPTURE EVIDENCE
→ REPORT
```

### 1. Understand

Identify:

- target URL or local application
- user journey
- required state
- acceptance criteria
- expected visual and functional behavior
- browser mode

### 2. Inspect

Before interacting, establish:

- application availability
- current page/state
- relevant accessibility or DOM structure
- authentication/session state
- viewport requirements

Prefer semantic/accessibility-oriented element discovery over brittle selectors when supported.

### 3. Open

Start or connect to the target application using the project's documented workflow. Never invent ports, credentials, or URLs when they are not known.

### 4. Interact

Perform the minimum actions required to reproduce or verify the workflow.

Examples:

- click controls
- fill fields
- select options
- navigate routes
- upload files
- scroll
- inspect dialogs
- wait for state transitions

### 5. Observe

Check both behavior and rendered results.

Look for:

- console/runtime errors
- broken layouts
- loading failures
- incorrect navigation
- inaccessible controls
- unexpected state changes
- network/data failures
- visual regressions

### 6. Verify

Compare actual behavior against acceptance criteria. Test important success and failure paths, not only the happy path.

### 7. Capture Evidence

When useful, capture:

- screenshots
- video
- accessibility snapshots
- console output
- relevant logs
- reproducible steps

Evidence must correspond to the actual run.

### 8. Report

Return:

```text
Mode: VISIBLE | HEADLESS
Target:
Scenario:
Actions:
Result: PASS | FAIL | BLOCKED
Evidence:
Issues:
Environment limitations:
```

## Decision Rules

### Visible vs Headless

Choose **VISIBLE** when human observation materially improves development, debugging, QA, or review.

Choose **HEADLESS** when repeatability, CI, scale, or lack of a display is the priority.

If the user explicitly requests visible execution, do not silently substitute headless execution.

### Element Selection

Prefer stable semantic/accessibility selectors. Avoid brittle selectors based on generated classes, arbitrary DOM position, or transient text when a stable target exists.

### Waiting

Wait for meaningful application state rather than relying on arbitrary sleep delays whenever the browser tool supports state-based waiting.

### Authentication

Reuse approved session state when available. Never expose credentials in logs, screenshots, source code, or reports.

### Evidence

Capture evidence when the result is visually important, difficult to reproduce, or required by SD3/QA acceptance criteria.

## Anti-Patterns

Avoid:

- silently running headless when visible execution was requested
- claiming visual verification without seeing the rendered result
- arbitrary sleep-heavy workflows when state-based waiting is available
- brittle CSS/XPath selectors when stable semantic targets exist
- hardcoding credentials
- exposing tokens in screenshots or logs
- testing only the happy path for important flows
- declaring success from a single click without checking resulting state
- ignoring console/runtime errors
- changing application code merely to make a browser check pass without identifying the underlying defect

## Quality Bar

A production browser verification should provide:

- correct target and environment
- explicit execution mode
- reproducible actions
- actual state verification
- relevant failure-path coverage
- evidence for important conclusions
- no exposed secrets
- clear limitations when the environment prevents full verification

## Security

Treat browser sessions as sensitive.

Protect:

- passwords
- authentication cookies
- access tokens
- personal information
- payment information
- private URLs
- uploaded confidential files

Do not store or report secrets discovered during browser execution. Use test accounts and test data when possible.

Be careful with external side effects such as purchases, account deletion, publishing, sending messages, or modifying production data. Require appropriate authorization and confirmation according to the surrounding task.

## Agent Compatibility

This is a shared skill.

```text
Claude Code ──┐
Codex ────────┼── Agent Browser Skill
SD1 ──────────┤
SD2 ──────────┤
SD3 ──────────┘
```

Runtime-specific browser invocation belongs in the runtime adapter layer. Do not fork this skill into separate Claude and Codex domain skills.

## SD3 Verification

SD3 may request browser-based evidence for completed frontend or web workflows.

Example:

```text
SD3: Verify login flow
        ↓
SD2: Delegate browser verification
        ↓
SD1: Open browser in visible mode
        ↓
Execute login flow
        ↓
Capture evidence
        ↓
SD3: Review result
```

If visible execution is impossible, SD1 must report the limitation and provide the available headless evidence instead.

## Definition of Done

- target application was reached
- correct browser mode was used
- required workflow was executed
- resulting state was actually inspected
- important errors were checked
- relevant evidence was captured
- security-sensitive information was protected
- result is reported as PASS, FAIL, or BLOCKED with evidence
