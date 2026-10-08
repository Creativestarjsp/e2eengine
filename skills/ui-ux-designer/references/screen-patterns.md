# Screen Patterns

Start each screen from the matching pattern, then adapt it to the product. A pattern is a default that has already solved the common problems; deviate when the user's task calls for it, and say why in `DESIGN.md`.

Every pattern assumes the states in `skills/ux-laws/references/platform-and-accessibility.md` (loading, empty, error, success, no permission) and the laws in `skills/ux-laws/references/ux-laws.md`.

## How to read a pattern

- **Job:** what the user is there to do.
- **Structure:** the elements, top to bottom.
- **Phone / Desktop:** what changes with width.
- **Get right:** the details that decide whether it works.
- **Avoid:** the usual mistakes.

---

## Navigation shell

**Job:** move between the product's main areas without thinking.

**Structure:** 3–5 primary destinations, the current one clearly marked; secondary destinations behind a "More" or profile entry; one place for global actions (search, create, notifications).

**Phone:** bottom tab bar with icons and labels for the primary destinations; a stack with a back affordance inside each tab; the primary creation action as a prominent button, not hidden in a menu.

**Desktop:** left sidebar with labels (collapsible to icons), or a top bar when there are few destinations; content area with a sensible maximum width; page title and page-level actions at the top of the content.

**Get right:** labels with every icon; the same destination order everywhere; a visible selected state that does not rely on colour alone.

**Avoid:** a hamburger menu as the only navigation on phone; more than five tabs; navigation that changes position between screens.

---

## Sign in and sign up

**Job:** get into the product with as little effort as possible.

**Structure:** product name or mark; a short heading; third-party sign-in buttons if offered; email and password fields with visible labels; primary button; a link to the other mode (sign in ↔ sign up) and to password reset.

**Phone:** one column, primary button full width and within thumb reach, correct keyboard type for each field, password manager and autofill supported.

**Desktop:** a centred card of readable width; no need to fill the screen.

**Get right:** show/hide password; inline validation after the field loses focus, not on every keystroke; errors beside the field in plain language; keep typed values after an error; ask only for what is needed to create the account.

**Avoid:** placeholder text as the only label; confirm-password fields where show/hide would do; clearing the form on error; an illustration that pushes the form below the fold.

---

## Onboarding

**Job:** reach the first moment of value quickly.

**Structure:** at most 3–4 steps, each with one idea or one question; a progress indicator; a way to skip what is optional; a final step that lands the user inside the product with something to do.

**Phone:** one step per screen, the primary action at the bottom, swipe and button both work.

**Desktop:** a focused centred panel, or inline setup inside the real product (a checklist) rather than a separate tour.

**Get right:** ask only for what changes the experience immediately; defer permissions until the feature that needs them; let the user leave and resume.

**Avoid:** a carousel of marketing slides before the user can do anything; mandatory profile completion; permission prompts on first launch with no context.

---

## Home or dashboard

**Job:** see what matters now and get to the next action.

**Structure:** the user's most frequent task first; then status at a glance (a few key numbers or items needing attention); then recent activity or shortcuts.

**Phone:** a single scrolling column, most important first; summary cards that open detail.

**Desktop:** a grid with a clear reading order; the primary content wider than the supporting column; no more than a handful of cards visible at once.

**Get right:** each number has a label, a time range, and, where useful, a comparison; cards are tappable to the detail behind them; the empty first-run version teaches what will appear here.

**Avoid:** every metric the system has; charts without a question they answer; equal visual weight on everything.

---

## List and detail

**Job:** find an item, then read or act on it.

**Structure (list):** title, search or filter when the list can be long, items with a primary line, a secondary line, and at most one or two pieces of metadata; a clear primary creation action.

**Structure (detail):** title and status, key facts first, then sections; actions that apply to the item at the top or in a fixed bar.

**Phone:** list and detail are separate screens; swipe actions only as a shortcut to actions that are also reachable another way; pull to refresh.

**Desktop:** list and detail side by side when it helps comparison; a table when users compare rows by column; row hover shows actions, which are also reachable by keyboard.

**Get right:** preserve scroll position and filters when returning from detail; skeleton rows while loading; pagination or incremental loading with a visible end; an empty state that offers the creation action.

**Avoid:** truncating the one field users search by; destructive actions without confirmation or undo; a table forced onto a phone.

---

## Search and filters

