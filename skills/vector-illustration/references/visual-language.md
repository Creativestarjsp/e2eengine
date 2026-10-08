# Visual Language

## If the project already has an illustration style

Preserve it. A new illustration must look like it belongs to the same product. Match:

character proportions · shape language · colour palette · stroke treatment · corner radius · shadows · line weight · visual density · composition · perspective · object proportions

## If it does not

Create an original illustration in a modern flat-vector style:

- clean geometric shapes and rounded forms
- simple characters with minimal facial detail
- flat shapes, controlled colours, clear silhouettes
- generous whitespace, simple objects
- subtle depth, minimal visual noise

The result should feel modern, friendly, minimal, professional, original, and product-ready.

## Originality

Create original artwork. Do not:

- copy or trace existing illustrations
- reproduce a specific illustration or a named asset from an illustration library
- copy a distinctive character design or composition
- reproduce another company's asset collection
- produce a near-identical version of a reference

When a reference is provided, use it only to understand broad characteristics: simplicity, colour density, vector style, character complexity, composition, level of detail, visual hierarchy. Then make a new composition. No pixel-level or structural replication.

## Building blocks

- **Shapes:** circles, rounded rectangles, simple polygons, organic shapes, clean paths.
- **Objects:** simplified to their most recognisable form: laptop, phone, cloud, database, folder, calendar, chart, document, rocket, book, server, lock, magnifier, envelope, shopping cart, code editor, dashboard.
- **Characters:** simple head, simple hair, minimal facial features, simplified body and clothing, natural poses.

## Characters

Simple, friendly, geometric, consistent, easy to recognise, and appropriate to the product. Avoid photorealistic people, excessive facial detail, hyper-realistic anatomy, unnecessary clothing detail, and complex textures. A character supports the story; it is the whole focus only when the illustration is specifically character-driven.

Hand-written SVG characters are the hardest thing to get right. If a scene needs people, plan for the unDraw fallback.

## Composition

Every illustration has one clear focal point.

Prefer: one primary subject, supporting secondary objects, balanced composition, clear hierarchy, generous negative space, strong silhouettes, logical relationships between elements.

Avoid: random floating objects, excessive decoration, overcrowding, tiny details, unrelated objects, visual noise.

## Storytelling

Communicate an action or a state, not a display of objects.

| Weak | Better |
| --- | --- |
| Laptop + cloud + chart | A person working on a laptop with a dashboard visible, cloud and data elements supporting the idea of productivity |
| A lock | A person interacting with a secure interface that contains a lock and privacy elements |

## Colour

Use the application's design system. If a primary brand colour exists, it is the visual anchor.

Typical roles:

```text
Primary:    the product's brand colour
Dark:       #1F2937
Light:      #F3F4F6
Secondary:  an accent derived from the primary
Background: transparent
```

Keep the palette controlled: one primary, one or two supporting colours, and neutrals. Do not hard-code a brand colour when the application provides one. When the application exposes `primaryColor`, `secondaryColor`, `backgroundColor`, and `textColor`, map the illustration onto them.

## Dark mode

Design both themes. Check for adequate contrast, muddy colours, dark shapes that disappear, and a hierarchy that still reads. Do not simply invert: choose the dark-theme neutrals deliberately and keep the primary recognisable.

## Shadows and depth

Use subtle depth only when it helps: soft shadows at low opacity, one consistent light direction, simple layering, limited overlap. Avoid heavy drop shadows, photorealistic lighting, excessive gradients, and 3D rendering.

## Background

Transparent by default, so the artwork works on cards, pages, hero sections, and both themes. If a background is needed, use simple shapes rather than a scene.
