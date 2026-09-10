---
name: web-intelligence
description: Research public websites, crawl rendered pages, extract structured fields, inspect site patterns, and produce web intelligence for engineering, mock-data, product, SEO, and marketing work.
---

# Web Intelligence

## Purpose

Use the E2E `web.crawl` capability for controlled read-only research of public web pages. Crawl4AI is the current implementation provider; the skill stays vendor-neutral so the provider can change later.

## Use When

- Researching a public website or documentation site.
- Understanding page hierarchy, navigation, content structure, CTAs, forms, pricing layouts, or feature organization.
- Extracting repeated public fields into a schema for mock/test fixture design.
- Auditing public SEO metadata, headings, links, images, and structured content.
- Supporting competitor, positioning, content, or marketing research.
- Inspecting rendered pages that require browser execution.

## When Not to Use

- Do not use as a substitute for an approved API when an API is available and authoritative.
- Do not crawl private, authenticated, internal, localhost, cloud-metadata, or otherwise non-public network targets.
- Do not collect secrets, credentials, session tokens, or personal data as a fixture source.
- Do not copy proprietary site assets or implementation; use observations as inspiration and produce original output.
- Do not use extracted real customer data as mock data. Generate synthetic fixtures from the observed schema.

## Workflow

1. Validate the URL through the E2E web-intelligence boundary.
2. Crawl the smallest useful page set.
3. Prefer Markdown for general research and CSS/schema extraction for repeatable structured fields.
4. Record the source URL and purpose in evidence; do not store secrets or unnecessary personal data.
5. For mock data, infer field names, types, constraints, and relationships, then synthesize fictional values.
6. For inspiration, convert observations into requirements and design principles rather than copying content or assets.
7. For marketing/SEO, distinguish observed facts from derived recommendations.
8. Let SD3 verify evidence, scope, and security before the result is treated as trusted engineering input.

## Provider

The default provider is Crawl4AI 0.9.3 through `e2e.web_intelligence`. It is optional and must not become an E2E core dependency.

Crawl4AI's normal Markdown and CSS extraction paths do not require an LLM. Use LLM extraction only when explicitly authorized by a separate capability and policy.

## Safety

The adapter rejects non-HTTP(S) URLs, URLs containing userinfo, and hostnames resolving to non-global IP addresses. The E2E tool registry remains deny-by-default; `web.crawl` requires the `web.crawl` and `network.read` scopes.