**Job:** narrow a large set to the few items wanted.

**Structure:** a search field, the active filters shown as removable chips, the result count, the results, and a "clear all".

**Phone:** filters in a sheet with an "Apply" action showing the result count; active filters visible above the results.

**Desktop:** filters in a side panel or a bar above the results, applied immediately.

**Get right:** tolerate typos and partial matches; keep the query in the field after searching; a no-results state that says what was searched and offers to relax a filter.

**Avoid:** filters hidden with no indication they are active; resetting filters on back navigation; a blank page for no results.

---

## Forms (create and edit)

**Job:** enter information correctly the first time.

**Structure:** a title that says what is being created; fields in one column grouped by topic; labels above fields; helper text only where needed; primary action last, secondary beside it.

**Phone:** one column, the right keyboard and autofill hints, the primary button visible above the keyboard or fixed at the bottom.

**Desktop:** still one column for scanning; a readable maximum width; long forms split into sections or steps with progress.

**Get right:** mark optional fields rather than required ones when most are required; sensible defaults; accept forgiving input (spaces in numbers, any date format that is unambiguous); validate on blur; on submit, focus the first error and summarise; warn before discarding unsaved changes.

**Avoid:** multi-column layouts that break reading order; disabling the submit button with no explanation; asking for information the system already has.

---

## Settings

**Job:** change one thing and leave.

**Structure:** grouped sections with plain names; each setting with a label and, where the effect is not obvious, a one-line description; changes saved immediately with confirmation, or one clear Save per section.

**Phone:** a list of groups that open sub-screens.

**Desktop:** section navigation at the side, content at a readable width.

**Get right:** search when there are many settings; dangerous actions (delete account, revoke access) separated, labelled plainly, and confirmed.

**Avoid:** mixing saved-immediately and needs-Save controls on one screen; internal terminology; illustrations.

---

## Checkout and payment

**Job:** pay with confidence.

**Structure:** order summary always reachable; contact, delivery, and payment in that order; total with all costs before the final action; a primary button that states the action and the amount.

**Phone:** one step per screen or a single short page; platform wallets offered first; numeric keyboards for card fields.

**Desktop:** form on one side, order summary fixed on the other.

**Get right:** guest checkout; saved details prefilled with an edit link; card number formatted as typed and spaces accepted; errors beside the field with the reason; a processing state that prevents double payment; a confirmation with what happens next.

**Avoid:** surprise costs at the last step; forced account creation; leaving the page for a third-party payment form without warning.

---

## Profile and account

**Job:** see and manage one's own identity in the product.

**Structure:** avatar and name; key account facts; entry points to edit profile, security, notifications, billing, and sign out.

**Get right:** sign out easy to find but not adjacent to destructive actions; edits confirmed; email or password changes verified.

**Avoid:** burying sign out; exposing internal identifiers.

---

## Notifications and activity

**Job:** catch up on what happened and act on what needs it.

**Structure:** newest first, grouped by day; each item says who did what to which thing, with a time; unread items distinguished by more than colour; a way to mark all read.

**Get right:** tapping an item goes to the thing it is about; settings to control what generates a notification.

**Avoid:** notifications that cannot be acted on; a badge count that never clears.

---

## States every screen has

| State | Pattern |
| --- | --- |
| Loading | A skeleton in the shape of the content for waits over about a second; a spinner only for small, short actions (`lottie-animation` for a branded loader) |
| Empty (first use) | What will appear here, why it is empty, and the action that fills it; an illustration only if it helps (`vector-illustration`) |
| Empty (no results) | What was searched or filtered, and one action to broaden it |
| Error | What went wrong in plain words, whether the user's data is safe, and a retry or alternative |
| Success | Confirmation of what happened and the next step; for routine actions a brief toast is enough; a short play-once animation only for moments worth marking (`lottie-animation`) |
| Offline or degraded | What still works, and that changes will sync |
| No permission | Why the area is unavailable and who can grant access |

---

## Dialogs, sheets, and toasts

- **Dialog:** for a decision that must be made before continuing. A title that asks the question, buttons labelled with the action ("Delete project", not "OK"), the safe choice easiest to reach, dismissible by Escape or back.
- **Bottom sheet (phone) / side panel (desktop):** for a short task that keeps the context visible.
- **Toast:** for confirmation that needs no decision; offer Undo for destructive actions instead of a confirmation dialog where possible. Never put the only copy of important information in a toast.
