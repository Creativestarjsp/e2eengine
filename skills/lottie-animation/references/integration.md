# Integrating a Lottie Animation

Load animations from the project's own bundle, size them from their container, respect reduced motion, and treat them as decorative unless they carry meaning.

## Web (lottie-web)

```ts
import lottie from "lottie-web";
import animationData from "./payment-success/lottie.json";

const reduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
const anim = lottie.loadAnimation({ container, renderer: "svg", loop: false, autoplay: !reduced, animationData });
if (reduced) anim.goToAndStop(anim.totalFrames - 1, true); // show the final, stable pose
container.setAttribute("aria-hidden", "true");             // decorative; the heading carries the meaning
```

For React, `lottie-react` wraps the same player; pass `animationData`, `loop`, and `autoplay`, and use `lottieRef` to jump to the last frame when motion is reduced.

## React Native

- `lottie-react-native`: `<LottieView source={require("./lottie.json")} autoPlay loop={false} style={{ width: 120, height: 120 }} />`. Read `AccessibilityInfo.isReduceMotionEnabled()` and set `progress={1}` instead of autoplay when it is on.
- Skia (`@shopify/react-native-skia`) has its own Skottie bindings; same rules apply.

## Theming

Prefer slots for the accent colour and drive them from the player where the player supports slots (Skottie does; lottie-web does not). Where slots are unsupported, keep the file's default colour equal to the design token and regenerate per theme, or recolour at load time with the player's API.

## Performance

- Keep UI animations under the checker's size budget and under 120 frames.
- Lazy-load animations below the fold and destroy players when their view unmounts.
- Prefer the SVG renderer for small icons and the canvas renderer for larger scenes on web.

## Accessibility

- Decorative: `aria-hidden="true"` (web) or `accessible={false}` (React Native).
- Meaningful: give the container an accessible name that says what happened ("Payment successful"), and never let the animation be the only confirmation.
- Avoid flashing content; no more than three flashes per second.
