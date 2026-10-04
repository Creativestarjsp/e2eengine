---
name: mobile-release
description: "Build, sign, distribute, and release iOS and Android apps: internal test builds, TestFlight and Google Play testing tracks, Firebase App Distribution, App Store and Play Store submission, staged rollout, and over-the-air updates. Covers EAS Build, Submit, and Update, and Fastlane. Use when shipping a mobile build to testers or the stores, setting up signing and build profiles, publishing an OTA update, or halting a bad mobile release."
version: 1.0.0
level: L2
consumes: CREDENTIALS.md, DEPLOYMENT.md
---

# Mobile Release

## Purpose

Take a mobile app from source to testers' devices and then to the stores, with signing material kept out of the repository and a plan for what happens when a release is bad. A mobile binary cannot be recalled once installed, so the controls are different from a web deploy: test tracks first, staged rollout, and over-the-air updates for what they can correct.

## When to Use

- Producing an installable iOS or Android build for testers (internal distribution, TestFlight, Play internal testing, Firebase App Distribution).
- Submitting to the App Store or Google Play, or promoting a tested build to production.
- Setting up build profiles, signing, and version and build numbers.
- Publishing or rolling back an over-the-air (OTA) JavaScript update.
- Halting a staged rollout or shipping an urgent corrective build.
- A blueprint with a mobile app is in its `preview` or `release` phase.

## When Not to Use

- Not a substitute for `app-deployment`: the backend the app talks to is deployed there, and it comes first.
- Not a substitute for `expo-developer` or `react-native-cli-developer` when the work is building or fixing the app itself.
- Not a substitute for `aso-appstore-screenshots` when the task is producing store listing images.
- Not a substitute for `ci-cd-pipeline` when the work is automating the build in CI.

## Inputs

Required:
- the platform(s): iOS, Android, or both
- the destination: internal testers, a store testing track, or production

Discoverable from the repository:
- project type: Expo (`app.json` / `app.config.*`, `eas.json`) or bare React Native (`ios/`, `android/`, `fastlane/`)
- bundle identifier, package name, current version and build numbers
- `CREDENTIALS.md` for which signing and store credentials exist and where they live
- `DEPLOYMENT.md` for the backend URL each build profile must point at

Ask when it cannot be inferred: which store accounts exist, who the release owner is, and whether the app has been submitted before.

## Outputs

- A build artifact or store build number, and where testers get it
- The `## Mobile Release` section of `DEPLOYMENT.md`: build profiles, signing location, distribution tracks, OTA policy, and what to do with a bad release
- Mobile items in `RELEASE-CHECKLIST.md` with evidence
- A report: version and build numbers, track, review status, remaining risks

## Workflow

```text
INSPECT → PREFLIGHT → CONFIGURE → BUILD → DISTRIBUTE TO TESTERS → VERIFY → (APPROVAL) → SUBMIT → STAGED ROLLOUT → MONITOR
```

1. **Inspect.** Identify the project type and read `references/expo-eas.md` (Expo) or the Fastlane section of `references/store-submission.md` (bare React Native).
2. **Preflight.** Run `e2e deploy check --env preview` from the mobile project root; it includes `mobile_preflight.py` for mobile projects. It must pass: no signing material tracked by git, identifiers present, build profiles defined. Without the engine, run `python skills/mobile-release/scripts/mobile_preflight.py --root <project>`.
3. **Configure.** Each build profile points at the matching backend environment from `DEPLOYMENT.md`. Preview builds never point at production data. Bump the version or let the build service auto-increment the build number.
4. **Build.** Produce the build with the preview profile. Signing credentials come from the build service's managed credentials or the CI secret store, never from the repository.
5. **Distribute to testers.** Internal distribution, TestFlight internal testers, Play internal testing, or Firebase App Distribution.
6. **Verify.** Install the build on a real device or run the mobile end-to-end checks. Record the result against each story's acceptance criteria.
7. **Approval.** Store submission and production rollout need the release owner's explicit approval. Stop here without it.
8. **Submit.** Build with the production profile and submit. A first-ever Android release must be uploaded through the Play Console once before the API accepts uploads.
9. **Staged rollout.** Release to a percentage of users (Play staged rollout, App Store phased release) rather than everyone at once.
10. **Monitor.** Watch crash and error reports for the new version. Halt the rollout if they rise.

