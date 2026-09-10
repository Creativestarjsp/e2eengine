from __future__ import annotations

import socket

import pytest

from e2e.web_intelligence import WebIntelligenceError, validate_public_url


def test_rejects_non_http_urls() -> None:
    with pytest.raises(WebIntelligenceError, match="only http"):
        validate_public_url("file:///tmp/example.html")


def test_rejects_url_userinfo() -> None:
    with pytest.raises(WebIntelligenceError, match="userinfo"):
        validate_public_url("https://user:pass@example.com")


def test_rejects_private_resolution(monkeypatch: pytest.MonkeyPatch) -> None:
    def fake_getaddrinfo(*args, **kwargs):
        return [(socket.AF_INET, socket.SOCK_STREAM, 6, "", ("127.0.0.1", 443))]

    monkeypatch.setattr(socket, "getaddrinfo", fake_getaddrinfo)
    with pytest.raises(WebIntelligenceError, match="non-public"):
        validate_public_url("https://example.com")


def test_accepts_public_resolution(monkeypatch: pytest.MonkeyPatch) -> None:
    def fake_getaddrinfo(*args, **kwargs):
        return [(socket.AF_INET, socket.SOCK_STREAM, 6, "", ("93.184.216.34", 443))]

    monkeypatch.setattr(socket, "getaddrinfo", fake_getaddrinfo)
    assert validate_public_url("https://example.com") == "https://example.com"
