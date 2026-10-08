# unDraw as a Fallback

unDraw (https://undraw.co/illustrations) is a library of open-source illustrations whose colour can be set on the site before download. Use it when generated artwork is not good enough: scenes with people, complex compositions, or after two failed attempts at original artwork.

## What the license allows and forbids

Read the current text at https://undraw.co/license before relying on this summary (checked October 2026):

- Allowed: use in commercial and non-commercial projects, modification, and distribution as part of your project, with no attribution required.
- Not allowed: compiling the assets to build a similar or competing service, or distributing them in packs.
- Not allowed without consent: automated or non-automated ways to link, embed, scrape, search, or download the assets from the website.
- Not allowed: using the assets to train, fine-tune, or develop AI or machine-learning models.

## What that means for an agent

A person chooses and downloads the illustration. The agent does not touch the site.

Do not:

- crawl, scrape, search, or fetch pages or files from undraw.co with any tool
- hotlink or embed an unDraw URL in the product; the file is committed to the project instead
- bulk-download illustrations, or add unDraw files to this skill or any shared library
- generate artwork that recreates a specific unDraw illustration; use the real asset or make something different

## Procedure

1. **Brief the person.** State the concept in a few words to search for (for example "empty folder", "team collaboration", "secure login") and the product's primary colour as a hex value to enter in the site's colour picker.
2. **The person downloads** the SVG from the site and places it in the project's illustration folder.
3. **Validate.** Run `svg_check.py` on the file. Downloaded files are untrusted until it passes. Remove fixed `width`/`height` on the root so it scales.
4. **Review.** Run `render_preview.py` and look at it in place: does it match the product's other illustrations in density and tone, and does it read on dark?
5. **Adapt lightly.** Replace the downloaded primary colour with the product's token or a component prop. Do not redraw it into a different illustration.
6. **Name and record.** Give it a semantic name and add it to `## Illustrations` in `DESIGN.md` with source `unDraw` and the date it was downloaded.

## Consistency

Mixing generated artwork with unDraw artwork in one product usually looks inconsistent. Once a product uses unDraw for one illustration, prefer it for the others, or keep unDraw for marketing pages and original artwork for in-app states.
