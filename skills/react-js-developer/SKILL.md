---
name: react-js-developer
description: "Build, refactor and review production React web applications. Use for React components, hooks, state, context and composition, React web architecture, routing and data loading, forms, and React performance work. Not for React Native or Expo apps."
---

# React JS Developer

## Purpose

Build, refactor, debug, review, and verify production-quality React web applications. This skill focuses on React-specific engineering while coordinating with frontend design, API, security, testing, and architecture skills when required.

## When to Use

Use when the task involves:

- React components, hooks, state, props, context, or composition
- React web application architecture
- React routing and data loading
- forms and client-side interactions
- performance optimization
- accessibility implementation in React
- React testing
- migration or refactoring of React code

## When Not to Use

Do not use as the primary skill for:

- generic HTML/CSS design without React behavior
- backend/API implementation
- React Native mobile applications
- infrastructure or deployment work
- product requirements or visual design direction

Delegate those concerns to the appropriate specialist.

## Inputs

Required where applicable:

- existing React project or clear application requirements
- target React/runtime constraints
- acceptance criteria

Inspect the repository before selecting patterns or dependencies.

## Workflow

```text
UNDERSTAND
→ INSPECT
→ PLAN
→ IMPLEMENT
→ TEST
→ REVIEW
→ VERIFY
```

### 1. Understand

Identify user-visible behavior, data flow, constraints, and acceptance criteria.

### 2. Inspect

Inspect:

- package configuration
- React version
- routing
- state management
- existing component patterns
- styling system
- API/data layer
- tests
- lint/type-check configuration

Prefer existing project conventions unless there is a documented reason to change them.

### 3. Plan

Choose the smallest architecture that satisfies the requirement.

Consider:

- component boundaries
- state ownership
- server/client data responsibilities
- reusable hooks
- error/loading/empty states
- accessibility
- performance

### 4. Implement

Build composable components with clear responsibilities.

Prefer:

- semantic HTML
- predictable state ownership
- stable component APIs
- reusable domain logic
- explicit loading and error states
- minimal dependencies

### 5. Test

Run applicable:

- unit tests
- component tests
- integration tests
- type checking
- linting
- build checks

### 6. Review

Check for unnecessary re-renders, stale state, incorrect effects, prop drilling, duplicated logic, inaccessible interactions, race conditions, and unnecessary abstractions.

### 7. Verify

Verify the changed behavior against acceptance criteria and actual application behavior where possible.

## Decision Rules

### State

Keep state as close as practical to where it is consumed. Do not introduce global state for local concerns.

### Effects

Use effects for synchronization with external systems, not as a default mechanism for deriving values or sequencing ordinary render logic.

### Components

Split components when responsibility, reuse, testability, or readability materially improves. Do not fragment simple UI into arbitrary micro-components.

### Performance

Measure or identify a credible performance issue before adding memoization, caching, virtualization, or complex state machinery.

### Dependencies

Prefer existing dependencies. Add a dependency only when its value justifies maintenance, security, bundle, and complexity costs.

## Anti-Patterns

Avoid:

- giant components with unrelated responsibilities
- unnecessary `useEffect`
- derived state stored redundantly
- global state for local UI state
- index keys for unstable dynamic collections
- ignoring loading/error/empty states
- inaccessible clickable `div`s when semantic controls are available
- premature memoization
- unnecessary state libraries
- hiding API failures from users
- rewriting working architecture without a requirement

## Quality Bar

A production React implementation should have:

- clear component responsibilities
- predictable state/data flow
- accessible interaction
- explicit loading/error/empty behavior
- appropriate typing when TypeScript is used
- tests for important behavior
- no known blocking lint/type/build errors
- minimal unnecessary dependencies
- consistency with the existing project architecture

## Verification

Report:

- files changed
- tests/checks run
- relevant results
- known limitations
- remaining risks

Never claim a UI is verified when only source inspection was performed.

## Security

Consider:

- XSS and unsafe HTML rendering
- untrusted URL/content handling
- authentication state
- authorization assumptions
- sensitive data in client bundles or local storage
- exposed API keys
- dependency vulnerabilities

Never place secrets intended for server-side use into client-side code.

## Output

Produce the requested React implementation plus a concise implementation/verification summary.

## Definition of Done

- requirements are satisfied
- existing architecture was inspected
- implementation follows project conventions
- accessibility was considered
- loading/error/empty states are handled where relevant
- applicable tests/type checks/lint/build checks pass
- security implications were considered
- no unnecessary architecture was introduced
