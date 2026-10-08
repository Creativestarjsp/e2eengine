# React Native Motion: Reanimated and Gesture Handler

Confirm APIs against the installed major version; Reanimated 3 and 4 differ in setup (v4 requires the New Architecture and the worklets plugin). Expo projects include Reanimated; follow the Expo setup docs for the Babel plugin.

## Setup checklist

- `react-native-reanimated` and `react-native-gesture-handler` installed at versions compatible with the React Native version in use.
- The Babel plugin configured as the installed version requires (`react-native-reanimated/plugin` for v3, the worklets plugin for v4), last in the plugin list.
- `GestureHandlerRootView` at the app root.

## Shared values and styles

```tsx
import Animated, { useSharedValue, useAnimatedStyle, withTiming, withSpring, useReducedMotion } from "react-native-reanimated";

const scale = useSharedValue(1);
const style = useAnimatedStyle(() => ({ transform: [{ scale: scale.value }] }));
// on press in:  scale.value = withSpring(0.97, { stiffness: 400, damping: 30 });
// on press out: scale.value = withSpring(1,    { stiffness: 400, damping: 30 });
```

- Animate from the shared value's current state; assigning a new `withTiming`/`withSpring` retargets smoothly, so re-triggers never snap.
- Animate `transform` and `opacity`. Height changes go through layout animations or `withTiming` on a measured value only when unavoidable.
- `withSequence`, `withDelay`, `withRepeat` compose; `withRepeat(x, -1)` is infinite and needs a reason and a cancel path (`cancelAnimation`).

## Reduced motion

- `useReducedMotion()` returns the OS setting; choose `withTiming(value, { duration: 0 })` or skip the animation when it is on.
- Animation configs accept a `reduceMotion` option (`ReduceMotion.System` by default in recent versions) so animations can honour the setting without per-call branching; confirm it exists in the installed version.
- `AccessibilityInfo.isReduceMotionEnabled()` from React Native is the fallback where Reanimated's hook is unavailable.

## Layout animations

`entering={FadeIn.duration(200)}`, `exiting={FadeOut.duration(150)}`, and `layout={LinearTransition}` on `Animated.View` animate mount, unmount, and position changes declaratively. Build custom ones for sheets and cards when the presets do not fit.

## Gestures

```tsx
import { Gesture, GestureDetector } from "react-native-gesture-handler";

const pan = Gesture.Pan()
  .activeOffsetX([-10, 10])            // let vertical scroll win on ambiguity
  .onUpdate((e) => { x.value = e.translationX; })
  .onEnd((e) => { x.value = Math.abs(e.translationX) > 120 ? withTiming(Math.sign(e.translationX) * 500) : withSpring(0); });
```

- Keep gesture callbacks as worklets (they are by default inside `Gesture` builders) so the element follows the finger at frame rate.
- Call JavaScript from a worklet with `runOnJS` only at decision points (delete, navigate), not every frame.
- Set activation offsets so a swipe does not steal a scroll.

## Navigation transitions

Use the navigator's own transition presets (native stack gives platform-correct ones) rather than hand-animating screen changes. Customise only when the design calls for it, and keep the platform's back gesture working.

## Performance

- Everything that moves per frame lives on the UI thread: shared values, animated styles, gesture worklets.
- Avoid `setState` during a gesture; derive visual state from shared values.
- Test on a real mid-range Android device; the simulator hides jank.

## Accessibility

- Decorative animated views: `accessible={false}` or `importantForAccessibility="no"`.
- Announce state changes that motion conveys (`AccessibilityInfo.announceForAccessibility`) when the screen reader cannot infer them.
