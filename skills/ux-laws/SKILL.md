---
name: ux-laws
description: "Apply and audit established UX laws and human-computer interaction principles (Fitts, Hick, Jakob, Miller, Gestalt grouping, Doherty threshold, Tesler, Postel, and others) when designing, generating, or reviewing an interface. Use for a UX review or usability audit with scored, prioritized findings, for checking a design against UX laws, and for reducing cognitive load or improving touch targets, visual hierarchy, and loading, empty, error, and success states on phone and desktop."
version: 1.0.0
level: L2
---

# UX Laws & Design Principles

## Purpose

Act as an expert UI/UX reviewer and interface-generation assistant that applies established UX laws and human-computer interaction principles, so interfaces are easy to understand, fast to navigate, familiar, visually clear, accessible, efficient, consistent, responsive, pleasant to use, and suited to both phone and desktop.

The laws are guidelines, not rules. Select the ones relevant to the interface, platform, and task; do not apply every law to every screen.

## When to Use

- Reviewing or auditing an existing screen, flow, or app for usability, with scores and prioritized findings.
- Checking a design or `DESIGN.md` against UX laws before it is built.
- Generating or improving an interface, where the laws shape layout, hierarchy, and states without being narrated.
- Resolving a design disagreement by naming the principle and the trade-off.
- Reducing cognitive load, choice overload, or friction in a form, dashboard, onboarding, or checkout.

## When Not to Use

- Not a substitute for `ui-ux-designer` when the work is creating the product's flows, visual direction, and design system; this skill supplies the principles and the audit.
- Not a substitute for a full WCAG conformance audit; the accessibility rules here are the baseline every interface needs, not a certification.
- Not a substitute for user research or usability testing with real users; the laws predict problems, they do not prove them.
- Not a substitute for `frontend-developer`, `react-js-developer`, or the mobile developer skills for implementing the changes.

## Inputs

Required (one of):
- an existing interface: screenshots, a running app, a design file, or the UI source
- a brief for an interface to be generated

Discoverable from the repository:
- `DESIGN.md`, the design system or component library in use, platform (web, iOS, Android)
- stories and their acceptance criteria, for the user's goal on each screen

Before generating, establish (assume and label what is unknown):

1. Who is the user?
2. What is the user's primary goal?
3. What is the most important action?
4. What information is essential?
5. What information is secondary?
6. What decisions does the user need to make?
7. What actions should be easiest to reach?
8. What could create cognitive overload?
9. What happens during loading?
10. What happens when there is no data?
11. What happens when an error occurs?
12. What happens after successful completion?

## Outputs

- **Generating:** the interface or specification with the relevant principles applied to layout, navigation, component hierarchy, typography, spacing, CTAs, forms, modals, tables, cards, dashboards, empty, loading, error, and success states, responsive behaviour, accessibility, and interaction patterns. The laws are applied silently; they are explained only when asked.
- **Reviewing:** the report in the format below.

## Workflow

```text
UNDERSTAND → SELECT LAWS → APPLY or AUDIT → PRIORITIZE → REPORT
```

1. **Understand.** Answer the twelve questions above for the screen or flow. Identify the platform.
2. **Select.** From `references/ux-laws.md`, pick the laws that bear on this interface and task. Add the platform rules from `references/platform-and-accessibility.md`.
3. **Apply (generating).** Design the hierarchy around the primary action, then the states, then responsive behaviour. Resolve conflicts with the priority order below.
4. **Audit (reviewing).** Walk the primary task step by step. For each significant problem record what was observed, where, the applicable principle, why it harms the user, and a specific fix.
5. **Prioritize.** Classify each finding by its effect on task completion.
6. **Report.** Scores, problems by priority, and what could not be assessed.

## Decision Priority

When principles conflict, the higher one wins:

1. User task completion
2. Accessibility
3. Clarity
4. Usability
5. Performance
6. Consistency
7. Familiarity
8. Visual aesthetics
9. Animation and decorative effects

Never sacrifice usability for visual novelty.

## Review Report Format

```markdown
### UX Score
- Usability: /10
- Clarity: /10
- Navigation: /10
- Accessibility: /10
- Responsiveness: /10
- Visual hierarchy: /10
- Performance perception: /10

### Problems
For each: the issue and where it occurs · the applicable UX principle · why it is a problem · a specific improvement

### Priority
- 🔴 Critical — blocks or seriously harms task completion
- 🟠 High — significant usability problem
- 🟡 Medium — noticeable friction
- 🟢 Low — polish/improvement

### Not Assessed
What could not be judged from the material provided, and what would be needed.
```

## Rules / Constraints

- The laws are guidelines. Do not force a principle onto an interface when it conflicts with user goals, business requirements, accessibility, platform conventions, technical constraints, or the context of use. Use professional judgement and say which consideration won.
- Do not invent problems to lengthen a report. A short report on a good interface is a correct result.
- Every finding names something observed: the screen, the element, and what it does. No finding rests on a law alone.
- A score is given only for what was inspected. A dimension that could not be assessed (for example responsiveness from a single screenshot) is marked not assessed, not guessed.
- Recommendations are specific enough to implement: what changes, where.
- Do not treat Miller's "7 ± 2" as a limit on items. It is a reminder to reduce cognitive load.
- Do not use psychological effects (Zeigarnik, goal-gradient, scarcity) to manipulate users against their interest.
- Animation never hides poor performance, and visual polish never overrides usability.
- Accessibility is considered during design, not added afterward.
- When generating, do not narrate each law; apply them.

## Error Handling

| Situation | Action |
| --- | --- |
| Only a static screenshot is available | Review what is visible; mark interaction, responsiveness, and performance as not assessed. |
| User, goal, or platform unknown | State labeled assumptions and proceed; a wrong assumption about the primary goal changes the findings, so say so. |
| Two laws point in opposite directions | Apply the decision priority and report the trade-off. |
| A recommendation conflicts with the existing design system | Prefer consistency unless the system itself causes the problem; then flag the system. |
| Asked to make every element stand out, or to add urgency patterns | Explain the cost briefly and offer the usable alternative. |

## Validation

- Every problem cites an observation, a principle, a reason, and a specific fix.
- Priorities follow the definitions: only task-blocking problems are Critical.
- Scores are consistent with the findings; no dimension is scored without evidence.
- Generated interfaces cover loading, empty, error, and success states, and work at mobile and desktop widths.
- Baseline accessibility holds: contrast, focus states, keyboard access, labels, touch target size, no meaning by colour alone.

## Examples

`examples/review-example.md` is a complete review of a mobile checkout screen in the report format.

## Definition of Done

Relevant laws were selected rather than all applied; findings are evidenced, prioritized, and actionable (or the interface was generated with states, responsiveness, and accessibility covered); conflicts were resolved by the priority order; limits of the assessment are stated. The result should feel simple, familiar, intentional, responsive, accessible, and visually polished.

## Limitations

- Heuristic review predicts usability problems; it does not measure them. Testing with users can overturn a finding.
- Scores are a judgement to compare versions of the same interface, not an absolute measure.
- Perceived performance can only be assessed on a running interface.
