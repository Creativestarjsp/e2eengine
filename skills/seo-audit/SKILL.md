---
name: seo-audit
description: "Audit a site's search visibility, technical health, content quality, structured data, performance and AI-search readiness from evidence on the actual site. Use to diagnose crawl or indexing problems, review technical and on-page SEO, or produce a prioritized SEO action plan."
---

# SEO Audit

## Purpose

Audit a website's search visibility, technical health, content quality, structured data, performance, accessibility, and AI-search readiness using evidence from the actual site.

## When to Use

Use when asked to:

- audit a website for SEO
- diagnose crawl/indexing problems
- review technical SEO
- assess on-page SEO
- evaluate AI-search readiness
- create a prioritized SEO action plan

## When Not to Use

Do not use as the primary skill for implementing application code, generic marketing strategy, or unsupported search-ranking predictions.

## Inputs

Required:

- target URL/domain

Useful optional context:

- business type
- target market/location
- target audience
- Google Search Console or analytics access
- backlink/SERP data provider access

Never invent unavailable metrics.

## Workflow

```text
DISCOVER
→ RENDER
→ CRAWL
→ AUDIT SPECIALIST AREAS
→ AGGREGATE
→ PRIORITIZE
→ VERIFY
→ REPORT
```

### 1. Discover

Identify site type, major templates, language/region, primary business goal, and important page types.

### 2. Render

Inspect raw HTML and rendered output. Use browser automation for JavaScript-heavy applications. Capture accessibility and visual evidence when relevant.

### 3. Crawl

Crawl within an explicit limit, respect robots.txt, follow redirects, rate-limit requests, and record inaccessible areas.

### 4. Specialist Areas

Evaluate applicable areas:

- technical SEO
- crawlability/indexability
- on-page SEO
- content quality
- structured data
- performance/Core Web Vitals
- mobile experience
- image SEO
- internal linking
- internationalization/hreflang
- local SEO
- ecommerce SEO
- AI-search/citability readiness
- backlinks when reliable data is available

Use specialist skills/agents when available rather than duplicating their work.

### 5. Aggregate

Produce an evidence-backed health score only when scoring criteria are defined. Keep score components traceable to findings.

### 6. Prioritize

Rank issues by impact, severity, confidence, effort, and dependency.

### 7. Verify

Re-check important findings and distinguish measured facts from heuristics.

## Quality Bar

A high-quality audit:

- separates observed facts from recommendations
- cites the affected URL/page where possible
- identifies limitations in crawl or data access
- avoids obsolete SEO claims
- does not imply rankings are guaranteed by individual fixes
- produces actionable recommendations rather than generic SEO advice

## Anti-Patterns

Avoid:

- inventing traffic, rankings, backlink counts, or Search Console data
- treating every recommendation as a ranking factor
- declaring a page indexed without evidence
- ignoring robots.txt limitations
- over-weighting a single SEO score
- recommending outdated tactics without qualification
- making broad conclusions from one page on a large site

## Verification

Where practical verify with:

- raw HTTP/HTML responses
- rendered browser output
- sitemap/robots inspection
- structured-data validation
- Lighthouse/PageSpeed/CrUX data when available
- Search Console data when authenticated
- browser screenshots for visual claims
- reproducible crawl results

## Output

Create a structured report containing:

```text
SEO Health:
Scope:
Data sources:
Limitations:

Critical:
High:
Medium:
Low:

Quick wins:
Roadmap:
Verification notes:
```

For large audits, store structured findings so later reporting or comparison can reuse them.

## Security

Protect authenticated SEO data, private analytics, Search Console information, API keys, and site credentials. Never expose secrets in reports or screenshots.

## Definition of Done

- target site was actually inspected
- crawl/render limitations are documented
- findings are evidence-backed
- severity is justified
- recommendations are actionable
- no unavailable metrics are invented
- verification is documented
