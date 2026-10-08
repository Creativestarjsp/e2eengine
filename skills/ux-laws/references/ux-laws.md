# UX Laws

Select the laws relevant to the interface. Each entry: what it says, how to apply it, and its limit.

## Reaching and choosing

### 1. Fitts's Law
Important interactive targets should be easy and fast to reach.
- Make primary buttons sufficiently large.
- Keep important actions within comfortable reach.
- Increase touch target sizes on mobile.
- Avoid tiny icons for important actions.
- Place frequently used actions close to the user's interaction area.

### 2. Hick's Law
More choices increase decision time.
- Reduce unnecessary choices.
- Prioritize primary actions.
- Group related options.
- Use progressive disclosure.
- Break complex workflows into manageable steps.
- Avoid overwhelming dashboards.

### 3. Jakob's Law
Users expect interfaces to behave like products they already know.
- Use familiar navigation patterns and conventional icons.
- Keep common UI locations consistent.
- Avoid unnecessary interaction innovation.
- Follow established platform conventions.

Limit: do not reinvent common patterns unless there is a strong usability reason.

## Memory and attention

### 4. Miller's Law
Users have limited working memory.
- Chunk information and group related data.
- Avoid excessive information density.
- Break complex information into sections.
- Use progressive disclosure where appropriate.

Limit: "7 ± 2" is not a UI limit. Treat it as a reminder to reduce cognitive load.

### 14. Serial Position Effect
Users remember the beginning and end of a list best.
- Prioritize important navigation items.
- Place primary actions prominently.
- Avoid burying critical actions in long menus.

### 15. Von Restorff Effect
Distinctive elements are more memorable.
- Highlight the primary CTA.
- Clearly identify selected states.
- Use visual emphasis sparingly.
- Make important information stand out.

Limit: do not make every element visually prominent.

## Perception and grouping (Gestalt)

### 6. Law of Proximity
Elements placed close together are perceived as related.
- Group labels with their controls, and related actions together.
- Use whitespace to separate unrelated sections.
- Keep spacing relationships consistent.

### 7. Law of Similarity
Visually similar elements are perceived as belonging together.
- Use consistent component styles, typography, and iconography.
- Keep similar actions visually consistent.
- Use visual patterns to communicate relationships.

### 8. Law of Common Region
Elements inside the same container are perceived as related.
- Use cards or containers for related information.
- Create clear dashboard sections and separate unrelated content.

Limit: avoid cards where whitespace is sufficient.

### 9. Law of Continuity
Users follow continuous visual paths.
- Create logical content flow and maintain alignment.
- Use consistent grids.
- Design navigation with predictable progression.

### 10. Law of Closure
Users mentally complete incomplete visual structures.
- Use simplified visual patterns.
- Avoid unnecessary borders.
- Let whitespace and partial cues establish relationships.

### 11. Law of Figure-Ground
Users distinguish foreground content from background.
- Create clear hierarchy and make primary content dominant.
- Maintain sufficient contrast and avoid distracting backgrounds.
- Clearly separate modal or dialog content from the page beneath.

### 5. Aesthetic-Usability Effect
Users perceive visually polished interfaces as easier to use.
- Maintain visual hierarchy, consistent spacing, strong typography, balanced layouts, consistent colours.
- Avoid unnecessary visual clutter.
- Create polished loading, empty, success, and error states.

Limit: visual quality must never override usability.

## Time and feedback

### 12. Doherty Threshold
Interfaces should respond quickly enough to keep the user engaged.
- Optimize API calls and reduce unnecessary rendering.
- Use optimistic UI where appropriate.
- Show skeleton loaders for meaningful waits and give progress feedback.
- Avoid unexplained loading states.

Limit: never use animation merely to hide poor performance.

### 13. Peak-End Rule
Users remember the peak moment and the ending most.
- Polish important moments and design excellent success states.
- Make onboarding memorable and completion feedback satisfying.
- Make error recovery clear and reassuring.

### 18. Zeigarnik Effect
People remember incomplete tasks.
- Show progress and incomplete profile or setup states.
- Provide continuation options and make unfinished workflows easy to resume.

Limit: do not create artificial unfinished tasks to manipulate users.

### 19. Goal-Gradient Effect
Motivation rises as a goal gets closer.
- Show progress indicators, milestones, and completion percentages.
- Break large tasks into visible stages.

## Complexity and effort

### 16. Tesler's Law
Every system has inherent complexity that someone must handle.
- Remove unnecessary complexity.
- Move complexity from the user to the system when practical.
- Use sensible defaults and automate repetitive tasks.
- Avoid unnecessary configuration.

### 17. Postel's Law
Be conservative in what you send and flexible in what you accept.
- Accept reasonable input variations and provide forgiving forms.
- Validate input intelligently and give useful error messages.
- Avoid unnecessary restrictions.

### 20. Occam's Razor
Prefer the simplest solution that solves the user's problem.
- Remove unnecessary UI and redundant controls.
- Simplify workflows and avoid decorative complexity.
- Prefer simple interaction patterns.

### 21. Pareto Principle
A small number of features provide most of the value.
- Identify the most important user actions and prioritize frequently used features.
- Keep secondary functionality accessible but less prominent.
- Avoid feature overload.

### 22. Parkinson's Law
Work expands to fill the available time.
- Create focused workflows and reduce unnecessary steps.
- Use sensible defaults and provide a clear next action.
- Avoid unnecessarily long forms.

## Where each law usually matters

| Surface | Laws to check first |
| --- | --- |
| Forms | Postel, Tesler, Proximity, Parkinson, Hick |
| Navigation | Jakob, Serial Position, Hick, Fitts |
| Dashboards | Hick, Miller, Common Region, Pareto, Figure-Ground |
| Primary actions and CTAs | Fitts, Von Restorff, Serial Position |
| Onboarding and multi-step flows | Goal-Gradient, Zeigarnik, Peak-End, Hick |
| Loading and async actions | Doherty Threshold, Peak-End |
| Modals and dialogs | Figure-Ground, Hick, Fitts |
| Tables and lists | Miller, Similarity, Proximity, Continuity |
| Empty, error, and success states | Peak-End, Aesthetic-Usability, Postel |
