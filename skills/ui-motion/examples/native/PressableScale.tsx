import { Pressable, type PressableProps } from "react-native";
import Animated, { useAnimatedStyle, useReducedMotion, useSharedValue, withSpring, withTiming } from "react-native-reanimated";

const AnimatedPressable = Animated.createAnimatedComponent(Pressable);
const SPRING = { stiffness: 400, damping: 30 }; // settles in about 150 ms, no overshoot

/** Press feedback that follows the finger on the UI thread and retargets smoothly when re-triggered. */
export function PressableScale({ children, style, ...props }: PressableProps) {
  const scale = useSharedValue(1);
  const reduce = useReducedMotion();
  const animatedStyle = useAnimatedStyle(() => ({ transform: [{ scale: scale.value }] }));

  const to = (value: number) => {
    // Under reduced motion the press still registers visually, instantly.
    scale.value = reduce ? withTiming(value, { duration: 0 }) : withSpring(value, SPRING);
  };

  return (
    <AnimatedPressable
      {...props}
      style={[style, animatedStyle]}
      onPressIn={(e) => { to(0.97); props.onPressIn?.(e); }}
      onPressOut={(e) => { to(1); props.onPressOut?.(e); }}
    >
      {children}
    </AnimatedPressable>
  );
}
