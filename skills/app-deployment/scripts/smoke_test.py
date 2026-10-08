#!/usr/bin/env python3
"""Prove a deployment answers: request a few paths and compare status and content.

Usage:
  smoke_test.py --url https://preview.example.com --path /health --path /api/version
  smoke_test.py --url https://preview.example.com --path /admin=401 --contains ok
  smoke_test.py --url https://preview.example.com --checks smoke.json

  --path PATH[=STATUS]   expected status defaults to 200; repeatable
  --contains TEXT        text the first path's body must contain
  --checks FILE          JSON list of {"path", "status", "contains"} for richer suites
  --header "Name: value" sent with every request (e.g. a preview-protection bypass); repeatable
  --retries N            attempts per check while a deploy warms up (default 3)
  --delay SECONDS        wait between attempts (default 2)
  --timeout SECONDS      per request (default 10)
  --json                 machine-readable output

Exit 0 when every check passes, 1 otherwise. Header values are never printed.
The summary line is the evidence to paste into DEPLOYMENT.md.
No third-party dependencies.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path
from urllib.parse import urljoin, urlsplit


def parse_path(value: str) -> dict:
    path, sep, status = value.partition("=")
    if sep and not status.isdigit():
        raise ValueError(f"--path {value}: status must be a number")
    return {"path": path, "status": int(status) if sep else 200, "contains": None}


def load_checks(args: argparse.Namespace) -> list[dict]:
    checks = [parse_path(p) for p in args.path]
    if args.checks:
        data = json.loads(Path(args.checks).read_text(encoding="utf-8"))
        if not isinstance(data, list):
            raise ValueError("--checks file must contain a JSON list")
        for item in data:
            if not isinstance(item, dict) or "path" not in item:
                raise ValueError("each check needs a `path`")
            checks.append({"path": str(item["path"]), "status": int(item.get("status", 200)), "contains": item.get("contains")})
    if not checks:
        checks = [{"path": "/", "status": 200, "contains": None}]
    if args.contains:
        checks[0]["contains"] = args.contains
    return checks


def parse_headers(values: list[str]) -> dict[str, str]:
    headers = {}
    for value in values:
        name, sep, content = value.partition(":")
        if not sep or not name.strip():
            raise ValueError("--header must look like `Name: value`")
        headers[name.strip()] = content.strip()
    return headers


def request(url: str, headers: dict[str, str], timeout: float) -> tuple[int | None, str, str | None]:
    """``(status, body, transport error)`` for one GET."""
    req = urllib.request.Request(url, headers={"User-Agent": "e2e-smoke-test", **headers})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as response:  # noqa: S310 - scheme checked by caller
            return response.status, response.read(1_000_000).decode("utf-8", errors="replace"), None
    except urllib.error.HTTPError as exc:
        return exc.code, exc.read(1_000_000).decode("utf-8", errors="replace"), None
    except (urllib.error.URLError, OSError, ValueError) as exc:
        return None, "", str(getattr(exc, "reason", exc))


def run_check(base: str, check: dict, headers: dict[str, str], timeout: float, retries: int, delay: float) -> dict:
    url = urljoin(base if base.endswith("/") else base + "/", check["path"].lstrip("/"))
    result = {"path": check["path"], "expected": check["status"], "status": None, "ok": False, "reason": "", "ms": None, "attempts": 0}
    for attempt in range(1, retries + 1):
        started = time.monotonic()
        status, body, error = request(url, headers, timeout)
        result.update(status=status, ms=round((time.monotonic() - started) * 1000), attempts=attempt)
        if error:
            result["reason"] = f"no response: {error}"
        elif status != check["status"]:
            result["reason"] = f"expected {check['status']}, got {status}"
        elif check["contains"] and check["contains"] not in body:
            result["reason"] = "response does not contain the expected text"
        else:
            result.update(ok=True, reason="")
            break
        if attempt < retries:
            time.sleep(delay)
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--url", required=True, help="base URL of the deployment")
    parser.add_argument("--path", action="append", default=[], metavar="PATH[=STATUS]")
    parser.add_argument("--contains")
    parser.add_argument("--checks")
    parser.add_argument("--header", action="append", default=[])
    parser.add_argument("--retries", type=int, default=3)
    parser.add_argument("--delay", type=float, default=2.0)
    parser.add_argument("--timeout", type=float, default=10.0)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    parts = urlsplit(args.url)
    if parts.scheme not in {"http", "https"} or not parts.netloc:
        print("smoke_test: FAIL (--url must be an http(s) URL)")
        return 1
    try:
        checks = load_checks(args)
        headers = parse_headers(args.header)
    except (ValueError, OSError) as exc:
        print(f"smoke_test: FAIL ({exc})")
        return 1

    results = [run_check(args.url, c, headers, args.timeout, max(1, args.retries), max(0.0, args.delay)) for c in checks]
    passed = sum(1 for r in results if r["ok"])
    ok = passed == len(results)
    if args.json:
        print(json.dumps({"url": args.url, "ok": ok, "passed": passed, "total": len(results), "checks": results}, indent=2))
        return 0 if ok else 1
    for r in results:
        if r["ok"]:
            print(f"PASS    {r['path']} {r['status']} in {r['ms']} ms")
        else:
            print(f"FAIL    {r['path']} {r['reason']} (after {r['attempts']} attempts)")
    print(f"smoke_test: {'OK' if ok else 'FAIL'} ({passed}/{len(results)} checks) {args.url}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
