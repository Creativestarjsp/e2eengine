# Example: Review of a Mobile Checkout Screen

Material: three screenshots of a single-page checkout on a 390 pt wide phone (cart summary, address and payment form, and the state after tapping Pay with an invalid card). Assumed user: a returning shopper completing a purchase one-handed. Primary goal: pay.

### UX Score

- Usability: 5/10
- Clarity: 6/10
- Navigation: 7/10
- Accessibility: 4/10
- Responsiveness: not assessed (one screen width only)
- Visual hierarchy: 5/10
- Performance perception: not assessed (static screenshots)

### Problems

**🔴 Critical**

1. **The Pay button gives no reason when it fails.** After tapping Pay with an invalid card number, the form scrolls to the top and shows "Something went wrong". The field at fault is off-screen and unmarked.
   - Principle: Postel's Law; error identification (accessibility).
   - Why: the user cannot tell what to correct, so the purchase stops.
   - Fix: keep the scroll position, mark the card number field with an inline message ("Card number is incomplete"), and move focus to it.

**🟠 High**

2. **Fourteen fields on one screen, including optional company name, second address line, and a newsletter choice.**
   - Principle: Hick's Law; Parkinson's Law; Tesler's Law.
   - Why: the form looks long before it starts and asks for decisions unrelated to paying.
   - Fix: prefill the saved address with an Edit link, collapse optional fields behind "Add company or apartment", and move the newsletter choice to the confirmation screen.

3. **Pay and "Continue shopping" are the same size and colour, side by side, with "Continue shopping" on the right.**
   - Principle: Von Restorff Effect; Fitts's Law; Serial Position Effect.
   - Why: the primary action does not stand out, and the easier thumb position goes to the action that abandons checkout.
   - Fix: make Pay a full-width filled button at the bottom; make "Continue shopping" a text link above the form.

4. **Field labels are light grey placeholder text that disappears on input, at roughly 2.6:1 contrast.**
   - Principle: Miller's Law (recall instead of recognition); contrast baseline.
   - Why: users lose track of what a field is once they type, and the text fails WCAG AA.
   - Fix: persistent labels above each field at 4.5:1 or better.

**🟡 Medium**

5. **Order total appears only at the top of the page; the Pay button says "Pay".**
   - Principle: Proximity; Peak-End Rule.
   - Why: at the moment of commitment the amount is out of view.
   - Fix: label the button with the amount ("Pay $48.20").

6. **Card number rejects spaces.**
   - Principle: Postel's Law.
   - Why: people type card numbers in groups of four as printed.
   - Fix: accept spaces and dashes, format as the user types.

**🟢 Low**

7. **No progress indication while payment is processing in the third screenshot.**
   - Principle: Doherty Threshold.
   - Fix: disable the button and show a spinner with "Processing payment…".

### Not Assessed

- Keyboard behaviour, focus order, and screen-reader labels: needs the running app or source.
- Tablet and desktop layouts: needs those widths.
- Actual response time after tapping Pay: needs the running app.

The cart summary, saved-card selector, and navigation bar follow platform conventions and need no change.
