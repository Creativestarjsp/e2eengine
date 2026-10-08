import { useState } from "react";
import { AnimatePresence, motion, useReducedMotion } from "motion/react";

// Tokens come from the design system; shown inline here so the example stands alone.
const BASE = 0.2;   // seconds
const EASE_OUT: [number, number, number, number] = [0, 0, 0.2, 1];
const EASE_IN: [number, number, number, number] = [0.4, 0, 1, 1];

export function ExpandableCard({ title, children }: { title: string; children: React.ReactNode }) {
  const [open, setOpen] = useState(false);
  const reduce = useReducedMotion(); // the OS setting; MotionConfig at the app root covers transforms globally

  return (
    // `layout` animates the card's size change with transforms instead of reflowing every frame.
    <motion.section layout transition={{ duration: reduce ? 0 : BASE, ease: EASE_OUT }} style={{ borderRadius: 12, overflow: "hidden" }}>
      <button type="button" aria-expanded={open} onClick={() => setOpen((v) => !v)}>
        {title}
      </button>
      <AnimatePresence initial={false}>
        {open && (
          <motion.div
            key="body"
            initial={reduce ? { opacity: 0 } : { opacity: 0, y: -8 }}
            animate={{ opacity: 1, y: 0 }}
            exit={reduce ? { opacity: 0 } : { opacity: 0, y: -8 }}
            transition={{ duration: reduce ? 0.1 : BASE, ease: open ? EASE_OUT : EASE_IN }}
          >
            {children}
          </motion.div>
        )}
      </AnimatePresence>
    </motion.section>
  );
}
