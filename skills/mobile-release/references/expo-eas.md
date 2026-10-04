# Expo Application Services (EAS)

Confirm commands with `eas --help` on the installed CLI; this file is a map, not a transcript.

## Files

- `eas.json`: build and submit profiles.
- `app.json` or `app.config.js|ts`: version, `ios.bundleIdentifier`, `android.package`, runtime version, update settings.

## Build profiles

A typical `eas.json` has three:

| Profile | Purpose | Notes |
| --- | --- | --- |
| `development` | Development client for local work | internal distribution |
| `preview` | Testers | internal distribution; points at the preview backend |
| `production` | Stores | store distribution; auto-increment the build number |

Per-profile environment values select the backend. Anything set there is compiled into the app and is public.

## Authentication

- Local: `eas login`.
- CI: an access token in `EXPO_TOKEN`.

## Signing

Let EAS manage credentials unless there is a reason not to: it generates and stores the iOS distribution certificate and provisioning profile and the Android keystore. `eas credentials` inspects them. If credentials are supplied locally instead, the files stay out of git.

## Build

`eas build --platform ios|android|all --profile <profile>`. Internal-distribution builds return an install link; iOS internal builds require the test devices to be registered.

## Submit

`eas submit --platform ios|android --profile production` uploads the latest (or a chosen) build to App Store Connect or Google Play. It needs an App Store Connect API key for iOS and a Play service-account key for Android, held by EAS or the CI secret store. `eas build --auto-submit` chains the two.

Android's first release must be uploaded manually in the Play Console before API submission works.

## Over-the-air updates (EAS Update)

- `eas update --channel <channel> --message "<what changed>"` publishes JavaScript and assets to builds on that channel.
- A build receives an update only if the update's runtime version matches the build's. Set a runtime version policy and change it whenever native code changes.
- Publish to the preview channel first; promote to production after verification.
- Bad update: republish the previous good update to the channel, or use the CLI's update rollback. Confirm the exact subcommand with `eas update --help`.

OTA cannot change native modules, permissions, or the app icon. Stores also restrict what an update may change; keep updates to fixes and content within the app's reviewed purpose.

## CI notes

Run `eas build --non-interactive` in CI with `EXPO_TOKEN`. Builds are queued on EAS; either wait for the result or let the job finish and have EAS report status.

## Gotchas

- Changing `bundleIdentifier` or `package` after publishing creates a new app.
- Build numbers must increase for every store upload; use auto-increment.
- A missing or mismatched runtime version is the usual reason an update never arrives.
