---
name: seo-technical
description: "Diagnose technical search problems across crawlability, indexability, security, URLs, mobile experience, performance, JavaScript rendering and structured data. Use for robots.txt and sitemap issues, canonical and noindex problems, Core Web Vitals, and SSR/CSR rendering issues."
---

# Technical SEO

## Purpose

Diagnose technical search visibility problems across crawlability, indexability, security, URLs, mobile experience, performance, JavaScript rendering, structured data, and internationalization-related controls.

## When to Use

Use for:

- robots.txt and sitemap issues
- indexing/canonical/noindex problems
- Core Web Vitals and page performance
- HTTPS and security-header review
- JavaScript rendering and SSR/CSR SEO issues
- URL/redirect architecture
- mobile SEO
- structured-data implementation checks
- hreflang and international technical issues

## Inputs

Required:
- target URL/domain

Optional:
- site architecture
- sitemap URLs
- Search Console data
- PageSpeed/CrUX data
- target markets/languages

Inspect actual responses before making conclusions.

## Workflow

```text
RENDER
→ CRAWL
→ CHECK CRAWLABILITY
→ CHECK INDEXABILITY
→ CHECK SECURITY
→ CHECK PERFORMANCE
→ CHECK JS RENDERING
→ CHECK STRUCTURED DATA
→ CHECK MOBILE / INTERNATIONAL
→ VERIFY
→ REPORT
```

## Core Checks

### Crawlability

Inspect:

- robots.txt
- XML sitemaps
- crawlable internal links
- blocked resources
- redirects
- crawl depth where measurable

### Indexability

Inspect:

- HTTP status
- canonical tags
- robots directives
- duplicate/parameter variants
- sitemap/canonical consistency
- accidental thin or duplicate URL surfaces

### Security

Review HTTPS, mixed content, and relevant security headers. Security headers should be treated as a technical-quality concern, not automatically as direct ranking factors.

### Performance

Use appropriate real-user or lab evidence where available. Treat Core Web Vitals as measured signals rather than guessing from code alone.

### JavaScript

Check whether title, canonical, robots, primary content, links, and structured data are present correctly in the initial response when practical. Verify rendered output for JS-heavy applications.

### Mobile

Check responsive behavior, content parity, viewport configuration, touch usability, and layout stability.

### Structured Data

Detect supported structured data, inspect validity, and route detailed schema work to a specialized schema skill when available.

## Decision Rules

- Prefer evidence from actual HTTP/rendered responses.
- Separate technical defects from recommendations.
- Do not claim a page is indexed without appropriate evidence.
- Do not recommend obsolete SEO practices without verifying current guidance.
- When a fix depends on Google processing time, state that it may take time to be reflected.

## Anti-Patterns

Avoid:

- declaring crawlability from robots.txt alone
- assuming a 200 response means successful indexing
- relying only on Lighthouse scores
- treating every security header as a ranking signal
- recommending canonical/noindex changes without checking site-wide URL relationships
- ignoring JavaScript-rendered output
- changing production SEO directives without considering traffic/indexation impact

## Verification

Use applicable:

- HTTP response inspection
- browser rendering
- sitemap/robots validation
- PageSpeed Insights or CrUX data
- structured-data validation
- Search Console evidence when available
- screenshots for visual/mobile claims

## Security

Protect private analytics, Search Console credentials, API tokens, and authenticated site data.

## Output

Report:

```text
Technical SEO Score:
Evidence sources:
Critical:
High:
Medium:
Low:
Recommended fixes:
Verification status:
Limitations:
```

## Definition of Done

- affected technical surface was inspected
- evidence supports findings
- important crawl/indexability/security/performance issues were considered
- JS/mobile impacts were checked where relevant
- recommendations are actionable
- limitations are explicit
