---
name: seo-geo
description: "Assess how well a site can be discovered, understood and cited by search engines and AI answer systems. Use for AI-search readiness audits, citability review, crawler and fetcher access review, llms.txt evaluation, and entity or brand clarity."
---

# SEO GEO / AI Search Readiness

## Purpose

Evaluate how well a website can be discovered, understood, cited, and represented by search engines and AI answer systems without confusing AI visibility with traditional search ranking.

## When to Use

Use for:

- AI-search readiness audits
- citability reviews
- crawler/fetcher access review
- llms.txt and machine-readable content evaluation
- entity/brand clarity
- AI-friendly page structure

## Inputs

- target URL/domain
- audience/market
- business/entity context where available

Optional:

- analytics/search data
- brand/entity references
- crawler logs

## Workflow

```text
IDENTIFY ENTITY
→ INSPECT ACCESS
→ INSPECT CONTENT STRUCTURE
→ CHECK MACHINE-READABLE SIGNALS
→ CHECK CITABILITY
→ CHECK ACCESSIBILITY
→ ASSESS RISKS
→ RECOMMEND
→ VERIFY
```

## Decision Framework

Consider separately:

1. Traditional search discoverability
2. AI crawler/fetcher accessibility
3. Content clarity and citability
4. Entity/brand understanding
5. Structured data and semantic signals
6. Human usability and accessibility

Do not collapse these into a single unsupported score.

## Anti-Patterns

Avoid:

- claiming AI citations are guaranteed
- blocking AI crawlers without understanding business goals
- treating `llms.txt` as a guaranteed ranking or citation mechanism
- confusing training crawlers with user-triggered fetchers
- inventing AI visibility metrics
- optimizing for machines at the expense of human usability

## Quality Bar

A strong audit should identify:

- whether important content is crawlable and understandable
- whether pages use clear semantic structure
- whether important facts are easy to quote accurately
- whether entity identity and topical authority are clear
- whether structured data supports understanding
- whether accessibility signals improve machine comprehension

## Verification

Where available, inspect:

- robots.txt
- rendered HTML
- accessibility tree
- structured data
- server responses
- relevant crawler logs
- screenshots for visual/interaction claims

## Output

Return:

```text
AI Search Readiness:
Entity clarity:
Crawl/access findings:
Citability findings:
Machine-readable signals:
Human usability risks:
Recommended actions:
Limitations:
```

## Security

Do not expose private crawler logs, analytics, credentials, or authenticated data.

## Definition of Done

- AI/search concepts are kept distinct
- actual page behavior was inspected
- recommendations are evidence-backed
- uncertain future behavior is labeled as such
- human usability remains part of the evaluation
