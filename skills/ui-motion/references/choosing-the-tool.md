# Choosing the Motion Tool

Use what the project already uses unless it cannot do the job. Otherwise:

## Web

| Need | Tool | Why |
| --- | --- | --- |
| Hover, focus, press, toggled state on one element | CSS `transition` | No JavaScript, runs on the compositor when it animates transform and opacity |
| Keyframed entrance of static content | CSS `@keyframes` | Same |
| Enter and exit in React (an element leaves the tree) | Motion `AnimatePresence` | CSS cannot animate an element that has been removed |
| Layout change: size, position, reordering | Motion `layout` / `layoutId` | Animates with transforms behind the scenes instead of reflow |
| Drag, swipe, gesture-driven values | Motion `drag`, `useMotionValue`, `useTransform` | Values follow the pointer without re-rendering React |
| Route transitions in a React app | Motion `AnimatePresence` around the route outlet, or the View Transitions API where the router supports it | Keep it simple; a cross-fade is usually enough |
| Scroll-linked effects on marketing pages | Motion `useScroll`, or CSS scroll-driven animations where supported | Out of scope for product UI; keep subtle |
| Vanilla JavaScript without React | `animate()` from `motion` | Same engine, no React |

Package: `motion` (`import { motion, AnimatePresence, useReducedMotion, MotionConfig } from "motion/react"`). `framer-motion` is the legacy name of the same library; new code uses `motion`.

## React Native

| Need | Tool | Why |
| --- | --- | --- |
| Any animation | `react-native-reanimated` | Runs on the UI thread; the standard in Expo and bare projects |
| Gestures | `react-native-gesture-handler` with Reanimated | Gesture and animation on the same thread, no bridge round-trips |
| Mount, unmount, and reorder | Reanimated layout animations (`FadeIn`, `FadeOut`, `LinearTransition`, custom) | Declarative entering/exiting/layout on `Animated.View` |
| Simple cross-fade or move with no gesture | Reanimated `withTiming` / `withSpring` | Same tool, simplest API |
| Shared element across screens | The navigation library's shared-element support, if any | Reliability varies by router and version; cross-fade fallback |

The built-in `Animated` API still works for trivial cases in legacy code; do not introduce it in new work.

## Rule of thumb

Pick the lowest tool that does the job: CSS before Motion on web; `withTiming` before a custom gesture on native. Fewer moving parts means fewer ways to jank.
