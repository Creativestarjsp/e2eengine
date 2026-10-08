# Motion Tokens and the Motion Spec

## Durations

| Token | Value | Use |
| --- | --- | --- |
| `fast` | 100–150 ms | Hover, focus, press feedback, toggles |
| `base` | 150–300 ms | State changes, small enters and exits, tab indicators |
| `slow` | 300–400 ms | Sheets, dialogs, larger elements entering or leaving |
| `page` | 300–500 ms | Route and screen transitions |

Anything longer in functional UI delays the user. Larger distances and larger elements take the longer end of the range; small ones the short end.

## Easings

| Token | Curve | Use |
| --- | --- | --- |
| `ease-out` | `cubic-bezier(0, 0, 0.2, 1)` | Entering; things arriving decelerate |
| `ease-in` | `cubic-bezier(0.4, 0, 1, 1)` | Leaving; things departing accelerate |
| `ease-in-out` | `cubic-bezier(0.4, 0, 0.2, 1)` | Moving from one on-screen place to another |
| `spring` | stiffness about 300–500, damping about 25–35 | Gesture release, press feedback; tune per element, no overshoot on functional UI |
| `linear` | `linear` | Only for progress and continuous rotation |

Define the tokens once (CSS custom properties, a theme object, a Reanimated config) and use them everywhere.

## Reduced motion

Every spec has a reduced-motion column. The usual answers:

- Movement across the screen → cross-fade or instant.
- Scale and bounce → none; show the final state.
- Enter and exit → short opacity fade or instant.
- Progress and loaders → keep (they convey state), but no decorative motion around them.
- Parallax and scroll-linked motion → off.

## The spec row

Write motion in `DESIGN.md` under `## Motion` before implementing it:

| Interaction | Trigger | What moves | Duration | Easing | Reduced motion |
| --- | --- | --- | --- | --- | --- |
| Open filters sheet | tap "Filters" | sheet: translateY from 100% to 0; scrim: opacity 0 → 1 | `slow` | `ease-out` | sheet appears instantly, scrim fades |
| Delete list item | swipe past threshold | row: translateX off-screen, then height collapses via layout animation | `base` | `ease-in` | row disappears instantly, list reflows |
| Primary button press | press in / out | scale 1 → 0.97 → 1 | `fast` | `spring` | none |

A row that cannot name what moves and why is not ready to implement.

## Laws that apply

Doherty threshold (motion must not add to perceived wait), Fitts (feedback confirms the target was hit), Jakob (platform conventions for sheets, back gestures, and tabs), Aesthetic-usability (polish within restraint). See `skills/ux-laws/references/ux-laws.md`.
