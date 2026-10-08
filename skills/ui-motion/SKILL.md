---
name: ui-motion
description: "Implement interface motion: transitions, hover and press feedback, enter and exit animation, layout and shared-element transitions, gestures, and route transitions, on web with CSS and Motion and on React Native with Reanimated. Use when an element should animate, when motion feels sluggish, janky, or distracting, when adding gesture-driven interaction, or when checking motion for reduced-motion support."
version: 1.0.0
level: L2
---

# UI Motion

## Purpose

Make interface motion purposeful, quick, and accessible. Motion here means movement driven by interaction: a sheet sliding up, an item leaving, a control responding to a press, a tab indicator moving. It is written in the platform's motion tools, respects the user's reduced-motion preference by default, and is looked at before it ships.

Canned, art-directed animation (loaders, success celebrations, animated illustrations) is `lottie-animation`'s job.

## When to Use

- Adding or changing transitions between views or routes.
- Hover, focus, press, and drag feedback.
- Elements entering, leaving, reordering, or changing size.
- Shared-element and layout transitions.
- Gesture-driven interaction: swipe to dismiss, pull to refresh, drag to reorder.
- Motion that feels sluggish, janky, excessive, or distracting, or that ignores reduced-motion preferences.

## When Not to Use

- Not a substitute for `lottie-animation` for self-contained animated artwork: loaders, success and error feedback, animated icons.
- Not a substitute for `vector-illustration` for still artwork.
- Not a substitute for `ux-laws` for deciding whether an element needs motion at all; its restraint and Doherty-threshold rules decide that.
- Not a substitute for the frontend and mobile developer skills for the surrounding implementation; this skill specifies and implements the motion itself.

## Inputs

Required:
- the interaction or state change to animate, and the platform (web, iOS, Android)

Discoverable from the repository:
- the motion tool already in use (CSS, Motion or `framer-motion`, Reanimated, Animated), and how reduced motion is handled today
- design tokens for duration and easing, if any
- `DESIGN.md` for the screen and its pattern

Ask only when the answer changes the result: whether a transition must be interruptible mid-way, or the exact choreography of a multi-step sequence.

## Outputs

- The implemented motion in the project's tool, with the reduced-motion alternative
- A `## Motion` entry in `DESIGN.md`: interaction, trigger, what moves, duration, easing, reduced-motion behaviour
- `motion_check.py` passing, and captured or recorded evidence that the motion was looked at

## Workflow

```text
DECIDE → CHOOSE THE TOOL → SPECIFY → IMPLEMENT → CHECK → REVIEW → RECORD
```

1. **Decide.** Motion must do a job: show where something came from or went, confirm an action, keep context during a change, or guide attention once. If it does none, do not add it.
2. **Choose the tool.** Use `references/choosing-the-tool.md`. On web: CSS for simple state transitions, Motion for enter/exit, layout, and gesture work in React. On React Native: Reanimated with Gesture Handler. Use what the project already uses unless it cannot do the job.
3. **Specify.** Write the motion as a row in `DESIGN.md`'s `## Motion` table before coding: trigger, what moves, duration, easing, and what happens under reduced motion. Take durations and easings from `references/motion-tokens.md`.
4. **Implement.** Follow `references/web-motion.md` or `references/native-motion.md`. Animate transform and opacity; honour reduced motion; make transitions interruptible.
5. **Check.** Run `python skills/ui-motion/scripts/motion_check.py --root <project>`. It must exit 0.
6. **Review.** Look at it moving: on web, capture the before and after states with `skills/ux-laws/scripts/capture_screens.py` and run the interaction in the browser skill; on mobile, run it on a device or simulator. Watch for jank, overshoot that fights the layout, motion that delays the user, and anything that keeps moving.
7. **Record.** Complete the `DESIGN.md` row and note any token added.

## Rules / Constraints

