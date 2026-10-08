# Platform, Accessibility, and Responsive Rules

## Mobile

- Prioritize thumb reach.
- Use sufficiently large touch targets; follow the platform's guidance (Apple's guidelines use 44 pt, Material uses 48 dp) and keep spacing between targets.
- Avoid tiny text and controls.
- Keep primary actions accessible.
- Use bottom navigation for major destinations when appropriate.
- Avoid excessive nested navigation.
- Respect platform conventions (iOS and Android differ in back behaviour, navigation, and system controls).
- Design for different screen sizes.
- Support portrait and landscape when appropriate.
- Account for the keyboard, safe areas, and system UI.
- Provide clear loading, empty, error, and success states.

## Desktop

- Use available screen space effectively.
- Maintain strong visual hierarchy.
- Support keyboard and mouse interaction where appropriate.
- Use hover states when useful, never as the only way to reach something.
- Avoid whitespace so generous that it reduces information efficiency.
- Use familiar navigation patterns.
- Support responsive resizing.
- Do not force a mobile layout onto desktop.

## Accessibility baseline

Every interface considers:

- Sufficient colour contrast (WCAG AA: 4.5:1 for body text, 3:1 for large text and interface components)
- Readable typography
- Clear focus states
- Keyboard navigation
- Touch target size
- Meaningful labels
- Screen-reader-friendly semantics
- Error identification
- Communication that does not rely on colour alone
- Reduced-motion preferences where appropriate

Accessibility is part of design, not a later pass. This baseline is not a conformance audit.

## Responsive design

Never design for one screen size. Consider mobile, tablet, laptop, desktop, and large desktop displays. Use responsive layouts rather than scaling the desktop UI down: reflow, reprioritize, and change navigation patterns where the width demands it.

## States every screen needs

| State | The user should see |
| --- | --- |
| Loading | What is loading and, for meaningful waits, progress or a skeleton |
| Empty | Why it is empty and the action that fills it |
| Error | What went wrong in plain language and how to recover |
| Success | Confirmation and the next step |
| Disabled or no permission | Why the action is unavailable |
