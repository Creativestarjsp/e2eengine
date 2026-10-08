# Output Formats

## SVG

Required:

- a valid `<svg>` root with `xmlns` and a `viewBox`
- scalable vector geometry only: `<path>`, `<circle>`, `<rect>`, `<ellipse>`, `<line>`, `<polygon>`, `<polyline>`, `<g>`
- no raster images unless explicitly requested
- transparent background by default
- no `width`/`height` in pixels on the root, so the artwork scales with its container
- layers in named groups (`<g id="folder">`)
- repeated colours defined once: a small `<style>` block with classes in a standalone file, props in a component
- no text; copy belongs to the interface

```svg
<svg viewBox="0 0 800 600" xmlns="http://www.w3.org/2000/svg" fill="none">
  <style>.primary{fill:#6366F1}.dark{fill:#1F2937}.light{fill:#F3F4F6}</style>
  <g id="subject">…</g>
</svg>
```

Forbidden, because SVG is executable content: `<script>`, event-handler attributes, `<foreignObject>`, `javascript:` links, references to external URLs, embedded `data:` images, `DOCTYPE` and entity declarations.

## Optimization

Avoid thousands of nodes, duplicate paths, hidden objects, unused definitions, stacked filters, and unnecessary clipping paths. Optimize without changing how it looks. A standalone file loaded through `<img>` cannot read the page's CSS variables, so theming belongs in the component form.

## React

One reusable component per illustration, for example `EmptyProjectsIllustration.tsx`:

- props: `primaryColor`, `secondaryColor`, `className`, `width`, `height`, and `title`
- colours default to the design system's tokens, never to an unrelated palette
- with a `title` the SVG gets `role="img"` and an accessible name; without one it is `aria-hidden`
- no page-specific layout inside the component

## React Native

Use `react-native-svg` (`Svg`, `G`, `Path`, `Rect`, `Circle`, `Ellipse`). Keep colours configurable through props, size responsive through `width`/`height` with the `viewBox` preserved, and interface logic outside the illustration component. `<style>` blocks are not supported there: set `fill` on each element from props.

## Naming

Semantic, PascalCase, ending in `Illustration`:

`EmptyProjectsIllustration`, `NoResultsIllustration`, `PaymentSuccessIllustration`, `TeamCollaborationIllustration`, `SecureAccountIllustration`

Never `image1`, `image2`, `final-final`, `new-image`, `test`.

## Accessibility

- An illustration is not the only way important information is conveyed; the heading and description carry it.
- Meaningful artwork: provide equivalent text and an accessible label.
- Decorative artwork: hide it from assistive technology (`aria-hidden="true"`, or an empty `alt` on an `<img>`).
- Do not rely on colour alone; keep sufficient contrast between the subject and its surroundings.

## Recording the asset

Add a row to `## Illustrations` in `DESIGN.md`:

| Asset | Used on | Source | Notes |
| --- | --- | --- | --- |
| `EmptyProjectsIllustration` | Projects list, empty state | original | primary + neutral palette |
