# Web Intelligence

E2E exposes public-web research as a controlled capability instead of coupling the core runtime to a crawler vendor.

## Architecture

```text
SD1 / SD2 / SD3
       │
       ▼
 web-intelligence skill
       │
       ▼
 E2E tool policy
       │
       ├── web.crawl
       └── network.read
       │
       ▼
 e2e.web_intelligence
       │
       ▼
 Crawl4AI 0.9.3 (optional)
```

Crawl4AI is intentionally an implementation provider. A future crawler/browser provider can replace it without changing the skill contract or SD orchestration model.

## Capabilities

- Rendered-page crawling to Markdown.
- CSS/schema-based structured extraction without an LLM.
- Public-site research for engineering and product work.
- Website structure and UI inspiration analysis.
- Synthetic mock-data schema discovery.
- SEO and marketing research.

## Security boundary

The adapter validates HTTP(S) URLs, rejects URL userinfo, resolves the hostname, and rejects non-global IP addresses before Crawl4AI is invoked. The E2E registry remains deny-by-default and requires `web.crawl` plus `network.read` scopes.

Do not expose arbitrary URL input from an untrusted network directly to the adapter. If E2E is deployed as a service, enforce outbound network policy, DNS/rebinding protections, rate limits, and request budgets at the service/network boundary as well.

Crawl4AI has had recent security releases addressing SSRF and file-write issues, so E2E pins the optional integration to `0.9.3` rather than using an unconstrained dependency. Keep the pin current through deliberate dependency updates.

## LLM policy

Basic Markdown crawling and CSS/schema extraction are local operations and do not require an LLM. LLM extraction remains a separate capability and must use the existing E2E authorization, secret handling, and audit controls.

## Intended workflows

### Mock data

```text
public website
    ↓
page/schema discovery
    ↓
field names + types + constraints
    ↓
synthetic fixture generation
    ↓
tests / demos
```

Real customer, credential, or other sensitive data must never be copied into fixtures.

### Website inspiration

```text
public sites
    ↓
structure / navigation / CTA / content observations
    ↓
design requirements
    ↓
original implementation
```

The output should capture patterns and requirements, not copy proprietary assets or implementation.

### Marketing / SEO

```text
public pages
    ↓
metadata / headings / links / content patterns
    ↓
competitive + SEO observations
    ↓
marketing recommendations
```

Observed facts and derived recommendations should remain clearly separated in evidence.
