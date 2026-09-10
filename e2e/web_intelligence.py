"""Controlled Crawl4AI adapter for E2E web intelligence.

Crawl4AI remains an optional dependency. This module is deliberately small: E2E
owns authorization and URL safety, while Crawl4AI owns browser/crawling details.
"""

from __future__ import annotations

import asyncio
import ipaddress
import json
import socket
from dataclasses import dataclass
from urllib.parse import urlparse


class WebIntelligenceError(RuntimeError):
    """Raised when the optional crawler cannot be used safely."""


@dataclass(frozen=True)
class CrawlResult:
    url: str
    markdown: str
    success: bool
    status_code: int | None
    title: str | None


def validate_public_url(url: str) -> str:
    """Allow only HTTP(S) URLs whose resolved addresses are globally routable."""
    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"}:
        raise WebIntelligenceError("only http:// and https:// URLs are allowed")
    if not parsed.hostname:
        raise WebIntelligenceError("URL must include a hostname")
    if parsed.username or parsed.password:
        raise WebIntelligenceError("userinfo in URLs is not allowed")

    try:
        addresses = {
            info[4][0]
            for info in socket.getaddrinfo(parsed.hostname, parsed.port or (443 if parsed.scheme == "https" else 80), type=socket.SOCK_STREAM)
        }
    except OSError as exc:
        raise WebIntelligenceError(f"hostname resolution failed: {parsed.hostname}") from exc

    if not addresses:
        raise WebIntelligenceError("hostname did not resolve to an address")
    for address in addresses:
        ip = ipaddress.ip_address(address)
        if not ip.is_global:
            raise WebIntelligenceError("target resolves to a non-public network address")
    return url


def _require_crawl4ai():
    try:
        from crawl4ai import AsyncWebCrawler, CacheMode, CrawlerRunConfig
    except ImportError as exc:
        raise WebIntelligenceError(
            "Crawl4AI is optional. Install E2E with `pip install -e .[web]`."
        ) from exc
    return AsyncWebCrawler, CacheMode, CrawlerRunConfig


async def crawl(url: str, *, timeout_ms: int = 30000) -> CrawlResult:
    """Crawl one public URL and return LLM-ready Markdown without LLM calls."""
    safe_url = validate_public_url(url)
    AsyncWebCrawler, CacheMode, CrawlerRunConfig = _require_crawl4ai()
    config = CrawlerRunConfig(cache_mode=CacheMode.BYPASS, page_timeout=timeout_ms)

    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(url=safe_url, config=config)

    metadata = getattr(result, "metadata", {}) or {}
    return CrawlResult(
        url=safe_url,
        markdown=getattr(result, "markdown", "") or "",
        success=bool(getattr(result, "success", False)),
        status_code=getattr(result, "status_code", None),
        title=metadata.get("title") if isinstance(metadata, dict) else None,
    )


def crawl_sync(url: str, *, timeout_ms: int = 30000) -> CrawlResult:
    """Synchronous boundary for CLI/runtime callers."""
    return asyncio.run(crawl(url, timeout_ms=timeout_ms))


def extract_css_sync(url: str, schema: dict) -> list[dict]:
    """Extract structured fields with Crawl4AI's non-LLM CSS strategy."""
    safe_url = validate_public_url(url)
    try:
        from crawl4ai import AsyncWebCrawler, CacheMode, CrawlerRunConfig, JsonCssExtractionStrategy
    except ImportError as exc:
        raise WebIntelligenceError(
            "Crawl4AI is optional. Install E2E with `pip install -e .[web]`."
        ) from exc

    async def _run() -> list[dict]:
        config = CrawlerRunConfig(
            cache_mode=CacheMode.BYPASS,
            extraction_strategy=JsonCssExtractionStrategy(schema),
        )
        async with AsyncWebCrawler() as crawler:
            result = await crawler.arun(url=safe_url, config=config)
        if not getattr(result, "success", False):
            raise WebIntelligenceError(getattr(result, "error_message", "crawl failed"))
        raw = getattr(result, "extracted_content", "") or "[]"
        data = json.loads(raw)
        if not isinstance(data, list):
            raise WebIntelligenceError("structured extraction did not return a list")
        return data

    return asyncio.run(_run())
