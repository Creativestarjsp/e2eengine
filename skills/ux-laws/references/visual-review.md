# Visual Review of Built Screens

A design can satisfy every rule on paper and still look wrong when built. This review looks at the rendered result.

## When

- Before release, on every screen in `DESIGN.md` (the blueprint's `harden` phase).
- After a story that adds or changes a screen.
- Whenever a review would otherwise rest on source code alone.

## Capture

**Web.** With the app running locally or on a preview URL:

```sh
python skills/ux-laws/scripts/capture_screens.py --url <base-url> --path / --path /login --path /projects
```

This writes one image per path at a phone width (390×844) and a desktop width (1440×900) into `ux-review/screens/`. Add `--viewports tablet=768x1024` for more. Phone-width images show the page in a frame of the exact width with a grey band beside it, because a headless browser window cannot go narrower than about 500 px; an empty frame means the site forbids framing. It captures the first viewport of each page; for scrolled positions, signed-in pages, hover, focus, dialogs, and error states, capture with the browser skill (`agent-browser`).

**Mobile apps.** Take screenshots from a simulator or device with the platform's tools (for example `xcrun simctl io booted screenshot <file>` on iOS, `adb exec-out screencap -p > <file>` on Android) and put them in `ux-review/screens/`.

**States.** Capture the empty, loading, error, and success states of each screen where they can be reached, not only the populated one.

## Look

Open every image. For each screen, at each width:

1. **First glance.** What draws the eye first? It should be the primary content or action.
2. **Hierarchy.** Is there one clear primary action? Are heading, body, and secondary text distinguishable?
3. **Alignment and spacing.** Do edges line up? Is spacing consistent between like elements? Is anything cramped or floating?
4. **Overflow.** Is any text clipped, wrapped badly, or overlapping? Does anything run off the screen?
5. **Reach and size.** On phone, is the primary action within thumb reach and are targets large enough?
6. **Contrast.** Can all text be read? Do disabled and placeholder styles still pass?
7. **Density.** Does the desktop layout use its width, or is it a phone layout stretched?
8. **Consistency.** Do the same components look the same across screens?
9. **Match.** Does it match `DESIGN.md` and the pattern it started from?

Then apply the laws in `ux-laws.md` as usual.

## Record

Write `UX-REVIEW.md` (`e2e template copy UX-REVIEW`): the screens reviewed with their image paths, scores, findings by priority, and what could not be assessed. Critical and High findings go back to the developer skill as correction tasks before release.

## Honesty rules

- A screen that was not captured is listed under Not Assessed, never scored.
- If no browser was available, say so at the top of the review.
- Findings name the image they come from.
