---
name: expo-developer
description: "Build, debug and ship React Native apps on Expo. Use for Expo SDK APIs and modules, Expo Router, app config, development builds, EAS Build, permissions and device capabilities, and OTA update strategy. Not for bare React Native CLI projects."
---

# Expo Developer

## Purpose

Build, refactor, debug, test, and review production React Native applications using Expo and the Expo development/build ecosystem.

## When to Use

Use for:

- Expo applications
- Expo Router
- Expo SDK APIs
- Expo modules
- app configuration
- development builds
- EAS Build and related release workflows
- permissions and device capabilities
- OTA update strategy
- React Native features implemented through Expo

## When Not to Use

Do not use as the primary skill for generic React web applications, non-Expo React Native CLI projects, backend services, or product/visual design.

## Inputs

Inspect before changing:

- `package.json`
- Expo SDK version
- `app.json` / `app.config.*`
- Expo Router structure when present
- native directories if present
- EAS configuration
- installed Expo modules
- build/update configuration
- tests

Determine whether the project uses managed, prebuild, or a custom native workflow before changing configuration.

## Workflow

```text
REQUIREMENTS
→ EXPO PROJECT INSPECTION
→ SDK / WORKFLOW CHECK
→ PLAN
→ IMPLEMENT
→ VALIDATE
→ BUILD / DEVICE VERIFY
→ RELEASE REVIEW
```

### SDK Compatibility

Use APIs and packages compatible with the project's Expo SDK. Do not casually mix package versions across SDK generations.

### Configuration

Understand whether a value belongs in Expo config, environment configuration, native configuration, or runtime application code.

Never put secrets into values that are bundled into the client application.

### Native Capabilities

When a feature requires native functionality, determine whether an Expo API/module already provides it before introducing custom native code.

### Builds

For features that depend on native configuration, verify a development/release build rather than relying only on Metro or JavaScript tests.

### Updates

When using OTA updates, distinguish JavaScript/assets changes from native binary changes. Do not assume an OTA update can replace a required native binary change.

## Decision Rules

- Prefer Expo-supported APIs and modules when appropriate.
- Preserve the project's existing workflow unless a migration is required.
- Use Expo Router when it is already established in the project; do not introduce a second navigation architecture unnecessarily.
- Keep configuration centralized and explicit.
- Treat native dependency compatibility as a release concern.
- Use development builds when native capabilities require them.
- Separate build-time configuration from runtime secrets.

## Anti-Patterns

Avoid:

- blindly copying configuration from another Expo project
- mixing incompatible Expo SDK/package versions
- putting secrets in `app.json` or client environment variables
- assuming every native package works in Expo Go
- skipping development/release build verification
- using OTA updates to deliver native changes
- unnecessary prebuild/native customization
- changing SDK versions to solve unrelated bugs
- ignoring Android/iOS differences

## Quality Bar

Production Expo work should have:

- SDK-compatible dependencies
- correct app configuration
- predictable navigation
- explicit loading/error/permission states
- tested device capabilities
- appropriate accessibility
- validated development/release build when native behavior changed
- clear update/release implications

## Verification

Run applicable:

- lint
- type checking
- tests
- Expo diagnostics/checks
- development build
- Android/iOS device or emulator verification
- EAS build checks where release behavior is affected

Confirm that configuration changes are reflected in the actual generated/built application when applicable.

## Security

Review:

- client-visible environment variables
- secure token storage
- permissions
- deep links
- WebViews
- push notification credentials
- EAS credentials and signing configuration
- third-party modules

Never commit signing credentials, private keys, or secrets.

## Output

Report implementation details, Expo SDK/package impact, configuration changes, validation/build results, and known release limitations.

## Definition of Done

- requirement is implemented
- Expo workflow was identified before changes
- SDK compatibility was checked
- configuration is correct
- relevant tests/checks pass
- native behavior was built/tested where applicable
- security and release implications were reviewed
- no unnecessary migration or native complexity was introduced
