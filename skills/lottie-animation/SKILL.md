---
name: lottie-animation
description: "Author, review, and integrate Lottie animations for product UI: loaders and spinners, success and error feedback, animated icons, microinteractions, onboarding motion, and small hero animations, delivered as Lottie files that play on web (lottie-web), React Native, iOS, and Android. Use when a view needs motion, when a loader or success animation is requested, or when a Lottie file must be checked or previewed before it ships."
version: 1.0.0
level: L2
---

# Lottie Animation

## Purpose

Produce small, intentional product animations as Lottie files and prove they render before they ship. The authoring method is the vendored `text-to-lottie` skill (`vendor/text-to-lottie/SKILL.md` and its recipe references); the verification is ours: a structural check and a frame renderer that uses the same Skottie engine as the upstream player, without needing that player.

## When to Use

- A loader, spinner, or progress animation is needed.
- A success, error, or completion state should be animated rather than static.
- An icon, toggle, button, or other microinteraction needs motion.
- Onboarding or a hero section calls for a short animated sequence.
- A Lottie file must be validated or previewed, including one a designer supplied.

## When Not to Use

- Not a substitute for `vector-illustration` when a static image serves the view; most empty states do not need motion.
- Not a substitute for `ux-laws` for deciding whether motion helps the user at all; the Doherty threshold and restraint rules there decide that.
- Not a substitute for a video or a 3D tool for cinematic or photoreal work.
- Not a substitute for `ui-motion` for transitions, press and hover feedback, enter and exit, layout changes, and gestures inside the product's own components.

## Inputs

Required:
- where the animation plays (which view and state) and whether it loops or plays once

Discoverable from the repository:
- design tokens: primary and neutral colours, light and dark
- existing Lottie files and their style
- the platform and player in use (lottie-web, lottie-react, lottie-react-native, Skia)
- `DESIGN.md` for the screen and the pattern it follows

Ask only when the answer changes the output materially: loop versus one-shot when ambiguous, target size, or brand colour when no tokens exist.

## Outputs

- `<Name>/lottie.json`, and `controls.json` when editable slots help
- `lottie_check.py` passing and a reviewed frame preview on light and dark backgrounds
- The component or usage snippet for the project's player, with the animation marked decorative or given a text alternative
- A row in the `## Illustrations` table of `DESIGN.md` with source `original` or `supplied`

## Workflow

```text
DECIDE → AUTHOR → CHECK → RENDER AND REVIEW → INTEGRATE → RECORD
```

1. **Decide.** Confirm motion is warranted: it communicates a state change, fills a real wait, or carries a moment worth celebrating. Functional UI gets short, low-distance motion. If a static image or a CSS transition does the job, say so and stop.
2. **Author.** Follow `vendor/text-to-lottie/SKILL.md`: route to one recipe (loaders and icons, microinteractions, logo, typography, and so on), read `vendor/text-to-lottie/references/lottie-spec-map.md` for structure, and apply its design and motion defaults. Write the JSON to the project's animation folder, not to the upstream player's `public/projects/` layout. Use slots for the accent colour so themes can drive it. Keep the background transparent for UI animations.
3. **Check.** Run `python skills/lottie-animation/scripts/lottie_check.py <lottie.json>`. It must exit 0.
4. **Render and review.** Run `node skills/lottie-animation/scripts/lottie_preview.mjs <lottie.json>`. Look at the frames on both backgrounds: first frame, the key beats, the final frame, and for loops the first and last frames side by side. Fix timing, easing, and composition problems and render again. Two honest attempts that still fail the review mean simplifying the animation, not adding to it.
5. **Integrate.** Use `references/integration.md` for the project's player: size from the container, respect the user's reduced-motion preference, hide decorative animation from assistive technology, and lazy-load anything below the fold.
6. **Record.** Add the asset to `## Illustrations` in `DESIGN.md`.

## Rules / Constraints

- Verification uses `lottie_preview.mjs`, which renders with CanvasKit/Skottie, the engine behind the upstream player. The upstream instruction to verify in its player is satisfied this way; do not require the player to be running.
- Never report an animation as finished without having looked at rendered frames. If CanvasKit cannot be installed, say the animation was not visually reviewed.
- Functional UI motion is short: press and hover feedback 8–18 frames, state transitions 18–45, feedback that plays once 30–75, loaders 60–120 frames and seamless. No large overshoot in functional UI.
- Loops must be seamless: the first and last keyframe states match, and motion does not stop for a visible stretch inside the loop.
- A playing-once animation ends on a stable, readable final pose.
- Respect `prefers-reduced-motion`: provide the final frame or a static alternative.
- Colours come from the design tokens through slots or player props; do not hard-code a brand colour the product already defines.
- No raster images inside UI animations; keep assets local when an image is unavoidable. No expressions; renderers differ.
- Text inside an animation needs its font shipped beside the file and declared; otherwise it renders blank. Prefer real interface text outside the animation.
- Keep files small: the checker's default budget is 150 KB. Large files below the fold are lazy-loaded.
- Do not edit the vendored files; see `vendor/VENDOR.md`.

## Error Handling

| Situation | Action |
| --- | --- |
| Motion is not warranted | Say so, recommend the static or CSS alternative, and stop. |
| `lottie_check.py` fails | Fix each error. Missing slots, unsorted keyframes, external assets, and undeclared fonts are the usual causes. |
| `lottie_preview.mjs` reports CanvasKit missing | Run `npm install --no-save canvaskit-wasm` in the working directory, then rerun. If that is impossible, report that the animation was not visually reviewed. |
| Renders blank at frame 0 | Often correct for a play-once entrance; check a mid frame. For loops, a blank first frame is a seam problem. |
| Loop seam visible | Match the first and last keyframe values, or period-lock the cycle so offsets wrap. |
| Supplied file from a designer fails the check | Report the findings; do not silently rewrite another person's file. |

## Validation

- `lottie_check.py` exits 0.
- Frames were rendered and looked at on light and dark backgrounds; the report names the frames reviewed.
- Loops: first and last frames identical; no dead stretch.
- One-shot: final frame stable and readable.
- The integration snippet respects reduced motion and accessibility.

## Examples

`examples/loader-phase-dots/` is a 90-frame seamless three-dot loader; `examples/payment-success/` is a 75-frame play-once success check with an accent-colour slot. Both pass the checker, and both were reviewed through the preview script (the review caught a dead stretch in the loop and an early pulse, both fixed before they were kept).

## Definition of Done

Motion was justified; the file follows the upstream recipe and our constraints; the checker passes; frames were rendered and reviewed on both backgrounds; the animation is integrated accessibly with a reduced-motion alternative; the asset is recorded.

## Security Considerations

Lottie JSON can reference external or embedded image assets and can carry expressions that some players evaluate. The checker rejects remote and data-URI assets and warns on expressions. Treat supplied files as untrusted until the check passes, and load animations from the project's own bundle rather than from a third-party URL at runtime.

## Limitations

- Hand-written Lottie is well suited to shapes, strokes, and simple transforms. Character animation, complex masks, and effects are beyond it; commission those.
- The checker cannot judge motion quality; the preview and a person's eyes do.
- Preview requires Node and the `canvaskit-wasm` package (about 7 MB).