- **Reduced motion is honoured, always.** Web: `prefers-reduced-motion`, or `MotionConfig reducedMotion="user"` at the app root. React Native: `useReducedMotion()` or the Reanimated reduce-motion config. The fallback is an instant state change or a cross-fade, never a frozen half-state.
- **Animate transform and opacity.** Not width, height, top, left, margin, or padding; those cause layout work every frame. Use layout animation tools (Motion's `layout`, Reanimated's layout transitions) when size or position must change.
- **Functional motion is short.** Press and hover feedback about 100–150 ms; state transitions 150–300 ms; enter and exit 200–400 ms; nothing in functional UI longer than about 500 ms. Loaders and ambient motion are `lottie-animation`'s territory and must be pausable.
- **Ease by direction.** Enter with ease-out, exit with ease-in, move with ease-in-out, springs for gesture release. One set of tokens across the product.
- **Interruptible.** A transition that is triggered again mid-way reverses or retargets from its current position; it never snaps to the start.
- **Nothing moves on its own.** Attention-seeking motion (pulsing, bouncing, wiggling) is used at most once per screen and only for something the user must act on.
- **Never animate reading.** Text that the user is reading does not move; motion happens around it.
- **Infinite animation is a loader.** Anything with `repeat: Infinity`, `infinite`, or `withRepeat(-1)` needs a reason and a stop condition.
- **Use the current package names:** `motion` (imported from `motion/react`) on web; `react-native-reanimated` with `react-native-gesture-handler` on React Native. Confirm versions against the installed packages; APIs differ between majors.
- **Gestures stay native.** Drag, swipe, and pull run on the UI thread (Reanimated worklets, Motion drag) so they follow the finger at frame rate.

## Error Handling

| Situation | Action |
| --- | --- |
| Motion is not warranted | Say so and leave the state change instant. |
| `motion_check.py` reports no reduced-motion handling | Add it at the app root first (one place), then per animation where the fallback differs. |
| Jank on a mid-range device | Replace layout-affecting properties with transforms; cut the number of animated elements; remove shadows and blurs from moving elements. |
| Motion feels slow | Shorten before easing; most functional motion is under 300 ms. |
| Transition snaps when re-triggered | Drive it from the current value (Motion does this by default; in Reanimated animate from the shared value, not from a constant). |
| Shared-element transition is unreliable across routes | Fall back to a cross-fade; do not spend days on it. |
| Gesture conflicts with a scroll view | Set the gesture's activation thresholds and let the scroll view win on ambiguity. |

## Validation

- `motion_check.py` exits 0 for the files touched.
- Reduced motion verified: with the OS setting on, the interaction still completes and ends in the right state.
- Looked at on web at a phone and a desktop width, or on a device for native; evidence recorded (screenshots of before and after states, or a short recording).
- Durations and easings match the tokens in `DESIGN.md`.
- Re-triggering mid-transition does not snap.

## Examples

- `examples/web/ExpandableCard.tsx`: Motion layout animation with enter/exit and a reduced-motion path.
- `examples/web/transitions.css`: CSS motion tokens, a state transition, and the reduced-motion rule.
- `examples/native/PressableScale.tsx`: Reanimated press feedback with a spring and reduced-motion handling.

## Definition of Done

Motion exists only where it does a job; it is specified in `DESIGN.md`, implemented with transform and opacity in the project's tool, interruptible, honours reduced motion, passes the checker, and was looked at moving.

## Security Considerations

No material security surface: motion code runs in the product's own bundle and handles no untrusted input. Gesture handlers that trigger destructive actions (swipe to delete) need confirmation or undo, which is an interaction rule rather than a security one.

## Limitations

- The checker is static and pattern-based; it finds the common mistakes (layout properties, missing reduced-motion handling, long or infinite durations), not every one.
- Captured screenshots show states, not motion. Judging the motion itself needs the browser skill, a device, or a recording.
- Framework-specific APIs change between major versions; the references name the current ones and tell the agent to confirm against the installed version.
