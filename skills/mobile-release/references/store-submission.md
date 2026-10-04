# Test Tracks, Stores, and Fastlane

Store rules and review behaviour change; check the current App Store Review Guidelines and Google Play policies before a first submission.

## Distribution ladder

| Stage | iOS | Android | Who gets it |
| --- | --- | --- | --- |
| Internal | Ad hoc / internal distribution, TestFlight internal testers | Internal testing track, Firebase App Distribution | The team, within minutes |
| Beta | TestFlight external testers (needs beta review) | Closed or open testing track | Invited or public testers |
| Production | App Store, phased release | Production track, staged rollout | Users |

Move up one stage at a time. Promote the same build that was tested rather than rebuilding it.

## Before the first submission

- Store accounts and the app record exist (App Store Connect, Play Console).
- Bundle identifier and package name are final.
- Privacy policy URL, data-collection disclosures (App Privacy details, Data safety form), and content rating are completed.
- Permission usage strings explain why each permission is needed.
- Sign-in required for review: provide a demo account in the review notes.
- Store listing text and screenshots are ready (`aso-appstore-screenshots` produces the images when that skill is available).

## Staged rollout

- **Google Play:** release to a percentage, raise it in steps, halt it if crashes rise. A halted rollout stops new installs of that version.
- **App Store:** phased release spreads automatic updates over several days and can be paused. Users can still update manually.

Record the starting percentage, the steps, and the halt condition in `DEPLOYMENT.md`.

## Firebase App Distribution

For quick tester builds on either platform, outside the stores:

`firebase appdistribution:distribute <path-to-apk-or-ipa> --app <firebase-app-id> --groups <tester-group>`

iOS builds still need the testers' devices in the provisioning profile unless distributed through an enterprise program.

## Fastlane (bare React Native)

`fastlane/Fastfile` defines lanes; typical ones:

- `ios beta`: increment build number, build the app, upload to TestFlight.
- `android internal`: build the release bundle, upload to the internal track.
- `ios release` / `android release`: promote or submit to production.

Signing: `match` keeps iOS certificates and profiles in a private, encrypted store; the Android upload keystore and its passwords come from CI secrets. Store API credentials are the App Store Connect API key and a Play service-account key. None of these files belong in the app repository.

## Review and timing

Review can take from hours to days and can reject a build. Plan release dates with that margin, and never promise a date that depends on review.

## Credentials to register in `CREDENTIALS.md`

Names only: Expo access token, App Store Connect API key (key id, issuer id, key file location), Play service-account key location, Android upload keystore location and alias, Firebase app ids and CI credential. For each: where it is stored and who owns it.
