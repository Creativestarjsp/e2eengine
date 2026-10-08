---
name: vector-illustration
description: "Decide whether an interface benefits from an illustration and, when it does, produce an original vector illustration in SVG that follows the product's palette and illustration style, with unDraw as a fallback source. Use for empty-state, no-results, and hero illustrations, for choosing between an icon and an illustration, and for validating SVG artwork before it ships."
version: 1.0.0
level: L2
---

# Vector Illustration & Visual Assets

## Purpose

Act as a UI illustration designer and vector-graphics specialist. Decide whether a screen, state, or section actually benefits from an illustration; when it does, deliver original, modern vector artwork that belongs to the product's design system, as SVG or as a themable component.

The governing principle: **do not create an illustration unless it provides meaningful UX or visual value.**

## When to Use

- An empty-state, no-results, or first-run view needs artwork that explains the state.
- A hero section needs artwork.
- Deciding between an icon, an illustration, typography, whitespace, or a chart for a given spot.
- Extending an existing illustration set with artwork in the same style.
- Validating an SVG illustration, or integrating one a person downloaded from unDraw.

## When Not to Use

- Not a substitute for `ui-ux-designer` when the work is the layout, flow, or visual system the artwork sits in.
- Not a substitute for an icon library when a small symbolic glyph communicates the idea.
- Not a substitute for a brand designer when the asset is a logo, wordmark, or mascot.
- Not a substitute for `aso-appstore-screenshots` when the deliverable is store listing imagery.
- Not a substitute for a charting library when the content is data.
- Not a substitute for `lottie-animation` when the view needs motion (a loader, an animated success state); this skill produces still artwork.

## Inputs

Required:
- the place the artwork goes (which view or section, and what the user is doing there)

Discoverable from the repository:
- existing illustrations and their style (search for `*.svg`, illustration components, an assets or illustrations folder)
- design tokens: primary, secondary, neutral, and background colours, light and dark
- platform and framework: web, React, React Native
- `DESIGN.md` for the screen's hierarchy and primary action

Do not put these questions to the user unless the request is genuinely ambiguous; use professional judgement and state assumptions.

## Outputs

- A decision, stated in one or two sentences: illustration, icon, or nothing, and why
- When an illustration is warranted: an `.svg` file and, where the project uses them, a React or `react-native-svg` component with configurable colours and size
- `svg_check.py` passing, and a rendered preview that was actually looked at
- A row in the `## Illustrations` table of `DESIGN.md`: asset name, where used, source (original, existing, or unDraw)

## Workflow

```text
DECIDE → REUSE → DESIGN → DRAW → CHECK → RENDER AND REVIEW → INTEGRATE → RECORD
```

1. **Decide.** Apply `references/decision-guide.md`. If an icon, typography, whitespace, or a chart serves the user better, say so and stop.
2. **Reuse.** Search the project for an existing illustration or design-system asset that fits or can be adapted. Generate new artwork only when none does.
3. **Design.** Fix the concept in a sentence that describes an action or state, not a pile of objects. Pick the type and the level of detail from `references/types-and-responsive.md`. Take the palette from the product's tokens. If the project has an illustration style, match it (`references/visual-language.md`).
4. **Draw.** Write the SVG following `references/output-formats.md`: `viewBox`, transparent background, grouped and named layers, a small palette, no raster, no text.
5. **Check.** Run `python skills/vector-illustration/scripts/svg_check.py <file.svg>`. It must exit 0.
6. **Render and review.** Run `python skills/vector-illustration/scripts/render_preview.py <file.svg>` and look at the result at a small and a large size, on light and dark backgrounds. Ask: is the subject recognisable at the small size, are proportions right, does anything overlap or float, does it read on dark? Fix and repeat.
7. **Fallback.** If two honest attempts do not produce artwork that passes the review, or the concept needs people or a complex scene, stop drawing and use the unDraw fallback in `references/undraw-fallback.md`. Say plainly that the generated artwork was not good enough.
8. **Integrate.** Give the asset a semantic name. Wrap it in a component when the framework calls for one. Mark it decorative or give it a text alternative.
9. **Record.** Add the asset to the `## Illustrations` table in `DESIGN.md`.

## Rules / Constraints

- No illustration merely because there is empty space. Dense, task-focused, or small views usually get none.
- The illustration never competes with the primary action. On small screens reduce it or remove it.
- Original artwork only. Do not copy, trace, or closely recreate an existing illustration, a named library asset, or a distinctive character or composition. A reference informs simplicity, colour density, and level of detail, nothing more.
- Use the product's palette. Do not hard-code a brand colour the application already provides.
- Transparent background unless the layout requires one.
- No text inside the artwork; headings and descriptions are real text in the interface.
- An illustration is never the only carrier of information. Meaningful artwork gets a text alternative; decorative artwork is hidden from assistive technology.
- SVG must be inert: no scripts, event handlers, `foreignObject`, external references, or embedded raster images. `svg_check.py` enforces this for generated and downloaded files alike.
- Never claim artwork is production-ready without having looked at a rendered preview. If no renderer is available, say the visual review was not performed.
- unDraw: a person selects and downloads the file. Do not crawl, search, scrape, hotlink, or bulk-download the site, and do not store unDraw files in this skill. See `references/undraw-fallback.md`.
- Dark mode is designed, not inverted.
- Keep the asset small enough that it does not delay the interface; large artwork below the fold is lazy-loaded.

The UX laws that bear on illustration (Fitts, Hick, Jakob, Miller, Aesthetic-Usability, Proximity, Similarity, Figure-Ground, Doherty) are in `skills/ux-laws/references/ux-laws.md`; apply them, do not restate them.

## Error Handling

| Situation | Action |
| --- | --- |
| The spot does not warrant an illustration | Say so, recommend the icon, text, or whitespace alternative, and stop. |
| `svg_check.py` fails | Fix each error. For a downloaded file with scripts or external references, remove them or reject the file. |
| No renderer available for the preview | Report that the artwork was not visually reviewed; open `preview.html` in a browser by another means or ask the user to look. |
| Generated artwork fails the visual review twice | Stop iterating; use the unDraw fallback or recommend a designer. |
| Project style cannot be matched | Report what differs and let the user decide between a new style and commissioning artwork. |
| A reference image is supplied with "make it like this" | Extract broad characteristics only and produce a new composition; decline near-replication. |

## Validation

- The decision to illustrate is stated with its reason.
- `svg_check.py` exits 0.
- A rendered preview was viewed at small and large sizes on light and dark backgrounds, or the report says it was not.
- The subject is recognisable at 120 px wide.
- Colours come from the product's tokens or the component's props.
- The asset has a semantic name and an accessibility treatment.

## Examples

`examples/EmptyProjectsIllustration.svg` is an original empty-state illustration that passes the checker; `examples/EmptyProjectsIllustration.tsx` is the same artwork as a React component with configurable colours.

## Definition of Done

An illustration exists only where it adds value; it is original or properly sourced, matches the product, passes the checker, has been looked at in a rendered preview, is named, accessible, themable, and recorded in `DESIGN.md`.

## Security Considerations

SVG is executable content: it can contain scripts, event handlers, and references that load remote resources. Treat every SVG that did not come from this workflow, including downloads, as untrusted until `svg_check.py` passes. Prefer rendering through `<img>` or a component over injecting raw SVG markup from an untrusted source.

## Limitations

- Geometric, object-based scenes are within reach of hand-written SVG. Characters, hands, and complex perspective often are not; that is what the fallback is for.
- The checker verifies structure, safety, and budget. It cannot judge whether the artwork is good.
- Raster illustration, animation, and 3D are out of scope.
