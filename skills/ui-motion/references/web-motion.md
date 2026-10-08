# Web Motion: CSS and Motion

Confirm APIs against the installed version; `motion` publishes breaking changes between majors.

## Tokens in CSS

```css
:root {
  --motion-fast: 120ms; --motion-base: 200ms; --motion-slow: 320ms;
  --ease-out: cubic-bezier(0, 0, 0.2, 1); --ease-in: cubic-bezier(0.4, 0, 1, 1); --ease-in-out: cubic-bezier(0.4, 0, 0.2, 1);
}
@media (prefers-reduced-motion: reduce) {
  :root { --motion-fast: 0ms; --motion-base: 0ms; --motion-slow: 0ms; }
}
```

Zeroing the tokens under reduced motion turns every CSS transition into an instant change in one place. Keep opacity fades where they help by giving them their own token.

## CSS transitions

- Name the properties: `transition: transform var(--motion-base) var(--ease-out), opacity var(--motion-base) var(--ease-out);`. Never `transition: all`.
- Animate `transform` and `opacity`. For height changes use `grid-template-rows: 0fr → 1fr` on a wrapper, or a layout tool.
- `@starting-style` animates an element's first render in browsers that support it; pair it with a transition.
- Keep `will-change` for elements that animate often, and remove it when they stop; it costs memory.

## Motion (React)

```tsx
import { motion, AnimatePresence, MotionConfig, useReducedMotion } from "motion/react";
```

- **App root:** `<MotionConfig reducedMotion="user">` makes transform animations respect the OS setting while keeping opacity and colour changes. Add it once.
- **Enter and exit:** wrap conditional children in `<AnimatePresence>`; give the child `initial`, `animate`, `exit`, and a stable `key`.
- **Layout:** `layout` on an element animates its size and position changes with transforms; `layoutId` connects two elements across mount/unmount for a shared-element effect. Use `layout="position"` when size must not animate.
- **Values without re-render:** `useMotionValue`, `useTransform`, `useSpring` for drag and scroll-linked values.
- **Gestures:** `whileHover`, `whileTap`, `whileFocus`, `drag` with `dragConstraints`, `onDragEnd` for swipe decisions.
- **Interruptible by default:** Motion animates from the current value when a target changes.
- **Per-component fallback:** `const reduce = useReducedMotion();` then `animate={reduce ? { opacity: 1 } : { opacity: 1, y: 0 }}`.

## Route transitions

Keep them subtle: a 200 ms cross-fade, or a small slide for hierarchical navigation. Wrap the route outlet in `AnimatePresence mode="wait"` keyed by pathname, or use the View Transitions API (`document.startViewTransition`) where the router integrates it and the browser supports it; provide the no-transition path for browsers that do not.

## Performance

- Animate only `transform` and `opacity` on elements that move; avoid box-shadow and filter on moving elements.
- Limit simultaneous animated elements; stagger lists by at most a few items.
- Measure with the browser's performance panel on a throttled CPU; frame times above 16 ms are jank.

## Accessibility

- Focus is not lost during a transition: move it after the element is visible.
- Elements leaving the tree are removed from the accessibility tree at the end of the exit, not left with `opacity: 0`.
- Motion never carries the only cue; the state is visible without it.
