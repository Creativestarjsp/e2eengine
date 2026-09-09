---
name: seo-ecommerce
description: "Improve search visibility for ecommerce: product discovery, category architecture, structured data, faceted navigation, internal linking and product-page quality. Use for ecommerce SEO audits, product and category SEO, and faceted-navigation review."
---

# Ecommerce SEO

## Purpose

Audit and improve search visibility for ecommerce sites, focusing on product discovery, category architecture, structured data, faceted navigation, internal linking, and product-page quality.

## When to Use

Use for:

- ecommerce SEO audits
- product/category SEO
- faceted-navigation review
- product structured-data review
- marketplace/search visibility planning

## Inputs

- ecommerce domain
- key product/category URLs
- market/locale
- product/catalog context

Optional:

- Search Console data
- analytics
- feed/catalog data
- merchant platform context

## Workflow

```text
MAP CATALOG
→ INSPECT CATEGORY ARCHITECTURE
→ INSPECT PRODUCT PAGES
→ CHECK CRAWL/INDEX CONTROLS
→ CHECK STRUCTURED DATA
→ CHECK INTERNAL LINKING
→ ASSESS DUPLICATION / FACETS
→ PRIORITIZE
→ VERIFY
```

## Decision Rules

- Distinguish indexable landing pages from filter combinations that create low-value URL expansion.
- Preserve strong product/category discoverability.
- Treat structured data as support for machine understanding, not a guarantee of rich results.
- Avoid removing useful search demand pages merely to reduce URL count.
- Consider out-of-stock, discontinued, variant, and duplicate product behavior explicitly.

## Anti-Patterns

Avoid:

- indexing every filter combination without strategy
- deleting products without redirect/availability logic
- duplicating manufacturer descriptions at scale
- relying on product schema without validating rendered markup
- keyword-stuffing category copy
- ignoring pagination and internal link depth

## Quality Bar

Review:

- product/category discoverability
- crawl efficiency
- canonical/indexation strategy
- product and category content quality
- structured data validity
- internal linking
- faceted navigation behavior
- mobile usability

## Verification

Use browser rendering, sitemap/robots inspection, structured-data validation, and search/analytics evidence when available.

## Output

Provide:

```text
Catalog findings:
Critical issues:
High-impact opportunities:
Architecture changes:
Product-page recommendations:
Verification:
```

## Security

Protect catalog credentials, analytics, merchant feeds, private pricing, and customer data.

## Definition of Done

- key catalog paths were inspected
- crawl/index risks are understood
- structured data was checked where relevant
- recommendations consider product lifecycle and facets
- evidence and limitations are documented
