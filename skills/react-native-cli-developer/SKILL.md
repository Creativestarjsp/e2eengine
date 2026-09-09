---
name: react-native-cli-developer
description: "Build React Native apps on the bare CLI workflow with native Android and iOS projects. Use for native module integration, platform APIs, Android/iOS build configuration and native release workflows. Not for Expo-managed projects, which have their own skill."
---

# React Native CLI Developer

## Purpose

Build, refactor, debug, test, and review production React Native applications using the React Native CLI workflow and native Android/iOS projects.

## When to Use

Use for:

- React Native CLI applications
- native Android/iOS integration
- React Native components and hooks
- navigation and application state
- native modules and platform APIs
- Android/iOS build configuration
- permissions and deep linking
- performance and release debugging

## When Not to Use

Do not use as the primary skill for Expo-only workflows, backend services, generic React web applications, or product/visual design.

## Inputs

Inspect before changing:

- `package.json`
- React Native version
- Android project
- iOS project
- native dependencies
- build configuration
- Metro/Babel configuration
- tests
- existing architecture

## Workflow

```text
REQUIREMENTS
→ REPOSITORY INSPECTION
→ PLATFORM PLAN
→ IMPLEMENT
→ TYPE/LINT CHECK
→ NATIVE BUILD/TEST
→ DEVICE/EMULATOR VERIFY
→ REVIEW
```

### Platform Awareness

Explicitly consider Android and iOS differences for permissions, APIs, navigation, file systems, build configuration, notifications, deep links, and native dependencies.

### Native Changes

Inspect existing native configuration before modifying it. Keep native changes minimal and document platform-specific behavior.

### Dependencies

Check compatibility with the project's React Native version before adding native packages. Consider autolinking, minimum platform versions, build tooling, and maintenance cost.

## Decision Rules

- Prefer React Native APIs when they satisfy the requirement.
- Use platform-specific files only when behavior genuinely differs.
- Keep native modules isolated behind clear interfaces.
- Avoid unnecessary native dependencies.
- Do not mix Expo-specific assumptions into a CLI-native project without an explicit migration plan.
- Do not upgrade React Native or native tooling merely to solve an unrelated feature.

## Anti-Patterns

Avoid:

- editing native files without inspecting the existing configuration
- ignoring one platform
- hardcoding device-specific behavior
- storing secrets in the app bundle
- unnecessary native modules
- blocking the JS thread with expensive work
- unhandled permission denial
- assuming simulator behavior equals real-device behavior
- ignoring release builds

## Quality Bar

Production work should provide:

- consistent behavior on required platforms
- correct permissions
- resilient offline/error/loading behavior where relevant
- appropriate accessibility
- tested native integration
- successful applicable Android/iOS checks
- no known blocking build errors

## Verification

Run applicable:

- lint
- type checking
- unit/component tests
- Metro/build checks
- Android build/tests
- iOS build/tests
- emulator/device verification

For native changes, verify the affected platform directly where possible.

## Security

Review:

- permissions
- deep links and URL handling
- WebView usage
- secure storage
- authentication tokens
- native configuration
- exported Android components
- iOS entitlements/capabilities
- third-party native dependencies

Never commit certificates, provisioning secrets, signing keys, API secrets, or credentials.

## Output

Report changed files, platform impact, checks performed, build/test results, and known limitations.

## Definition of Done

- requirement is implemented
- existing native configuration was inspected
- Android/iOS impact is addressed
- relevant tests/checks pass
- affected platform builds successfully where applicable
- security and permissions were reviewed
- no unnecessary native complexity was introduced