## When a Release Is Bad

A shipped binary cannot be rolled back. In order of speed:

1. **Halt** the staged rollout or pause the phased release so no more users receive it.
2. **OTA update** if the fault is in JavaScript or assets and the update is compatible with the installed runtime: republish the last good update or roll back the bad one.
3. **Fix forward:** ship a new build with a higher build number; request expedited review when justified.
4. **Backend mitigation:** disable the feature server-side or keep the old API behaviour so old app versions keep working.

Write which of these apply in `DEPLOYMENT.md` before the release, not during the incident.

## Rules / Constraints

- Never commit signing material: distribution certificates, provisioning profiles, upload keystores, App Store Connect API keys, or Play service-account files. `mobile_preflight.py` fails when git tracks them.
- Never submit to a store or start a production rollout without the release owner's explicit approval for that build. The engine refuses `store.submit` until `e2e deploy check --env production` has passed for the current commit; `mobile.build` needs the preview gate.
- Testers first. Nothing goes to production that has not been installed from a test track.
- An OTA update must target the runtime version of the binaries that will receive it. Native code changes need a new binary, not an update.
- The backend must stay compatible with every app version still in use; users update slowly.
- Never print or paste credential values. Refer to them by the names in `CREDENTIALS.md`.
- Confirm commands against `eas --help` / `fastlane --help` for the installed version before running them.
- Do not change bundle identifiers, package names, or signing keys of a published app; doing so creates a different app.

## Error Handling

| Failure | Action |
| --- | --- |
| Preflight finds tracked signing material | Remove it from the index, add the pattern to `.gitignore`, and report that the credential should be rotated. |
| Build fails on signing | Check which credentials the build service holds for that profile and platform; do not generate replacements for a published app without the owner's decision. |
| Store rejects the build or review | Report the rejection reason verbatim, fix the cause, resubmit with a higher build number. |
| Version or build number already used | Increment the build number; never reuse one. |
| OTA update not received | Compare the update's runtime version and channel with the installed build's; they must match. |
| Crash rate rises during rollout | Halt the rollout first, then diagnose. |

Two failed builds with the same error is a stop: report the build log's cause rather than retrying.

## Validation

- `mobile_preflight.py --env <preview|production>` exits 0.
- The build installs and launches on a real device or passes the mobile end-to-end checks.
- The build's backend URL matches the intended environment.
- `DEPLOYMENT.md` records tracks, OTA policy, and the bad-release plan.
- For production: approval recorded in `RELEASE-CHECKLIST.md`; rollout is staged.

## Examples

```text
Task: get a build to testers.
1. Expo project (eas.json present). mobile_preflight.py: OK (profiles: development, preview, production).
2. Preview profile points at the preview API URL from DEPLOYMENT.md.
3. Build both platforms with the preview profile; internal distribution links returned.
4. Installed on one iOS and one Android device; sign-in story AC1–AC3 verified and recorded.
5. Stop: store submission needs owner approval.
```

## Definition of Done

Testers have an installable build that points at the right backend; signing material is outside the repository; the bad-release plan is written; store submission and production rollout happened only with recorded owner approval and as a staged rollout.

## Security Considerations

Signing keys and store credentials let someone publish as you; losing an Android upload key or leaking an App Store Connect key is a serious incident. Keep them in the build service or CI secret store with the narrowest role. Anything inside the app bundle (API URLs, public keys, configuration) is readable by anyone who downloads it: never embed a secret in a mobile binary or an OTA update.

## Limitations

- Store review times and policies are outside the engine's control and change; check current store guidelines.
- The preflight reads `app.json` and `eas.json`; a dynamic `app.config.js` or `.ts` is reported for manual checking.
- Native build troubleshooting (Xcode, Gradle) belongs to the platform developer skills.
