#!/usr/bin/env python3
"""Capture built screens at phone and desktop widths so a UX review looks at the real result.

Usage:
  capture_screens.py --url http://localhost:3000 --path / --path /login [--out DIR]
                     [--viewports phone=390x844,desktop=1440x900] [--json]

Writes one PNG per path per viewport, named `<path>-<viewport>.png`, using a
headless Chrome or Chromium. Each image shows the first viewport of the page;
scrolled, authenticated, or interactive states need the browser skill instead.

A headless browser window cannot be narrower than about 500 px: asked for 390,
it lays the page out at 500 and crops the picture, which looks like an overflow
bug that is not there. Viewports narrower than that are therefore rendered in a
frame of the exact width inside a wider window; the grey band beside the frame
is not part of the page. A site that forbids framing shows an empty frame;
capture it with the browser skill instead.

Exit 0 when every capture succeeded, 1 on bad input or a failed capture,
2 when no browser is installed (the review must then say screens were not looked at).

Only http(s) URLs are accepted. No third-party dependencies.
"""

from __future__ import annotations

import argparse
import html
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path
from urllib.parse import urljoin, urlsplit

CHROME_CANDIDATES = (
    "google-chrome", "google-chrome-stable", "chromium", "chromium-browser", "chrome",
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/Applications/Chromium.app/Contents/MacOS/Chromium",
    "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
)
DEFAULT_VIEWPORTS = "phone=390x844,desktop=1440x900"
#: Below this a headless window stops shrinking its layout.
MIN_WINDOW_WIDTH = 500


def find_chrome() -> str | None:
    for candidate in CHROME_CANDIDATES:
        found = shutil.which(candidate) or (candidate if Path(candidate).is_file() else None)
        if found:
            return found
    return None


def parse_viewports(value: str) -> list[tuple[str, int, int]]:
    viewports = []
    for item in value.split(","):
        match = re.fullmatch(r"\s*([A-Za-z][\w-]*)=(\d{2,5})x(\d{2,5})\s*", item)
        if not match:
            raise ValueError(f"viewport `{item.strip()}` must look like phone=390x844")
        viewports.append((match.group(1), int(match.group(2)), int(match.group(3))))
    if not viewports:
        raise ValueError("at least one viewport is required")
    return viewports


def slug(path: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9]+", "-", path).strip("-")
    return cleaned or "home"


def plan(base: str, paths: list[str], viewports: list[tuple[str, int, int]], out: Path) -> list[dict]:
    """Every capture to make, before anything runs."""
    parts = urlsplit(base)
    if parts.scheme not in {"http", "https"} or not parts.netloc:
        raise ValueError("--url must be an http(s) URL")
    root = base if base.endswith("/") else base + "/"
    return [
        {"path": path, "viewport": name, "width": width, "height": height,
         "url": urljoin(root, path.lstrip("/")), "file": (out / f"{slug(path)}-{name}.png").as_posix()}
        for path in (paths or ["/"])
        for name, width, height in viewports
    ]


def frame_page(shot: dict) -> Path:
    """A local page holding the target in a frame of the exact viewport size."""
    target = Path(shot["file"])
    page = target.parent / "_frames" / (target.stem + ".html")
    page.parent.mkdir(parents=True, exist_ok=True)
    page.write_text(
        '<!doctype html><html><body style="margin:0;background:#D1D5DB">'
        f'<iframe src="{html.escape(shot["url"], quote=True)}" width="{shot["width"]}" height="{shot["height"]}" '
        'style="border:0;display:block;background:#fff"></iframe></body></html>',
        encoding="utf-8",
    )
    return page


def command(chrome: str, shot: dict) -> list[str]:
    framed = shot["width"] < MIN_WINDOW_WIDTH
    shot["framed"] = framed
    target = frame_page(shot).resolve().as_uri() if framed else shot["url"]
    width = MIN_WINDOW_WIDTH if framed else shot["width"]
    return [
        chrome, "--headless", "--disable-gpu", "--hide-scrollbars",
        f"--window-size={width},{shot['height']}", f"--screenshot={shot['file']}", target,
    ]


def capture(chrome: str, shot: dict, timeout: int = 90) -> bool:
    target = Path(shot["file"])
    target.unlink(missing_ok=True)
    try:
        subprocess.run(command(chrome, shot), capture_output=True, timeout=timeout)
    except (OSError, subprocess.SubprocessError):
        return False
    return target.is_file() and target.stat().st_size > 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--url", required=True, help="base URL of the running app")
    parser.add_argument("--path", action="append", default=[], help="path to capture; repeatable (default: /)")
    parser.add_argument("--viewports", default=DEFAULT_VIEWPORTS)
    parser.add_argument("--out", default="ux-review/screens")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    out = Path(args.out)
    try:
        shots = plan(args.url, args.path, parse_viewports(args.viewports), out)
    except ValueError as exc:
        print(f"capture_screens: FAIL ({exc})")
        return 1
    chrome = find_chrome()
    if chrome is None:
        print("capture_screens: NO BROWSER (install Chrome or Chromium, or capture with the browser skill; screens were not looked at)")
        return 2
    out.mkdir(parents=True, exist_ok=True)
    for shot in shots:
        shot["ok"] = capture(chrome, shot)
    failed = [s for s in shots if not s["ok"]]
    if args.json:
        print(json.dumps({"ok": not failed, "captures": shots}, indent=2))
        return 0 if not failed else 1
    for shot in shots:
        note = ", framed" if shot.get("framed") else ""
        print(f"{'image   ' if shot['ok'] else 'FAILED  '} {shot['file']}  ({shot['path']} at {shot['width']}x{shot['height']}{note})")
    print(f"capture_screens: {'OK' if not failed else 'FAIL'} ({len(shots) - len(failed)}/{len(shots)} captured). Look at each image before scoring.")
    return 0 if not failed else 1


if __name__ == "__main__":
    sys.exit(main())
