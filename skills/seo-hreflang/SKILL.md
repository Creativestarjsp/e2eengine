---
name: seo-hreflang
description: "Review multilingual and multi-region site architecture for correct language and region targeting, hreflang relationships, canonical consistency and URL structure. Use when a site serves multiple languages, countries or regional versions."
---

# SEO Hreflang / International

## Purpose

Review multilingual and multi-region website architectures for correct language/region targeting, hreflang relationships, canonical consistency, URL structure, and discoverability.

## When to Use

Use when a site serves multiple languages, countries, or regional versions.

## Inputs

- target domain
- supported locales
- language/region mapping
- representative URL sets

Optional:

- sitemap data
- Search Console data
- country/language traffic data

## Workflow

```text
MAP LOCALES
→ MAP URL SETS
→ CHECK HREFLANG
→ CHECK CANONICALS
→ CHECK RETURN LINKS
→ CHECK INDEXABILITY
→ CHECK SITEMAPS
→ VERIFY
→ REPORT
```

## Decision Rules

- Use language-region codes deliberately and consistently.
- Each localized URL should generally point to the intended equivalent localized versions when equivalents exist.
- Verify reciprocal annotations where the implementation requires them.
- Keep canonical and indexation directives consistent with the intended regional page.
- Do not create unnecessary locale variants without meaningful content or business value.

## Anti-Patterns

Avoid:

- conflicting canonical and hreflang signals
- missing reciprocal relationships
- invalid locale codes
- locale pages that are blocked from indexing
- automatic redirects that prevent crawlers/users from accessing intended variants
- near-duplicate localized pages with no meaningful localization

## Verification

Inspect rendered HTML, response headers where applicable, sitemap references, and representative locale pairs. Use browser automation for language/region switching behavior.

## Output

Report:

```text
Locale map:
Findings:
Critical:
High:
Medium:
Recommended fixes:
Verification:
Limitations:
```

## Security

Protect analytics, Search Console, CMS, and localization-management credentials.

## Definition of Done

- locale relationships are mapped
- hreflang and canonical interactions are checked
- representative pages are verified
- recommendations are specific and testable
